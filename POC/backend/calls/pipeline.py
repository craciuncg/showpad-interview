"""One finished call, step by step.

The screen calls process_call. The steps are the boxes in the diagram:
store the text, queue a job, ask Ollama, drop quotes that are not in the
file, match names only at this company, then let the writer update the graph.
The model never writes a record itself.
"""

from pathlib import Path

from backend.calls.queue import JobQueue
from backend.calls.store import TranscriptStore
from backend.calls.validate import validate_mentions
from backend.llm.client import extract_mentions
from backend.resolve_and_graph.resolve import resolve_competitor, resolve_person
from backend.resolve_and_graph.writer import write_meeting
from backend.seller_confirm_reject.memory import DecisionMemory

DATA = Path(__file__).resolve().parent / "data"

# The two sample calls. The file is the transcript. The opportunity id
# must already exist in the graph, which is why CRM sync comes first.
CALLS = {
    "acme": {
        "file": "acme.txt",
        "meeting_id": "meeting-1",
        "opportunity_id": "opportunity:deal-1",
        "label": "Acme call",
    },
    "sam": {
        "file": "sam.txt",
        "meeting_id": "meeting-2",
        "opportunity_id": "opportunity:deal-2",
        "label": "Globex call",
    },
}


def available_calls():
    listed = []
    for call_id, spec in CALLS.items():
        listed.append(
            {
                "id": call_id,
                "label": spec["label"],
                "opportunity_id": spec["opportunity_id"],
                "text": (DATA / spec["file"]).read_text(encoding="utf-8"),
            }
        )
    return listed


def process_call(graph, store: TranscriptStore, job_queue: JobQueue, memory: DecisionMemory, call_id: str):
    spec = CALLS.get(call_id)
    if spec is None:
        raise KeyError(call_id)
    deal = graph.get(spec["opportunity_id"])
    if deal is None:
        raise RuntimeError("Sync the CRM before processing a call.")
    account = graph.get(deal["account_id"])
    text = (DATA / spec["file"]).read_text(encoding="utf-8")
    steps = []

    stored = store.save(
        call_id,
        text,
        spec["meeting_id"],
        spec["opportunity_id"],
        account["id"],
        spec["label"],
    )
    steps.append({"component": "Transcript store", "detail": f"Saved {spec['label']} outside the graph."})

    # Put the job on the line and take it in the same request. A real worker
    # would take it later. The step list still shows both moments.
    job_queue.enqueue({"call_id": call_id, "meeting_id": spec["meeting_id"]})
    job = job_queue.dequeue()
    steps.append({"component": "Queue", "detail": "The finished call waited as a job, then a worker took it."})

    contacts = _contacts(graph, account["id"])
    competitors = _competitors(graph)
    raw, model_payload = extract_mentions(
        text,
        [{"crm_id": item["crm_id"], "name": item["name"]} for item in contacts],
        [{"name": item["name"]} for item in competitors],
    )
    steps.append({"component": "Extract", "detail": f"The model returned {len(raw)} claim(s). It does not write the graph."})

    kept, dropped = validate_mentions(text, raw)
    steps.append(
        {
            "component": "Validate",
            "detail": f"Kept {len(kept)} claim(s) whose sentence is in the call. Dropped {len(dropped)}.",
        }
    )

    mentions = []
    for item in kept:
        mentions.append(_resolve_one(item, account, contacts, competitors, graph, memory))
    steps.append({"component": "Resolve", "detail": "Spoken names were matched only against this company's records."})

    write_meeting(
        graph,
        {
            "id": spec["meeting_id"],
            "opportunity_id": spec["opportunity_id"],
            "account_id": account["id"],
            "transcript_id": stored["id"],
            "label": spec["label"],
            "mentions": mentions,
        },
    )
    job_queue.finish(job)
    steps.append({"component": "Graph writer", "detail": "This call's claims replaced any earlier copy of the same call."})

    return {
        "call_id": call_id,
        "label": spec["label"],
        "opportunity_id": spec["opportunity_id"],
        "transcript": text,
        "steps": steps,
        "model_claims": raw,
        "model_output": model_payload,
        "kept": kept,
        "dropped": dropped,
        "resolved": [
            {
                "surface": item["surface"],
                "type": item["node_type"],
                "status": item["status"],
                "note": item["note"],
            }
            for item in mentions
        ],
    }


def _resolve_one(item, account, contacts, competitors, graph, memory):
    if item["type"] == "person":
        suggested = ""
        for contact in contacts:
            # The model may send a CRM id or a graph id. Both are accepted here.
            # resolve_person still ignores the suggestion if the names disagree.
            if item["suggested_contact_id"] in (contact["id"], contact["crm_id"]):
                suggested = contact["id"]
        decision = memory.find(account["crm_id"], item["surface"])
        result = resolve_person(item["surface"], contacts, decision, suggested)
        return {**item, "node_type": "person_mention", **result, "candidates": result.get("candidates", [])}
    if item["type"] == "competitor":
        result = resolve_competitor(
            item["surface"],
            competitors,
            [node["name"] for node in graph.of_type("account")],
        )
        return {**item, "node_type": "competitor_mention", "candidates": [], **result}
    return {
        **item,
        "node_type": "concept_mention",
        "status": "classified",
        "target_id": f"concept:{item['concept_type']}",
        "candidates": [],
        "note": f"Counted under the label {item['concept_type']}.",
    }


def _contacts(graph, account_id):
    found = []
    for contact in graph.of_type("contact"):
        if contact.get("account_id") == account_id:
            found.append(
                {
                    "id": contact["id"],
                    "crm_id": contact["crm_id"],
                    "name": contact["name"],
                    "title": contact.get("title", ""),
                }
            )
    return found


def _competitors(graph):
    return [
        {"id": node["id"], "name": node["name"], "aliases": node.get("aliases", [])}
        for node in graph.of_type("competitor")
    ]
