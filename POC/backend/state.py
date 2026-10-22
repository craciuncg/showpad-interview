"""The one set of objects the demo process shares.

The HTTP routes all use these. There is no database. Reset empties them.
"""

from backend.calls.queue import JobQueue
from backend.calls.store import TranscriptStore
from backend.resolve_and_graph.graph import Graph
from backend.seller_confirm_reject.memory import DecisionMemory

# Created once when the process starts.
graph = Graph()
store = TranscriptStore()
queue = JobQueue()
memory = DecisionMemory()


def reset():
    """Empty every store. The sample files on disk are not deleted."""
    graph.clear()
    store.clear()
    queue.clear()
    memory.clear()
