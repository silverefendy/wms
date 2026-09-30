import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime

MANUAL_ROLE = "WMS Warehouse Manager"


class WMSBagTransfer(Document):
	def validate(self):
		self.validate_warehouses()
		self.validate_bags()
		if self.status == "Draft":
			self.validate_bags_at_source()

	def validate_warehouses(self):
		if self.source_warehouse == self.target_warehouse:
			frappe.throw(_("Source and target Warehouse must be different."))

		info = {}
		for wh in (self.source_warehouse, self.target_warehouse):
			data = frappe.db.get_value(
				"Warehouse", wh, ["is_group", "parent_warehouse", "company"], as_dict=True
			)
			if not data:
				frappe.throw(_("Warehouse {0} was not found.").format(wh))
			if data.is_group:
				frappe.throw(_("Warehouse {0} is a group and cannot be used.").format(wh))
			info[wh] = data

		src, tgt = info[self.source_warehouse], info[self.target_warehouse]
		if src.company != tgt.company:
			frappe.throw(_("Source and target Warehouse must belong to the same Company."))
		if src.parent_warehouse != tgt.parent_warehouse:
			frappe.throw(_("Source and target Warehouse must share the same parent Warehouse."))

	def validate_bags(self):
		if not self.bags:
			frappe.throw(_("At least one bag is required."))

		seen = set()
		for row in self.bags:
			if row.serial_no in seen:
				frappe.throw(_("Row {0}: Serial No {1} is duplicated.").format(row.idx, row.serial_no))
			seen.add(row.serial_no)

			item_code = frappe.db.get_value("Serial No", row.serial_no, "item_code")
			if not frappe.db.get_value("Item", item_code, "is_wms_reusable_container"):
				frappe.throw(
					_("Row {0}: Item {1} is not flagged as a WMS Reusable Container.").format(
						row.idx, item_code
					)
				)

	def validate_bags_at_source(self):
		for row in self.bags:
			warehouse, status = frappe.db.get_value("Serial No", row.serial_no, ["warehouse", "status"])
			if status != "Active":
				frappe.throw(
					_("Row {0}: Serial No {1} is not Active (status: {2}).").format(
						row.idx, row.serial_no, status
					)
				)
			if warehouse != self.source_warehouse:
				frappe.throw(
					_("Row {0}: Serial No {1} is in {2}, not in {3}.").format(
						row.idx, row.serial_no, warehouse, self.source_warehouse
					)
				)

	def post_transfer(self, serials):
		"""Satu Stock Entry Material Transfer untuk semua bag yang diterima."""
		items = []
		for serial in sorted(serials):
			item_code = frappe.db.get_value("Serial No", serial, "item_code")
			items.append(
				{
					"item_code": item_code,
					"qty": 1,
					"uom": frappe.db.get_value("Item", item_code, "stock_uom"),
					"s_warehouse": self.source_warehouse,
					"t_warehouse": self.target_warehouse,
					"use_serial_batch_fields": 1,
					"serial_no": serial,
				}
			)

		stock_entry = frappe.get_doc(
			{
				"doctype": "Stock Entry",
				"stock_entry_type": "Material Transfer",
				"purpose": "Material Transfer",
				"company": frappe.db.get_value("Warehouse", self.source_warehouse, "company"),
				"remarks": _("WMS Bag Transfer {0}").format(self.name),
				"items": items,
			}
		)
		stock_entry.insert(ignore_permissions=True)
		stock_entry.submit()
		return stock_entry.name


def _load(name):
	doc = frappe.get_doc("WMS Bag Transfer", name)
	doc.check_permission("write")
	return doc


def resolve_bag(code):
	"""Resolve kode scan (RFID, QR, atau nama Serial No) ke nama Serial No."""
	code = (code or "").strip()
	if not code:
		frappe.throw(_("Scan code is empty."))
	for field in ("wms_rfid_tag", "wms_qr_code", "name"):
		found = frappe.db.get_value("Serial No", {field: code}, "name")
		if found:
			return found
	frappe.throw(_("Scan code {0} does not match any Serial No.").format(code))


