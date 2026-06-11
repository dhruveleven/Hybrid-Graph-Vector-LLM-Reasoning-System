# GraphRAG Knowledge Graph Reasoning System

## Overview

This project implements a graph-based Retrieval-Augmented Generation (Graph RAG) system that transforms unstructured documents into a persistent knowledge graph and uses graph-aware retrieval for explainable question answering.

Unlike traditional RAG systems that retrieve raw text chunks, this system extracts entities and relationships from documents, stores them in a Neo4j knowledge graph, performs semantic entity retrieval using vector embeddings, traverses connected graph knowledge, and generates grounded answers using retrieved graph facts.

The result is a retrieval pipeline capable of reasoning over structured knowledge rather than isolated text passages.

---

## Architecture

### Stage 1: Knowledge Graph Construction

```text
PDF / Document
        ↓
Document Loading & Chunking
        ↓
LLM-Based Entity & Relationship Extraction
        ↓
Schema Validation
        ↓
Neo4j Graph Storage
        ↓
Persistent Knowledge Graph
```

### Stage 2: Hybrid Retrieval & Reasoning

```text
User Question
        ↓
Question Embedding
        ↓
Semantic Entity Retrieval
        ↓
Graph Traversal
        ↓
Fact Aggregation & Filtering
        ↓
LLM-Based Reasoning
        ↓
Grounded Answer Generation
```

---

## Features

### Knowledge Graph Construction

* PDF document ingestion and chunking
* LLM-powered entity extraction
* Relationship extraction with controlled schema
* Structured validation using Pydantic
* Persistent graph storage in Neo4j

### Semantic Retrieval

* Entity embeddings generated using Sentence Transformers
* Semantic similarity search over graph entities
* Retrieval based on meaning rather than keyword matching

### Graph-Based Reasoning

* Multi-hop graph traversal
* Context assembly from connected entities
* Duplicate fact removal
* Relationship filtering for noise reduction

### Explainable Answer Generation

* Retrieval grounded in graph facts
* Source-aware reasoning
* Citation-supported responses
* Reduced hallucination through structured context

---

## Tech Stack

### Knowledge Graph

* Neo4j

### LLM Integration

* OpenRouter
* GPT-OSS-120B

### Embeddings

* Sentence Transformers
* all-MiniLM-L6-v2

### Backend

* Python

### Data Validation

* Pydantic

### APIs & Infrastructure

* Requests
* Neo4j Python Driver

---

## Project Structure

```text
.
├── stage1
│   ├── graph
│   │   └── neo4j_writer.py
│   ├── ingestion
│   │   ├── extractor.py
│   │   └── loader.py
│   ├── models
│   │   └── schema.py
│   ├── main.py
│   └── sample.pdf
│
├── stage2
│   ├── semantic_retriever.py
│   ├── graph_traversal.py
│   ├── answer_generator.py
│   └── full_pipeline_test.py
│
└── README.md
```

---

## How It Works

### 1. Build the Knowledge Graph

The document is split into chunks and processed by an LLM to extract:

* Entities
* Concepts
* Organizations
* Metrics
* Events
* Relationships

These are validated and stored as nodes and edges in Neo4j.

### 2. Generate Entity Embeddings

Extracted entities are converted into vector embeddings using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

These embeddings enable semantic retrieval over graph entities.

### 3. Retrieve Relevant Knowledge

When a question is asked:

* The question is embedded
* Similar entities are retrieved
* Relevant graph nodes are identified

### 4. Traverse the Graph

The system performs graph traversal around retrieved entities to collect connected facts and relationships.

### 5. Generate the Answer

The retrieved graph context is supplied to the LLM, which generates a grounded answer supported by graph evidence and source references.

---

## Example Workflow

```text
Document
    ↓
Knowledge Graph
    ↓
Question:
"Why are people skills more important than technical knowledge?"
    ↓
Entity Retrieval
    ↓
Graph Traversal
    ↓
Connected Facts
    ↓
LLM Reasoning
    ↓
Answer
```

---

## Key Outcomes

* Converts unstructured documents into structured graph memory
* Enables semantic retrieval over extracted knowledge
* Supports multi-hop reasoning through graph traversal
* Produces grounded answers using connected graph facts
* Provides explainability through source-aware context generation

---

## Author

Dhruv Patel
