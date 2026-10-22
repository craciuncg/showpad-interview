"""Saved confirm and reject choices.

Keyed by company plus spoken name, so 'Bob' at Acme is not the same decision
as 'Bob' at another company. A later run of the same call must find this row
and reuse it. The model does not learn the choice. This dictionary does.
"""


def _key(account_crm_id, surface):
    """Stable key. Case and extra spaces do not create a second decision."""
    return (account_crm_id, " ".join(surface.casefold().split()))


class DecisionMemory:
    """One dictionary of decisions for the demo process."""

    def __init__(self):
        self.rows = {}

    def clear(self):
        """Forget every decision. Used by Reset."""
        self.rows = {}

    def record(self, account_crm_id, surface, decision, contact_id=""):
        """Save confirm or reject. A new choice for the same name replaces the old one."""
        if decision not in ("confirm", "reject"):
            raise ValueError("Decision must be confirm or reject.")
        row = {
            "account_id": account_crm_id,
            "surface": surface.strip(),
            "decision": decision,
            "contact_id": contact_id,
        }
        self.rows[_key(account_crm_id, surface)] = row
        return row

    def find(self, account_crm_id, surface):
        """Return the saved row, or None if the user has not chosen yet."""
        return self.rows.get(_key(account_crm_id, surface))

    def all_rows(self):
        """Every saved decision, for the screen or for a re-run."""
        return list(self.rows.values())
