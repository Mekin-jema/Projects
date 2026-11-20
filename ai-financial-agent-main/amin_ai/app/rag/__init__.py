"""RAG (Retrieval Augmented Generation) components."""

from .document_loader import ingest_rag_document
from .retriever import get_retriever

__all__ = [
    "ingest_rag_document",
    "get_retriever",
]
