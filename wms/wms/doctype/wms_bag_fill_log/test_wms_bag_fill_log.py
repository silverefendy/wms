import unittest

import frappe


class TestWMSBagFillLog(unittest.TestCase):
	"""Validation and workflow tests for WMS Bag Fill Log."""

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
				"company_name": "WMS Bag Fill Test Company",
				"abbr": "WBFTC",
				"default_currency": "USD",
				"country": "United States",
			}
		).insert(ignore_permissions=True).name

	def make_warehouse(self, label):
		return frappe.get_doc(
			{
				"doctype": "Warehouse",
				"warehouse_name": f"WMS Bag Fill Test {label} {frappe.generate_hash(6)}",
				"company": self.company,
				"is_group": 0,
			}
		).insert(ignore_permissions=True)

	def get_or_create_user(self):
		user = frappe.get_all("User", {"email": "bagfill_operator@test.com"}, pluck="name", limit=1)
		if user:
			return user[0]

		return frappe.get_doc(
			{
				"doctype": "User",
				"email": "bagfill_operator@test.com",
				"first_name": "BagFill",
				"last_name": "Operator",
				"send_welcome_email": 0,
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

	def make_bulk_pellet_item(self, item_code):
		return frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": item_code,
				"item_name": item_code,
				"item_group": "All Item Groups",
				"is_stock_item": 1,
				"has_serial_no": 0,
				"stock_uom": "Kg",
				"valuation_method": "Moving Average",
			}
		).insert(ignore_permissions=True)

	def make_serial_no(self, item_code, serial_no):
		return frappe.get_doc(
			{
				"doctype": "Serial No",
				"serial_no": serial_no,
				"item_code": item_code,
				"warehouse": self.warehouse.name,
				"status": "Active",
			}
		).insert(ignore_permissions=True)

	def make_fill_log(self, fill_log_number, **values):
		data = {
			"doctype": "WMS Bag Fill Log",
			"fill_log_number": fill_log_number,
			"fill_datetime": frappe.utils.now(),
			"operator": self.operator,
			"qty_consumed": 500.0,
			"uom": "Kg",
			**values,
		}
		return frappe.get_doc(data)

	def test_bag_serial_not_reusable_container_rejected(self):
		item = self.make_non_reusable_item("NON-REUSABLE-BAG")
		serial = self.make_serial_no(item.name, "SN-NON-REUSABLE")
		bulk_item = self.make_bulk_pellet_item("BULK-PELLET")
		log = self.make_fill_log("TEST-001", source_item=bulk_item.name, source_warehouse=self.warehouse.name, bag_serial_no=serial.name)
		with self.assertRaises(frappe.ValidationError):
			log.insert(ignore_permissions=True)

	def test_qty_consumed_zero_rejected(self):
		item = self.make_reusable_container_item("BIGBAG-TEST")
		serial = self.make_serial_no(item.name, "SN-ZERO-QTY")
		bulk_item = self.make_bulk_pellet_item("BULK-PELLET-2")
		log = self.make_fill_log("TEST-002", source_item=bulk_item.name, source_warehouse=self.warehouse.name, bag_serial_no=serial.name, qty_consumed=0)
		with self.assertRaises(frappe.ValidationError):
			log.insert(ignore_permissions=True)

	def test_qty_consumed_negative_rejected(self):
		item = self.make_reusable_container_item("BIGBAG-TEST-2")
		serial = self.make_serial_no(item.name, "SN-NEG-QTY")
		bulk_item = self.make_bulk_pellet_item("BULK-PELLET-3")
		log = self.make_fill_log("TEST-003", source_item=bulk_item.name, source_warehouse=self.warehouse.name, bag_serial_no=serial.name, qty_consumed=-100)
		with self.assertRaises(frappe.ValidationError):
			log.insert(ignore_permissions=True)

	def test_source_item_non_stock_rejected(self):
		item = self.make_reusable_container_item("BIGBAG-TEST-3")
		serial = self.make_serial_no(item.name, "SN-NON-STOCK")
		non_stock_item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": "SERVICE-ITEM",
				"item_name": "Service Item",
				"item_group": "All Item Groups",
				"is_stock_item": 0,
				"stock_uom": "Nos",
			}
		).insert(ignore_permissions=True)
		log = self.make_fill_log("TEST-004", source_item=non_stock_item.name, source_warehouse=self.warehouse.name, bag_serial_no=serial.name)
		with self.assertRaises(frappe.ValidationError):
			log.insert(ignore_permissions=True)

	def test_insufficient_stock_causes_submission_failure(self):
		item = self.make_reusable_container_item("BIGBAG-TEST-4")
		serial = self.make_serial_no(item.name, "SN-NO-STOCK")
		bulk_item = self.make_bulk_pellet_item("BULK-PELLET-4")
		log = self.make_fill_log("TEST-005", source_item=bulk_item.name, source_warehouse=self.warehouse.name, bag_serial_no=serial.name, qty_consumed=10000.0)
		log.insert(ignore_permissions=True)
		with self.assertRaises(frappe.ValidationError):
			log.submit()
		self.assertEqual(log.status, "Draft")

	def test_submit_creates_stock_entry_and_sets_status_completed(self):
		item = self.make_reusable_container_item("BIGBAG-TEST-5")
		serial = self.make_serial_no(item.name, "SN-SUBMIT-TEST")
		bulk_item = self.make_bulk_pellet_item("BULK-PELLET-5")
		
		# Add some stock to the bulk item in the warehouse
		stock_entry = frappe.get_doc(
			{
				"doctype": "Stock Entry",
				"stock_entry_type": "Material Receipt",
				"purpose": "Material Receipt",
				"company": self.company,
				"items": [
					{
						"item_code": bulk_item.name,
						"warehouse": self.warehouse.name,
						"qty": 1000.0,
						"uom": "Kg",
						"transfer_qty": 1000.0,
						"transfer_uom": "Kg",
					}
				],
			}
		)
		stock_entry.insert(ignore_permissions=True)
		stock_entry.submit()

		log = self.make_fill_log("TEST-006", source_item=bulk_item.name, source_warehouse=self.warehouse.name, bag_serial_no=serial.name, qty_consumed=500.0)
		log.insert(ignore_permissions=True)
		log.submit()

		self.assertEqual(log.status, "Completed")
		self.assertIsNotNone(log.stock_entry)
		
		# Verify the Stock Entry exists and is submitted
		linked_stock_entry = frappe.get_doc("Stock Entry", log.stock_entry)
		self.assertEqual(linked_stock_entry.docstatus, 1)
		self.assertEqual(linked_stock_entry.stock_entry_type, "Manufacture")

	def test_cancel_cancels_stock_entry_and_sets_status_cancelled(self):
		item = self.make_reusable_container_item("BIGBAG-TEST-6")
		serial = self.make_serial_no(item.name, "SN-CANCEL-TEST")
		bulk_item = self.make_bulk_pellet_item("BULK-PELLET-6")
		
		# Add stock
		stock_entry = frappe.get_doc(
			{
				"doctype": "Stock Entry",
				"stock_entry_type": "Material Receipt",
				"purpose": "Material Receipt",
				"company": self.company,
				"items": [
					{
						"item_code": bulk_item.name,
						"warehouse": self.warehouse.name,
						"qty": 1000.0,
						"uom": "Kg",
						"transfer_qty": 1000.0,
						"transfer_uom": "Kg",
					}
				],
			}
		)
		stock_entry.insert(ignore_permissions=True)
		stock_entry.submit()

		log = self.make_fill_log("TEST-007", source_item=bulk_item.name, source_warehouse=self.warehouse.name, bag_serial_no=serial.name, qty_consumed=500.0)
		log.insert(ignore_permissions=True)
		log.submit()

		stock_entry_name = log.stock_entry
		log.cancel()

		self.assertEqual(log.status, "Cancelled")
		
		# Verify the Stock Entry is cancelled
		linked_stock_entry = frappe.get_doc("Stock Entry", stock_entry_name)
		self.assertEqual(linked_stock_entry.docstatus, 2)
