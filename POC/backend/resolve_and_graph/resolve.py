"""Match a spoken name to a known record, or leave it open.

No model and no library. The inputs are strings and lists. The output is
a small dictionary: status, the chosen id if any, and a note for the screen.
"""


def _norm(value):
    """Lowercase and collapse spaces, so '  Bob ' and 'bob' compare equal."""
    return " ".join(str(value or "").casefold().split())


def _first(value):
    """The first word of a name. 'Sam' against 'Sam Lee' uses this."""
    parts = _norm(value).split()
    return parts[0] if parts else ""


def score_contact(surface, contact):
    """How well a spoken name matches one CRM contact. Higher is better.

    100: the full name is the same.
    60: only the first name matches. Weak, so two first-name hits stay ambiguous.
    40: the spoken name is only part of the full name.
    0: no match. A zero is not even kept as a candidate.
    """
    spoken = _norm(surface)
    name = _norm(contact.get("name"))
    if not spoken or not name:
        return 0
    if spoken == name:
        return 100
    if spoken == _first(name):
        return 60
    if spoken in name:
        return 40
    return 0


def resolve_person(surface, contacts, memory_decision, suggested_contact_id):
    """Decide what a spoken person name is.

    contacts: only the people at this one company. Other companies are not searched.
    memory_decision: a saved confirm or reject. It wins over a fresh score.
    suggested_contact_id: the model's guess. It is used only if the names agree.
    """
    # A saved user choice is applied before any scoring.
    if memory_decision:
        decision = memory_decision["decision"]
        if decision == "reject":
            return {
                "status": "rejected",
                "target_id": None,
                "candidates": [],
                "note": "The user rejected this match. It is not linked.",
            }
        contact_id = memory_decision.get("contact_id") or ""
        if decision == "confirm" and contact_id:
            # The user said this spoken name is a specific CRM person.
            return {
                "status": "resolved",
                "target_id": contact_id,
                "candidates": [contact_id],
                "note": "Reused the user's earlier confirmation.",
            }
        if decision == "confirm":
            # Real person, but nobody has added them to the CRM yet.
            return {
                "status": "confirmed_by_seller",
                "target_id": None,
                "candidates": [],
                "note": "The user confirmed this person is real. They are still not in the CRM.",
            }

    # Score every contact at this company. Drop zeros.
    scored = []
    for contact in contacts:
        score = score_contact(surface, contact)
        if score:
            scored.append((score, contact["id"]))
    scored.sort(reverse=True)

    # The model may suggest a contact id. Ignore it unless the name actually matches.
    suggestion_note = ""
    if suggested_contact_id:
        suggested = next((contact for contact in contacts if contact["id"] == suggested_contact_id), None)
        if suggested is None or score_contact(surface, suggested) < 80:
            suggestion_note = "The model suggested a contact. The names do not agree, so the suggestion was ignored."

    if not scored:
        return {
            "status": "unresolved",
            "target_id": None,
            "candidates": [],
            "note": suggestion_note or "No contact at this company matches the spoken name.",
        }

    best_score, best_id = scored[0]
    second = scored[1][0] if len(scored) > 1 else 0
    # Two scores within 20 points of each other are too close to pick.
    close_ids = [contact_id for score, contact_id in scored if best_score - score < 20]
    if best_score >= 60 and len(close_ids) > 1:
        return {
            "status": "ambiguous",
            "target_id": None,
            "candidates": close_ids,
            "note": "More than one contact is close to this name. No one was chosen.",
        }
    # A full-name match, or one first name that is clearly ahead of the next.
    if best_score >= 80 or (best_score >= 60 and best_score - second >= 20):
        return {
            "status": "resolved",
            "target_id": best_id,
            "candidates": [best_id],
            "note": suggestion_note or "One contact is clearly ahead of the others.",
        }
    return {
        "status": "unresolved",
        "target_id": None,
        "candidates": [contact_id for _, contact_id in scored],
        "note": suggestion_note or "The name is too weak to link.",
    }


def resolve_competitor(surface, competitors, account_names):
    """Match a spoken vendor name to the catalog, or leave it open.

    If the same name is also a buyer company, do not auto-link. That would
    mix a customer with a vendor.
    """
    spoken = _norm(surface)
    if spoken in {_norm(name) for name in account_names}:
        return {
            "status": "ambiguous",
            "target_id": None,
            "note": "This name is both a company in the CRM and a vendor. It was not auto-linked.",
        }
    matches = []
    for competitor in competitors:
        names = [_norm(competitor["name"]), *[_norm(alias) for alias in competitor.get("aliases", [])]]
        if spoken in names:
            matches.append(competitor["id"])
    if len(matches) == 1:
        return {"status": "resolved", "target_id": matches[0], "note": "The spoken name matches the vendor list."}
    if len(matches) > 1:
        return {"status": "ambiguous", "target_id": None, "note": "More than one vendor matches this name."}
    return {"status": "unresolved", "target_id": None, "note": "This vendor is not in the catalog."}
