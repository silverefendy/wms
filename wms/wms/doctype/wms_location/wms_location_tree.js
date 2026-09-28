frappe.treeview_settings["WMS Location"] = {
    fields: [
        {
            fieldtype: "Link",
            fieldname: "erpnext_warehouse",
            label: __("ERPNext Warehouse"),
            options: "Warehouse",
            depends_on: "eval:['Warehouse','State'].includes(doc.location_type)",
        },
        {
            fieldtype: "Link",
            fieldname: "state_name",
            label: __("State Name"),
            options: "WMS Location State",
            depends_on: "eval:doc.location_type=='State'",
        },
    ],
};
