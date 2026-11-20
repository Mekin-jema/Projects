Absolutely. Since you're already using **OpenSearch for your agentic RAG / research assistant**, I’ll teach it from the fundamentals up to the exact concepts you need for **BM25 + vector search + hybrid search + RRF**.

# OpenSearch Tutorial — From Zero to RAG

## 1. What is OpenSearch?

OpenSearch is an open-source search and analytics engine based on Elasticsearch's original architecture.

At a high level:

```text
Your Application
      │
      ▼
   OpenSearch
      │
 ┌────┴─────────┐
 │              │
Keyword       Vector
Search        Search
(BM25)        (k-NN)
 │              │
 └──────┬───────┘
        ▼
   Search Results
```

For your **Research Agent**, OpenSearch can store:

* Paper metadata
* Paper titles
* Authors
* Abstracts
* Full-text chunks
* Embeddings
* arXiv IDs
* Publication dates
* Categories

and then retrieve the most relevant chunks when the user asks a question.

---

# 2. The Core Concepts

Before writing code, understand these 6 concepts:

| Concept  | Meaning                                |
| -------- | -------------------------------------- |
| Cluster  | Collection of OpenSearch nodes         |
| Node     | One OpenSearch server                  |
| Index    | Similar to a database/table collection |
| Document | One JSON record                        |
| Field    | Property inside a document             |
| Query    | Request to search/filter documents     |

For example, imagine:

```json
{
  "arxiv_id": "2610.00838",
  "title": "Agentic RAG Systems",
  "authors": ["John Doe"],
  "abstract": "This paper studies retrieval augmented generation...",
  "year": 2026
}
```

This entire JSON object is a **document**.

`title`, `authors`, `abstract`, and `year` are **fields**.

The documents might be stored inside:

```text
arxiv-papers
```

which is an **index**.

---

# 3. OpenSearch vs PostgreSQL

Since you're also using PostgreSQL, this comparison is important.

### PostgreSQL

```text
Database
   │
   └── Table
        │
        └── Row
             │
             └── Column
```

### OpenSearch

```text
Cluster
   │
   └── Index
        │
        └── Document
             │
             └── Field
```

Conceptually:

```text
PostgreSQL              OpenSearch

Database       ≈        Cluster
Table          ≈        Index
Row            ≈        Document
Column         ≈        Field
SQL            ≈        Query DSL
```

But don't treat them as identical.

PostgreSQL is primarily a **relational database**.

OpenSearch is primarily a **search and analytics engine**.

---

# 4. Running OpenSearch

You already have:

```text
http://opensearch:9200
```

inside your Docker environment.

From your host, you may have something like:

```text
http://localhost:9200
```

depending on your Docker Compose configuration.

Check whether OpenSearch is running:

```bash
curl http://localhost:9200
```

You should get JSON containing information such as:

```json
{
  "name": "opensearch-node",
  "cluster_name": "opensearch-cluster",
  "version": {
    "number": "2.x.x"
  }
}
```

---

# 5. Creating Your First Index

Let's create an index called:

```text
papers
```

```bash
curl -X PUT "http://localhost:9200/papers" \
  -H "Content-Type: application/json"
```

Then:

```bash
curl "http://localhost:9200/_cat/indices?v"
```

You should see your index.

---

# 6. Mapping

This is one of the **most important OpenSearch concepts**.

A mapping tells OpenSearch what type each field contains.

For example:

```json
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text"
      },
      "abstract": {
        "type": "text"
      },
      "authors": {
        "type": "keyword"
      },
      "year": {
        "type": "integer"
      }
    }
  }
}
```

Create it:

```bash
curl -X PUT "http://localhost:9200/papers" \
  -H "Content-Type: application/json" \
  -d '{
    "mappings": {
      "properties": {
        "title": {
          "type": "text"
        },
        "abstract": {
          "type": "text"
        },
        "authors": {
          "type": "keyword"
        },
        "year": {
          "type": "integer"
        }
      }
    }
  }'
```

---

# 7. `text` vs `keyword`

This causes a lot of confusion.

## `text`

Used for natural language.

Example:

```json
"title": {
    "type": "text"
}
```

This allows OpenSearch to analyze:

```text
Agentic Retrieval Augmented Generation
```

into searchable terms.

Useful for:

* titles
* abstracts
* body text
* paper chunks

---

## `keyword`

Used for exact values.

Example:

```json
"arxiv_id": {
    "type": "keyword"
}
```

You want:

```text
2610.00838v1
```

