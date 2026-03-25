"""Triggers a print of a stock item label when a PO item is received"""

from plugin import InvenTreePlugin

from plugin.mixins import EventMixin, SettingsMixin

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

    # Respond to InvenTree events (from EventMixin)
    # Ref: https://docs.inventree.org/en/latest/plugins/mixins/event/
    def wants_process_event(self, event: str) -> bool:
        """Return True if the plugin wants to process the given event."""
        # Example: only process the 'create part' event
        return event == "part_part.created"

    def process_event(self, event: str, *args, **kwargs) -> None:
        """Process the provided event."""
        print("Processing custom event:", event)
        print("Arguments:", args)
        print("Keyword arguments:", kwargs)