@frappe.whitelist()
def send_transfer(name: str):
	doc = _load(name)
	if doc.status != "Draft":
		frappe.throw(_("Only a Draft transfer can be sent (current status: {0}).").format(doc.status))

	doc.validate_bags_at_source()
	for row in doc.bags:
		other = frappe.db.sql(
			"""select p.name from `tabWMS Bag Transfer` p
			join `tabWMS Bag Transfer Item` c on c.parent = p.name
			where c.serial_no = %s and p.status = 'Dikirim' and p.name != %s limit 1""",
			(row.serial_no, doc.name),
		)
		if other:
			frappe.throw(
				_("Row {0}: Serial No {1} is already in sent transfer {2}.").format(
					row.idx, row.serial_no, other[0][0]
				)
			)

	doc.status = "Dikirim"
	doc.sender = frappe.session.user
	doc.sent_at = now_datetime()
	doc.save()
	return doc.status


@frappe.whitelist()
def confirm_receipt(name: str, results: str | list | None = None):
	"""results: list dict {serial_no, method (Scan/Manual), scan_code, remark, result (opsional)}.
	Bag yang tidak ada di results otomatis Selisih."""
	doc = _load(name)
	if doc.status != "Dikirim":
		frappe.throw(_("Only a sent transfer can be confirmed (current status: {0}).").format(doc.status))

	if isinstance(results, str):
		results = json.loads(results)
	by_serial = {r.get("serial_no"): r for r in (results or [])}

	unknown = set(by_serial) - {row.serial_no for row in doc.bags}
	if unknown:
		frappe.throw(_("Serial No not in this transfer: {0}").format(", ".join(sorted(unknown))))

	received = []
	for row in doc.bags:
		entry = by_serial.get(row.serial_no)
		remark = ((entry or {}).get("remark") or "").strip()

		if not entry:
			row.result, row.method, row.scan_code = "Selisih", None, None
			row.remark = row.remark or _("Not scanned at confirmation")
		elif entry.get("result") == "Selisih":
			if not remark:
				frappe.throw(_("Row {0}: remark is required for Selisih.").format(row.idx))
			row.result, row.method, row.scan_code, row.remark = "Selisih", None, None, remark
		elif entry.get("method") == "Manual":
			if MANUAL_ROLE not in frappe.get_roles():
				frappe.throw(_("Manual confirmation requires the role {0}.").format(MANUAL_ROLE))
			if not remark:
				frappe.throw(_("Row {0}: remark is required for manual confirmation.").format(row.idx))
			row.result, row.method, row.scan_code, row.remark = "Diterima", "Manual", None, remark
			received.append(row.serial_no)
		else:
			resolved = resolve_bag(entry.get("scan_code"))
			if resolved != row.serial_no:
				frappe.throw(
					_("Row {0}: scan code belongs to {1}, expected {2}.").format(
						row.idx, resolved, row.serial_no
					)
				)
			row.result, row.method, row.scan_code = "Diterima", "Scan", entry.get("scan_code").strip()
			if remark:
				row.remark = remark
			received.append(row.serial_no)

	for serial in received:
		warehouse = frappe.db.get_value("Serial No", serial, "warehouse")
		if warehouse != doc.source_warehouse:
			frappe.throw(
				_("Serial No {0} is now in {1}, not in {2}.").format(serial, warehouse, doc.source_warehouse)
			)

	if received:
		doc.stock_entry = doc.post_transfer(received)

	doc.status = "Diterima" if len(received) == len(doc.bags) else "Diterima dengan Selisih"
	doc.receiver = frappe.session.user
	doc.received_at = now_datetime()
	doc.save()
	return {"status": doc.status, "stock_entry": doc.stock_entry, "received": len(received)}


@frappe.whitelist()
def cancel_transfer(name: str):
	doc = _load(name)
	if doc.status not in ("Draft", "Dikirim"):
		frappe.throw(
			_(
				"Transfer with status {0} cannot be cancelled. Create a reverse transfer to correct it."
			).format(doc.status)
		)
	doc.status = "Dibatalkan"
	doc.save()
	return doc.status


@frappe.whitelist()
def confirm_by_scan(name: str, scan_codes: str | list):
	"""Konfirmasi lewat daftar kode scan (satu per baris atau list). Bag yang tidak discan menjadi Selisih."""
	if isinstance(scan_codes, str):
		scan_codes = [c.strip() for c in scan_codes.splitlines() if c.strip()]

	results = []
	for code in scan_codes:
		results.append({"serial_no": resolve_bag(code), "method": "Scan", "scan_code": code})
	return confirm_receipt(name, results)
