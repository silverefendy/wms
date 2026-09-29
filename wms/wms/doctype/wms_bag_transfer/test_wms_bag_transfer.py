import unittest

import frappe

from wms.wms.doctype.wms_bag_transfer.wms_bag_transfer import (
	cancel_transfer,
	confirm_by_scan,
	confirm_receipt,
	send_transfer,
)


class TestWMSBagTransfer(unittest.TestCase):
	"""Alur Draft, Dikirim, dan konfirmasi terima untuk WMS Bag Transfer."""

	def setUp(self):
		super().setUp()
		self.company = frappe.get_all("Company", pluck="name", limit=1)[0]
		self.parent = self.make_warehouse("TBT Parent", is_group=1)
		self.wh_a = self.make_warehouse("TBT A", parent=self.parent)
		self.wh_b = self.make_warehouse("TBT B", parent=self.parent)
		self.item = self.make_item("TBT-BAG")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback()

	# ---------- helper ----------

	def make_warehouse(self, name, is_group=0, parent=None):
		existing = frappe.db.get_value("Warehouse", {"warehouse_name": name, "company": self.company})
		if existing:
			return existing
		data = {"doctype": "Warehouse", "warehouse_name": name, "company": self.company, "is_group": is_group}
		if parent:
			data["parent_warehouse"] = parent
		return frappe.get_doc(data).insert(ignore_permissions=True).name

	def make_item(self, code):
		if frappe.db.exists("Item", code):
			return code
		return frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": code,
				"item_name": code,
				"item_group": "All Item Groups",
				"is_stock_item": 1,
				"has_serial_no": 1,
				"is_wms_reusable_container": 1,
				"stock_uom": "Nos",
			}
		).insert(ignore_permissions=True).name

	def receive(self, serials, warehouse):
		stock_entry = frappe.get_doc(
			{
				"doctype": "Stock Entry",
				"stock_entry_type": "Material Receipt",
				"purpose": "Material Receipt",
				"company": self.company,
				"items": [
					{
						"item_code": self.item,
						"qty": len(serials),
						"uom": "Nos",
						"t_warehouse": warehouse,
						"basic_rate": 0,
						"allow_zero_valuation_rate": 1,
						"use_serial_batch_fields": 1,
						"serial_no": "\n".join(serials),
					}
				],
			}
		)
		stock_entry.insert(ignore_permissions=True)
		stock_entry.submit()
		for serial in serials:
			frappe.db.set_value(
				"Serial No", serial, {"wms_rfid_tag": f"{serial}-RFID", "wms_qr_code": f"{serial}-QR"}
			)

	def make_transfer(self, source, target, serials):
		return frappe.get_doc(
			{
				"doctype": "WMS Bag Transfer",
				"naming_series": "WBT-.YYYY.-.#####",
				"source_warehouse": source,
				"target_warehouse": target,
				"bags": [{"serial_no": s} for s in serials],
			}
		).insert(ignore_permissions=True)

	def location(self, serial):
		return frappe.db.get_value("Serial No", serial, "warehouse")

	def sent_transfer(self, serials):
		self.receive(serials, self.wh_a)
		transfer = self.make_transfer(self.wh_a, self.wh_b, serials)
		send_transfer(transfer.name)
		return transfer

	# ---------- tes ----------

	def test_full_scan_received(self):
		transfer = self.sent_transfer(["TBT-1", "TBT-2"])
		result = confirm_by_scan(transfer.name, "TBT-1-RFID\nTBT-2-QR")

		self.assertEqual(result["status"], "Diterima")
		self.assertEqual(frappe.db.get_value("Stock Entry", result["stock_entry"], "docstatus"), 1)
		self.assertEqual(self.location("TBT-1"), self.wh_b)
		self.assertEqual(self.location("TBT-2"), self.wh_b)

	def test_partial_scan_selisih(self):
		transfer = self.sent_transfer(["TBT-1", "TBT-2", "TBT-3"])
		result = confirm_by_scan(transfer.name, "TBT-1-RFID\nTBT-2-QR")

		self.assertEqual(result["status"], "Diterima dengan Selisih")
		self.assertEqual(self.location("TBT-1"), self.wh_b)
		self.assertEqual(self.location("TBT-3"), self.wh_a)
		rows = {r.serial_no: r.result for r in frappe.get_doc("WMS Bag Transfer", transfer.name).bags}
		self.assertEqual(rows["TBT-3"], "Selisih")
		self.assertEqual(rows["TBT-1"], "Diterima")

	def test_wrong_scan_rejected(self):
		transfer = self.sent_transfer(["TBT-1"])
		with self.assertRaises(frappe.ValidationError):
			confirm_receipt(
				transfer.name, [{"serial_no": "TBT-1", "method": "Scan", "scan_code": "TBT-2-QR"}]
			)
		self.assertEqual(self.location("TBT-1"), self.wh_a)

	def test_manual_requires_role(self):
		transfer = self.sent_transfer(["TBT-1"])
		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": "tbt_operator@test.com",
				"first_name": "TBT",
				"send_welcome_email": 0,
				"roles": [{"role": "Warehouse"}],
			}
		).insert(ignore_permissions=True)
		frappe.set_user(user.name)
		with self.assertRaises(frappe.ValidationError):
			confirm_receipt(
				transfer.name, [{"serial_no": "TBT-1", "method": "Manual", "remark": "label rusak"}]
			)
		frappe.set_user("Administrator")
		self.assertEqual(self.location("TBT-1"), self.wh_a)

	def test_manual_requires_remark(self):
		transfer = self.sent_transfer(["TBT-1"])
		with self.assertRaises(frappe.ValidationError):
			confirm_receipt(transfer.name, [{"serial_no": "TBT-1", "method": "Manual"}])

	def test_manual_with_role_and_remark(self):
		transfer = self.sent_transfer(["TBT-1"])
		result = confirm_receipt(
			transfer.name, [{"serial_no": "TBT-1", "method": "Manual", "remark": "tag RFID rusak"}]
		)
		self.assertEqual(result["status"], "Diterima")
		self.assertEqual(self.location("TBT-1"), self.wh_b)

	def test_cancel_rules(self):
		self.receive(["TBT-1", "TBT-2"], self.wh_a)
		draft = self.make_transfer(self.wh_a, self.wh_b, ["TBT-1"])
		self.assertEqual(cancel_transfer(draft.name), "Dibatalkan")

		sent = self.make_transfer(self.wh_a, self.wh_b, ["TBT-2"])
		send_transfer(sent.name)
		confirm_by_scan(sent.name, "TBT-2-QR")
		with self.assertRaises(frappe.ValidationError):
			cancel_transfer(sent.name)

	def test_bag_not_at_source_rejected(self):
		self.receive(["TBT-1"], self.wh_a)
		with self.assertRaises(frappe.ValidationError):
			self.make_transfer(self.wh_b, self.wh_a, ["TBT-1"])

	def test_group_and_cross_parent_rejected(self):
		self.receive(["TBT-1"], self.wh_a)
		with self.assertRaises(frappe.ValidationError):
			self.make_transfer(self.wh_a, self.parent, ["TBT-1"])

		other_parent = self.make_warehouse("TBT Other Parent", is_group=1)
		other_leaf = self.make_warehouse("TBT Other Leaf", parent=other_parent)
		with self.assertRaises(frappe.ValidationError):
			self.make_transfer(self.wh_a, other_leaf, ["TBT-1"])

	def test_same_bag_in_two_sent_transfers(self):
		self.receive(["TBT-1"], self.wh_a)
		first = self.make_transfer(self.wh_a, self.wh_b, ["TBT-1"])
		second = self.make_transfer(self.wh_a, self.wh_b, ["TBT-1"])
		send_transfer(first.name)
		with self.assertRaises(frappe.ValidationError):
			send_transfer(second.name)
