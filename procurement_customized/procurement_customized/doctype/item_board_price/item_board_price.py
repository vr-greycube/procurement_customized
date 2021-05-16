# -*- coding: utf-8 -*-
# Copyright (c) 2021, Greycube and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe.utils import cstr
from frappe.model.document import Document


class ItemBoardPrice(Document):
    def autoname(self):
        self.name = "{0}_{1}".format(
            self.item, cstr(self.board_price_per_kg).replace(".", "_")
        )
