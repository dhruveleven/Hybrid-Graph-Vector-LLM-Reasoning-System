from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import numpy as np


# -----------------------------
# Config
# -----------------------------

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "local_db_one"  # change this

TOP_K = 5


# -----------------------------
# Load Embedding Model
# -----------------------------

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


# -----------------------------
# Semantic Retriever
# -----------------------------

class SemanticEntityRetriever:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def embed_query(self, query: str) -> list:
        embedding = model.encode(query)
        return embedding.astype(float).tolist()

    def retrieve(self, query: str, top_k: int = TOP_K):
        query_embedding = self.embed_query(query)

        cypher = """
        CALL db.index.vector.queryNodes(
            'entity_embedding_index',
            $top_k,
            $embedding
        )
        YIELD node, score
        RETURN
            node.id AS id,
            node.name AS name,
            node.type AS type,
            node.subtype AS subtype,
            score
        ORDER BY score DESC
        """

        with self.driver.session() as session:
            result = session.run(
                cypher,
                top_k=top_k,
                embedding=query_embedding
            )
            return [record.data() for record in result]
