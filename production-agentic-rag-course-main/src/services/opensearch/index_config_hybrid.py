"""
OpenSearch index configuration for hybrid search (BM25 + Vector).

This configuration supports two search approaches:

1. BM25 / keyword search:
   - Searches text fields such as title, abstract, and chunk_text.
   - Uses OpenSearch text analyzers to tokenize and normalize text.

2. Vector / semantic search:
   - Searches embedding vectors using k-NN.
   - Uses HNSW (Hierarchical Navigable Small World) for efficient
     approximate nearest-neighbor vector search.

3. Hybrid search:
   - Combines BM25 and vector-search results.
   - Uses Reciprocal Rank Fusion (RRF) to produce the final ranking.
"""


# ============================================================
# INDEX NAME
# ============================================================

# Name of the OpenSearch index that stores paper chunks.
#
# Example:
#   OpenSearch
#       └── arxiv-papers-chunks
#               ├── chunk 1
#               ├── chunk 2
#               ├── chunk 3
#               └── ...
ARXIV_PAPERS_INDEX = "arxiv-papers-chunks"
# ARXIV_PAPERS_CHUNKS_INDEX = "arxiv-papers-chunks"
# 

 
# ============================================================
# INDEX MAPPING
# ============================================================

# Defines the complete configuration/schema of the OpenSearch index.
#
# It controls:
# - Index settings
# - Text analysis
# - Field types
# - BM25 searchable fields
# - Vector/embedding fields
# - HNSW vector-search configuration
ARXIV_PAPERS_CHUNKS_MAPPING= {

    # ========================================================
    # INDEX SETTINGS
    # ========================================================

    "settings": {

        # Number of primary shards used by the index.
        #
        # Shards divide an OpenSearch index into smaller partitions.
        #
        # 1 is simple and suitable for local development or small
        # datasets.
        "number_of_shards": 1,

        # Number of replica shards.
        #
        # 0 means there are no replica copies of the primary shard.
        #
        # This reduces resource usage and is commonly used in
        # local development.
        "number_of_replicas": 0,

        # Enable OpenSearch k-NN/vector search for this index.
        #
        # Required because the index contains a knn_vector field
        # used for semantic similarity search.
        "index.knn": True,

        # Default vector similarity space used by the index.
        #
        # "cosinesimil" means vectors are compared using
        # cosine similarity.
        #
        # Higher similarity means the vectorj are more semantically
        # similar.
        "index.knn.space_type": "cosinesimil",


        # ====================================================
        # TEXT ANALYSIS
        # ====================================================

        # Defines analyzers used for BM25/text search.
        #
        # Analyzer pipeline:
        #
        # Raw text
        #     ↓
        # Tokenization
        #     ↓
        # Lowercase
        #     ↓
        # Remove stopwords
        #     ↓
        # Stemming
        #     ↓
        # Searchable tokens
        "analysis": {

            "analyzer": {

                # ------------------------------------------------
                # STANDARD ANALYZER
                # ------------------------------------------------
                #
                # Uses OpenSearch's built-in standard analyzer.
                #
                # "_english_" tells OpenSearch to remove common
                # English stopwords such as:
                #
                #   the, a, an, is, of, to, etc.
                #
                "standard_analyzer": {
                    "type": "standard",
                    "stopwords": "_english_"
                },


                # ------------------------------------------------
                # CUSTOM TEXT ANALYZER
                # ------------------------------------------------
                #
                # Used for fields that require more text
                # normalization before BM25 search.
                #
                # Processing pipeline:
                #
                #   standard tokenizer
                #          ↓
                #      lowercase
                #          ↓
                #     stopword removal
                #          ↓
                #       stemming
                #
                "text_analyzer": {
                    "type": "custom",

                    # Break text into individual tokens/words.
                    "tokenizer": "standard",

                    # Filters applied to the generated tokens.
                    "filter": [
                        # Convert tokens to lowercase.
                        "lowercase",

                        # Remove common stopwords.
                        "stop",

                        # Apply Snowball stemming so related word
                        # forms can be matched more effectively.
                        "snowball"
                    ]
                },
            }
        },
    },


    # ============================================================
    # FIELD MAPPINGS
    # ============================================================

    # Defines the schema of documents stored in the index.
    "mappings": {

        # Prevent OpenSearch from automatically adding fields
        # that are not explicitly defined below.
        #
        # Example:
        #
        # Mapping defines:
        #   title
        #   abstract
        #   embedding
        #
        # But document contains:
        #   unknown_field
        #
        # With "strict", OpenSearch rejects the unexpected field.
        "dynamic": "strict",

        "properties": {

            # ====================================================
            # DOCUMENT IDENTIFIERS
            # ====================================================

            # Unique identifier for an individual chunk.
            #
            # keyword = exact value, no text analysis.
            #
            # Example:
            #   "2501.12345_chunk_001"
            "chunk_id": {
                "type": "keyword"
            },


            # arXiv paper identifier.
            #
            # Example:
            #   "2501.12345"
            #
            # Stored as keyword because it is an identifier,
            # not natural-language text.
            "arxiv_id": {
                "type": "keyword"
            },


            # Internal/application-level paper identifier.             #32
            # Also stored as an exact keyword value.
            "paper_id": {
                "type": "keyword"
            },


            # ====================================================
            # CHUNK INFORMATION
            # ====================================================

            # Position of the chunk inside the original paper.
            #
            # Example:
            #
            #   chunk 0
            #   chunk 1
            #   chunk 2
            #   ...
            "chunk_index": {
                "type": "integer"
            },


            # Actual textual content of the paper chunk.
            #
            # "text" makes the field searchable using BM25.
            "chunk_text": {

                "type": "text",

                # Use our custom analyzer for BM25 indexing/search.
                "analyzer": "text_analyzer",

                # Multi-field:
                #
                # chunk_text
                #     ├── text
                #     │     └── BM25/full-text search
                #     │
                #     └── keyword
                #           └── exact matching
                #
                "fields": {

                    # Exact-value version of chunk_text.
                    #
                    # Useful for exact matching, sorting, or
                    # aggregations.
                    "keyword": {
                        "type": "keyword",

                        # Do not index the keyword version if the
                        # value exceeds 256 characters.
                        #
                        # The original chunk_text field is still
                        # available as normal text.
                        "ignore_above": 256
                    }
                },
            },


            # Number of words contained in the chunk.
            #
            # Useful for chunk-size analysis and filtering.
            "chunk_word_count": {
                "type": "integer"
            },


            # Starting character position of the chunk in the
            # original paper text.
            #
            # Example:
            #
            #   start_char = 5000
            "start_char": {
                "type": "integer"
            },


            # Ending character position of the chunk in the
            # original paper text.
            #
            # Example:
            #
            #   end_char = 7200
            "end_char": {
                "type": "integer"
            },


            # ====================================================
            # VECTOR / EMBEDDING CONFIGURATION
            # ====================================================

            # Vector representation of the paper chunk.
            #
            # The embedding is generated by an embedding model
            # before the document is indexed into OpenSearch.
            #
            # Example:
            #
            #   chunk_text
            #       ↓
            #   Embedding Model
            #       ↓
            #   [0.12, -0.43, 0.87, ...]
            #
            # OpenSearch then uses this vector for semantic search.
            "embedding": {

                # OpenSearch k-NN vector field.
                "type": "knn_vector",

                # Number of dimensions in each embedding vector.
                #
                # IMPORTANT:
                # This must match the output dimension of the
                # embedding model.
                #
                # Example:
                #
                #   1024-dimensional embedding
                #
                "dimension": 1024,


                # =================================================
                # HNSW CONFIGURATION
                # =================================================

                # Configure the approximate nearest-neighbor
                # algorithm used for vector search.
                "method": {

                    # HNSW =
                    # Hierarchical Navigable Small World.
                    #
                    # HNSW creates a graph of vectors that allows
                    # OpenSearch to find similar vectors efficiently
                    # without comparing against every vector.
                    "name": "hnsw",

                    # Similarity function used to compare vectors.
                    #
                    # cosine similarity measures how similar the
                    # direction of two vectors is.
                    "space_type": "cosinesimil",

                    # Vector search engine implementation.
                    "engine": "nmslib",

                    # HNSW algorithm parameters.
                    "parameters": {

                        # Controls how much work is performed when
                        # constructing the HNSW graph.
                        #
                        # Higher value:
                        #   + potentially better recall
                        #   - slower indexing
                        #   - more resources during construction
                        "ef_construction": 512,


                        # Number of graph connections maintained
                        # for each vector/node.
                        #
                        # Higher value can improve search quality,
                        # but increases memory/storage requirements.
                        "m": 16,
                    },
                },
            },


            # ====================================================
            # PAPER TITLE
            # ====================================================

            # Paper title.
            #
            # "text" enables BM25/full-text search.
            "title": {
                "type": "text",

                # Use custom text analysis.
                "analyzer": "text_analyzer",

                # Also create an exact keyword representation.
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                },
            },


            # ====================================================
            # AUTHORS
            # ====================================================

            # Paper authors.
            #
            # Text version supports text search.
            "authors": {
                "type": "text",

                # Use the standard analyzer for author names.
                "analyzer": "standard_analyzer",

                # Keyword version supports exact matching.
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                },
            },


            # ====================================================
            # ABSTRACT
            # ====================================================

            # Paper abstract.
            #
            # Full-text searchable using BM25.
            "abstract": {
                "type": "text",
                "analyzer": "text_analyzer"
            },


            # ====================================================
            # PAPER CATEGORIES
            # ====================================================

            # arXiv categories such as:
            #
            #   cs.AI
            #   cs.LG
            #   cs.IR
            #
            # Keyword is appropriate because categories are
            # structured/exact values.
            "categories": {
                "type": "keyword"
            },


            # ====================================================
            # DATES
            # ====================================================

            # Date when the paper was published.
            #
            # Enables date filtering and range queries.
            "published_date": {
                "type": "date"
            },


            # Section containing the chunk.
            #
            # Examples:
            #
            #   Introduction
            #   Methods
            #   Results
            #   Conclusion
            #
            # Stored as keyword because this is a structured value.
            "section_title": {
                "type": "keyword"
            },


            # Name/version of the model that generated the embedding.
            #
            # Example:
            #
            #   jina-embeddings-v3
            #
            # Useful when multiple embedding models are used.
            "embedding_model": {
                "type": "keyword"
            },


            # Timestamp when the document/chunk was created.
            "created_at": {
                "type": "date"
            },


            # Timestamp when the document/chunk was last updated.
            "updated_at": {
                "type": "date"
            },
        },
    },
}


