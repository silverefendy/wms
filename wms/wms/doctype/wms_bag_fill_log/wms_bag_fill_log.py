import frappe
from frappe import _
from frappe.model.document import Document


class WMSBagFillLog(Document):
	def validate(self):
		self.validate_bag_serial()
		self.validate_qty_consumed()
		self.validate_source_item()

	def validate_bag_serial(self) -> None:
		"""Ensure bag_serial_no exists, is active, and belongs to a reusable container."""
		if not frappe.db.exists("Serial No", self.bag_serial_no):
			frappe.throw(_("Serial No {0} does not exist.").format(self.bag_serial_no))

		serial_status = frappe.db.get_value("Serial No", self.bag_serial_no, "status")
		if serial_status not in ("Active", "In Stock"):
			frappe.throw(
				_(
					"Serial No {0} is not in an active state (current status: {1})."
				).format(self.bag_serial_no, serial_status)
			)

		item_code = frappe.db.get_value("Serial No", self.bag_serial_no, "item_code")
		if not item_code:
			frappe.throw(_("Serial No {0} has no associated Item.").format(self.bag_serial_no))

		is_reusable = frappe.db.get_value("Item", item_code, "is_wms_reusable_container")
		if not is_reusable:
			frappe.throw(
				_(
					"Serial No {0} belongs to Item {1}, which is not flagged as a WMS Reusable Container."
				).format(self.bag_serial_no, item_code)
			)

	def validate_qty_consumed(self) -> None:
		"""Ensure qty_consumed is greater than 0."""
		if self.qty_consumed <= 0:
			frappe.throw(_("Qty Consumed must be greater than 0."))

	def validate_source_item(self) -> None:
		"""Ensure source_item exists and is a stock item."""
		if not frappe.db.exists("Item", self.source_item):
			frappe.throw(_("Source Item {0} does not exist.").format(self.source_item))

		is_stock_item = frappe.db.get_value("Item", self.source_item, "is_stock_item")
		if not is_stock_item:
			frappe.throw(_("Source Item {0} is not a stock item.").format(self.source_item))

	def on_submit(self) -> None:
		"""Create and submit a Stock Entry (Manufacture) for the bag fill operation."""
		bag_item_code = frappe.db.get_value("Serial No", self.bag_serial_no, "item_code")
		if not bag_item_code:
			frappe.throw(_("Serial No {0} has no associated Item.").format(self.bag_serial_no))

		stock_entry = frappe.get_doc(
			{
				"doctype": "Stock Entry",
				"stock_entry_type": "Manufacture",
				"purpose": "Manufacture",
				"company": frappe.db.get_value("Warehouse", self.source_warehouse, "company"),
				"items": [
					{
						"item_code": self.source_item,
						"warehouse": self.source_warehouse,
						"qty": self.qty_consumed,
						"uom": self.uom if self.uom else frappe.db.get_value("Item", self.source_item, "stock_uom"),
						"transfer_qty": self.qty_consumed,
						"transfer_uom": self.uom if self.uom else frappe.db.get_value("Item", self.source_item, "stock_uom"),
						"is_finished_item": 0,
						"is_sub_contracted_item": 0,
					},
					{
						"item_code": bag_item_code,
						"warehouse": self.source_warehouse,
						"qty": 1,
						"uom": frappe.db.get_value("Item", bag_item_code, "stock_uom"),
						"transfer_qty": 1,
						"transfer_uom": frappe.db.get_value("Item", bag_item_code, "stock_uom"),
						"serial_no": self.bag_serial_no,
						"is_finished_item": 1,
						"is_sub_contracted_item": 0,
					},
				],
			}
		)

		try:
			stock_entry.insert(ignore_permissions=True)
			stock_entry.submit()
		except Exception as e:
			frappe.throw(
				_(
					"Failed to create or submit Stock Entry: {0}. Please check stock availability and item configuration."
				).format(str(e))
			)

		self.stock_entry = stock_entry.name
		self.status = "Completed"
		self.db_set("stock_entry", stock_entry.name)
		self.db_set("status", "Completed")

	def on_cancel(self) -> None:
		"""Cancel the linked Stock Entry and set status to Cancelled."""
		if not self.stock_entry:
			frappe.throw(_("No Stock Entry linked to this Fill Log."))

		if not frappe.db.exists("Stock Entry", self.stock_entry):
			frappe.throw(_("Linked Stock Entry {0} does not exist.").format(self.stock_entry))

		stock_entry_doc = frappe.get_doc("Stock Entry", self.stock_entry)
		if stock_entry_doc.docstatus == 0:
			frappe.throw(_("Linked Stock Entry {0} is not submitted.").format(self.stock_entry))

		if stock_entry_doc.docstatus == 2:
			self.status = "Cancelled"
			self.db_set("status", "Cancelled")
			return

		try:
			stock_entry_doc.cancel()
		except Exception as e:
			frappe.throw(_("Failed to cancel Stock Entry {0}: {1}").format(self.stock_entry, str(e)))

		self.status = "Cancelled"
		self.db_set("status", "Cancelled")
