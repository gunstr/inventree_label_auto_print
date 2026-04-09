"""Triggers a print of a stock item label when a PO item is received"""

import structlog

from django.utils.translation import gettext_lazy as _

from plugin import InvenTreePlugin

from plugin.mixins import EventMixin, SettingsMixin

from stock.models import StockItem
from report.models import LabelTemplate

from plugin.builtin.labels.inventree_machine import get_machine_and_driver
from machine.machine_types import LabelPrinterBaseDriver, LabelPrinterMachine
from plugin.machine import call_machine_function, registry

from InvenTree.tasks import offload_task

from . import PLUGIN_VERSION

logger = structlog.get_logger('inventree_label_auto_print')


class InvenTreeLabelAutoPrint(EventMixin, SettingsMixin, InvenTreePlugin):
    """InvenTreeLabelAutoPrint - custom InvenTree plugin."""

    # Plugin metadata
    TITLE = "InvenTree Label Auto Print"
    NAME = "InvenTreeLabelAutoPrint"
    SLUG = "inventree-label-auto-print"
    DESCRIPTION = "Triggers a print of a stock item label when a PO item is received"
    VERSION = PLUGIN_VERSION

    # Additional project information
    AUTHOR = "gunstr"
    WEBSITE = "https://my-project-url.com"
    LICENSE = "MIT"

    # Optionally specify supported InvenTree versions
    MIN_VERSION = "1.0.0"
    # MAX_VERSION = '2.0.0'

    @staticmethod
    def get_label_choices() -> list[tuple[str, str]]:
        try:
            # Import the base template model
            from report.models import LabelTemplate

            # Filter for templates where the 'model_type' is 'stockitem'
            labels = LabelTemplate.objects.filter(model_type='stockitem')

            choices = [(str(l.pk), str(l.name)) for l in labels]
            return choices if choices else [("", "No Stock Item labels found")]

        except Exception as e:
            return [("", f"Error: {str(e)}")]

    @staticmethod
    def get_machine_choices() -> list[tuple[str, str]]:
        """
        Dynamically fetch registered machine instances.
        We import inside the function to avoid circular import issues 
        during InvenTree startup.
        """
        try:
            from machine.models import MachineConfig

            choices = [(str(m.pk), str(m.name)) for m in MachineConfig.objects.all()]

            # If empty, return a list of string tuples
            if not choices:
                return [("", "No printers found")]

            return choices

        except ImportError:
            # Fallback if the machine app is not enabled or version differs
            return [("", "Error loading machines")]

    # Plugin settings (from SettingsMixin)
    # Ref: https://docs.inventree.org/en/latest/plugins/mixins/settings/
    SETTINGS = {
        'SELECTED_LABEL': {
            'name': str(_('Label Template')),
            'description': str(_('Select a Stock Item label template')),
            'choices': get_label_choices,
        },
        'SELECTED_PRINTER': {
            'name': str(_('Label Printer')),
            'description': str(_('Select a machine to use as a label printer')),
            'choices': get_machine_choices,
        },
    }

    # Respond to InvenTree events (from EventMixin)
    # Ref: https://docs.inventree.org/en/latest/plugins/mixins/event/

    def wants_process_event(self, event: str) -> bool:
        """Return True if the plugin wants to process the given event."""
        # Process only the 'purchase order item received' event
        return event == "purchaseorderitem.received"

    def process_event(self, event: str, *args, **kwargs) -> None:
        """Process the provided event."""
        if event == 'purchaseorderitem.received':
            # Extract the stock item IDs from the event kwargs
            stock_item_ids: list[str] | None = kwargs.get('item_ids')

            # Retrieve the machine and label IDs from settings
            machine_pk = self.get_setting('SELECTED_PRINTER')
            label_pk = self.get_setting('SELECTED_LABEL')

            if not machine_pk:
                # Handle the case where no printer is selected yet
                logger.warning("No label printer selected.")
                return
            if not label_pk:
                # Handle the case where no label template is selected yet
                logger.warning("No label template selected.")
                return

            try:

                machine: LabelPrinterMachine | None = None
                driver: LabelPrinterBaseDriver | None = None
                machine, driver = get_machine_and_driver(machine_pk)

                if machine is None or driver is None:
                    logger.error("No valid machine or driver found for label printing.")
                    return

                # Iterate over the stock item IDs and add to a list of items to print
                items = [StockItem.objects.get(pk=stock_item_id) for stock_item_id in stock_item_ids] if stock_item_ids else []

                # Get the label template to use
                label = LabelTemplate.objects.get(pk=label_pk)

                # Call the machine function to print the labels
                # No need to offload this to a background task, as the machine driver will handle that internally if needed
                # and the process_event method is anyway already called in a background task context by InvenTree
                if label and items:
                    call_machine_function(
                        machine.pk,
                        'print_labels',
                        label,
                        items,
                        printing_options={'copies': 1},
                        group='plugin',
                    )

            except (StockItem.DoesNotExist, Exception) as e:
                # Log the error if needed
                logger.error(f"Error processing event '{event}': {e}")
