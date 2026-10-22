"""The only code that creates records and links.

CRM sync and a processed call both call this file. The model does not.
Ids are built from the CRM id, so a second sync updates the same record.
A second run of the same call deletes that call's old claims first.
Past sales are stored with history=True and then counted into one rollup.
"""

from backend.resolve_and_graph.resolve import resolve_person


def _account_node_id(crm_id):
    return f"account:{crm_id}"


def _contact_node_id(crm_id):
    return f"contact:{crm_id}"


def _deal_node_id(crm_id):
    return f"opportunity:{crm_id}"


def sync_crm(graph, payload):
    """Copy the CRM file into the graph. Running it twice updates the same records."""
    for name in payload["concept_types"]:
        graph.upsert(f"concept:{name}", "concept_type", name=name, label=name)
    for name in payload["action_types"]:
        graph.upsert(f"action:{name}", "action_type", name=name, label=name)
    for competitor in payload["competitors"]:
        graph.upsert(
            f"competitor:{competitor['id']}",
            "competitor",
            name=competitor["name"],
            aliases=competitor.get("aliases", []),
        )
    for account in payload["accounts"]:
        graph.upsert(
            _account_node_id(account["crm_id"]),
            "account",
            crm_id=account["crm_id"],
            name=account["name"],
            industry=account["industry"],
            # The history company is a bucket for past sales. The live view hides it.
            history=account["crm_id"] == "account-history",
        )
    for contact in payload["contacts"]:
        graph.upsert(
            _contact_node_id(contact["crm_id"]),
            "contact",
            crm_id=contact["crm_id"],
            name=contact["name"],
            title=contact["title"],
            account_id=_account_node_id(contact["account_id"]),
        )
        graph.link("BELONGS_TO", _contact_node_id(contact["crm_id"]), _account_node_id(contact["account_id"]), origin="crm")
    for deal in payload["opportunities"]:
        deal_id = _deal_node_id(deal["crm_id"])
        graph.upsert(
            deal_id,
            "opportunity",
            crm_id=deal["crm_id"],
            name=deal["name"],
            stage=deal["stage"],
            amount=deal["amount"],
            outcome=deal["outcome"],
            last_activity_days_ago=deal["last_activity_days_ago"],
            owner=deal["owner"],
            competitor_field=deal.get("competitor_field", ""),
            account_id=_account_node_id(deal["account_id"]),
            history=False,
        )
        graph.link("WITH", deal_id, _account_node_id(deal["account_id"]), origin="crm")
        for person in deal.get("involved", []):
            graph.link(
                "INVOLVED_IN",
                _contact_node_id(person["contact_id"]),
                deal_id,
                role=person["role"],
                origin="crm",
            )
    history = payload["finished_sales"]
    wins = history["won_with_small_start"]
    losses = history["lost_with_full_switch"]
    for index in range(wins):
        _add_finished_sale(graph, history, index + 1, "won", "small_start")
    for index in range(losses):
        _add_finished_sale(graph, history, index + 1, "lost", "full_switch")
    recompute_rollups(graph)
    return {
        "accounts": len(payload["accounts"]),
        "contacts": len(payload["contacts"]),
        "opportunities": len(payload["opportunities"]),
        "finished_sales": wins + losses,
    }


def _add_finished_sale(graph, history, index, outcome, action):
    node_id = f"opportunity:history-{outcome}-{index}"
    graph.upsert(
        node_id,
        "opportunity",
        crm_id=f"history-{outcome}-{index}",
        name=f"Past retail sale ({outcome} {index})",
        stage="Closed",
        amount=0,
        outcome=outcome,
        competitor_field="",
        account_id=_account_node_id(history["account_id"]),
        history=True,
    )
    graph.link("WITH", node_id, _account_node_id(history["account_id"]), origin="history")
    graph.link("RAISED", node_id, f"concept:{history['concept_type']}", origin="history")
    graph.link("TOOK_ACTION", node_id, f"action:{action}", origin="history")


