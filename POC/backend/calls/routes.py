"""HTTP entry for a finished call.

Pydantic checks that the body has a call_id string before any work starts.
The pipeline then stores the text, asks Ollama, checks quotes, matches names,
and writes the graph.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.calls.pipeline import available_calls, process_call
from backend.resolve_and_graph.view import view
from backend.llm.client import ModelError
from backend import state

router = APIRouter(prefix="/api/calls", tags=["calls"])


class CallIn(BaseModel):
    """Body of POST /api/calls/process. One field: which sample call to run."""

    # "acme" or "sam". Extra fields in the JSON are ignored by default.
    call_id: str = Field(description="Which sample call to process, acme or sam.")


@router.get("")
def list_calls():
    """Show the sample calls and the jobs that have already run."""
    return {"calls": available_calls(), "jobs": state.queue.snapshot()}


@router.post("/process")
def process(body: CallIn):
    """Run one call through store, queue, extract, validate, resolve, and write."""
    try:
        result = process_call(state.graph, state.store, state.queue, state.memory, body.call_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown call.") from None
    except RuntimeError as exc:
        # Raised when the CRM has not been copied into the graph yet.
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ModelError as exc:
        # Ollama was down, or it did not return JSON we can read.
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    result["graph"] = view(state.graph)
    return result