# ================================================================
# HYBRID SEARCH RRF PIPELINE
# ================================================================

# Defines how OpenSearch combines results from different
# retrieval methods.
#
# The hybrid search process is approximately:
#
#     User Query
#         │
#         ├───────────────┐
#         ▼               ▼
#       BM25          Vector Search
#         │               │
#         ▼               ▼
#     BM25 ranking    Vector ranking
#         │               │
#         └───────┬───────┘
#                 ▼
#                RRF
#                 │
#                 ▼
#          Final ranking
HYBRID_RRF_PIPELINE = {

    # Unique identifier for this search pipeline.
    "id": "hybrid-rrf-pipeline",

    # Human-readable description.
    "description": "Post processor for hybrid RRF search",

    # Processors that modify/combine search results after the
    # individual search phases have produced their results.
    "phase_results_processors": [

        {
            # Processor responsible for combining rankings.
            "score-ranker-processor": {

                "combination": {

                    # RRF = Reciprocal Rank Fusion.
                    #
                    # Instead of directly comparing BM25 scores
                    # and vector scores, RRF uses their ranking
                    # positions.
                    "technique": "rrf",

                    # RRF rank constant.
                    #
                    # Basic formula:
                    #
                    #     1 / (rank_constant + rank)
                    #
                    # A value of 60 is commonly used as the
                    # RRF rank constant.
                    "rank_constant": 60,
                }
            }
        }
    ],
}


