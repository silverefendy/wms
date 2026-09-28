const WMS_STATION_API = "wms.wms.doctype.wms_bag_fill_log.wms_bag_fill_log.scan_station";

const WMS_STATIONS = {
	"1. Kirim ke Gudang Kosong (buat log baru)": "kirim",
	"2. Terima di Gudang Kosong": "kosong",
	"3. Mulai Isi": "mulai_isi",
	"4. Terima di Gudang Isi (isi Qty)": "isi",
	"5. Tuang ke Container": "tuang",
	"6. Kembali ke Gudang Kosong": "kembali",
};

function wms_scan_station(listview) {
	const d = new frappe.ui.Dialog({
		title: "Scan Station - Bag Fill",
		fields: [
			{
				fieldname: "stage",
				fieldtype: "Select",
				label: "Tahap",
				options: Object.keys(WMS_STATIONS).join("\n"),
				default: Object.keys(WMS_STATIONS)[1],
				reqd: 1,
			},
			{
				fieldname: "qty_filled",
				fieldtype: "Float",
				label: "Qty Filled (Kg)",
				depends_on: "eval:doc.stage && doc.stage.startsWith('4.')",
			},
			{
				fieldname: "scan_code",
				fieldtype: "Data",
				label: "Scan QR / RFID",
			},
			{ fieldname: "result", fieldtype: "HTML" },
		],
		primary_action_label: "Proses",
		primary_action: () => run(),
	});

	const lines = [];
	const show = (ok, text) => {
		lines.unshift(
			`<div style="color:${ok ? "green" : "red"}">${ok ? "OK" : "GAGAL"} - ${frappe.utils.escape_html(text)}</div>`
		);
		d.fields_dict.result.$wrapper.html(lines.slice(0, 30).join(""));
	};

	function run() {
		const stage = WMS_STATIONS[d.get_value("stage")];
		const code = (d.get_value("scan_code") || "").trim();
		if (!code) return;
		frappe.call({
			method: WMS_STATION_API,
			args: { stage: stage, scan_code: code, qty_filled: d.get_value("qty_filled") },
			callback: (r) => {
				const m = r.message || {};
				show(true, `${code} -> ${m.bag} | ${m.log} | ${m.status}`);
			},
			error: () => show(false, `${code} ditolak (lihat pesan)`),
			always: () => {
				d.set_value("scan_code", "");
				d.fields_dict.scan_code.$input.focus();
				listview.refresh();
			},
		});
	}

	d.show();
	d.fields_dict.scan_code.$input.on("keydown", (e) => {
		if (e.key === "Enter") {
			e.preventDefault();
			run();
		}
	});
	d.fields_dict.scan_code.$input.focus();
}

frappe.listview_settings["WMS Bag Fill Log"] = {
	onload(listview) {
		listview.page.add_inner_button("Scan Station", () => wms_scan_station(listview));
	},
};
