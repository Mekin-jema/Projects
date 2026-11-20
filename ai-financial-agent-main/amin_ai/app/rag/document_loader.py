"""Document loading and ingestion for RAG."""

from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from app.config import embeddings
from app.monitoring import get_logger


DB_PATH = Path("data/faiss_db")
logger = get_logger()


def ingest_rag_document(file_path: str) -> None:
    """
    Load a PDF document, split it into chunks, and index it using FAISS.
    
    Args:
        file_path: Path to the PDF file to ingest.
        
    Raises:
        ValueError: If the PDF is invalid or contains no extractable text.
        Exception: For other processing errors.
    """
    # Ensure the database directory exists
    DB_PATH.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Starting document ingestion: {file_path}")
    
    try:
        # Load the PDF
        logger.info("Step 1: Loading PDF with PyPDFLoader...")
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        logger.info(f"Step 1 ✓: Loaded {len(docs)} pages from PDF")
        
        # Validate that documents were loaded
        if not docs:
            raise ValueError("PDF is empty or unreadable. No pages extracted.")
        
        # Check if documents have content
        total_chars = sum(len(doc.page_content.strip()) for doc in docs)
        logger.info(f"Total characters extracted: {total_chars}")
        if total_chars == 0:
            raise ValueError("PDF contains no extractable text. The file may be scanned images or corrupted.")
        
        # Split documents into chunks
        logger.info("Step 2: Splitting documents into chunks...")
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)
        logger.info(f"Step 2 ✓: Created {len(chunks)} chunks from document")
        
        # Validate chunks
        if not chunks:
            raise ValueError("No text could be extracted from the PDF. The file may be scanned or corrupted.")
        
        # Validate chunk content
        empty_chunks = sum(1 for chunk in chunks if not chunk.page_content.strip())
        logger.info(f"Empty chunks: {empty_chunks}/{len(chunks)}")
        if empty_chunks == len(chunks):
            raise ValueError("All chunks are empty. PDF contains no usable text content.")
        
        # Create and save the vector store
        logger.info("Step 3: Creating embeddings and indexing with FAISS...")
        try:
            vector_store = FAISS.from_documents(chunks, embeddings)
            logger.info("Step 3 ✓: FAISS vector store created successfully")
        except IndexError as ie:
            logger.error(f"IndexError during FAISS indexing (likely embedding issue): {str(ie)}", exc_info=True)
            raise ValueError(f"Failed to create embeddings for PDF chunks. This may indicate an API issue or incompatible content: {str(ie)}")
        
        logger.info("Step 4: Saving vector store to disk...")
        vector_store.save_local(str(DB_PATH))
        logger.info(f"Step 4 ✓: Successfully indexed {len(chunks)} chunks into FAISS")
        
    except ValueError as e:
        logger.error(f"Validation error during document ingestion: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during document ingestion: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to process PDF: {str(e)}")