# ================================================================
# ALTERNATIVE HYBRID SEARCH PIPELINE
# ================================================================

# This is an alternative approach to combining BM25 and vector
# scores.
#
# It is NOT the default pipeline above.
#
# Instead of RRF, it:
#
#     BM25 score
#          +
#     Vector score
#          ↓
#     L2 normalization
#          ↓
#     Weighted harmonic mean
#          ↓
#     Final score
#
# The configuration below gives:
#
#     BM25   = 30%
#     Vector = 70%
#
# It is commented out because HYBRID_RRF_PIPELINE is being used
# by default.
#
# Note:
# Score normalization/combination behavior can depend on the
# OpenSearch version and search-pipeline configuration, so this
# should be tested against the exact OpenSearch version being used.


# HYBRID_SEARCH_PIPELINE = {
#
#     # Unique pipeline identifier.
#     "id": "hybrid-ranking-pipeline",
#
#     # Description of the pipeline.
#     "description": (
#         "Hybrid search pipeline using weighted average "
#         "for BM25 and vector similarity"
#     ),
#
#     # Process search results after the retrieval phases.
#     "phase_results_processors": [
#
#         {
#             # Normalizes the scores before combining them.
#             "normalization-processor": {
#
#                 "normalization": {
#
#                     # L2 normalization helps put scores into a
#                     # more comparable distribution.
#                     "technique": "l2"
#                 },
#
#                 "combination": {
#
#                     # Combine the normalized scores using a
#                     # harmonic mean.
#                     "technique": "harmonic_mean",
#
#                     "parameters": {
#
#                         # Relative contribution of each search
#                         # method:
#                         #
#                         # 30% BM25
#                         # 70% vector search
#                         #
#                         "weights": [0.3, 0.7]
#                     }
#                 }
#             }
#         }
#     ]
# }