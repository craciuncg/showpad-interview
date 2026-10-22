"""Drop a claim whose sentence is not in the saved call.

This is the hallucination gate. It does not call the model again. It only
checks strings: is the quote in the transcript, and is the name inside that quote?
"""

from backend.shared.ontology import CONCEPT_TYPES


def _squash(value):
    """Collapse repeated spaces so a wrapped quote can still be found."""
    return " ".join(str(value).split())


def find_quote(transcript, quote):
    """Find the quote in the call text.

    Returns (start, end, exact_slice) or None.
    The slice is the call's own characters, so the graph stores what was said,
    not a cleaned copy the model rewrote.
    A case-only difference is accepted. A different sentence is not.
    """
    cleaned = _squash(quote)
    if not cleaned:
        return None
    exact = transcript.find(cleaned)
    if exact >= 0:
        return exact, exact + len(cleaned), cleaned
    folded_text = transcript.casefold()
    folded_quote = cleaned.casefold()
    folded = folded_text.find(folded_quote)
    if folded >= 0:
        return folded, folded + len(cleaned), transcript[folded:folded + len(cleaned)]
    return None


def validate_mentions(transcript, raw_mentions):
    """Split the model's claims into kept and dropped.

    A person or vendor must have their name inside the quote.
    A worry only needs a real quote. Its label must be one of CONCEPT_TYPES,
    or it is stored as "other" and left out of the similar-sale count.
    """
    kept = []
    dropped = []
    for raw in raw_mentions:
        mention_type = str(raw.get("type", "")).strip().casefold()
        surface = _squash(str(raw.get("surface", "")))
        quote = str(raw.get("quote", ""))
        if mention_type not in ("person", "competitor", "concept"):
            dropped.append({**_public(raw), "reason": "The type is not person, competitor, or concept."})
            continue
        located = find_quote(transcript, quote)
        if located is None:
            # The usual invented sentence dies here. It is never stored.
            dropped.append({**_public(raw), "reason": "That sentence is not in the call."})
            continue
        start, end, stored_quote = located
        if mention_type in ("person", "competitor") and (not surface or surface.casefold() not in stored_quote.casefold()):
            dropped.append({**_public(raw), "reason": "The name does not appear inside the quoted sentence."})
            continue
        concept_type = str(raw.get("concept_type", "")).strip().casefold()
        if mention_type == "concept" and concept_type not in CONCEPT_TYPES:
            concept_type = "other"
        if mention_type == "concept" and not surface:
            surface = concept_type
        kept.append(
            {
                "type": mention_type,
                "surface": surface,
                "quote": stored_quote,
                "start": start,
                "end": end,
                "role_hint": _squash(str(raw.get("role_hint", ""))),
                "concept_type": concept_type if mention_type == "concept" else "",
                "kind": "objection" if mention_type == "concept" else "",
                "suggested_contact_id": str(raw.get("suggested_contact_id", "")).strip(),
            }
        )
    return kept, dropped


def _public(raw):
    """The fields the screen shows for a dropped claim."""
    return {
        "type": raw.get("type", ""),
        "surface": raw.get("surface", ""),
        "quote": raw.get("quote", ""),
    }
