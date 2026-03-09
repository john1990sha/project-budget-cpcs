// Copyright (c) 2026, john and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Budget Consumption Log"] = {
    "filters": [
        {
            fieldname: "project",
            label: "Project",
            fieldtype: "Link",
            options: "Project"
        },
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date"
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date"
        },
        {
            fieldname: "is_cancelled",
            label: "Show Cancelled Log",
            fieldtype: "Check",
            default: 0
        }
    ]
};