"""The process that serves the screen.

FastAPI is only the HTTP layer. The graph, the quote check, and name
matching are ordinary Python. Pydantic models live in the route files and
check each JSON body. This file connects the folders and serves the page.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.calls.routes import router as calls_router
from backend.crm.routes import router as crm_router
from backend.resolve_and_graph.view import view
from backend.llm.client import status as model_status
from backend.query_api.routes import router as query_router
from backend.seller_confirm_reject.routes import router as seller_router
from backend import state

# The HTML, CSS, and JavaScript sit next to the backend folder.
FRONTEND = Path(__file__).resolve().parents[1] / "frontend"

app = FastAPI(title="Knowledge graph proof of concept")

# Each router is one box in the diagram. Order does not change behavior.
app.include_router(crm_router)
app.include_router(calls_router)
app.include_router(seller_router)
app.include_router(query_router)


@app.get("/api/health")
def health():
    """Tell the screen whether Ollama has the model, and whether the CRM is loaded."""
    crm_synced = any(node["type"] == "account" for node in state.graph.nodes.values())
    return {"model": model_status(), "crm_synced": crm_synced}


@app.get("/api/graph")
def graph():
    """Return the live records. Past sales stay as a count inside this view."""
    return view(state.graph)


@app.post("/api/reset")
def reset():
    """Empty the graph, the saved calls, the job line, and the user decisions."""
    state.reset()
    return {"ok": True}


@app.get("/")
def index():
    """Serve the single page. The page then calls only /api routes."""
    return FileResponse(FRONTEND / "index.html")


# CSS and JavaScript. Mounted after the routes so /api is not swallowed.
app.mount("/static", StaticFiles(directory=FRONTEND), name="static")
