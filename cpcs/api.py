import frappe
from frappe.utils import flt
from collections import defaultdict
from cpcs.cpcs.budget.utils import get_active_budget

def update_budget_on_submit(doc, method):
    for item in doc.items:
        if not doc.project:
            continue
        
        budget_name = frappe.db.get_value(
            "Project Budget",
            {"project": doc.project},
            "name"
        )
        
        if not budget_name:
            continue
        
        budget = frappe.get_doc("Project Budget", budget_name)

        for row in budget.budget_items:
            if row.cost_type == item.item_group:
                row.actual_cost = flt(row.actual_cost) + flt(item.base_net_amount)

        if budget.variance < 0:
            frappe.msgprint(
                f"""
                <b>Over Budget Warning</b><br>
                Project: {budget.project}<br>
                Over Amount: {abs(budget.variance)}
                """,
                indicator="red"
            )

        active_budget = get_active_budget(doc.project)

        if not active_budget:
            continue

        frappe.get_doc({
                "doctype": "Budget Consumption Log",
                "posting_date": doc.posting_date,
                "project": doc.project,
                "budget": active_budget,
                "cost_type": item.item_group,
                "reference_type": "Purchase Invoice",
                "reference_name": doc.name,
                "amount": item.amount
            }).insert(ignore_permissions=True)

        budget.save(ignore_permissions=True)

def update_budget_on_cancel(doc, method):
    
    for item in doc.items:
        if not doc.project:
            continue

        budget_name = frappe.db.get_value(
            "Project Budget",
            {"project": doc.project},
            "name"
        )
 
        if not budget_name:
            continue

        budget = frappe.get_doc("Project Budget", budget_name)

        for row in budget.budget_items:
            if row.cost_type == item.item_group:
                row.actual_cost = flt(row.actual_cost) - flt(item.base_net_amount)

        budget.save(ignore_permissions=True)

        frappe.db.set_value(
            "Budget Consumption Log",
            {
                "reference_type": "Purchase Invoice",
                "reference_name": doc.name
            },
            "is_cancelled",
            1
        )

@frappe.whitelist()
def recalculate_actual_cost(project):
    if not project:
        return

    # Get Project Budget
    budget_name = frappe.db.get_value(
        "Project Budget",
        {"project": project},
        "name"
    )

    if not budget_name:
        frappe.throw("Project Budget not found for this project")

    budget = frappe.get_doc("Project Budget", budget_name)

    # Reset actual cost
    for row in budget.budget_items:
        row.actual_cost = 0

    # Aggregate invoice data using SQL join (FASTER)
    # invoice_data = frappe.db.sql("""
    #     SELECT pii.item_group, SUM(pii.base_net_amount) as total_amount
    #     FROM `tabPurchase Invoice` pi
    #     JOIN `tabPurchase Invoice Item` pii ON pi.name = pii.parent
    #     WHERE pi.project = %s
    #     AND pi.docstatus = 1
    #     GROUP BY pii.item_group
    # """, (project,), as_dict=True)

    invoice_data = frappe.db.sql("""
    SELECT cost_type, SUM(amount) AS total_amount
    FROM `tabBudget Consumption Log`
    WHERE project = %s
    AND is_cancelled = 0
    GROUP BY cost_type
""", (project,), as_dict=True)

    # Convert to dictionary
    actual_map = {d.cost_type: flt(d.total_amount) for d in invoice_data}

    # Update child rows
    for row in budget.budget_items:
        if row.cost_type in actual_map:
            row.actual_cost = actual_map[row.cost_type]

    # Save (validate recalculates totals)
    budget.save(ignore_permissions=True)

    frappe.msgprint("Actual cost successfully recalculated.")


# code to connect expense claim with project budget
def update_budget_from_expense_claim(doc, method):

    if not doc.project:
        return

    # Get active project budget
    budget_name = frappe.db.get_value(
        "Project Budget",
        {"project": doc.project, "is_active_revision": 1},
        "name"
    )

    if not budget_name:
        return

    budget = frappe.get_doc("Project Budget", budget_name)

    for item in doc.expenses:

        for row in budget.budget_items:

            if row.cost_type == item.expense_type:
                row.actual_cost = flt(row.actual_cost) + flt(item.amount)

                # Create budget consumption log
                frappe.get_doc({
                    "doctype": "Budget Consumption Log",
                    "posting_date": doc.posting_date,
                    "project": doc.project,
                    "budget": budget.name,
                    "cost_type": row.cost_type,
                    "reference_type": "Expense Claim",
                    "reference_name": doc.name,
                    "amount": item.amount
                }).insert(ignore_permissions=True)

    budget.save(ignore_permissions=True)

