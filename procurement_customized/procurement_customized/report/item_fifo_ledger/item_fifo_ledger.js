// Copyright (c) 2016, Greycube and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Fifo Ledger"] = {
  filters: [
    {
      fieldname: "item",
      label: __("Item"),
      fieldtype: "Link",
      options: "Item",
      reqd: 1,
      get_query: () => {
        return {
          filters: {
            disabled: 0,
          },
        };
      },
    },
  ],
  onload: function (report) {},
};
