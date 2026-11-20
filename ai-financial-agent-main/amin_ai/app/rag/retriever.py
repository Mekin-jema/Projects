"""Retriever for querying indexed documents."""

from pathlib import Path
from langchain_community.vectorstores import FAISS
from app.config import embeddings


DB_PATH = Path("data/faiss_db")


def get_retriever():
    """
    Load the FAISS vector store and return a retriever.
    
    Returns:
        A retriever configured for similarity search with k=4.
    """
    vector_store = FAISS.load_local(
        folder_path=str(DB_PATH),
        embeddings=embeddings,
        allow_dangerous_deserialization=True
    )
    
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    return retriever
