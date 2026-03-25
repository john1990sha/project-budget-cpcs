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

## account mapping with cost type
def get_cost_type_from_account(account):
    """
    Fetch cost type from Account Cost Type Mapping
    """

    if not account:
        return None

    mapping = frappe.get_all(
        "Account Cost Type Mapping",
        filters={"account": account},
        fields=["cost_type"],
        order_by="priority asc",
        limit=1
    )

    if mapping:
        return mapping[0].cost_type

    return None