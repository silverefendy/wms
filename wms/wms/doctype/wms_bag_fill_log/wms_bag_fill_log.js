const WMS_API = "wms.wms.doctype.wms_bag_fill_log.wms_bag_fill_log";

const WMS_FLOW = {
	"Draft": [
		["Kirim ke Gudang Kosong (Send)", "send_to_empty_warehouse", false],
	],
	"Menunggu Diterima Gudang Kosong": [
		["Konfirmasi Terima (Scan)", "confirm_receipt_kosong", true],
	],
	"Terkonfirmasi di Gudang Kosong": [
		["Mulai Isi (Start Fill)", "start_fill_process", false],
	],
	"Menunggu Diterima Gudang Isi": [
		["Konfirmasi Terima Isi (Scan)", "confirm_receipt_isi", true],
	],
	"Terisi": [
		["Tuang ke Container (Pour)", "start_pour", false],
	],
	"Menunggu Kembali ke Gudang Kosong": [
		["Konfirmasi Kembali (Scan)", "confirm_return_kosong", true],
	],
};

const WMS_CAN_REPORT = [
	"Terkonfirmasi di Gudang Kosong",
	"Menunggu Diterima Gudang Isi",
	"Terisi",
	"Menunggu Kembali ke Gudang Kosong",
];

const WMS_CAN_CANCEL = [
	"Draft",
	"Menunggu Diterima Gudang Kosong",
	"Terkonfirmasi di Gudang Kosong",
	"Menunggu Diterima Gudang Isi",
];

function wms_call(frm, method, args) {
	const go = () =>
		frm.call({
			doc: frm.doc,
			method: method,
			args: args || {},
			freeze: true,
			callback: () => frm.reload_doc(),
		});
	if (frm.is_dirty()) {
		frm.save().then(go);
	} else {
		go();
	}
}

frappe.ui.form.on("WMS Bag Fill Log", {
	scan_bag(frm) {
		const code = (frm.doc.scan_bag || "").trim();
		if (!code) return;
		frappe.call({
			method: WMS_API + ".resolve_bag",
			args: { scan_code: code },
			callback: (r) => {
				frm.set_value("bag_serial_no", r.message);
				frm.set_value("scan_bag", "");
			},
			error: () => frm.set_value("scan_bag", ""),
		});
	},

	refresh(frm) {
		if (frm.is_new()) return;
		const status = frm.doc.status;
		const is_manager = frappe.user.has_role("WMS Warehouse Manager");

		(WMS_FLOW[status] || []).forEach(([label, method, needs_scan]) => {
			if (needs_scan) {
				frm.add_custom_button(label, () => {
					frappe.prompt(
						[
							{
								fieldname: "scan_code",
								fieldtype: "Data",
								label: "Scan QR / RFID",
								reqd: 1,
							},
						],
						(v) => wms_call(frm, method, { scan_code: v.scan_code }),
						label,
						"Konfirmasi"
					);
				});
				if (is_manager) {
					frm.add_custom_button(
						"Konfirmasi Manual (Bypass)",
						() =>
							frappe.prompt(
								[
									{
										fieldname: "manual_reason",
										fieldtype: "Small Text",
										label: "Alasan / Catatan (wajib)",
										reqd: 1,
									},
								],
								(v) =>
									wms_call(frm, method, {
										manual: 1,
										manual_reason: v.manual_reason,
									}),
								"Konfirmasi Manual tanpa Scan",
								"Konfirmasi"
							),
						"Manager"
					);
				}
			} else {
				frm.add_custom_button(label, () => wms_call(frm, method));
			}
		});

		if (WMS_CAN_REPORT.includes(status)) {
			frm.add_custom_button("Lapor Rusak (Damaged)", () => wms_call(frm, "report_damaged"), "Masalah");
			frm.add_custom_button("Lapor Hilang (Lost)", () => wms_call(frm, "report_lost"), "Masalah");
		}
		if (WMS_CAN_CANCEL.includes(status)) {
			frm.add_custom_button("Batalkan Log (Cancel)", () => wms_call(frm, "cancel_log"), "Masalah");
		}
	},
});
