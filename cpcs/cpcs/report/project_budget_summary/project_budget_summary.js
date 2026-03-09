// Copyright (c) 2026, john and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Project Budget Summary"] = {
    filters: [
        {
            fieldname: "project",
            label: "Project",
            fieldtype: "Link",
            options: "Project"
        },
        {
            fieldname: "budget_status",
            label: "Budget Status",
            fieldtype: "Select",
            options: "\nOver Budget\nUnder Budget\nOn Budget"
        },
        {
            fieldname: "over_budget_only",
            label: "Show Only Over Budget",
            fieldtype: "Check"
        }
    ],

    formatter: function(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (column.fieldname == "budget_status") {

            if (data.budget_status === "Over Budget") {
                value = `<span style="color:red; font-weight:bold;">${value}</span>`;
            }

            if (data.budget_status === "Under Budget") {
                value = `<span style="color:green; font-weight:bold;">${value}</span>`;
            }

            if (data.budget_status === "On Budget") {
                value = `<span style="color:orange; font-weight:bold;">${value}</span>`;
            }
        }

        if (column.fieldname == "budget_utilization_percentage") {
	        if (data.budget_utilization_percentage > 100) {
	            value = `<span style="color:red;font-weight:bold">${value}</span>`;
	        } else if (data.budget_utilization_percentage >= 80) {
	            value = `<span style="color:orange;font-weight:bold">${value}</span>`;
	        } else {
	            value = `<span style="color:green;font-weight:bold">${value}</span>`;
	        }
	    }

        return value;
    }
};
