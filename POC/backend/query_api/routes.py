"""HTTP entry for reading the graph.

The screen never opens the graph itself. The brief is fixed questions.
The ask route sends those facts to Ollama and then checks the citations.
Pydantic checks the question body.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.llm.client import ModelError
from backend.query_api.brief import build_brief
from backend.query_api.question import ask
from backend import state

router = APIRouter(prefix="/api/query", tags=["query"])


class QuestionIn(BaseModel):
    """Body of POST /api/query/ask."""

    # Graph id of the sale, such as "opportunity:deal-1".
    opportunity_id: str
    # The words the user typed, such as "Why is this stuck?"
    question: str = Field(min_length=1)


@router.get("/brief")
def brief(opportunity_id: str):
    """Three fixed questions about one sale. No model."""
    return build_brief(state.graph, opportunity_id)


@router.post("/ask")
def question(body: QuestionIn):
    """Phrase an answer from the brief, then drop sentences with bad citations."""
    try:
        return ask(state.graph, body.opportunity_id, body.question.strip())
    except ModelError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
