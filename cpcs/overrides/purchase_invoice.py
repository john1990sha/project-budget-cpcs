import frappe
from frappe import _

def before_submit(doc, method):
    for item in doc.items:

        if not doc.project:
            frappe.throw(_("Project is required in Purchase Invoice Items."))

        # Get budget using get_all first
        budget_list = frappe.get_all(
            "Project Budget",
            filters={
                "project": doc.project, 
                "is_active_revision": 1
            },
            fields=["name", "status", "total_actual_cost", "total_estimated_budget"],
            limit=1
        )

        if not budget_list:
            frappe.throw(_("No Project Budget found for Project {0}").format(item.project))

        budget = budget_list[0]

        if budget.status != "Approved":
            frappe.throw(_("Project Budget {0} is not Approved.").format(budget.name))

        # 🔥 Calculate new utilization after this invoice
        new_actual = (budget.total_actual_cost or 0) + (item.amount or 0)

        if budget.total_estimated_budget and budget.total_estimated_budget > 0:
            new_utilization = (new_actual / budget.total_estimated_budget) * 100
        else:
            new_utilization = 0

        # 🟠 Warning zone
        if 100 < new_utilization <= 110:
            frappe.msgprint(
                _("Warning: Budget utilization will reach {0:.2f}%").format(new_utilization)
            )

        # 🔴 Hard block
        if new_utilization > 110:
            if "Accounts Manager" not in frappe.get_roles():
                frappe.throw(
                    _("Budget utilization exceeds 110%. Accounts Manager approval required.")
                )
# def before_submit(doc, method):
#     for item in doc.items:
#         if not item.project:
#             frappe.throw(_("Project is required in Purchase Invoice Items."))

#         # Get Project Budget linked to this project
#         budget = frappe.get_all(
#             "Project Budget",
#             filters={"project": item.project},
#             fields=["name", "status"],
#             limit=1
#         )

#         if not budget:
#             frappe.throw(_("No Project Budget found for Project {0}").format(item.project))

#         if budget[0].status != "Approved":
#             frappe.throw(_("Project Budget {0} is not Approved. Cannot submit Purchase Invoice.").format(budget[0].name))