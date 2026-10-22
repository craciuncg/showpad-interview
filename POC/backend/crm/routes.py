"""HTTP entry for the customer file.

The screen calls these routes. They load the mock CRM JSON and hand it to
the writer. No model runs here. Pydantic is not needed on these two routes
because they take no JSON body.
"""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from backend.resolve_and_graph.view import view
from backend.resolve_and_graph.writer import sync_crm
from backend import state

# Prefix groups these URLs under /api/crm so the folder matches the URL.
router = APIRouter(prefix="/api/crm", tags=["crm"])

# The mock customer file that stands in for a real CRM export.
DATA = Path(__file__).resolve().parent / "data" / "mock_crm.json"


def load_mock():
    """Read the customer file from disk into a plain dictionary."""
    return json.loads(DATA.read_text(encoding="utf-8"))


@router.get("")
def show_crm():
    """Return the raw customer file, before it is copied into the graph."""
    return load_mock()


@router.post("/sync")
def run_sync():
    """Copy the customer file into the graph. Safe to run more than once."""
    try:
        summary = sync_crm(state.graph, load_mock())
    except Exception as exc:
        # A bad file should not crash the process. The screen shows this text.
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"summary": summary, "graph": view(state.graph)}
