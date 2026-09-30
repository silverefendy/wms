import frappe

# Pemetaan kartu -> warehouse_name tahap (ADR-0008 butir 1).
STAGES = {
    "kosong": "Kosong",
    "isi": "Isi",
    "rusak": "Rusak",
    "hilang": "Hilang",
}
GROUP_PREFIX = "WMS Jumbo Bag"
MAX_NAMES = 300


def _bags_at(stage):
    """Serial No bag Active yang berada di Warehouse tahap tertentu."""
    frappe.has_permission("Serial No", "read", throw=True)
    return frappe.db.sql_list(
        """
        select sn.name
        from `tabSerial No` sn
        join `tabItem` i on i.name = sn.item_code
        join `tabWarehouse` w on w.name = sn.warehouse
        join `tabWarehouse` p on p.name = w.parent_warehouse
        where sn.status = 'Active'
          and i.is_wms_reusable_container = 1
          and w.warehouse_name = %s
          and p.name like %s
        order by sn.name
        """,
        (stage, GROUP_PREFIX + "%"),
    )


def _card(key):
    names = _bags_at(STAGES[key])
    result = {"value": len(names), "fieldtype": "Int", "route": ["List", "Serial No"]}
    if not names:
        result["route_options"] = {"name": "-"}
    elif len(names) <= MAX_NAMES:
        result["route_options"] = {"name": ["in", names]}
    return result


@frappe.whitelist()
def bag_kosong():
    return _card("kosong")


@frappe.whitelist()
def bag_isi():
    return _card("isi")


@frappe.whitelist()
def bag_rusak():
    return _card("rusak")


@frappe.whitelist()
def bag_hilang():
    return _card("hilang")
