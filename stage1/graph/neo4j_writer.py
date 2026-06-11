from neo4j import GraphDatabase
from typing import List

from models.schema import ExtractedEntity, ExtractedRelationship


class Neo4jWriter:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    # -------------------------
    # Public API
    # -------------------------

    def write_extraction(
        self,
        entities: List[ExtractedEntity],
        relationships: List[ExtractedRelationship]
    ):
        with self.driver.session() as session:
            session.execute_write(
                self._write_entities_and_relationships,
                entities,
                relationships
            )

    # -------------------------
    # Internal transaction
    # -------------------------

    @staticmethod
    def _write_entities_and_relationships(tx, entities, relationships):
        # Write entities
        for entity in entities:
            tx.run(
                """
                MERGE (e:Entity {id: $id})
                SET
                    e.name = $name,
                    e.type = $type,
                    e.subtype = $subtype,
                    e.confidence = $confidence
                """,
                id=entity.id,
                name=entity.name,
                type=entity.type,
                subtype=entity.subtype,
                confidence=entity.confidence
            )

        # Write relationships
        for rel in relationships:
            tx.run(
                f"""
                MATCH (s:Entity {{id: $source_id}})
                MATCH (t:Entity {{id: $target_id}})
                MERGE (s)-[r:{rel.type}]->(t)
                SET
                    r.confidence = $confidence,
                    r.source_chunk_id = $source_chunk_id
                """,
                source_id=rel.source_id,
                target_id=rel.target_id,
                confidence=rel.confidence,
                source_chunk_id=rel.source_chunk_id
            )

