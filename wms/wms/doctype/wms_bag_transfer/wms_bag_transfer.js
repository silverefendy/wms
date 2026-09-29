const WBT_METHOD = "wms.wms.doctype.wms_bag_transfer.wms_bag_transfer.";

frappe.ui.form.on("WMS Bag Transfer", {
    refresh(frm) {
        if (frm.is_new()) {
            return;
        }

        const run = (method, args) =>
            frappe
                .call({
                    method: WBT_METHOD + method,
                    args: Object.assign({ name: frm.doc.name }, args || {}),
                    freeze: true,
                })
                .then(() => frm.reload_doc());

        if (frm.doc.status === "Draft") {
            frm.add_custom_button(__("Kirim"), () => {
                if (frm.is_dirty()) {
                    frappe.msgprint(__("Simpan dokumen terlebih dahulu."));
                    return;
                }
                run("send_transfer");
            });
        }

        if (frm.doc.status === "Dikirim") {
            frm.add_custom_button(__("Konfirmasi Terima"), () => {
                const dialog = new frappe.ui.Dialog({
                    title: __("Konfirmasi Terima"),
                    fields: [
                        {
                            fieldname: "scan_codes",
                            fieldtype: "Small Text",
                            label: __("Kode scan (RFID / QR), satu per baris"),
                            reqd: 1,
                        },
                        {
                            fieldtype: "HTML",
                            options: `<p class="text-muted">${__(
                                "Bag yang tidak discan otomatis ditandai Selisih."
                            )}</p>`,
                        },
                    ],
                    primary_action_label: __("Konfirmasi"),
                    primary_action(values) {
                        dialog.hide();
                        run("confirm_by_scan", { scan_codes: values.scan_codes });
                    },
                });
                dialog.show();
            });

            frm.add_custom_button(__("Batalkan"), () => {
                frappe.confirm(__("Batalkan transfer ini?"), () => run("cancel_transfer"));
            });
        }

        if (frm.doc.status === "Draft") {
            frm.add_custom_button(__("Batalkan"), () => {
                frappe.confirm(__("Batalkan transfer ini?"), () => run("cancel_transfer"));
            });
        }
    },
});
