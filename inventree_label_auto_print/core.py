"""Triggers a print of a stock item label when a PO item is received"""

from venv import logger

from plugin import InvenTreePlugin

from plugin.mixins import EventMixin, SettingsMixin

from stock.models import StockItem
from report.models import LabelTemplate
import report.helpers

from plugin.builtin.labels.inventree_machine import get_machine_and_driver
from machine.machine_types import LabelPrinterBaseDriver, LabelPrinterMachine
from plugin.machine import call_machine_function, registry

from InvenTree.tasks import offload_task

from . import PLUGIN_VERSION


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
    # MIN_VERSION = '0.18.0'
    # MAX_VERSION = '2.0.0'

    # Plugin settings (from SettingsMixin)
    # Ref: https://docs.inventree.org/en/latest/plugins/mixins/settings/
    SETTINGS = {
        # Define your plugin settings here...
        "CUSTOM_VALUE": {
            "name": "Custom Value",
            "description": "A custom value",
            "validator": int,
            "default": 42,
        }
    }

    QL700_UUID = "8a74d153-55f4-422f-8e86-a2d90cf78466"

    # Respond to InvenTree events (from EventMixin)
    # Ref: https://docs.inventree.org/en/latest/plugins/mixins/event/
    def wants_process_event(self, event: str) -> bool:
        """Return True if the plugin wants to process the given event."""
        # Example: only process the 'create part' event
        return event == "purchaseorderitem.received"

    def process_event(self, event: str, *args, **kwargs) -> None:
        """Process the provided event."""
        if event == 'purchaseorderitem.received':
            stock_item_ids: list[str] | None = kwargs.get('item_ids')

            try:

                machine: LabelPrinterMachine | None = None
                driver: LabelPrinterBaseDriver | None = None
                machine, driver = get_machine_and_driver(self.QL700_UUID)

                if machine is None or driver is None:
                    logger.error("No valid machine or driver found for label printing.")
                    return

                # 1. Get the newly created stock item
                item = [StockItem.objects.get(pk=stock_item_ids[0])] if stock_item_ids else []

                # Get the label template you want to use
                label = LabelTemplate.objects.get(pk=7)  # Get your label template

                if label and item:
                    offload_task(
                        call_machine_function,
                        machine.pk,
                        'print_labels',
                        label,
                        item,
                        printing_options={'copies': 1},
                        group='plugin',
                    )

            except (StockItem.DoesNotExist, Exception) as e:
                # Log the error if needed
                print(f"AutoPrint Error: {e}")
