"""The only file that talks to the local model.

Ollama is already running on this machine. The model name is gemma4:e2b.
This file uses urllib from the standard library. It asks for JSON and
temperature 0 so the same call tends to come back the same way.
Extract returns claims. Answer returns sentences. Neither writes the graph.
"""

import json
from pathlib import Path
from urllib import error, request

MODEL = "gemma4:e2b"
CHAT_URL = "http://127.0.0.1:11434/api/chat"
TAGS_URL = "http://127.0.0.1:11434/api/tags"
PROMPT_DIR = Path(__file__).resolve().parent / "prompts"


class ModelError(RuntimeError):
    """Ollama is down, or the text it returned is not JSON we can read."""


def status():
    try:
        with request.urlopen(TAGS_URL, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (error.URLError, TimeoutError) as exc:
        return {"ok": False, "model": MODEL, "detail": "Ollama is not running."}
    names = [item.get("name", "") for item in payload.get("models", [])]
    ready = MODEL in names
    return {"ok": ready, "model": MODEL, "detail": "Model is available." if ready else f"{MODEL} is not in the local model list."}


def extract_mentions(transcript, contacts, competitors):
    instruction = (PROMPT_DIR / "extract.txt").read_text(encoding="utf-8")
    contact_lines = "\n".join(f"- {item['crm_id']}: {item['name']}" for item in contacts) or "- none"
    competitor_lines = "\n".join(f"- {item['name']}" for item in competitors) or "- none"
    user = (
        f"Transcript:\n{transcript}\n\n"
        f"Known contacts at this company:\n{contact_lines}\n\n"
        f"Known vendors:\n{competitor_lines}"
    )
    payload = _chat(
        [
            {"role": "system", "content": instruction},
            {"role": "user", "content": user},
        ]
    )
    return _mentions_from(payload), payload


def answer(question, packet):
    instruction = (PROMPT_DIR / "answer.txt").read_text(encoding="utf-8")
    user = f"Question: {question}\n\nPacket:\n{json.dumps(packet, indent=2)}"
    payload = _chat(
        [
            {"role": "system", "content": instruction},
            {"role": "user", "content": user},
        ]
    )
    prose = ""
    sentences = []
    if isinstance(payload, dict):
        prose = str(payload.get("answer") or "").strip()
        if isinstance(payload.get("sentences"), list):
            sentences = payload["sentences"]
    cleaned = []
    for sentence in sentences:
        if not isinstance(sentence, dict):
            continue
        citations = sentence.get("citations") or sentence.get("span_ids") or []
        if isinstance(citations, str):
            citations = [citations]
        cleaned.append({"text": str(sentence.get("text", "")).strip(), "citations": [str(item) for item in citations]})
    return [item for item in cleaned if item["text"]], prose, payload


def _chat(messages):
    body = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        # format json asks Ollama for an object. temperature 0 reduces drift.
        "format": "json",
        "options": {"temperature": 0},
    }
    raw = json.dumps(body).encode("utf-8")
    call = request.Request(CHAT_URL, data=raw, headers={"Content-Type": "application/json"})
    try:
        with request.urlopen(call, timeout=180) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ModelError(f"Ollama returned {exc.code}: {detail}") from exc
    except (error.URLError, TimeoutError) as exc:
        raise ModelError("Could not reach Ollama. Start it, then try the call again.") from exc
    content = payload.get("message", {}).get("content", "")
    return _load_json(content)


def _load_json(content):
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise ModelError("The model did not return JSON.")


def _mentions_from(payload):
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        rows = None
        for key in ("mentions", "entities", "items"):
            if isinstance(payload.get(key), list):
                rows = payload[key]
                break
        if rows is None and "quote" in payload:
            rows = [payload]
        rows = rows or []
    else:
        rows = []
    mentions = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        mentions.append(
            {
                "type": row.get("type", ""),
                "surface": row.get("surface") or row.get("name") or "",
                "quote": row.get("quote") or row.get("evidence") or "",
                "role_hint": row.get("role_hint") or row.get("role") or "",
                "concept_type": row.get("concept_type") or row.get("label") or "",
                "kind": row.get("kind") or "",
                "suggested_contact_id": row.get("suggested_contact_id") or "",
            }
        )
    return mentions
