import frappe
from frappe.tests.utils import IntegrationTestCase


class TestWMSLocation(IntegrationTestCase):
	"""Validation tests for the physical WMS location tree."""

	def setUp(self):
		super().setUp()
		self.company = self.get_or_create_company()
		self.warehouse = self.make_warehouse("Primary")
		self.other_warehouse = self.make_warehouse("Secondary")

	def get_or_create_company(self):
		company = frappe.get_all("Company", pluck="name", limit=1)
		if company:
			return company[0]

		return frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": "WMS Location Test Company",
				"abbr": "WLTC",
				"default_currency": "USD",
				"country": "United States",
			}
		).insert(ignore_permissions=True).name

	def make_warehouse(self, label):
		return frappe.get_doc(
			{
				"doctype": "Warehouse",
				"warehouse_name": f"WMS Location Test {label} {frappe.generate_hash(6)}",
				"company": self.company,
				"is_group": 1,
			}
		).insert(ignore_permissions=True)

	def make_location(self, code, location_type, parent=None, **values):
		data = {
			"doctype": "WMS Location",
			"location_code": code,
			"location_name": code,
			"location_type": location_type,
			"parent_location": parent,
			"is_group": values.pop("is_group", location_type != "Bin"),
			"is_active": values.pop("is_active", 1),
			**values,
		}
		return frappe.get_doc(data)

	def test_full_hierarchy(self):
		root = self.make_location("TEST-WH-FULL", "Warehouse", erpnext_warehouse=self.warehouse.name).insert(
			ignore_permissions=True
		)
		zone = self.make_location("TEST-ZONE", "Zone", root.name).insert(ignore_permissions=True)
		aisle = self.make_location("TEST-A01", "Aisle", zone.name).insert(ignore_permissions=True)
		rack = self.make_location("TEST-R01", "Rack", aisle.name).insert(ignore_permissions=True)
		shelf = self.make_location("TEST-S01", "Shelf", rack.name).insert(ignore_permissions=True)
		bin_location = self.make_location("TEST-BIN-001", "Bin", shelf.name).insert(ignore_permissions=True)

		self.assertEqual(bin_location.erpnext_warehouse, self.warehouse.name)
		self.assertEqual(bin_location.company, self.company)
		self.assertGreater(bin_location.rgt, bin_location.lft)

	def test_simplified_warehouse_to_bin(self):
		root = self.make_location("TEST-WH-SIMPLE", "Warehouse", erpnext_warehouse=self.warehouse.name).insert(
			ignore_permissions=True
		)
		bin_location = self.make_location("TEST-BIN-SIMPLE", "Bin", root.name).insert(ignore_permissions=True)

		self.assertEqual(bin_location.parent_location, root.name)

	def test_missing_parent_is_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			self.make_location("TEST-NO-PARENT", "Zone").insert(ignore_permissions=True)

	def test_warehouse_requires_erpnext_warehouse(self):
		with self.assertRaises(frappe.ValidationError):
			self.make_location("TEST-NO-WAREHOUSE", "Warehouse").insert(ignore_permissions=True)

	def test_self_parent_is_rejected(self):
		root = self.make_location("TEST-SELF-PARENT", "Warehouse", erpnext_warehouse=self.warehouse.name).insert(
			ignore_permissions=True
		)
		root.parent_location = root.name

		with self.assertRaises(frappe.ValidationError):
			root.save(ignore_permissions=True)

	def test_circular_parent_is_rejected(self):
		root = self.make_location("TEST-CYCLE-ROOT", "Warehouse", erpnext_warehouse=self.warehouse.name).insert(
			ignore_permissions=True
		)
		first = self.make_location("TEST-CYCLE-FIRST", "Zone", root.name).insert(ignore_permissions=True)
		second = self.make_location("TEST-CYCLE-SECOND", "Zone", first.name).insert(ignore_permissions=True)
		first.parent_location = second.name

		with self.assertRaises(frappe.ValidationError):
			first.save(ignore_permissions=True)

	def test_leaf_location_cannot_have_children(self):
		root = self.make_location(
			"TEST-LEAF-ROOT", "Warehouse", erpnext_warehouse=self.warehouse.name, is_group=False
		).insert(ignore_permissions=True)

		with self.assertRaises(frappe.ValidationError):
			self.make_location("TEST-LEAF-CHILD", "Bin", root.name).insert(ignore_permissions=True)

	def test_cross_warehouse_child_is_rejected(self):
		root = self.make_location("TEST-CROSS-ROOT", "Warehouse", erpnext_warehouse=self.warehouse.name).insert(
			ignore_permissions=True
		)

		with self.assertRaises(frappe.ValidationError):
			self.make_location(
				"TEST-CROSS-CHILD", "Bin", root.name, erpnext_warehouse=self.other_warehouse.name
			).insert(ignore_permissions=True)

	def test_same_warehouse_hierarchy_is_allowed(self):
		root = self.make_location("TEST-SAME-ROOT", "Warehouse", erpnext_warehouse=self.warehouse.name).insert(
			ignore_permissions=True
		)
		child = self.make_location(
			"TEST-SAME-CHILD", "Bin", root.name, erpnext_warehouse=self.warehouse.name
		).insert(ignore_permissions=True)

		self.assertEqual(child.erpnext_warehouse, root.erpnext_warehouse)

	def test_inactive_parent_is_rejected_for_active_child(self):
		root = self.make_location(
			"TEST-INACTIVE-ROOT", "Warehouse", erpnext_warehouse=self.warehouse.name, is_active=False
		).insert(ignore_permissions=True)

		with self.assertRaises(frappe.ValidationError):
			self.make_location("TEST-INACTIVE-CHILD", "Bin", root.name).insert(ignore_permissions=True)

	def test_duplicate_location_code_is_rejected(self):
		self.make_location("TEST-DUPLICATE", "Warehouse", erpnext_warehouse=self.warehouse.name).insert(
			ignore_permissions=True
		)

		with self.assertRaises((frappe.DuplicateEntryError, frappe.ValidationError)):
			self.make_location("TEST-DUPLICATE", "Warehouse", erpnext_warehouse=self.other_warehouse.name).insert(
				ignore_permissions=True
			)
