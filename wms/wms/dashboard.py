import frappe

LOCATIONS = {
    "kosong": "WP-KOSONG",
    "isi": "WP-ISI",
    "rusak": "WP-RUSAK",
    "hilang": "WP-HILANG",
}
MAX_NAMES = 300


def _bags_at(location):
    frappe.has_permission("Serial No", "read", throw=True)
    rows = frappe.db.sql(
        """
        select sabe.serial_no,
               sum(case when sabe.is_outward = 1 then -abs(sabe.qty) else abs(sabe.qty) end) as net
        from `tabStock Ledger Entry` sle
        join `tabSerial and Batch Entry` sabe on sabe.parent = sle.serial_and_batch_bundle
        join `tabSerial No` sn on sn.name = sabe.serial_no
        join `tabItem` i on i.name = sn.item_code
        where sle.is_cancelled = 0
          and sle.target_wms_location = %s
          and i.is_wms_reusable_container = 1
        group by sabe.serial_no
        having net > 0
        """,
        location,
    )
    return [r[0] for r in rows]


def _card(key):
    names = _bags_at(LOCATIONS[key])
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
