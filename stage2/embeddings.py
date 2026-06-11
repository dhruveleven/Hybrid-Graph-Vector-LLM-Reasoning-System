from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import numpy as np


# -----------------------------
# Neo4j Config
# -----------------------------

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "local_db_one"  # change this


# -----------------------------
# Load Embedding Model
# -----------------------------

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


# -----------------------------
# Neo4j Embedding Writer
# -----------------------------

class Neo4jEmbeddingWriter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def fetch_entities(self):
        query = """
        MATCH (e:Entity)
        RETURN e.id AS id, e.name AS name, e.type AS type, e.subtype AS subtype
        """
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]

    def store_embedding(self, entity_id: str, embedding: list):
        query = """
        MATCH (e:Entity {id: $id})
        SET e.embedding = $embedding
        """
        with self.driver.session() as session:
            session.run(query, id=entity_id, embedding=embedding)


# -----------------------------
# Main Embedding Pipeline
# -----------------------------

def build_embeddings():
    writer = Neo4jEmbeddingWriter(
        NEO4J_URI,
        NEO4J_USER,
        NEO4J_PASSWORD
    )

    entities = writer.fetch_entities()
    print(f"[INFO] Found {len(entities)} entities")

    for i, entity in enumerate(entities):
        text = f"{entity['name']} ({entity['type']})"
        if entity.get("subtype"):
            text += f" - {entity['subtype']}"

        embedding = model.encode(text)
        embedding = embedding.astype(float).tolist()

        writer.store_embedding(entity["id"], embedding)

        if (i + 1) % 10 == 0:
            print(f"[INFO] Embedded {i + 1}/{len(entities)} entities")

    writer.close()
    print("[INFO] Embedding generation complete.")


if __name__ == "__main__":
    build_embeddings()
