# -*- coding: utf-8 -*-
# Copyright (c) 2015, nodux and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json
import copy
from frappe import throw, _
from frappe.utils import flt, cint

class NoduxPricingRule(Document):
	def validate(self):
		self.validate_mandatory()
		self.validate_applicable_for_selling()
		#self.validate_min_max_qty()
		#self.cleanup_fields_value()
		#self.validate_price_or_discount()
		#self.validate_max_discount()
		self.validate_selling_price()
		self.validate_price_or_discount()

		if not self.margin_type: self.margin_rate_or_amount = 0.0

	def validate_mandatory(self):
		for field in ["apply_on"]:
			tocheck = frappe.scrub(self.get(field) or "")
			if tocheck and not self.get(tocheck):
				throw(_("{0} is required").format(self.meta.get_label(tocheck)), frappe.MandatoryError)

	def validate_applicable_for_selling(self):
		if not self.selling:
			throw(_("Selling must be selected for applying discount"))

    #Validar único precio de venta
	def validate_selling_price(self):
		if cint(self.definir_como_precio_de_venta):
			if frappe.db.get_value("Nodux Pricing Rule", {"definir_como_precio_de_venta": 1}):
				throw(_("Ya se encuentra definido un valor como precio de venta"))

 	def validate_price_or_discount(self):
		for field in ["Margin Rate or Amount"]:
			if flt(self.get(frappe.scrub(field))) < 0:
				throw(_("{0} can not be negative").format(field))
	

@frappe.whitelist()
def apply_pricing_rule(args):
	"""
		args = {
			"items": [{"doctype": "", "name": "", "item_code": "", "brand": "", "item_group": ""}, ...],
			"customer": "something",
			"customer_group": "something",
			"territory": "something",
			"supplier": "something",
			"supplier_type": "something",
			"currency": "something",
			"conversion_rate": "something",
			"price_list": "something",
			"plc_conversion_rate": "something",
			"company": "something",
			"transaction_date": "something",
			"campaign": "something",
			"sales_partner": "something",
			"ignore_pricing_rule": "something"
		}
	"""

	if isinstance(args, basestring):
		args = json.loads(args)

	args = frappe._dict(args)

	if not args.transaction_type:
		set_transaction_type(args)

	# list of dictionaries
	out = []

	if args.get("doctype") == "Material Request": return out

	item_list = args.get("items")
	args.pop("items")

	for item in item_list:
		args_copy = copy.deepcopy(args)
		args_copy.update(item)
		out.append(get_pricing_rule_for_item(args_copy))

	return out

def get_serial_no_for_item(args):
	from erpnext.stock.get_item_details import get_serial_no

	item_details = frappe._dict({
		"doctype": args.doctype,
		"name": args.name,
		"serial_no": args.serial_no
	})
	if args.get("parenttype") in ("Sales Invoice", "Delivery Note") and args.stock_qty > 0:
		item_details.serial_no = get_serial_no(args)
	return item_details

def get_pricing_rule_for_item(args):
	if args.get("parenttype") == "Material Request": return {}

	item_details = frappe._dict({
		"doctype": args.doctype,
		"name": args.name,
		"pricing_rule": None
	})
	
	if args.ignore_pricing_rule or not args.item_code:
		if frappe.db.exists(args.doctype, args.name) and args.get("pricing_rule"):
			item_details = remove_pricing_rule_for_item(args.get("pricing_rule"), item_details)
		return item_details

	if not (args.item_group and args.brand):
		try:
			args.item_group, args.brand = frappe.db.get_value("Item", args.item_code, ["item_group", "brand"])
		except TypeError:
			# invalid item_code
			return item_details
		if not args.item_group:
			frappe.throw(_("Item Group not mentioned in item master for item {0}").format(args.item_code))

	if args.transaction_type=="selling":
		if args.customer and not (args.customer_group and args.territory):
			customer = frappe.db.get_value("Customer", args.customer, ["customer_group", "territory"])
			if customer:
				args.customer_group, args.territory = customer

		args.supplier = args.supplier_type = None

	elif args.supplier and not args.supplier_type:
		args.supplier_type = frappe.db.get_value("Supplier", args.supplier, "supplier_type")
		args.customer = args.customer_group = args.territory = None

	pricing_rules = get_pricing_rules(args)
	pricing_rule = filter_pricing_rules(args, pricing_rules)

	if pricing_rule:
		item_details.pricing_rule = pricing_rule.name
		item_details.pricing_rule_for = pricing_rule.price_or_discount
		item_details.margin_type = pricing_rule.margin_type
		item_details.margin_rate_or_amount = pricing_rule.margin_rate_or_amount
		if pricing_rule.price_or_discount == "Price":
			item_details.update({
				"price_list_rate": (pricing_rule.price/flt(args.conversion_rate)) * args.conversion_factor or 1.0 \
					if args.conversion_rate else 0.0,
				"discount_percentage": 0.0
			})
		else:
			item_details.discount_percentage = pricing_rule.discount_percentage
	elif args.get('pricing_rule'):
		item_details = remove_pricing_rule_for_item(args.get("pricing_rule"), item_details)

	return item_details


def set_transaction_type(args):
	if args.doctype in ("Opportunity", "Quotation", "Sales Order", "Delivery Note", "Sales Invoice"):
		args.transaction_type = "selling"
	elif args.doctype in ("Material Request", "Supplier Quotation", "Purchase Order",
		"Purchase Receipt", "Purchase Invoice"):
			args.transaction_type = "buying"
	elif args.customer:
		args.transaction_type = "selling"
	else:
		args.transaction_type = "buying"

	