import frappe


def execute():
    """Buat Inventory Dimension 'WMS Location' bila belum ada (idempotent)."""
    if frappe.db.exists("Inventory Dimension", {"reference_document": "WMS Location"}):
        return
    frappe.get_doc(
        {
            "doctype": "Inventory Dimension",
            "dimension_name": "WMS Location",
            "reference_document": "WMS Location",
            "apply_to_all_doctypes": 1,
            "validate_negative_stock": 0,
        }
    ).insert(ignore_permissions=True)
