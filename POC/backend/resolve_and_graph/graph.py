"""The graph: records and the links between them.

This is ordinary Python. A dictionary holds records. A list holds links.
Nothing here talks to a database or to the model.
"""

from backend.shared.ontology import LINK_TYPES, NODE_TYPES


class Graph:
    """One in-memory graph for the demo process.

    nodes: id -> record dictionary. The id is stable, so a second CRM sync
    updates the same record instead of creating a copy.
    edges: a list of links. Each link has a type, a source id, and a target id.
    """

    def __init__(self):
        self.nodes = {}
        self.edges = []

    def clear(self):
        """Drop every record and every link. Used by Reset."""
        self.nodes = {}
        self.edges = []

    def upsert(self, node_id, node_type, **props):
        """Create a record, or update it if that id already exists.

        The type must be one of NODE_TYPES. That is how a made-up type
        from the model is refused before it can be stored.
        """
        if node_type not in NODE_TYPES:
            raise ValueError(f"Unknown record type: {node_type}")
        current = self.nodes.get(node_id, {"id": node_id, "type": node_type})
        current["type"] = node_type
        current.update(props)
        self.nodes[node_id] = current
        return current

    def link(self, link_type, from_id, to_id, **props):
        """Add a link. The same type between the same two records is replaced.

        props can hold role, status, or origin. "origin" says where the link
        came from: crm, calendar, call, or history. It is not the source id.
        """
        if link_type not in LINK_TYPES:
            raise ValueError(f"Unknown link type: {link_type}")
        self.edges = [
            edge
            for edge in self.edges
            if not (edge["type"] == link_type and edge["source"] == from_id and edge["target"] == to_id)
        ]
        edge = {"type": link_type, "source": from_id, "target": to_id, **props}
        self.edges.append(edge)
        return edge

    def remove_edges(self, predicate):
        """Delete links for which predicate(edge) is true."""
        self.edges = [edge for edge in self.edges if not predicate(edge)]

    def delete_nodes(self, node_ids):
        """Delete these records and any link that touches them."""
        node_ids = set(node_ids)
        for node_id in node_ids:
            self.nodes.pop(node_id, None)
        self.edges = [
            edge
            for edge in self.edges
            if edge["source"] not in node_ids and edge["target"] not in node_ids
        ]

    def get(self, node_id):
        """Return one record, or None if that id is not stored."""
        return self.nodes.get(node_id)

    def of_type(self, node_type):
        """Every record of one type. Example: all contacts."""
        return [node for node in self.nodes.values() if node["type"] == node_type]

    def outgoing(self, source, link_type):
        """Links of this type that start at source."""
        return [edge for edge in self.edges if edge["source"] == source and edge["type"] == link_type]

    def incoming(self, target, link_type):
        """Links of this type that end at target."""
        return [edge for edge in self.edges if edge["target"] == target and edge["type"] == link_type]

    def snapshot(self):
        """A copy of the records and links for the screen or for a view filter."""
        return {
            "nodes": list(self.nodes.values()),
            "edges": list(self.edges),
        }