to remain exactly:

```text
2610.00838v1
```

instead of being analyzed.

Good candidates:

```text
arxiv_id
paper_id
category
author_id
status
```

---

# 8. Adding a Document

Now insert a paper:

```bash
curl -X POST "http://localhost:9200/papers/_doc" \
  -H "Content-Type: application/json" \
  -d '{
    "arxiv_id": "2610.00838v1",
    "title": "Agentic Retrieval Augmented Generation",
    "abstract": "This paper investigates agentic retrieval augmented generation systems.",
    "authors": ["John Doe"],
    "year": 2026
  }'
```

OpenSearch generates an ID automatically.

---

# 9. Using Your Own ID

You can specify the document ID.

```bash
curl -X PUT \
"http://localhost:9200/papers/_doc/2610.00838v1" \
-H "Content-Type: application/json" \
-d '{
  "arxiv_id": "2610.00838v1",
  "title": "Agentic Retrieval Augmented Generation",
  "abstract": "This paper investigates agentic retrieval augmented generation systems.",
  "year": 2026
}'
```

Now:

```text
papers
   │
   └── 2610.00838v1
```

is the document.

---

# 10. Retrieve a Document

```bash
curl \
"http://localhost:9200/papers/_doc/2610.00838v1"
```

You will get something similar to:

```json
{
  "_index": "papers",
  "_id": "2610.00838v1",
  "_source": {
    "arxiv_id": "2610.00838v1",
    "title": "Agentic Retrieval Augmented Generation",
    "abstract": "...",
    "year": 2026
  }
}
```

`_source` contains your original document.

---

# 11. Search Everything

The simplest query:

```bash
curl -X GET "http://localhost:9200/papers/_search" \
-H "Content-Type: application/json" \
-d '{
  "query": {
    "match_all": {}
  }
}'
```

This means:

> Give me all documents.

---

# 12. Match Search

Suppose the user searches:

```text
agentic RAG
```

You can use:

```json
{
  "query": {
    "match": {
      "abstract": "agentic RAG"
    }
  }
}
```

OpenSearch analyzes the query and finds documents related to those terms.

---

# 13. BM25

This is extremely important for your project.

OpenSearch's traditional text search uses **BM25** scoring.

Suppose you have:

```text
Document A:
Agentic RAG improves retrieval.

Document B:
Machine learning is used for image classification.

Document C:
Agentic retrieval systems use RAG.
```

Search:

```text
agentic retrieval
```

OpenSearch calculates a relevance score for each document.

Conceptually:

```text
Query
 │
 ▼
BM25
 │
 ├── Document A → score 4.2
 ├── Document C → score 3.8
 └── Document B → score 0.1
```

The exact score isn't something you should interpret as a probability.

It is a **relative relevance score**.

---

# 14. Why BM25 Isn't Enough for RAG

Consider:

```text
Query:
How can AI agents find useful information?
```

Document:

```text
Autonomous systems retrieve relevant knowledge
from external information sources.
```

There may be very little exact word overlap.

Yet the meaning is similar.

BM25 mainly works with lexical/token matching.

This is where **vector search** becomes useful.

---

# 15. Embeddings

An embedding converts text into a vector.

For example:

```text
"AI agent retrieves documents"
```

might become:

```text
[
  0.021,
  -0.183,
  0.442,
  ...
]
```

Maybe 768 or 1024 dimensions depending on the embedding model.

Conceptually:

```text
Text
 │
 ▼
Embedding Model
 │
 ▼
[0.12, -0.43, 0.88, ...]
```

Semantically similar texts should have vectors that are close together.

---

# 16. Vector Search

Suppose:

```text
Query embedding

[0.12, 0.44, 0.81, ...]
```

and your documents have:

```text
Document A → [0.11, 0.43, 0.79, ...]
Document B → [0.91, 0.02, 0.12, ...]
Document C → [0.13, 0.42, 0.82, ...]
```

A and C are close to the query.

Therefore:

```text
Query
  │
  ▼
Embedding
  │
  ▼
Vector similarity
  │
  ├── A
  └── C
```

---

# 17. k-NN

OpenSearch provides vector search through its k-NN capabilities.

A simplified mapping looks like:

```json
{
  "mappings": {
    "properties": {
      "embedding": {
        "type": "knn_vector",
        "dimension": 768
      }
    }
  }
}
```

The `dimension` must match your embedding model.

For example:

```text
Embedding model
       │
       ▼
768 dimensions
       │
       ▼
OpenSearch
       │
       ▼
knn_vector dimension = 768
```

