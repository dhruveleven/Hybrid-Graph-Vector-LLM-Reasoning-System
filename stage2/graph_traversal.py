from neo4j import GraphDatabase
from typing import List, Dict


# -----------------------------
# Neo4j Config
# -----------------------------

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "local_db_one"  # change this


# -----------------------------
# Graph Traversal Engine
# -----------------------------

class GraphTraversalEngine:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def traverse(
        self,
        entity_ids: List[str],
        max_hops: int = 2,
        limit: int = 50
    ) -> Dict:
        """
        Traverse the graph starting from entity IDs
        """

        cypher = """
        MATCH (start:Entity)
        WHERE start.id IN $entity_ids

        MATCH path = (start)-[r*1..$max_hops]-(neighbor:Entity)

        UNWIND relationships(path) AS rel

        RETURN DISTINCT
            start.id AS start_id,
            start.name AS start_name,
            type(rel) AS relationship_type,
            neighbor.id AS neighbor_id,
            neighbor.name AS neighbor_name,
            neighbor.type AS neighbor_type,
            neighbor.subtype AS neighbor_subtype,
            rel.source_chunk_id AS source_chunk_id
        LIMIT $limit
        """

        with self.driver.session() as session:
            result = session.run(
                cypher,
                entity_ids=entity_ids,
                max_hops=max_hops,
                limit=limit
            )

            records = [r.data() for r in result]

        return self._structure_context(records)

    def _structure_context(self, records: List[Dict]) -> Dict:
        """
        Convert raw traversal output into structured context
        """

        context = {
            "facts": [],
            "entities": set(),
            "sources": set()
        }

        for r in records:
            context["facts"].append({
                "from": r["start_name"],
                "relationship": r["relationship_type"],
                "to": r["neighbor_name"],
                "neighbor_type": r["neighbor_type"],
                "source_chunk_id": r["source_chunk_id"]
            })

            context["entities"].add(r["start_name"])
            context["entities"].add(r["neighbor_name"])

            if r["source_chunk_id"]:
                context["sources"].add(r["source_chunk_id"])

        context["entities"] = list(context["entities"])
        context["sources"] = list(context["sources"])

        return context
