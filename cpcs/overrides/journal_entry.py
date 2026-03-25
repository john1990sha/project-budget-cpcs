import frappe
from frappe import _
from cpcs.cpcs.budget.utils import get_cost_type_from_account

def apply_cost_type_journal(doc, method):
    for row in doc.accounts:

        # Skip if already set manually
        if row.cost_type:
            continue

        row.cost_type = get_cost_type_from_account(row.account)