If the model produces 1024 dimensions, your mapping must use:

```json
"dimension": 1024
```

---

# 18. Your RAG Architecture

Your current research-agent architecture is roughly:

```text
                    User
                     │
                     ▼
               Research Agent
                     │
                     ▼
              Retrieval Layer
                     │
          ┌──────────┴──────────┐
          │                     │
       BM25                  Vector
          │                     │
          ▼                     ▼
      OpenSearch            OpenSearch
          │                     │
          └──────────┬──────────┘
                     ▼
                   RRF
                     │
                     ▼
              Top Documents
                     │
                     ▼
                   LLM
                     │
                     ▼
                Grounded Answer
```

This is where OpenSearch becomes particularly powerful.

---

# 19. Hybrid Search

You currently have:

```text
BM25
+
HNSW cosine similarity
+
RRF
```

This is a very common modern RAG architecture.

Why?

Because the two retrieval methods solve different problems.

### BM25

Good at:

```text
Exact terminology
Names
IDs
Technical terms
Rare keywords
```

### Vector search

Good at:

```text
Semantic similarity
Paraphrases
Conceptual similarity
Natural-language questions
```

Combining them gives you two retrieval signals.

---

# 20. HNSW

You mentioned HNSW in your project.

HNSW means:

**Hierarchical Navigable Small World**

You don't need to memorize the mathematical details initially.

Think of it as a graph structure that helps OpenSearch efficiently search a huge vector space.

Instead of:

```text
Query
 │
 ├── Compare against vector 1
 ├── Compare against vector 2
 ├── Compare against vector 3
 ├── ...
 └── Compare against vector 1,000,000
```

HNSW creates a graph:

```text
                 Layer 2
              A -------- D
               \        /
                \      /
                 \    /
                  B--C
                 /    \
                /      \
               E        F

                 Layer 1
          many more vectors
```

Search navigates the graph toward nearby vectors.

---

# 21. Cosine Similarity

For semantic search, you are using cosine similarity.

Conceptually:

```text
A · B
──────
|A||B|
```

Values closer to:

```text
1
```

mean vectors point in similar directions.

Example:

```text
Query ↔ Document A
similarity = 0.91

Query ↔ Document B
similarity = 0.22
```

Document A is semantically closer.

---

# 22. RRF

This is another important component of your architecture.

Suppose BM25 returns:

```text
1. Paper A
2. Paper C
3. Paper B
4. Paper D
```

Vector search returns:

```text
1. Paper C
2. Paper A
3. Paper E
4. Paper B
```

Each method has a ranking.

RRF combines those rankings.

Conceptually:

```text
BM25 ranking
      +
Vector ranking
      │
      ▼
     RRF
      │
      ▼
Combined ranking
```

The important idea is:

> RRF combines rankings rather than requiring BM25 and vector scores to be directly comparable.

That's particularly useful because BM25 scores and vector similarity scores have different meanings and scales.

---

# 23. Your Paper Chunk Structure

For your research-agent system, I would think of an OpenSearch document as something like:

```json
{
  "paper_id": "2610.00838v1",
  "arxiv_id": "2610.00838v1",
  "title": "Agentic RAG Systems",
  "authors": [
    "Author A",
    "Author B"
  ],
  "category": "cs.AI",
  "published": "2026-10-01",
  "chunk_id": 17,
  "chunk_text": "The retrieval system...",
  "embedding": [
    0.021,
    -0.123,
    0.441
  ]
}
```

Notice that you aren't necessarily storing one OpenSearch document per paper.

You can store:

```text
Paper
 │
 ├── Chunk 1
 ├── Chunk 2
 ├── Chunk 3
 ├── ...
 └── Chunk N
```

This is usually much better for RAG.

---

# 24. Why Chunk-Level Search?

Imagine a 30-page research paper.

User asks:

> How does the paper perform reranking?

You don't want to retrieve the entire 30-page PDF.

Instead:

```text
Paper
│
├── Chunk 1
├── Chunk 2
├── Chunk 3
├── ...
├── Chunk 42  ← reranking information
└── Chunk 43
```

OpenSearch retrieves:

```text
Chunk 42
```

Then your LLM gets the relevant context.

---

# 25. Filtering

OpenSearch can also filter results.

Suppose you want only:

```text
cs.AI
```

papers.

You can combine:

```text
semantic search
+
filter
```

For example:

