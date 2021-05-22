// Copyright (c) 2021, Greycube and contributors
// For license information, please see license.txt

frappe.ui.form.on("Item Board Price", {
  board_price_per_kg: function (frm) {
    frm.trigger("set_calculated_values");
  },

  length: function (frm) {
    frm.trigger("set_calculated_values");
  },

  breadth: function (frm) {
    frm.trigger("set_calculated_values");
  },

  gsm: function (frm) {
    frm.trigger("set_calculated_values");
  },

  wastage: function (frm) {
    frm.trigger("set_calculated_values");
  },

  finished_goods_tax: function (frm) {
    frm.trigger("set_calculated_values");
  },

  raw_material_tax: function (frm) {
    frm.trigger("set_calculated_values");
  },

  processing_share: function (frm) {
    frm.trigger("set_calculated_values");
  },

  set_calculated_values: function (frm) {
    let doc = frm.doc,
      weight = doc.length * doc.breadth * doc.gsm * 144 * 0.0000001,
      actual_price_with_wastage =
        ((doc.board_price_per_kg * weight) / 144 / doc.ups) *
        (1 + 0.01 * doc.wastage) *
        1000,
      total_price_actual_wastage_processing =
        actual_price_with_wastage + doc.processing_share,
      total_roundup = Math.ceil(total_price_actual_wastage_processing),
      total_with_fg_tax = total_roundup * (1 + 0.01 * doc.finished_goods_tax),
      process_price_per_unit =
        (total_with_fg_tax -
          actual_price_with_wastage * (1 + 0.01 * doc.raw_material_tax)) *
        0.001,
      raw_material_per_unit =
        total_with_fg_tax * 0.001 - process_price_per_unit;

    frm.set_value("weight", weight);
    frm.set_value("actual_price_with_wastage", actual_price_with_wastage);
    frm.set_value(
      "total_price_actual_wastage_processing",
      total_price_actual_wastage_processing
    );
    frm.set_value("total_roundup", total_roundup);
    frm.set_value("total_with_fg_tax", total_with_fg_tax);
    frm.set_value("process_price_per_unit", process_price_per_unit);
    frm.set_value("raw_material_per_unit", raw_material_per_unit);
  },
});
