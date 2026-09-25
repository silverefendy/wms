import frappe
from frappe import _
from frappe.model.document import Document


class WMSWeighbridgeTicket(Document):
	def validate(self):
		self.validate_net_weight()
		self.validate_bags()
		self.validate_reference_weight()

	def validate_net_weight(self) -> None:
		"""Ensure net_weight is non-negative (gross - tare)."""
		self.net_weight = self.gross_weight - self.tare_weight
		if self.net_weight < 0:
			frappe.throw(_("Net Weight cannot be negative. Gross Weight must be greater than or equal to Tare Weight."))

	def validate_bags(self) -> None:
		"""Validate all bag serial numbers belong to reusable container items."""
		if not self.bags:
			frappe.throw(_("At least one bag must be specified in the Bags table."))

		seen_serials = set()
		for idx, bag in enumerate(self.bags, start=1):
			self._validate_bag_serial_exists(bag, idx)
			self._validate_bag_is_reusable_container(bag, idx)
			self._validate_duplicate_serial(bag.serial_no, seen_serials, idx)

	def _validate_bag_serial_exists(self, bag: dict, row_idx: int) -> None:
		"""Ensure the serial number exists and is active."""
		if not frappe.db.exists("Serial No", bag.serial_no):
			frappe.throw(
				_("Row {0}: Serial No {1} does not exist.").format(row_idx, bag.serial_no)
			)

		serial_status = frappe.db.get_value("Serial No", bag.serial_no, "status")
		if serial_status not in ("Active", "In Stock"):
			frappe.throw(
				_(
					"Row {0}: Serial No {1} is not in an active state (current status: {2})."
				).format(row_idx, bag.serial_no, serial_status)
			)

	def _validate_bag_is_reusable_container(self, bag: dict, row_idx: int) -> None:
		"""Ensure the serial's item is flagged as a WMS reusable container."""
		item_code = frappe.db.get_value("Serial No", bag.serial_no, "item_code")
		if not item_code:
			frappe.throw(
				_("Row {0}: Serial No {1} has no associated Item.").format(row_idx, bag.serial_no)
			)

		is_reusable = frappe.db.get_value("Item", item_code, "is_wms_reusable_container")
		if not is_reusable:
			frappe.throw(
				_(
					"Row {0}: Serial No {1} belongs to Item {2}, which is not flagged as a WMS Reusable Container."
				).format(row_idx, bag.serial_no, item_code)
			)

	def _validate_duplicate_serial(self, serial_no: str, seen_serials: set, row_idx: int) -> None:
		"""Reject duplicate serial numbers within the same ticket."""
		if serial_no in seen_serials:
			frappe.throw(
				_("Row {0}: Serial No {1} is duplicated in this ticket.").format(row_idx, serial_no)
			)
		seen_serials.add(serial_no)

	def validate_reference_weight(self) -> None:
		"""Compare net_weight against reference document if linked."""
		if not self.reference_doctype or not self.reference_name:
			self.status = "Draft"
			return

		# Skip automatic comparison if the reference document type is ambiguous
		# or the comparable weight/quantity field is uncertain for this ERPNext v16 installation.
		# This is documented as an open question in the PR description.
		self.status = "Draft"
