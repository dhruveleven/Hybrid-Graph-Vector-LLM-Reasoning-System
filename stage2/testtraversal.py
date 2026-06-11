from semantic_retriever import SemanticEntityRetriever
from graph_traversal import GraphTraversalEngine

retriever = SemanticEntityRetriever(
    "neo4j://127.0.0.1:7687",
    "neo4j",
    "local_db_one"
)

traverser = GraphTraversalEngine(
    "neo4j://127.0.0.1:7687",
    "neo4j",
    "local_db_one"
)

query = "Why are people skills more important than technical knowledge?"

entities = retriever.retrieve(query)
entity_ids = [e["id"] for e in entities[:3]]

context = traverser.traverse(entity_ids)

print("\nFACTS:")
for f in context["facts"]:
    print(f)

print("\nSOURCES:", context["sources"])

retriever.close()
traverser.close()