def write_meeting(graph, meeting):
    """Replace this call's claims. A second run does not create a second copy."""
    meeting_id = meeting["id"]
    # Drop this call's old sentences and claims, then write the new ones.
    # The meeting record itself is kept and updated, so the id stays stable.
    derived_ids = {
        node["id"]
        for node in graph.nodes.values()
        if node.get("meeting_id") == meeting_id and node["type"] != "meeting"
    }
    graph.delete_nodes(derived_ids)
    graph.remove_edges(lambda edge: edge.get("meeting_id") == meeting_id)

    graph.upsert(
        meeting_id,
        "meeting",
        opportunity_id=meeting["opportunity_id"],
        account_id=meeting["account_id"],
        transcript_id=meeting["transcript_id"],
        label=meeting["label"],
    )
    graph.link("ABOUT", meeting_id, meeting["opportunity_id"], origin="calendar")

    for index, item in enumerate(meeting["mentions"], start=1):
        span_id = f"span:{meeting_id}:{index}"
        graph.upsert(
            span_id,
            "span",
            meeting_id=meeting_id,
            quote=item["quote"],
            start=item["start"],
            end=item["end"],
        )
        graph.link("HAS_SPAN", meeting_id, span_id, meeting_id=meeting_id)
        mention_id = f"mention:{meeting_id}:{index}"
        graph.upsert(
            mention_id,
            item["node_type"],
            meeting_id=meeting_id,
            account_id=meeting["account_id"],
            surface=item["surface"],
            status=item["status"],
            role_hint=item.get("role_hint", ""),
            concept_type=item.get("concept_type", ""),
            kind=item.get("kind", ""),
            note=item.get("note", ""),
            candidates=item.get("candidates", []),
        )
        graph.link("SUPPORTED_BY", mention_id, span_id, meeting_id=meeting_id)
        if item["node_type"] == "concept_mention" and item.get("concept_type"):
            graph.link("CLASSIFIED_AS", mention_id, f"concept:{item['concept_type']}", meeting_id=meeting_id)
            graph.link("RAISED", meeting["opportunity_id"], f"concept:{item['concept_type']}", meeting_id=meeting_id, origin="call")
        if item["node_type"] == "competitor_mention" and item.get("target_id"):
            graph.link("RESOLVES_TO", mention_id, item["target_id"], status=item["status"], meeting_id=meeting_id)
            graph.link("FACED", meeting["opportunity_id"], item["target_id"], meeting_id=meeting_id, origin="call")
        if item["node_type"] == "person_mention" and item.get("target_id"):
            graph.link("RESOLVES_TO", mention_id, item["target_id"], status=item["status"], meeting_id=meeting_id)

    recompute_rollups(graph)


def reapply_decisions(graph, memory):
    """User decisions can update people already in the graph without reading the call again."""
    for mention in graph.of_type("person_mention"):
        account = graph.get(mention["account_id"])
        contacts = _contacts_for_account(graph, mention["account_id"])
        decision = memory.find(account["crm_id"], mention["surface"])
        result = resolve_person(mention["surface"], contacts, decision, "")
        mention["status"] = result["status"]
        mention["note"] = result["note"]
        mention["candidates"] = result["candidates"]
        graph.remove_edges(
            lambda edge, mention_id=mention["id"]: edge["type"] == "RESOLVES_TO" and edge["source"] == mention_id
        )
        if result["target_id"]:
            graph.link("RESOLVES_TO", mention["id"], result["target_id"], status=result["status"], meeting_id=mention["meeting_id"])


def _contacts_for_account(graph, account_id):
    contacts = []
    for contact in graph.of_type("contact"):
        if contact.get("account_id") == account_id:
            contacts.append({"id": contact["id"], "name": contact["name"], "title": contact.get("title", "")})
    return contacts


def recompute_rollups(graph):
    """Count finished sales that share an industry and a worry label.

    The result is one hidden rollup record. The brief shows it only when
    the sample is at least three. Open sales are not counted.
    """
    graph.delete_nodes({node["id"] for node in graph.of_type("rollup")})
    groups = {}
    for deal in graph.of_type("opportunity"):
        if deal.get("outcome") not in ("won", "lost"):
            continue
        account = graph.get(deal.get("account_id"))
        industry = account["industry"] if account else ""
        for raised in graph.outgoing(deal["id"], "RAISED"):
            concept = graph.get(raised["target"])
            actions = [graph.get(edge["target"])["name"] for edge in graph.outgoing(deal["id"], "TOOK_ACTION")]
            action = actions[0] if actions else ""
            key = (industry, concept["name"])
            groups.setdefault(key, []).append({"outcome": deal["outcome"], "action": action})
    for (industry, concept_name), rows in groups.items():
        wins = [row for row in rows if row["outcome"] == "won"]
        losses = [row for row in rows if row["outcome"] == "lost"]
        graph.upsert(
            f"rollup:{industry}:{concept_name}",
            "rollup",
            industry=industry,
            concept_type=concept_name,
            sample_size=len(rows),
            wins=len(wins),
            losses=len(losses),
            win_action=_top_action(wins),
            loss_action=_top_action(losses),
            history=True,
        )


def _top_action(rows):
    counts = {}
    for row in rows:
        if row["action"]:
            counts[row["action"]] = counts.get(row["action"], 0) + 1
    if not counts:
        return ""
    return sorted(counts, key=counts.get, reverse=True)[0]
