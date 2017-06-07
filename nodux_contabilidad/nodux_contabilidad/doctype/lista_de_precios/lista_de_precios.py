# -*- coding: utf-8 -*-
# Copyright (c) 2015, nodux and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _, throw
from frappe.utils import cint, flt
import frappe.defaults

class ListadePrecios(Document):
	def validate(self):
		if not cint(self.selling):
			throw(_("Price List must be applicable for Selling"))
		#else:
			#if not frappe.db.get_value("Products", {"lista_precios":"self.price_list_name"}):
				#frappe.set_value("Products", "Products", "lista_precios", self.price_list_name)


		self.validate_price_or_discount()
		self.validate_selling_price()
		#self.set_default_if_missing()
		self.validate_new_formula()


	#def on_update(self):
	#	self.set_default_if_missing()
	

	def validate_price_or_discount(self):
		for field in ["Porcentaje"]:
			if flt(self.get(frappe.scrub(field))) < 0:
				throw(_("{0} can not be negative").format(field))

	def set_default_if_missing(self):
		if cint(self.selling):
			if not frappe.db.get_value("Products", {"lista_precios":("like self.price_list_name")}, "lista_precios"):
				frappe.set_value("Products", "Products", "lista_precios", self.price_list_name)
		

	def validate_selling_price(self):
		if cint(self.definir):
			if frappe.db.get_value("Lista de Precios", {"enabled": 1}):
				throw(_("Ya se encuentra definido un valor como precio de venta"))
	
	def validate_new_formula(self):
		if cint(self.nueva_formula):
			porcentaje = self.porcentaje
			formula = "product.cost_price / (1 - ", porcentaje,")"
			return formula
			throw(_(formula))
