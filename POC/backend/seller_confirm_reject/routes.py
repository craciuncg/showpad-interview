"""HTTP entry for a user's confirm or reject.

Pydantic checks the body before the decision is stored. The graph is then
updated from that saved choice, without calling the model again.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.resolve_and_graph.view import view
from backend.resolve_and_graph.writer import reapply_decisions
from backend import state

router = APIRouter(prefix="/api/seller", tags=["seller"])


class DecisionIn(BaseModel):
    """Body of POST /api/seller/decisions."""

    # CRM id of the buyer company, such as "account-1". Not the graph id.
    account_id: str
    # The name as it was spoken, such as "Bob".
    surface: str
    # "confirm" or "reject".
    decision: str
    # Optional. Empty means "this person is real, but they are not in the CRM yet."
    contact_id: str = Field(default="", description="CRM contact id, if the user picked one.")


@router.get("/decisions")
def list_decisions():
    """Return every saved confirm or reject."""
    return {"decisions": state.memory.all_rows()}


@router.post("/decisions")
def save_decision(body: DecisionIn):
    """Save the choice, then update person mentions already in the graph."""
    try:
        row = state.memory.record(body.account_id, body.surface, body.decision, body.contact_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    reapply_decisions(state.graph, state.memory)
    return {"decision": row, "graph": view(state.graph)}
