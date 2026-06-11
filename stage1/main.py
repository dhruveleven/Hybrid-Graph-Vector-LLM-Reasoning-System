from ingestion.loader import load_and_chunk_document
from ingestion.extractor import extract_knowledge_from_chunk
from graph.neo4j_writer import Neo4jWriter


# -----------------------------
# Neo4j Configuration
# -----------------------------

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "local_db_one"


# -----------------------------
# Main Pipeline
# -----------------------------

def main():
    # 1. Load & chunk document
    chunks = load_and_chunk_document("sample.pdf")

    print(f"[INFO] Loaded {len(chunks)} chunks")

    # 2. Initialize Neo4j writer
    writer = Neo4jWriter(
        uri=NEO4J_URI,
        user=NEO4J_USER,
        password=NEO4J_PASSWORD
    )

    # 3. Process each chunk
    for i, chunk in enumerate(chunks):
        print(f"[INFO] Processing chunk {i + 1}/{len(chunks)} → {chunk['chunk_id']}")

        extraction = extract_knowledge_from_chunk(
            chunk_id=chunk["chunk_id"],
            chunk_text=chunk["text"]
        )

        if extraction is None:
            print(f"[WARN] Extraction failed for {chunk['chunk_id']}")
            continue

        # 4. Persist to Neo4j
        writer.write_extraction(
            entities=extraction.entities,
            relationships=extraction.relationships
        )

    # 5. Close DB connection
    writer.close()

    print("[INFO] Ingestion complete.")


if __name__ == "__main__":
    main()
