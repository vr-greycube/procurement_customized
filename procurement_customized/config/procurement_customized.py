from __future__ import unicode_literals
import frappe
from frappe import _


def get_data():
    return [
        {
            "label": _("Documents"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Item Board Price",
                    "description": _("Item Board Price"),
                    "label": _("Item Board Price"),
                },
            ],
        },
        {
            "label": _("Setup"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Procurement Customized Settings",
                    "description": _("Procurement Customized Settings"),
                    "label": _("Procurement Customized Settings"),
                    "route": "#Form/Procurement Customized Settings",
                    "condition": frappe.utils.has_common(
                        ["System Manager"], frappe.get_roles()
                    ),
                },
            ],
        },
        {
            "label": _("Reports"),
            "items": [
                {
                    "name": "Item Fifo Ledger",
                    "type": "report",
                    "module_name": "Procurement Customized",
                    "label": _("Item Fifo Ledger"),
                    "route": "#query-report/Item Fifo Ledger",
                },
            ],
        },
    ]
