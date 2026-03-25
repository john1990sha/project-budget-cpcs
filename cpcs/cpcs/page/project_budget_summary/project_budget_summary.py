import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt
from frappe.desk.query_report import run
import json


@frappe.whitelist()
def get_project_budget_summary(filters=None):

    # ✅ Convert string to dict
    if isinstance(filters, str):
        filters = json.loads(filters)

    filters = filters or {}

    project = filters.get("project")

    if project:
        # filter by project
        data = run(
            "Project Budget Summary",
            filters={"project": project}
        )
    else:
        # load all projects
        data = run(
            "Project Budget Summary",
            filters={}
        )

    return data