def update_budget_on_cancel_expense_claim(doc, method):
    
    for item in doc.expenses:
        if not doc.project:
            continue

        budget_name = frappe.db.get_value(
            "Project Budget",
            {"project": doc.project},
            "name"
        )
 
        if not budget_name:
            continue

        budget = frappe.get_doc("Project Budget", budget_name)

        for row in budget.budget_items:
            if row.cost_type == item.expense_type:
                row.actual_cost = flt(row.actual_cost) - flt(item.amount)

        budget.save(ignore_permissions=True)

        frappe.db.set_value(
            "Budget Consumption Log",
            {
                "reference_type": "Expense Claim",
                "reference_name": doc.name
            },
            "is_cancelled",
            1
        )

def update_budget_from_journal_entry(doc, method):

    for row in doc.accounts:

        # Only consider debit entries with project
        if not row.project or flt(row.debit_in_account_currency) <= 0:
            continue

        # Get active project budget
        budget_name = frappe.db.get_value(
            "Project Budget",
            {"project": row.project, "is_active_revision": 1},
            "name"
        )

        if not budget_name:
            continue

        budget = frappe.get_doc("Project Budget", budget_name)

        # Match account with cost type
        for item in budget.budget_items:

            if item.cost_type == row.cost_type:

                item.actual_cost = flt(item.actual_cost) + flt(row.debit_in_account_currency)

                # Create budget consumption log
                frappe.get_doc({
                    "doctype": "Budget Consumption Log",
                    "posting_date": doc.posting_date,
                    "project": row.project,
                    "budget": budget.name,
                    "cost_type": item.cost_type,
                    "reference_type": "Journal Entry",
                    "reference_name": doc.name,
                    "amount": row.debit_in_account_currency
                }).insert(ignore_permissions=True)

        budget.save(ignore_permissions=True)

def cancel_budget_from_journal_entry(doc, method):

    for row in doc.accounts:

        if not row.project or flt(row.debit_in_account_currency) <= 0:
            continue

        budget_name = frappe.db.get_value(
            "Project Budget",
            {"project": row.project, "is_active_revision": 1},
            "name"
        )

        if not budget_name:
            continue

        budget = frappe.get_doc("Project Budget", budget_name)

        for item in budget.budget_items:

            if item.cost_type == row.cost_type:

                item.actual_cost = flt(item.actual_cost) - flt(row.debit_in_account_currency)

                # Mark consumption log as cancelled
                frappe.db.set_value(
                    "Budget Consumption Log",
                    {
                        "reference_name": doc.name,
                        "reference_type": "Journal Entry"
                    },
                    "is_cancelled",
                    1
                )

        budget.save(ignore_permissions=True)

def update_budget_from_po(doc, method):

    if not doc.project:
        return

    budget_name = frappe.db.get_value(
        "Project Budget",
        {"project": doc.project, "is_active_revision": 1},
        "name"
    )

    if not budget_name:
        return

    budget = frappe.get_doc("Project Budget", budget_name)

    for item in doc.items:

        for row in budget.budget_items:

            if row.cost_type == item.item_group:

                row.committed_cost = flt(row.committed_cost) + flt(item.base_net_amount)

                frappe.get_doc({
                    "doctype": "Budget Consumption Log",
                    "posting_date": doc.transaction_date,
                    "project": doc.project,
                    "budget": budget.name,
                    "cost_type": item.item_group,
                    "reference_type": "Purchase Order",
                    "reference_name": doc.name,
                    "amount": item.base_net_amount
                }).insert(ignore_permissions=True)

    budget.save(ignore_permissions=True)

def cancel_budget_from_po(doc, method):

    if not doc.project:
        return

    budget_name = frappe.db.get_value(
        "Project Budget",
        {"project": doc.project, "is_active_revision": 1},
        "name"
    )

    if not budget_name:
        return

    budget = frappe.get_doc("Project Budget", budget_name)

    for item in doc.items:

        for row in budget.budget_items:

            if row.cost_type == item.item_group:

                row.committed_cost = flt(row.committed_cost) - flt(item.base_net_amount)

                frappe.db.set_value(
                    "Budget Consumption Log",
                    {
                        "reference_name": doc.name,
                        "reference_type": "Purchase Order"
                    },
                    "is_cancelled",
                    1
                )

    budget.save(ignore_permissions=True)
