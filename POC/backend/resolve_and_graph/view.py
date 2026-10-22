"""What the screen is allowed to see.

Past finished sales are hidden as records. Only their count is returned,
so one sale's page does not list every other buyer's history.
"""


def view(graph):
    """Split the graph into live records and a past-sale count.

    A record is hidden when history is true: the past sales, their company,
    and the rollup row. Links are shown only when both ends are live, so a
    past sale's links do not appear either.
    """
    snap = graph.snapshot()
    live_nodes = [node for node in snap["nodes"] if not node.get("history")]
    live_ids = {node["id"] for node in live_nodes}
    live_edges = [
        edge
        for edge in snap["edges"]
        if edge["source"] in live_ids and edge["target"] in live_ids
    ]
    return {
        "nodes": live_nodes,
        "edges": live_edges,
        "history_records": sum(1 for node in snap["nodes"] if node.get("history")),
    }
