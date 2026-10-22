"""Turn a typed question into a short answer plus the facts it may use.

The brief is built first. The screen shows those facts in three groups:
the customer file, this call, and the similar-sale count. A model sentence
is left out only when it matches none of those groups. That sentence is
also taken out of the paragraph.
"""

from backend.llm.client import answer
from backend.query_api.brief import build_brief


def ask(graph, opportunity_id, question):
    brief = build_brief(graph, opportunity_id)
    if not brief.get("ready"):
        return brief
    packet = {
        "sale": {
            "name": brief["name"],
            "stage": brief["stage"],
            "competitor_field": brief["competitor_field"] or "empty",
            "account": brief["account"],
        },
        "missing_people": brief["missing_people"],
        "spoken": brief["spoken"],
        "similar_sales": brief["similar"],
        "allowed_citations": _allowed(brief),
    }
    sentences, prose, raw = answer(question, packet)
    allowed = set(packet["allowed_citations"])
    left_out = []
    for sentence in sentences:
        citations = sentence["citations"]
        cited = bool(citations) and all(citation in allowed for citation in citations)
        # A cited sentence is already backed by a group. An uncited sentence
        # stays in the reply when its words match a group. Otherwise it is extra.
        if cited or not _is_left_out(sentence["text"], brief):
            continue
        left_out.append(
            {
                **sentence,
                "reason": "This sentence is not in the customer file, this call, or the similar-sale count.",
            }
        )
    used_brief = False
    if not prose:
        prose = _reply(brief)
        used_brief = True
    else:
        for sentence in left_out:
            prose = _strip(prose, sentence["text"])
        prose = " ".join(prose.split())
        if not prose:
            prose = _reply(brief)
            used_brief = True
    return {
        "ready": True,
        "question": question,
        "prose": prose,
        "customer_file": _customer_file(brief),
        "call": _call_items(brief),
        "similar": _similar_items(brief),
        "left_out": left_out,
        "used_brief_instead": used_brief,
        "model_output": raw,
    }


def _customer_file(brief):
    """Fields copied from the CRM. They are shown even when the model cites no label."""
    return [
        {"label": "Stage", "value": brief["stage"]},
        {"label": "Vendor field", "value": brief["competitor_field"] or "empty"},
    ]


def _call_items(brief):
    """Quotes already kept from this sale's call."""
    items = []
    for item in brief["missing_people"] + brief["spoken"]:
        items.append(
            {
                "id": item["span_id"],
                "label": item.get("name") or item.get("label") or "Call",
                "quote": item["quote"],
            }
        )
    return items


def _similar_items(brief):
    """The count, when the sample is large enough to show."""
    items = []
    for item in brief["similar"]:
        if not item.get("shown"):
            continue
        items.append(
            {
                "label": item["concept_type"],
                "quote": (
                    f"{item['wins']} signed after {item['win_action']}, "
                    f"{item['losses']} lost after {item['loss_action']}. "
                    f"Sample: {item['sample_size']}."
                ),
            }
        )
    return items


def _is_left_out(text, brief):
    """True when this sentence does not mention a fact already in one of the three groups."""
    lowered = " ".join(text.casefold().split())
    if not lowered:
        return False
    if _mentions_customer_file(lowered, brief):
        return False
    if _mentions_call(lowered, brief):
        return False
    if _mentions_similar(lowered, brief):
        return False
    return True


def _mentions_customer_file(lowered, brief):
    tokens = [brief["stage"], brief["account"], brief["name"], "vendor field", "customer file"]
    if brief.get("competitor_field"):
        tokens.append(brief["competitor_field"])
    return any(token and token.casefold() in lowered for token in tokens)


def _mentions_call(lowered, brief):
    for item in brief["missing_people"] + brief["spoken"]:
        label = item.get("name") or item.get("label") or ""
        quote = item.get("quote") or ""
        if label and label.casefold() in lowered:
            return True
        if quote and quote.casefold() in lowered:
            return True
    return False


def _mentions_similar(lowered, brief):
    if "similar" in lowered:
        return True
    for item in brief["similar"]:
        if not item.get("shown"):
            continue
        for token in (item["concept_type"], item["win_action"], item["loss_action"], str(item["sample_size"])):
            if token and token.casefold() in lowered:
                return True
    return False


def _strip(prose, sentence):
    """Take a left-out sentence out of the paragraph, including a comma in place of its period."""
    cleaned = prose.replace(sentence, " ")
    trimmed = sentence.rstrip(" .")
    if trimmed:
        cleaned = cleaned.replace(trimmed, " ")
    return cleaned


def _allowed(brief):
    ids = ["crm:stage", "crm:vendor_field", "rollup"]
    for item in brief["missing_people"] + brief["spoken"]:
        ids.append(item["span_id"])
    return ids


def _reply(brief):
    parts = [f"{brief['name']} is in {brief['stage']}."]
    if not brief["competitor_field"]:
        parts.append("The vendor field in the customer file is empty.")
    for person in brief["missing_people"]:
        parts.append(f"{person['name']} was named and is not a confirmed contact.")
    for item in brief["spoken"]:
        if item["kind"] == "competitor":
            parts.append(f"The call compares this sale with {item['label']}.")
        else:
            parts.append(f"The call raises {item['label']}: \"{item['quote']}\"")
    for item in brief["similar"]:
        if item.get("shown"):
            parts.append(
                f"On {item['sample_size']} similar finished sales, {item['wins']} were signed after {item['win_action']} and {item['losses']} were lost after {item['loss_action']}."
            )
    return " ".join(parts)
