# InvenTreeLabelAutoPrint

Triggers a print of a stock item label when a PO item is received. The plugin assumes that label printers has been registered in the InvenTree machine plugin registry, and that a label template has been created for the stock item labels.

## Installation

### InvenTree Plugin Manager

Open the Plugin Manager and add this plugin with the following setting:

- Package name: `inventree_label_auto_print`
- Source URL: `git+https://github.com/gunstr/inventree_label_auto_print.git`

Version: Select the version to install

Enable `Confirm plugin installation` and click Install

Once the installation is ready, activate the plugin

### Command Line 

To install manually via the command line, run the following command:

```bash
pip install install git+https://github.com/gunstr/inventree_label_auto_print
```

## Configuration

There are two settings for the plugin

- Label printing machine: Select the machine to use for label printing. This should be a machine that has a driver which supports label printing (e.g. a Brother printer with the appropriate driver).
- Label template: Select the template to use for generating the labels.


## Usage

When the plugin is installed and configured, it will automatically print labels for stock items when a purchase order item is received. The plugin listens for the `purchaseorderitem.received` event, and when this event is triggered, it retrieves the associated stock items and sends them to the selected machine for printing using the selected label template.

The labels will be printed also when items are received using the InvenTree mobile app, as the same event is triggered regardless of how the items are received.
