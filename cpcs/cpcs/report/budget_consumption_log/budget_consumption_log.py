# Copyright (c) 2026, john and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():

    return [
        {"label": "Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},
        {"label": "Budget", "fieldname": "budget", "fieldtype": "Link", "options": "Project Budget", "width": 150},
        {"label": "Cost Type", "fieldname": "cost_type", "fieldtype": "Data", "width": 150},
        {"label": "Reference Type", "fieldname": "reference_type", "fieldtype": "Data", "width": 150},
        {"label": "Reference", "fieldname": "reference_name", "fieldtype": "Dynamic Link", "options": "reference_type", "width": 180},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 120},
    ]


def get_data(filters):

    conditions = ""

    if filters.get("project"):
        conditions += " AND project = %(project)s"

    if filters.get("from_date"):
        conditions += " AND posting_date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND posting_date <= %(to_date)s"

    if filters.get("is_cancelled"):
        conditions += "AND is_cancelled = 1"
    else:
    	conditions += "AND is_cancelled = 0"

    data = frappe.db.sql(f"""
        SELECT
            posting_date,
            project,
            budget,
            cost_type,
            reference_type,
            reference_name,
            amount
        FROM `tabBudget Consumption Log`
        WHERE 1=1 {conditions}
        ORDER BY posting_date DESC
    """, filters, as_dict=True)

    return data