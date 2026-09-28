import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt, now_datetime

LOC_KOSONG = "WP-KOSONG"
LOC_ISI = "WP-ISI"
LOC_RUSAK = "WP-RUSAK"
LOC_HILANG = "WP-HILANG"
MANAGER_ROLE = "WMS Warehouse Manager"

# Lokasi bag di ledger ERPNext menurut status log
STATUS_LOCATION = {
	"Terkonfirmasi di Gudang Kosong": LOC_KOSONG,
	"Menunggu Diterima Gudang Isi": LOC_KOSONG,
	"Terisi": LOC_ISI,
	"Menunggu Kembali ke Gudang Kosong": LOC_ISI,
}


def find_serial_by_scan(scan_code):
	"""Cari Serial No dari kode scan (RFID atau QR)."""
	if not scan_code:
		return None
	rows = frappe.get_all(
		"Serial No",
		or_filters={"wms_rfid_tag": scan_code, "wms_qr_code": scan_code},
		pluck="name",
		limit=2,
	)
	return rows[0] if len(rows) == 1 else None


class WMSBagFillLog(Document):
	"""Satu siklus bag: Kosong -> Isi -> tuang -> kembali ke Kosong.

	Stok pellet TIDAK berubah di sini (keluar di weighbridge). Yang berpindah
	hanya lokasi bag (Serial No) lewat Stock Entry Material Transfer.
	"""

	def validate(self):
		self.validate_bag_serial()
		if flt(self.qty_filled) < 0:
			frappe.throw(_("Qty Filled cannot be negative."))

	def validate_bag_serial(self):
		item_code = frappe.db.get_value("Serial No", self.bag_serial_no, "item_code")
		if not item_code:
			frappe.throw(_("Serial No {0} does not exist or has no Item.").format(self.bag_serial_no))
		if not frappe.db.get_value("Item", item_code, "is_wms_reusable_container"):
			frappe.throw(
				_("Serial No {0} belongs to Item {1}, which is not a WMS Reusable Container.").format(
					self.bag_serial_no, item_code
				)
			)

	# ---------- helper ----------

	def _require_status(self, *allowed):
		if self.status not in allowed:
			frappe.throw(
				_("Action not allowed in status {0}. Allowed: {1}").format(
					self.status, ", ".join(allowed)
				)
			)

	def _verify(self, scan_code, manual):
		"""Return 'Scan' atau 'Manual'. Throw kalau tidak valid."""
		if cint(manual):
			if MANAGER_ROLE not in frappe.get_roles():
				frappe.throw(_("Manual confirmation requires the role {0}.").format(MANAGER_ROLE))
			return "Manual"
		serial = find_serial_by_scan(scan_code)
		if not serial:
			frappe.throw(_("Scan code {0} does not match any bag.").format(scan_code))
		if serial != self.bag_serial_no:
			frappe.throw(
				_("Scanned bag {0} does not match this log (bag {1}).").format(serial, self.bag_serial_no)
			)
		return "Scan"

	def _stamp(self, stage, method):
		setattr(self, f"confirmed_by_{stage}", frappe.session.user)
		setattr(self, f"confirmed_at_{stage}", now_datetime())
		setattr(self, f"confirmation_method_{stage}", method)

	def _move_bag(self, source_loc, target_loc):
		"""Material Transfer 1 bag antar WMS Location. Return nama Stock Entry."""
		item_code, stock_uom = frappe.db.get_value(
			"Item",
			frappe.db.get_value("Serial No", self.bag_serial_no, "item_code"),
			["name", "stock_uom"],
		)
		src = frappe.db.get_value("WMS Location", source_loc, ["erpnext_warehouse", "company"], as_dict=True)
		tgt_wh = frappe.db.get_value("WMS Location", target_loc, "erpnext_warehouse")
		if not src or not src.erpnext_warehouse or not tgt_wh:
			frappe.throw(_("WMS Location {0} or {1} has no ERPNext Warehouse.").format(source_loc, target_loc))

		se = frappe.get_doc(
			{
				"doctype": "Stock Entry",
				"stock_entry_type": "Material Transfer",
				"purpose": "Material Transfer",
				"company": src.company,
				"items": [
					{
						"item_code": item_code,
						"qty": 1,
						"uom": stock_uom,
						"s_warehouse": src.erpnext_warehouse,
						"t_warehouse": tgt_wh,
						"use_serial_batch_fields": 1,
						"serial_no": self.bag_serial_no,
						"wms_location": source_loc,
						"to_wms_location": target_loc,
					}
				],
			}
		)
		se.insert(ignore_permissions=True)
		se.submit()
		return se.name

	# ---------- tahap normal ----------

	@frappe.whitelist()
	def send_to_empty_warehouse(self):
		self.check_permission("write")
		self._require_status("Draft")
		self.status = "Menunggu Diterima Gudang Kosong"
		self.save()

	@frappe.whitelist()
	def confirm_receipt_kosong(self, scan_code=None, manual=0):
		self.check_permission("write")
		self._require_status("Menunggu Diterima Gudang Kosong")
		method = self._verify(scan_code, manual)
		self._stamp("kosong", method)
		self.status = "Terkonfirmasi di Gudang Kosong"
		self.save()

	@frappe.whitelist()
	def start_fill_process(self):
		self.check_permission("write")
		self._require_status("Terkonfirmasi di Gudang Kosong")
		self.status = "Menunggu Diterima Gudang Isi"
		self.save()

	@frappe.whitelist()
	def confirm_receipt_isi(self, scan_code=None, manual=0):
		self.check_permission("write")
		self._require_status("Menunggu Diterima Gudang Isi")
		if flt(self.qty_filled) <= 0:
			frappe.throw(_("Qty Filled must be greater than 0."))
		method = self._verify(scan_code, manual)
		self._stamp("isi", method)
		self.stock_entry_isi = self._move_bag(LOC_KOSONG, LOC_ISI)
		self.status = "Terisi"
		self.save()

	@frappe.whitelist()
	def start_pour(self):
		self.check_permission("write")
		self._require_status("Terisi")
		self.status = "Menunggu Kembali ke Gudang Kosong"
		self.save()

	@frappe.whitelist()
	def confirm_return_kosong(self, scan_code=None, manual=0):
		self.check_permission("write")
		self._require_status("Menunggu Kembali ke Gudang Kosong")
		method = self._verify(scan_code, manual)
		self._stamp("kembali", method)
		self.stock_entry_kembali = self._move_bag(LOC_ISI, LOC_KOSONG)
		self.status = "Selesai"
		self.save()

	# ---------- cabang ----------

	def _report_problem(self, target_loc, new_status):
		self.check_permission("write")
		self._require_status(*STATUS_LOCATION.keys())
		if not (self.remarks or "").strip():
			frappe.throw(_("Remarks are required to report a damaged or lost bag."))
		self._move_bag(STATUS_LOCATION[self.status], target_loc)
		self.status = new_status
		self.save()

	@frappe.whitelist()
	def report_damaged(self):
		self._report_problem(LOC_RUSAK, "Rusak")

	@frappe.whitelist()
	def report_lost(self):
		self._report_problem(LOC_HILANG, "Hilang")

	@frappe.whitelist()
	def cancel_log(self):
		self.check_permission("write")
		self._require_status(
			"Draft",
			"Menunggu Diterima Gudang Kosong",
			"Terkonfirmasi di Gudang Kosong",
			"Menunggu Diterima Gudang Isi",
		)
		self.status = "Cancelled"
		self.save()
