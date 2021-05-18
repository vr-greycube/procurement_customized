# Copyright (c) 2013, Greycube and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.utils import cstr


def execute(filters=None):
    columns, data = get_columns(), get_data(filters)
    return columns, data


def get_data(filters):
    # PO DATE	Po No	Po Qty	Rate	Till date recived qty	Till date utilized qty
    # Utilized PO number 	Balance Qty	Cummulative Balance	Total po value	Utilized qty po vlaue	Bal vlaue
    out = frappe.db.sql(
        """
    select 
        po.transaction_date po_date,
        po.name po_name,
        poi.qty qty,
        poi.rate,
        coalesce(r.qty,0) received_qty,
        poi.qty - coalesce(r.qty,0) balance_qty,
        poi.qty * poi.rate total_value
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
            `tabPurchase Receipt Item` pri on pri.parent = pr.name
        where 
            pr.docstatus = 1 and pri.item_code = %(item)s
        group by 
            pri.purchase_order, pri.item_code
    ) r on r.purchase_order = po.name and r.item_code = poi.item_code
    where 
        po.docstatus = 1 
        and poi.item_code = %(item)s
    order by po.transaction_date, po.creation
    """,
        filters,
        as_dict=True,
    )
    utilized = get_utilized(filters)
    print(utilized)
    cumulative_balance = 0

    for d in out:
        d.utilized_po, d.td_utilized, d.cum_balance_qty = [], 0, 0
        cumulative_balance += d.get("balance_qty", 0)
        d.cum_balance_qty += cumulative_balance
        while utilized and d.received_qty > d.td_utilized:
            d.utilized_po.append(cstr(utilized[0].remarks) or "?")
            if (d.received_qty - d.td_utilized) > utilized[0].transfer_qty:
                d.td_utilized += utilized.pop(0).transfer_qty
            else:
                utilized[0].transfer_qty -= d.received_qty - d.td_utilized
                d.td_utilized = d.received_qty
        d.utilized_po = ", ".join(d.utilized_po)
        d.utilized_po_value = d.td_utilized * d.rate
        d.balance_value = d.total_value - d.utilized_po_value
    return out


def get_utilized(filters):
    filters["from_warehouse"] = frappe.db.get_single_value(
        "Procurement Customized Settings", "material_transfer_from_warehouse"
    )
    filters["to_warehouse"] = frappe.db.get_single_value(
        "Procurement Customized Settings", "material_transfer_to_warehouse"
    )

    print(filters)

    return frappe.db.sql(
        """
    select 
        posting_date, posting_time, sed.transfer_qty, remarks
    from 
        `tabStock Entry` se
    inner join 
        `tabStock Entry Detail` sed on sed.parent = se.name
    where 
        se.purpose='Material Transfer' and se.docstatus = 1
        and sed.item_code = %(item)s
        and sed.s_warehouse = %(from_warehouse)s
        and sed.t_warehouse = %(to_warehouse)s
    order by 
        se.posting_date, se.posting_time
    """,
        filters,
        as_dict=True,
    )


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
            "fieldname": "td_utilized",
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
