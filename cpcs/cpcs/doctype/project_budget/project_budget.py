# Copyright (c) 2026, john and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt

class ProjectBudget(Document):

    def validate(self):

        total_estimated = 0
        total_actual = 0
        total_committed = 0

        for row in self.budget_items:
            estimate = flt(row.estimate_cost)
            actual = flt(row.actual_cost)
            committed = flt(row.committed_cost)
 
            row.variance = estimate - (committed + actual)

            total_estimated += estimate
            total_actual += actual
            total_committed += committed

        self.total_estimated_budget = total_estimated
        self.total_actual_cost = total_actual
        self.total_committed_cost = total_committed

        self.variance = total_estimated - (total_committed + total_actual)

        self.variance_percentage = (
            (self.variance / total_estimated) * 100
            if total_estimated else 0
        )

        self.budget_status = (
            "Over Budget" if self.variance < 0
            else "Under Budget" if self.variance > 0
            else "On Budget"
        )

        # 🔥 New Logic
        if total_estimated > 0:
            self.budget_utilization_percentage = ((total_actual + total_committed) / total_estimated) * 100
        else:
            self.budget_utilization_percentage = 0

        # Only check when trying to submit
        if self.docstatus == 0 and not self.amended_from:
            existing_active = frappe.get_all(
                    "Project Budget",
                    filters={"project": self.project, "is_active_revision": 1, "name": ["!=", self.name]},
                    fields=["name"]
                )

            if existing_active:
                frappe.throw(_("Active Budget already exists for this Project. Please use Amend instead."))
    # def before_save(self):
        
    #     # Only check when trying to submit
    #     if self.docstatus == 0 and not self.amended_from:
    #         existing_active = frappe.get_all(
    #                 "Project Budget",
    #                 filters={"project": self.project, "is_active_revision": 1, "name": ["!=", self.name]},
    #                 fields=["name"]
    #             )

    #         #frappe.msgprint(str(existing_active))
    #         if existing_active:
    #             frappe.msgprint(
    #                 "Active Budget already exists for this Project. Please use Amend instead."
    #             )

    def before_submit(self):

        # If this is a revision
        if self.amended_from:

            # Find all other submitted budgets for same project
            previous_budgets = frappe.get_all(
                "Project Budget",
                filters={
                    "project": self.project,
                    "docstatus": 1,
                    "name": ["!=", self.name]
                },
                pluck="name"
            )

            # Mark them inactive
            for pb in previous_budgets:
                frappe.db.set_value(
                    "Project Budget",
                    pb,
                    "is_active_revision",
                    0
                )

        # Make current one active
        self.is_active_revision = 1


@frappe.whitelist()
def create_revision(budget_name):
    old_budget = frappe.get_doc("Project Budget", budget_name)

    if old_budget.status != "Approved":
        frappe.throw("Only Approved Budget can be revised.")

    # Deactivate old revision
    old_budget.is_active_revision = 0
    old_budget.save(ignore_permissions=True)

    # Create new revision
    new_budget = frappe.copy_doc(old_budget)
    new_budget.status = "Draft"
    new_budget.revision_no = (old_budget.revision_no or 1) + 1
    new_budget.previous_revision = old_budget.name
    new_budget.is_active_revision = 1

    new_budget.insert(ignore_permissions=True)

    return new_budget.name
