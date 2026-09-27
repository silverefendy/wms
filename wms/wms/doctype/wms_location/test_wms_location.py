import unittest

import frappe


class TestWMSLocation(unittest.TestCase):
	"""Validation tests for WMS Location."""

	def setUp(self):
		super().setUp()
		self.company = self.get_or_create_company()
		self.warehouse = self.make_warehouse("Primary")

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
				"is_group": 0,
			}
		).insert(ignore_permissions=True)

	def make_location(self, location_code, location_type, **kwargs):
		data = {
			"doctype": "WMS Location",
			"location_code": location_code,
			"location_name": location_code,
			"location_type": location_type,
			"is_group": location_type != "Bin" and location_type != "State",
			"is_active": 1,
			**kwargs,
		}
		return frappe.get_doc(data)

	def test_warehouse_root_location_created(self):
		"""Test that a Warehouse root location can be created."""
		location = self.make_location("WH-001", "Warehouse", erpnext_warehouse=self.warehouse.name)
		location.insert(ignore_permissions=True)
		self.assertEqual(location.location_type, "Warehouse")
		self.assertEqual(location.erpnext_warehouse, self.warehouse.name)
		self.assertEqual(location.is_group, 1)

	def test_warehouse_requires_erpnext_warehouse(self):
		"""Test that a Warehouse location must link to an ERPNext Warehouse."""
		location = self.make_location("WH-002", "Warehouse")
		with self.assertRaises(frappe.ValidationError):
			location.insert(ignore_permissions=True)

	def test_non_warehouse_requires_parent(self):
		"""Test that non-Warehouse locations must have a parent."""
		location = self.make_location("ZONE-001", "Zone")
		with self.assertRaises(frappe.ValidationError):
			location.insert(ignore_permissions=True)

	def test_warehouse_cannot_have_parent(self):
		"""Test that a Warehouse location cannot have a parent."""
		parent = self.make_location("WH-003", "Warehouse", erpnext_warehouse=self.warehouse.name)
		parent.insert(ignore_permissions=True)

		child = self.make_location("WH-004", "Warehouse", parent_location=parent.name)
		with self.assertRaises(frappe.ValidationError):
			child.insert(ignore_permissions=True)

	def test_child_inherits_warehouse_context(self):
		"""Test that child locations inherit warehouse context from root."""
		root = self.make_location("WH-005", "Warehouse", erpnext_warehouse=self.warehouse.name)
		root.insert(ignore_permissions=True)

		zone = self.make_location("ZONE-002", "Zone", parent_location=root.name)
		zone.insert(ignore_permissions=True)
		self.assertEqual(zone.erpnext_warehouse, self.warehouse.name)
		self.assertEqual(zone.company, self.company)

	def test_child_cannot_override_warehouse_context(self):
		"""Test that child locations cannot override inherited warehouse context."""
		root = self.make_location("WH-006", "Warehouse", erpnext_warehouse=self.warehouse.name)
		root.insert(ignore_permissions=True)

		other_warehouse = self.make_warehouse("Secondary")
		zone = self.make_location(
			"ZONE-003", "Zone", parent_location=root.name, erpnext_warehouse=other_warehouse.name
		)
		with self.assertRaises(frappe.ValidationError):
			zone.insert(ignore_permissions=True)

	def test_circular_parent_rejected(self):
		"""Test that circular parent relationships are rejected."""
		loc1 = self.make_location("WH-007", "Warehouse", erpnext_warehouse=self.warehouse.name)
		loc1.insert(ignore_permissions=True)

		loc2 = self.make_location("ZONE-004", "Zone", parent_location=loc1.name)
		loc2.insert(ignore_permissions=True)

		loc3 = self.make_location("AISLE-001", "Aisle", parent_location=loc2.name)
		loc3.insert(ignore_permissions=True)

		# Try to create a circular reference
		loc1.db_set("parent_location", loc3.name)
		with self.assertRaises(frappe.ValidationError):
			loc1.save()

	def test_active_location_requires_active_parent(self):
		"""Test that an active location cannot have an inactive parent."""
		root = self.make_location("WH-008", "Warehouse", erpnext_warehouse=self.warehouse.name)
		root.insert(ignore_permissions=True)

		zone = self.make_location("ZONE-005", "Zone", parent_location=root.name)
		zone.insert(ignore_permissions=True)

		# Deactivate the parent
		root.db_set("is_active", 0)

		# Try to save the child while parent is inactive
		zone.db_set("is_active", 1)
		with self.assertRaises(frappe.ValidationError):
			zone.save()

	def test_non_group_location_cannot_have_children(self):
		"""Test that a non-group location cannot have children."""
		root = self.make_location("WH-009", "Warehouse", erpnext_warehouse=self.warehouse.name)
		root.insert(ignore_permissions=True)

		zone = self.make_location("ZONE-006", "Zone", parent_location=root.name)
		zone.insert(ignore_permissions=True)

		aisle = self.make_location("AISLE-002", "Aisle", parent_location=zone.name)
		aisle.insert(ignore_permissions=True)

		rack = self.make_location("RACK-001", "Rack", parent_location=aisle.name)
		rack.insert(ignore_permissions=True)

		shelf = self.make_location("SHELF-001", "Shelf", parent_location=rack.name)
		shelf.insert(ignore_permissions=True)

		bin = self.make_location("BIN-001", "Bin", parent_location=shelf.name)
		bin.insert(ignore_permissions=True)

		# Try to add a child to the bin (which is not a group)
		child = self.make_location("CHILD-001", "Bin", parent_location=bin.name)
		with self.assertRaises(frappe.ValidationError):
			child.insert(ignore_permissions=True)

	def test_location_code_must_be_unique(self):
		"""Test that location codes must be unique."""
		loc1 = self.make_location("DUPLICATE", "Warehouse", erpnext_warehouse=self.warehouse.name)
		loc1.insert(ignore_permissions=True)

		loc2 = self.make_location("DUPLICATE", "Warehouse", erpnext_warehouse=self.warehouse.name)
		with self.assertRaises(frappe.ValidationError):
			loc2.insert(ignore_permissions=True)

	def test_state_location_requires_state_name(self):
		"""Test that State locations must have a state_name specified."""
		state = self.make_location("STATE-001", "State", erpnext_warehouse=self.warehouse.name)
		with self.assertRaises(frappe.ValidationError):
			state.insert(ignore_permissions=True)

	def test_state_location_cannot_have_parent(self):
		"""Test that State locations cannot have a parent in the physical tree."""
		root = self.make_location("WH-010", "Warehouse", erpnext_warehouse=self.warehouse.name)
		root.insert(ignore_permissions=True)

		state = self.make_location(
			"STATE-002", "State", parent_location=root.name, state_name="Receiving"
		)
		with self.assertRaises(frappe.ValidationError):
			state.insert(ignore_permissions=True)

	def test_state_location_requires_warehouse(self):
		"""Test that State locations must link to an ERPNext Warehouse."""
		state = self.make_location("STATE-003", "State", state_name="Receiving")
		with self.assertRaises(frappe.ValidationError):
			state.insert(ignore_permissions=True)

	def test_state_name_unique_per_warehouse(self):
		"""Test that state names are unique per warehouse."""
		state1 = self.make_location(
			"STATE-004", "State", erpnext_warehouse=self.warehouse.name, state_name="Receiving"
		)
		state1.insert(ignore_permissions=True)

		state2 = self.make_location(
			"STATE-005", "State", erpnext_warehouse=self.warehouse.name, state_name="Receiving"
		)
		with self.assertRaises(frappe.ValidationError):
			state2.insert(ignore_permissions=True)

	def test_state_location_with_different_warehouse_allowed(self):
		"""Test that the same state name can exist for different warehouses."""
		other_warehouse = self.make_warehouse("Other")

		state1 = self.make_location(
			"STATE-006", "State", erpnext_warehouse=self.warehouse.name, state_name="Receiving"
		)
		state1.insert(ignore_permissions=True)

		state2 = self.make_location(
			"STATE-007", "State", erpnext_warehouse=other_warehouse.name, state_name="Receiving"
		)
		state2.insert(ignore_permissions=True)
		self.assertEqual(state2.state_name, "Receiving")

	def test_full_hierarchy_creation(self):
		"""Test creating a full hierarchy: Warehouse -> Zone -> Aisle -> Rack -> Shelf -> Bin."""
		warehouse = self.make_location("WH-FULL", "Warehouse", erpnext_warehouse=self.warehouse.name)
		warehouse.insert(ignore_permissions=True)

		zone = self.make_location("ZONE-FULL", "Zone", parent_location=warehouse.name)
		zone.insert(ignore_permissions=True)

		aisle = self.make_location("AISLE-FULL", "Aisle", parent_location=zone.name)
		aisle.insert(ignore_permissions=True)

		rack = self.make_location("RACK-FULL", "Rack", parent_location=aisle.name)
		rack.insert(ignore_permissions=True)

		shelf = self.make_location("SHELF-FULL", "Shelf", parent_location=rack.name)
		shelf.insert(ignore_permissions=True)

		bin = self.make_location("BIN-FULL", "Bin", parent_location=shelf.name)
		bin.insert(ignore_permissions=True)

		# Verify the hierarchy
		self.assertEqual(bin.parent_location, shelf.name)
		self.assertEqual(shelf.parent_location, rack.name)
		self.assertEqual(rack.parent_location, aisle.name)
		self.assertEqual(aisle.parent_location, zone.name)
		self.assertEqual(zone.parent_location, warehouse.name)
		self.assertEqual(bin.erpnext_warehouse, self.warehouse.name)

	def test_simplified_hierarchy_warehouse_to_bin(self):
		"""Test that a simplified Warehouse -> Bin hierarchy is valid."""
		warehouse = self.make_location("WH-SIMPLE", "Warehouse", erpnext_warehouse=self.warehouse.name)
		warehouse.insert(ignore_permissions=True)

		bin = self.make_location("BIN-SIMPLE", "Bin", parent_location=warehouse.name)
		bin.insert(ignore_permissions=True)

		self.assertEqual(bin.parent_location, warehouse.name)
		self.assertEqual(bin.erpnext_warehouse, self.warehouse.name)

	def test_all_supported_location_types(self):
		"""Test that all supported location types can be created."""
		warehouse = self.make_location("WH-TYPES", "Warehouse", erpnext_warehouse=self.warehouse.name)
		warehouse.insert(ignore_permissions=True)

		for location_type in ["Zone", "Aisle", "Rack", "Shelf", "Bin"]:
			location = self.make_location(
				f"{location_type.upper()}-TYPE", location_type, parent_location=warehouse.name
			)
			location.insert(ignore_permissions=True)
			self.assertEqual(location.location_type, location_type)

	def test_invalid_location_type_rejected(self):
		"""Test that invalid location types are rejected."""
		location = self.make_location("INVALID", "InvalidType", erpnext_warehouse=self.warehouse.name)
		with self.assertRaises(frappe.ValidationError):
			location.insert(ignore_permissions=True)
