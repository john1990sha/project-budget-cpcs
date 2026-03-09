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
                "cost_type": "Material",
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
    invoice_data = frappe.db.sql("""
        SELECT pii.item_group, SUM(pii.base_net_amount) as total_amount
        FROM `tabPurchase Invoice` pi
        JOIN `tabPurchase Invoice Item` pii ON pi.name = pii.parent
        WHERE pi.project = %s
        AND pi.docstatus = 1
        GROUP BY pii.item_group
    """, (project,), as_dict=True)

    # Convert to dictionary
    actual_map = {d.item_group: flt(d.total_amount) for d in invoice_data}

    # Update child rows
    for row in budget.budget_items:
        if row.cost_type in actual_map:
            row.actual_cost = actual_map[row.cost_type]

    # Save (validate recalculates totals)
    budget.save(ignore_permissions=True)

    frappe.msgprint("Actual cost successfully recalculated.")