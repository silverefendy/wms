import frappe
from frappe import _
from frappe.utils.nestedset import NestedSet


class WMSLocation(NestedSet):
	"""Physical WMS location arranged below an ERPNext Warehouse root."""

	nsm_parent_field = "parent_location"

	def validate(self):
		self.validate_location_type()
		self.validate_parent_location()
		self.validate_erpnext_warehouse()
		self.validate_group_state()
		self.validate_location_code()

	def validate_location_type(self):
		if self.location_type not in {"Warehouse", "Zone", "Aisle", "Rack", "Shelf", "Bin"}:
			frappe.throw(_("Location Type must be one of the supported WMS location types."))

	def validate_parent_location(self):
		if not self.parent_location:
			if self.location_type != "Warehouse":
				frappe.throw(_("Only a Warehouse location can be a root location."))
			return

		if self.location_type == "Warehouse":
			frappe.throw(_("A Warehouse location cannot have a parent location."))

		seen = {self.name} if self.name else set()
		parent_name = self.parent_location
		root = None

		while parent_name:
			if parent_name in seen:
				frappe.throw(_("Circular parent relationships are not allowed."))
			seen.add(parent_name)
			parent = frappe.get_doc("WMS Location", parent_name)

			if self.is_active and not parent.is_active:
				frappe.throw(_("An active location cannot have an inactive parent."))
			if not parent.is_group:
				frappe.throw(_("{0} is not a group location and cannot contain children.").format(parent.name))

			root = parent
			parent_name = parent.parent_location

		if not root or root.location_type != "Warehouse":
			frappe.throw(_("Every physical location must belong to a Warehouse root."))

		self.validate_inherited_context(root)

	def validate_inherited_context(self, root):
		if self.erpnext_warehouse and self.erpnext_warehouse != root.erpnext_warehouse:
			frappe.throw(_("A child location must use its root ERPNext Warehouse."))
		if self.company and self.company != root.company:
			frappe.throw(_("A child location must use its root Company."))
		if self.branch and self.branch != root.branch:
			frappe.throw(_("A child location must use its root Branch."))

		self.erpnext_warehouse = root.erpnext_warehouse
		self.company = root.company
		self.branch = root.branch

	def validate_erpnext_warehouse(self):
		if self.location_type == "Warehouse" and not self.erpnext_warehouse:
			frappe.throw(_("A Warehouse location must link to an ERPNext Warehouse."))

		if not self.erpnext_warehouse:
			return

		warehouse_company = frappe.db.get_value("Warehouse", self.erpnext_warehouse, "company")
		if not warehouse_company:
			frappe.throw(_("ERPNext Warehouse {0} was not found or has no Company.").format(self.erpnext_warehouse))

		if self.company and self.company != warehouse_company:
			frappe.throw(_("The WMS Location Company must match the ERPNext Warehouse Company."))
		self.company = warehouse_company

	def validate_group_state(self):
		if not self.is_group and frappe.db.exists(
			"WMS Location", {"parent_location": self.name, "name": ["!=", self.name]}
		):
			frappe.throw(_("A location with children must remain a group location."))

	def validate_location_code(self):
		if frappe.db.exists(
			"WMS Location", {"location_code": self.location_code, "name": ["!=", self.name]}
		):
			frappe.throw(_("Location Code must be unique within the WMS location model."))
