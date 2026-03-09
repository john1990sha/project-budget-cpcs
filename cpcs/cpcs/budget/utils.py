import frappe

def get_active_budget(project):

    budget = frappe.db.get_all(
        "Project Budget",
        filters={
            "project": project,
            "is_active_revision": 1
        },
        fields=["name"],
        limit=1
    )

    return budget[0].name if budget else None