// Copyright (c) 2026, john and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project Budget', {

    refresh: function(frm) {

        // Warning message code for over budget
        if (frm.doc.variance != null && frm.doc.variance < 0) {

            frappe.msgprint({
                title: "Over Budget Alert",
                message: "Warning: Project is Over Budget!",
                indicator: "red"
            });
        }

        // Add recalulation button
        if (!frm.is_new()) {
            frm.add_custom_button("Recalculate Actual Cost", function() {
                frappe.call({
                    method: "cpcs.api.recalculate_actual_cost",
                    args: {
                        project: frm.doc.project
                    },
                    callback: function() {
                        frm.reload_doc();
                    }
                });
            });
        }

        // code for budget revision
        if (frm.doc.status === "Approved" && !frm.is_new()) {
            frm.add_custom_button("Create Revision", function() {
                frappe.call({
                    method: "cpcs.cpcs.doctype.project_budget.project_budget.create_revision",
                    args: {
                        budget_name: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.set_route("Form", "Project Budget", r.message);
                        }
                    }
                });
            });
        }
        // code for utilization bar
        // render_total_budget_bar(frm);
        if (frm.doc.budget_utilization_percentage >= 80 && frm.doc.budget_utilization_percentage < 100) {

            frm.dashboard.set_headline_alert(
                __("⚠ Budget utilization above 80%"),
                "orange"
            );
        }

        if (frm.doc.budget_utilization_percentage >= 100) {

            frm.dashboard.set_headline_alert(
                __("❗ Budget exceeded"),
                "red"
            );
        }
    }

});

