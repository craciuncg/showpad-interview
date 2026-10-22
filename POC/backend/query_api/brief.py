"""The three fixed questions for one sale. No model is used here.

1. Who is on the sale, and who was named but is not a confirmed contact?
2. What did the call say that the CRM field does not?
3. On similar finished sales, what happened, and is the sample large enough?
"""

from backend.shared.ontology import MINIMUM_SIMILAR_DEALS


def build_brief(graph, opportunity_id):
    deal = graph.get(opportunity_id)
    if deal is None or deal["type"] != "opportunity":
        return {"ready": False, "detail": "That sale is not in the graph. Sync the CRM first."}
    account = graph.get(deal["account_id"])
    meeting_ids = [edge["source"] for edge in graph.incoming(opportunity_id, "ABOUT")]
    span_ids = []
    for meeting_id in meeting_ids:
        span_ids.extend(edge["target"] for edge in graph.outgoing(meeting_id, "HAS_SPAN"))
    mention_ids = []
    for span_id in span_ids:
        mention_ids.extend(edge["source"] for edge in graph.incoming(span_id, "SUPPORTED_BY"))

    people = []
    missing = []
    spoken = []
    for contact_edge in graph.incoming(opportunity_id, "INVOLVED_IN"):
        contact = graph.get(contact_edge["source"])
        people.append(
            {
                "name": contact["name"],
                "role": contact_edge.get("role", ""),
                "where": "CRM",
            }
        )
    for mention_id in mention_ids:
        mention = graph.get(mention_id)
        span = _span_for(graph, mention_id)
        if mention["type"] == "person_mention":
            people.append(
                {
                    "name": mention["surface"],
                    "role": mention.get("role_hint", ""),
                    "where": mention["status"],
                }
            )
            if mention["status"] != "resolved":
                missing.append(
                    {
                        "name": mention["surface"],
                        "status": mention["status"],
                        "role_hint": mention.get("role_hint", ""),
                        "quote": span["quote"],
                        "span_id": span["id"],
                        "note": mention.get("note", ""),
                    }
                )
        if mention["type"] in ("competitor_mention", "concept_mention"):
            spoken.append(
                {
                    "kind": "competitor" if mention["type"] == "competitor_mention" else "concept",
                    "label": mention["surface"] if mention["type"] == "competitor_mention" else mention.get("concept_type", ""),
                    "status": mention["status"] if mention["type"] == "competitor_mention" else "classified",
                    "quote": span["quote"],
                    "span_id": span["id"],
                    "crm_competitor_field": deal.get("competitor_field", ""),
                }
            )

    concept_types = []
    for edge in graph.outgoing(opportunity_id, "RAISED"):
        concept = graph.get(edge["target"])
        # meeting_id is set only when a call raised this worry.
        # History links have no meeting_id, so past sales are not double counted here.
        if concept and edge.get("meeting_id"):
            concept_types.append(concept["name"])
    similar = []
    for concept_name in sorted(set(concept_types)):
        rollup = graph.get(f"rollup:{account['industry']}:{concept_name}")
        if rollup is None or rollup["sample_size"] < MINIMUM_SIMILAR_DEALS:
            similar.append(
                {
                    "concept_type": concept_name,
                    "shown": False,
                    "detail": "Not enough finished sales of this kind.",
                }
            )
        else:
            similar.append(
                {
                    "concept_type": concept_name,
                    "shown": True,
                    "sample_size": rollup["sample_size"],
                    "wins": rollup["wins"],
                    "losses": rollup["losses"],
                    "win_action": rollup["win_action"],
                    "loss_action": rollup["loss_action"],
                }
            )
    return {
        "ready": True,
        "opportunity_id": opportunity_id,
        "name": deal["name"],
        "stage": deal["stage"],
        "amount": deal["amount"],
        "outcome": deal["outcome"],
        "competitor_field": deal.get("competitor_field", ""),
        "account": account["name"],
        "industry": account["industry"],
        "people": people,
        "missing_people": missing,
        "spoken": spoken,
        "similar": similar,
    }


def _span_for(graph, mention_id):
    edges = graph.outgoing(mention_id, "SUPPORTED_BY")
    return graph.get(edges[0]["target"])