```json
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "chunk_text": "agentic retrieval"
          }
        }
      ],
      "filter": [
        {
          "term": {
            "category": "cs.AI"
          }
        }
      ]
    }
  }
}
```

This means:

> Find documents matching the query, but only inside the `cs.AI` category.

---

# 26. Date Filtering

You can also filter papers:

```json
{
  "range": {
    "published": {
      "gte": "2026-01-01",
      "lte": "2026-10-01"
    }
  }
}
```

Very useful for your historical arXiv ingestion.

---

# 27. Aggregations

OpenSearch isn't only for search.

It can also perform analytics.

For example:

```text
How many papers do I have per category?
```

You could aggregate:

```text
cs.AI       523
cs.LG       812
cs.CL       341
cs.CV       721
```

This makes OpenSearch useful for dashboards and analytics as well.

---

# 28. Python Client

Instead of using `curl`, your application can use Python.

For example:

```python
from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=[{"host": "opensearch", "port": 9200}]
)
```

Then:

```python
response = client.search(
    index="papers",
    body={
        "query": {
            "match": {
                "chunk_text": "agentic RAG"
            }
        }
    }
)
```

Get the results:

```python
for hit in response["hits"]["hits"]:
    print(hit["_source"])
```

---

# 29. Indexing Your Chunks

Your ingestion pipeline might look like:

```python
document = {
    "paper_id": paper_id,
    "arxiv_id": arxiv_id,
    "title": title,
    "chunk_id": chunk_id,
    "chunk_text": chunk_text,
    "embedding": embedding,
}
```

Then:

```python
client.index(
    index="arxiv-papers-chunks",
    body=document
)
```

For large ingestion pipelines, you should eventually use the **Bulk API** rather than sending one request per chunk.

Conceptually:

```text
100 papers
   │
   ▼
10,000 chunks
   │
   ▼
Bulk API
   │
   ▼
OpenSearch
```

rather than:

```text
chunk 1 → request
chunk 2 → request
chunk 3 → request
...
```

---

# 30. Your Complete Pipeline

For your project, the architecture can be understood as:

```text
                 arXiv
                   │
                   ▼
             Fetch papers
                   │
                   ▼
                PDFs
                   │
                   ▼
                Docling
                   │
                   ▼
               Full text
                   │
                   ▼
              Chunking
                   │
                   ▼
             Embeddings
                   │
                   ▼
              OpenSearch
                   │
       ┌───────────┴────────────┐
       │                        │
      BM25                    HNSW
       │                        │
       └──────────┬─────────────┘
                  │
                 RRF
                  │
                  ▼
             Top-K chunks
                  │
                  ▼
             LangGraph
                  │
                  ▼
                 LLM
                  │
                  ▼
             Final answer
```

That is the important mental model.

---

# 31. What You Should Learn Next

Since you're building a production-style RAG system, I would learn OpenSearch in this order:

### Level 1 — Fundamentals

Learn:

```text
Cluster
Node
Index
Document
Field
Mapping
CRUD
```

### Level 2 — Search

Then:

```text
match
term
bool
must
should
filter
range
multi_match
```

### Level 3 — Relevance

Then:

```text
BM25
TF-IDF
scoring
boosting
analyzers
tokenizers
```

### Level 4 — Vector Search

Then:

```text
embeddings
knn_vector
k-NN
cosine similarity
HNSW
ANN
```

### Level 5 — Hybrid RAG

Then:

```text
BM25
+
Vector Search
+
RRF
```

### Level 6 — Production

Finally:

```text
Bulk indexing
Index lifecycle
Shards
Replicas
Refresh
Caching
Monitoring
Snapshots
Security
Performance tuning
```

---

## The most important concepts for your project

If your goal is specifically to understand the OpenSearch implementation in your **Research Agent**, focus heavily on these:

```text
1. Mapping
       ↓
2. Text / Keyword fields
       ↓
3. BM25
       ↓
4. Embeddings
       ↓
5. knn_vector
       ↓
6. HNSW
       ↓
7. Cosine similarity
       ↓
8. Hybrid search
       ↓
9. RRF
       ↓
10. Retrieval evaluation
```

Once you understand those ten, you'll be able to explain **why OpenSearch is in your architecture**, not just how to operate it.

If you want to go deeper, the next useful lesson is a **hands-on OpenSearch lab**: create `arxiv-papers-chunks` from scratch, insert 5 sample papers, run BM25, create embeddings, run HNSW vector search, and finally combine both with RRF—essentially rebuilding the retrieval part of your Research Agent step by step.
