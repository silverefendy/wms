import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import cint, flt, now_datetime

LOC_KOSONG = "WP-KOSONG"
LOC_ISI = "WP-ISI"
LOC_RUSAK = "WP-RUSAK"
LOC_HILANG = "WP-HILANG"
MANAGER_ROLE = "WMS Warehouse Manager"
LOG_SERIES = "FL-.YYYY.-.#####"

TERMINAL_STATUS = ("Selesai", "Rusak", "Hilang", "Terjual", "Cancelled")

# Lokasi bag di ledger ERPNext menurut status log
STATUS_LOCATION = {
	"Terkonfirmasi di Gudang Kosong": LOC_KOSONG,
	"Menunggu Diterima Gudang Isi": LOC_KOSONG,
	"Terisi": LOC_ISI,
	"Menunggu Kembali ke Gudang Kosong": LOC_ISI,
}

# stage Scan Station -> (status yang dibutuhkan, method, perlu scan)
STATIONS = {
	"kosong": ("Menunggu Diterima Gudang Kosong", "confirm_receipt_kosong", True),
	"mulai_isi": ("Terkonfirmasi di Gudang Kosong", "start_fill_process", False),
	"isi": ("Menunggu Diterima Gudang Isi", "confirm_receipt_isi", True),
	"tuang": ("Terisi", "start_pour", False),
	"kembali": ("Menunggu Kembali ke Gudang Kosong", "confirm_return_kosong", True),
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


def get_bag_location(serial_no):
	"""Lokasi WMS bag menurut ledger ERPNext. None kalau tidak ada stok / ambigu."""
	rows = frappe.db.sql(
		"""
		select sle.target_wms_location as location,
			   sum(case when sabe.is_outward = 1 then -abs(sabe.qty) else abs(sabe.qty) end) as net
		from `tabStock Ledger Entry` sle
		join `tabSerial and Batch Entry` sabe on sabe.parent = sle.serial_and_batch_bundle
		where sabe.serial_no = %s and sle.is_cancelled = 0
		group by sle.target_wms_location
		having net > 0
		""",
		serial_no,
		as_dict=True,
	)
	return rows[0].location if len(rows) == 1 else None


@frappe.whitelist()
def resolve_bag(scan_code):
	"""Ubah kode scan menjadi Serial No bag (dipakai field Scan Bag di form)."""
	frappe.has_permission("WMS Bag Fill Log", "read", throw=True)
	serial = find_serial_by_scan((scan_code or "").strip())
	if not serial:
		frappe.throw(_("Scan code {0} does not match any bag.").format(scan_code))
	return serial


@frappe.whitelist()
def scan_station(stage, scan_code, qty_filled=None):
	"""Proses satu scan bag untuk satu tahap, tanpa membuka form."""
	scan_code = (scan_code or "").strip()
	serial = resolve_bag(scan_code)

	if stage == "kirim":
		frappe.has_permission("WMS Bag Fill Log", "create", throw=True)
		log = frappe.get_doc(
			{
				"doctype": "WMS Bag Fill Log",
				"fill_log_number": make_autoname(LOG_SERIES),
				"fill_datetime": now_datetime(),
				"operator": frappe.session.user,
				"bag_serial_no": serial,
			}
		)
		log.insert()
		log.send_to_empty_warehouse()
		return {"log": log.name, "bag": serial, "status": log.status}

	if stage not in STATIONS:
		frappe.throw(_("Unknown stage {0}.").format(stage))

	needed_status, method, needs_scan = STATIONS[stage]
	names = frappe.get_all(
		"WMS Bag Fill Log",
		filters={"bag_serial_no": serial, "status": needed_status},
		pluck="name",
		limit=2,
	)
	if not names:
		frappe.throw(_("No log for bag {0} in status {1}.").format(serial, needed_status))
	if len(names) > 1:
		frappe.throw(_("More than one log for bag {0} in status {1}.").format(serial, needed_status))

	log = frappe.get_doc("WMS Bag Fill Log", names[0])
	if stage == "isi" and qty_filled not in (None, ""):
		log.qty_filled = flt(qty_filled)
		log.save()

	getattr(log, method)(**({"scan_code": scan_code} if needs_scan else {}))
	return {"log": log.name, "bag": serial, "status": log.status}


class WMSBagFillLog(Document):
	"""Satu siklus bag: Kosong -> Isi -> tuang -> kembali ke Kosong.

	Stok pellet TIDAK berubah di sini (keluar di weighbridge). Yang berpindah
	hanya lokasi bag (Serial No) lewat Stock Entry Material Transfer.
	"""

	def validate(self):
		self.validate_bag_serial()
		self.validate_single_open_log()
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

	def validate_single_open_log(self):
		"""Satu bag hanya boleh punya satu log aktif."""
		if self.status in TERMINAL_STATUS:
			return
		other = frappe.db.exists(
			"WMS Bag Fill Log",
			{
				"bag_serial_no": self.bag_serial_no,
				"status": ["not in", TERMINAL_STATUS],
				"name": ["!=", self.name or ""],
			},
		)
		if other:
			frappe.throw(
				_("Bag {0} already has an active log: {1}.").format(self.bag_serial_no, other)
			)

	# ---------- helper ----------

	def _require_status(self, *allowed):
		if self.status not in allowed:
			frappe.throw(
				_("Action not allowed in status {0}. Allowed: {1}").format(
					self.status, ", ".join(allowed)
				)
			)

	def _verify(self, scan_code, manual, manual_reason):
		"""Return 'Scan' atau 'Manual'. Throw kalau tidak valid."""
		if cint(manual):
			if MANAGER_ROLE not in frappe.get_roles():
				frappe.throw(_("Manual confirmation requires the role {0}.").format(MANAGER_ROLE))
			if not (manual_reason or "").strip():
				frappe.throw(_("A reason (note) is required for manual confirmation."))
			return "Manual"
		serial = find_serial_by_scan((scan_code or "").strip())
		if not serial:
			frappe.throw(_("Scan code {0} does not match any bag.").format(scan_code))
		if serial != self.bag_serial_no:
			frappe.throw(
				_("Scanned bag {0} does not match this log (bag {1}).").format(serial, self.bag_serial_no)
			)
		return "Scan"

	def _assert_location(self, expected):
		current = get_bag_location(self.bag_serial_no)
		if current != expected:
			frappe.throw(
				_("Bag {0} is at {1} in the ledger, expected {2}.").format(
					self.bag_serial_no, current or _("(no stock)"), expected
				)
			)

	def _confirm_stage(self, stage, scan_code, manual, manual_reason, expected_location):
		method = self._verify(scan_code, manual, manual_reason)
		self._assert_location(expected_location)
		setattr(self, f"confirmed_by_{stage}", frappe.session.user)
		setattr(self, f"confirmed_at_{stage}", now_datetime())
		setattr(self, f"confirmation_method_{stage}", method)
		reason = (manual_reason or "").strip() if method == "Manual" else None
		setattr(self, f"manual_reason_{stage}", reason)

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
	def confirm_receipt_kosong(self, scan_code=None, manual=0, manual_reason=None):
		self.check_permission("write")
		self._require_status("Menunggu Diterima Gudang Kosong")
		self._confirm_stage("kosong", scan_code, manual, manual_reason, LOC_KOSONG)
		self.status = "Terkonfirmasi di Gudang Kosong"
		self.save()

	@frappe.whitelist()
	def start_fill_process(self):
		self.check_permission("write")
		self._require_status("Terkonfirmasi di Gudang Kosong")
		self.status = "Menunggu Diterima Gudang Isi"
		self.save()

	@frappe.whitelist()
	def confirm_receipt_isi(self, scan_code=None, manual=0, manual_reason=None):
		self.check_permission("write")
		self._require_status("Menunggu Diterima Gudang Isi")
		if flt(self.qty_filled) <= 0:
			frappe.throw(_("Qty Filled must be greater than 0."))
		self._confirm_stage("isi", scan_code, manual, manual_reason, LOC_KOSONG)
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
	def confirm_return_kosong(self, scan_code=None, manual=0, manual_reason=None):
		self.check_permission("write")
		self._require_status("Menunggu Kembali ke Gudang Kosong")
		self._confirm_stage("kembali", scan_code, manual, manual_reason, LOC_ISI)
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
