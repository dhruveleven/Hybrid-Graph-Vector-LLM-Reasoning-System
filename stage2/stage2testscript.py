from semantic_retriever import SemanticEntityRetriever

retriever = SemanticEntityRetriever(
    "neo4j://127.0.0.1:7687",
    "neo4j",
    "local_db_one"
)

questions = [
    "What factors contribute to financial success?",
    "Why are people skills more important than technical knowledge?",
    "What did the Carnegie Foundation discover?",
    "Why are the highest-paid engineers not the most technical?",
    "What did John D. Rockefeller say about dealing with people?"
]

for q in questions:
    print(f"\nQUESTION: {q}")
    results = retriever.retrieve(q)
    for r in results:
        print(r)

retriever.close()
