# Copyright (c) 2013, Greycube and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from typing import Deque

import frappe
from frappe import _
from frappe.utils import cstr


def execute(filters=None):
    columns, data = get_columns(), get_data(filters)
    return columns, data


def get_data(filters):
    filters["from_warehouse"] = frappe.db.get_single_value(
        "Procurement Customized Settings", "material_transfer_from_warehouse"
    )
    filters["to_warehouse"] = frappe.db.get_single_value(
        "Procurement Customized Settings", "material_transfer_to_warehouse"
    )

    out = frappe.db.sql(
        """
    select 
        po.transaction_date po_date,
        po.name po_name,
        poi.qty qty,
        poi.rate,
        coalesce(rec.qty,0) received_qty,
        poi.qty - coalesce(ste.utilized_qty,0) balance_qty, 
        poi.qty * poi.rate total_value,
        ste.utilized_qty,
        ste.utilized_po, 
        ste.utilized_qty * poi.rate utilized_po_value,
        (poi.qty - coalesce(ste.utilized_qty,0)) * poi.rate balance_value
    from 
        `tabPurchase Order` po
    inner join 
        `tabPurchase Order Item` poi on poi.parent = po.name
    left outer join (
        select 
            pri.purchase_order, pri.item_code, sum(pri.received_qty) qty 
        from 
            `tabPurchase Receipt` pr
        inner join 
            `tabPurchase Receipt Item` pri on pri.parent = pr.name and pr.docstatus = 1 
        group by 
            pri.purchase_order, pri.item_code
    ) rec on rec.purchase_order = po.name 
    left outer join (
    	    select 
		        sed.purchase_order_cf, sed.item_code, sum(sed.transfer_qty) utilized_qty, 
		        GROUP_CONCAT(coalesce(remarks,'')) utilized_po
		    from 
		        `tabStock Entry` se
		    inner join 
		        `tabStock Entry Detail` sed on sed.parent = se.name
		    where 
		        se.purpose='Material Transfer' and se.docstatus = 1
 		        and sed.s_warehouse = %(from_warehouse)s
 		        and sed.t_warehouse = %(to_warehouse)s
		   group by sed.purchase_order_cf
    ) ste on ste.purchase_order_cf= po.name and ste.item_code = poi.item_code
    where 
        po.docstatus = 1 
        and poi.item_code = %(item)s
        and rec.item_code = poi.item_code
    order by po.transaction_date, po.creation""",
        filters,
        as_dict=True,
        debug=True,
    )
    cumulative_balance = 0

    for d in out:
        cumulative_balance += d.get("balance_qty", 0)
        d.cum_balance_qty = cumulative_balance
    return out


def get_columns():
    return [
        {
            "label": _("PO Date"),
            "fieldname": "po_date",
            "fieldtype": "Date",
            "width": 90,
        },
        {
            "label": _("PO #"),
            "fieldname": "po_name",
            "fieldtype": "Link",
            "options": "Purchase Order",
            "width": 180,
        },
        {
            "label": _("PO Qty"),
            "fieldname": "qty",
            "fieldtype": "Int",
            "width": 70,
        },
        {
            "label": _("Rate"),
            "fieldname": "rate",
            "fieldtype": "Currency",
            "width": 90,
        },
        {
            "label": _("Till Date Received Qty"),
            "fieldname": "received_qty",
            "fieldtype": "Int",
            "width": 120,
        },
        {
            "label": _("Till Date Utilized Qty"),
            "fieldname": "utilized_qty",
            "fieldtype": "Int",
            "width": 120,
        },
        {
            "label": _("Utilized PO#"),
            "fieldname": "utilized_po",
            "fieldtype": "Data",
            "width": 190,
        },
        {
            "label": _("Balance Qty"),
            "fieldname": "balance_qty",
            "fieldtype": "Int",
            "width": 90,
        },
        {
            "label": _("Cum. Balance"),
            "fieldname": "cum_balance_qty",
            "fieldtype": "Int",
            "width": 90,
        },
        {
            "label": _("Utilized PO Value"),
            "fieldname": "utilized_po_value",
            "fieldtype": "Currency",
            "width": 90,
        },
        {
            "label": _("Balance Value"),
            "fieldname": "balance_value",
            "fieldtype": "Currency",
            "width": 90,
        },
    ]
