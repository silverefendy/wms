import unittest

import frappe


class TestWMSWeighbridgeTicket(unittest.TestCase):
	"""Validation tests for WMS Weighbridge Ticket."""

	def setUp(self):
		super().setUp()
		self.company = self.get_or_create_company()
		self.warehouse = self.make_warehouse("Primary")
		self.operator = self.get_or_create_user()

	def get_or_create_company(self):
		company = frappe.get_all("Company", pluck="name", limit=1)
		if company:
			return company[0]

		return frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": "WMS Weighbridge Test Company",
				"abbr": "WWTC",
				"default_currency": "USD",
				"country": "United States",
			}
		).insert(ignore_permissions=True).name

	def make_warehouse(self, label):
		return frappe.get_doc(
			{
				"doctype": "Warehouse",
				"warehouse_name": f"WMS Weighbridge Test {label} {frappe.generate_hash(6)}",
				"company": self.company,
				"is_group": 1,
			}
		).insert(ignore_permissions=True)

	def get_or_create_user(self):
		user = frappe.get_all("User", {"email": "weighbridge_operator@test.com"}, pluck="name", limit=1)
		if user:
			return user[0]

		return frappe.get_doc(
			{
				"doctype": "User",
				"email": "weighbridge_operator@test.com",
				"first_name": "Weighbridge",
				"last_name": "Operator",
			}
		).insert(ignore_permissions=True).name

	def make_reusable_container_item(self, item_code):
		return frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": item_code,
				"item_name": item_code,
				"item_group": "All Item Groups",
				"is_stock_item": 1,
				"has_serial_no": 1,
				"is_wms_reusable_container": 1,
				"stock_uom": "Nos",
				"valuation_method": "Moving Average",
			}
		).insert(ignore_permissions=True)

	def make_non_reusable_item(self, item_code):
		return frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": item_code,
				"item_name": item_code,
				"item_group": "All Item Groups",
				"is_stock_item": 1,
				"has_serial_no": 1,
				"is_wms_reusable_container": 0,
				"stock_uom": "Nos",
				"valuation_method": "Moving Average",
			}
		).insert(ignore_permissions=True)

	def make_serial_no(self, item_code, serial_no, rfid_tag=None, qr_code=None):
		return frappe.get_doc(
			{
				"doctype": "Serial No",
				"serial_no": serial_no,
				"item_code": item_code,
				"wms_rfid_tag": rfid_tag,
				"wms_qr_code": qr_code,
				"warehouse": self.warehouse.name,
				"status": "Active",
			}
		).insert(ignore_permissions=True)

	def make_ticket(self, ticket_number, **values):
		data = {
			"doctype": "WMS Weighbridge Ticket",
			"ticket_number": ticket_number,
			"ticket_datetime_in": frappe.utils.now(),
			"operator": self.operator,
			"gross_weight": 1000.0,
			"tare_weight": 200.0,
			"weight_uom": "Kg",
			"weight_tolerance_percent": 2.0,
			**values,
		}
		return frappe.get_doc(data)

	def test_net_weight_computed_correctly(self):
		ticket = self.make_ticket("TEST-001", gross_weight=1000.0, tare_weight=200.0)
		ticket.bags = []
		ticket.append(
			"bags",
			{
				"serial_no": self.make_serial_no(
					self.make_reusable_container_item("BIGBAG-001").name, "SN001"
				).name
			},
		)
		ticket.insert(ignore_permissions=True)
		self.assertEqual(ticket.net_weight, 800.0)

	def test_negative_net_weight_rejected(self):
		ticket = self.make_ticket("TEST-002", gross_weight=100.0, tare_weight=200.0)
		ticket.bags = []
		ticket.append(
			"bags",
			{
				"serial_no": self.make_serial_no(
					self.make_reusable_container_item("BIGBAG-002").name, "SN002"
				).name
			},
		)
		with self.assertRaises(frappe.ValidationError):
			ticket.insert(ignore_permissions=True)

	def test_non_reusable_container_item_rejected(self):
		item = self.make_non_reusable_item("NON-REUSABLE-001")
		serial = self.make_serial_no(item.name, "SN003")
		ticket = self.make_ticket("TEST-003")
		ticket.bags = []
		ticket.append("bags", {"serial_no": serial.name})
		with self.assertRaises(frappe.ValidationError):
			ticket.insert(ignore_permissions=True)

	def test_non_existent_serial_no_rejected(self):
		ticket = self.make_ticket("TEST-004")
		ticket.bags = []
		ticket.append("bags", {"serial_no": "NONEXISTENT-SN"})
		with self.assertRaises(frappe.ValidationError):
			ticket.insert(ignore_permissions=True)

	def test_duplicate_serial_no_rejected(self):
		item = self.make_reusable_container_item("BIGBAG-003")
		serial = self.make_serial_no(item.name, "SN004")
		ticket = self.make_ticket("TEST-005")
		ticket.bags = []
		ticket.append("bags", {"serial_no": serial.name})
		ticket.append("bags", {"serial_no": serial.name})
		with self.assertRaises(frappe.ValidationError):
			ticket.insert(ignore_permissions=True)

	def test_empty_bags_table_rejected(self):
		ticket = self.make_ticket("TEST-006")
		ticket.bags = []
		with self.assertRaises(frappe.ValidationError):
			ticket.insert(ignore_permissions=True)

	def test_status_defaults_to_draft(self):
		item = self.make_reusable_container_item("BIGBAG-004")
		serial = self.make_serial_no(item.name, "SN005")
		ticket = self.make_ticket("TEST-007")
		ticket.bags = []
		ticket.append("bags", {"serial_no": serial.name})
		ticket.insert(ignore_permissions=True)
		self.assertEqual(ticket.status, "Draft")

	def test_weight_tolerance_comparison_skipped_without_reference(self):
		item = self.make_reusable_container_item("BIGBAG-005")
		serial = self.make_serial_no(item.name, "SN006")
		ticket = self.make_ticket("TEST-008", reference_doctype=None, reference_name=None)
		ticket.bags = []
		ticket.append("bags", {"serial_no": serial.name})
		ticket.insert(ignore_permissions=True)
		self.assertEqual(ticket.status, "Draft")
