import frappe
from frappe.tests import IntegrationTestCase

from wms.wms.doctype.wms_bag_fill_log.wms_bag_fill_log import (
	get_bag_location,
	resolve_bag,
	scan_station,
)

BAG_ITEM = "TEST-WMSBF-BAG"


class TestWMSBagFillLog(IntegrationTestCase):
	"""Test alur Bag Fill Log. Butuh data seed WP-KOSONG dan WP-ISI di site."""

	def setUp(self):
		for loc in ("WP-KOSONG", "WP-ISI"):
			if not frappe.db.exists("WMS Location", loc):
				self.skipTest(f"Seed data missing: WMS Location {loc}")
		self.ensure_bag_item()
		self.addCleanup(frappe.set_user, "Administrator")

	def ensure_bag_item(self):
		if frappe.db.exists("Item", BAG_ITEM):
			return
		frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": BAG_ITEM,
				"item_name": BAG_ITEM,
				"item_group": "All Item Groups",
				"is_stock_item": 1,
				"has_serial_no": 1,
				"is_wms_reusable_container": 1,
				"stock_uom": "Nos",
				"valuation_method": "Moving Average",
			}
		).insert(ignore_permissions=True)

	def receive_bag(self, serial_no, location, tag):
		"""Material Receipt 1 bag ke lokasi tertentu, lalu isi tag RFID/QR."""
		warehouse, company = frappe.db.get_value(
			"WMS Location", location, ["erpnext_warehouse", "company"]
		)
		se = frappe.get_doc(
			{
				"doctype": "Stock Entry",
				"stock_entry_type": "Material Receipt",
				"purpose": "Material Receipt",
				"company": company,
				"items": [
					{
						"item_code": BAG_ITEM,
						"qty": 1,
						"uom": "Nos",
						"t_warehouse": warehouse,
						"basic_rate": 1,
						"allow_zero_valuation_rate": 1,
						"use_serial_batch_fields": 1,
						"serial_no": serial_no,
						"to_wms_location": location,
					}
				],
			}
		)
		se.insert(ignore_permissions=True)
		se.submit()
		frappe.db.set_value(
			"Serial No", serial_no, {"wms_rfid_tag": f"{tag}-RFID", "wms_qr_code": f"{tag}-QR"}
		)
		return f"{tag}-QR", f"{tag}-RFID"

	def test_resolve_bag_by_qr_and_rfid(self):
		qr, rfid = self.receive_bag("TEST-WMSBF-SN-1", "WP-KOSONG", "TWB1")
		self.assertEqual(resolve_bag(qr), "TEST-WMSBF-SN-1")
		self.assertEqual(resolve_bag(rfid), "TEST-WMSBF-SN-1")

	def test_unknown_scan_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			resolve_bag("TIDAK-ADA-XYZ")

	def test_single_open_log_per_bag(self):
		qr, _rfid = self.receive_bag("TEST-WMSBF-SN-2", "WP-KOSONG", "TWB2")
		scan_station("kirim", qr)
		with self.assertRaises(frappe.ValidationError):
			scan_station("kirim", qr)

	def test_status_guard(self):
		qr, _rfid = self.receive_bag("TEST-WMSBF-SN-3", "WP-KOSONG", "TWB3")
		log = frappe.get_doc(
			{
				"doctype": "WMS Bag Fill Log",
				"fill_log_number": "TEST-BF-GUARD",
				"fill_datetime": frappe.utils.now(),
				"operator": "Administrator",
				"bag_serial_no": "TEST-WMSBF-SN-3",
			}
		).insert(ignore_permissions=True)
		with self.assertRaises(frappe.ValidationError):
			log.confirm_receipt_kosong(scan_code=qr)

	def test_manual_requires_role_and_reason(self):
		self.receive_bag("TEST-WMSBF-SN-4", "WP-KOSONG", "TWB4")
		log = frappe.get_doc({"doctype": "WMS Bag Fill Log", "bag_serial_no": "TEST-WMSBF-SN-4"})
		with self.assertRaises(frappe.ValidationError):
			log._verify(None, 1, "")
		self.assertEqual(log._verify(None, 1, "tag rusak"), "Manual")
		frappe.set_user("Guest")
		with self.assertRaises(frappe.ValidationError):
			log._verify(None, 1, "tag rusak")

	def test_location_mismatch_rejected(self):
		qr, _rfid = self.receive_bag("TEST-WMSBF-SN-5", "WP-ISI", "TWB5")
		scan_station("kirim", qr)
		with self.assertRaises(frappe.ValidationError):
			scan_station("kosong", qr)

	def test_full_cycle(self):
		qr, rfid = self.receive_bag("TEST-WMSBF-SN-6", "WP-KOSONG", "TWB6")
		self.assertEqual(get_bag_location("TEST-WMSBF-SN-6"), "WP-KOSONG")

		scan_station("kirim", qr)
		scan_station("kosong", qr)
		scan_station("mulai_isi", qr)
		scan_station("isi", rfid, qty_filled=5)
		self.assertEqual(get_bag_location("TEST-WMSBF-SN-6"), "WP-ISI")

		scan_station("tuang", qr)
		result = scan_station("kembali", qr)
		self.assertEqual(result["status"], "Selesai")
		self.assertEqual(get_bag_location("TEST-WMSBF-SN-6"), "WP-KOSONG")

		log = frappe.get_doc("WMS Bag Fill Log", result["log"])
		self.assertTrue(log.stock_entry_isi)
		self.assertTrue(log.stock_entry_kembali)
		self.assertEqual(log.confirmation_method_kembali, "Scan")
