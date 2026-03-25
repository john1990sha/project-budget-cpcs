# Copyright (c) 2026, john and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    summary = get_summary(data)
    return columns, data, None, chart, summary

def get_columns():
    return [
        {
            "label": "Project",
            "fieldname": "project",
            "fieldtype": "Link",
            "options": "Project",
            "width": 180
        },
        {
            "label": "Total Estimated",
            "fieldname": "total_estimated_budget",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": "Total Actual",
            "fieldname": "total_actual_cost",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": "Total Committed",
            "fieldname": "total_committed_cost",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": "Variance",
            "fieldname": "variance",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": "Variance %",
            "fieldname": "variance_percentage",
            "fieldtype": "Percent",
            "width": 120
        },
        {
            "label": "Utilization %",
            "fieldname": "budget_utilization_percentage",
            "fieldtype": "Percent",
            "width": 120
        },
        {
            "label": "Status",
            "fieldname": "budget_status",
            "fieldtype": "Data",
            "width": 130
        },
    ]


def get_data(filters):
    conditions = {}
    conditions["is_active_revision"] = 1
    if filters.get("project"):
        conditions["project"] = filters.get("project")

    if filters.get("budget_status"):
        conditions["budget_status"] = filters.get("budget_status")

    if filters.get("over_budget_only"):
        conditions["budget_status"] = "Over Budget"

    # 🔹 First fetch data
    data = frappe.get_all(
        "Project Budget",
        filters=conditions,
        fields=[
            "project",
            "total_estimated_budget",
            "total_actual_cost",
            "total_committed_cost",
            "variance",
            "variance_percentage",
            "budget_status",
            "budget_utilization_percentage"
        ]
    )

    # 🔹 Now loop and modify each row
    for row in data:

        row["utilization_indicator"] = ""

        util = row.get("budget_utilization_percentage") or 0

        if util < 80:
            row["utilization_indicator"] = "Green"
        elif util <= 100:
            row["utilization_indicator"] = "Orange"
        else:
            row["utilization_indicator"] = "Red"

    return data

# chart function for project budget report
def get_chart_data(data):
    labels = []
    estimated_values = []
    actual_values = []
    variance_values = []

    for row in data:
        labels.append(row.get("project"))

        estimated = row.get("total_estimated_budget") or 0
        actual = row.get("total_actual_cost") or 0
        variance = row.get("variance") or 0

        estimated_values.append(estimated)
        actual_values.append(actual)
        variance_values.append(variance)

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Estimated",
                    "values": estimated_values
                },
                {
                    "name": "Actual",
                    "values": actual_values
                },
                {
                    "name": "Variance",
                    "values": variance_values
                }
            ]
        },
        "type": "bar"
    }

# KPI
def get_summary(data):
    total_projects = len(data)
    total_estimated = 0
    total_actual = 0
    total_variance = 0
    over_budget_count = 0

    for row in data:
        estimated = row.get("total_estimated_budget") or 0
        actual = row.get("total_actual_cost") or 0
        variance = row.get("variance") or 0

        total_estimated += estimated
        total_actual += actual
        total_variance += variance

        if variance < 0:
            over_budget_count += 1

    return [
        {
            "value": total_projects,
            "label": "Total Projects",
            "datatype": "Int"
        },
        {
            "value": total_estimated,
            "label": "Total Estimated",
            "datatype": "Currency"
        },
        {
            "value": total_actual,
            "label": "Total Actual",
            "datatype": "Currency"
        },
        {
            "value": total_variance,
            "label": "Total Variance",
            "datatype": "Currency"
        },
        {
            "value": over_budget_count,
            "label": "Over Budget Projects",
            "datatype": "Int",
            "indicator": "Red" if over_budget_count > 0 else "Green"
        }
    ]