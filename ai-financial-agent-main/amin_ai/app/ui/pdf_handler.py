"""PDF document upload and indexing."""

import hashlib
from pathlib import Path
import streamlit as st
from app import ingest_rag_document
from app.monitoring import get_logger


logger = get_logger("streamlit-ui")


def handle_pdf_upload(uploaded_files: list):
    """
    Process uploaded PDF files, index them, and store in session.
    
    Returns:
        bool: True if any PDF was processed, False otherwise.
    """
    pdf_processed = False
    
    for uploaded_file in uploaded_files:
        # Validate PDF type
        if uploaded_file.type != "application/pdf":
            st.warning(
                f"Skipping `{uploaded_file.name}` "
                "because it is not a PDF."
            )
            continue
        
        # Read file bytes
        file_bytes = uploaded_file.getvalue()
        
        # Calculate hash
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        
        # Avoid duplicate indexing
        if st.session_state.document_hash == file_hash:
            st.toast(
                f"`{uploaded_file.name}` "
                "is already indexed."
            )
            continue
        
        # Create upload directory
        upload_dir = Path("data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare file path
        document_name = Path(uploaded_file.name).name
        document_path = upload_dir / document_name
        
        # Write file to disk
        document_path.write_bytes(file_bytes)
        
        # Index document
        try:
            with st.status(
                f"Indexing `{document_name}`...",
                expanded=True,
            ) as status:
                ingest_rag_document(str(document_path))
                
                status.update(
                    label=(
                        f"`{document_name}` "
                        "is ready"
                    ),
                    state="complete",
                    expanded=False,
                )
            
            # Store in session
            st.session_state.document_hash = file_hash
            st.session_state.document_name = document_name
            
            pdf_processed = True
            logger.info(
                "PDF indexed successfully",
                extra={"extra_data": {"file": document_name}},
            )
        
        except ValueError as error:
            error_msg = str(error)
            if "empty" in error_msg.lower() or "no pages" in error_msg.lower():
                st.error(
                    f"**PDF Error**: The PDF appears to be empty or unreadable. "
                    f"Please ensure:\n"
                    f"- The file is a valid PDF\n"
                    f"- The PDF contains extractable text (not just scanned images)\n"
                    f"- The file is not corrupted\n\n"
                    f"**Details**: {error_msg}"
                )
            else:
                st.error(
                    f"**Could not index `{document_name}`**:\n{error_msg}"
                )
            logger.error(
                "PDF indexing failed",
                extra={"extra_data": {"file": document_name, "error": error_msg}},
            )
        
        except Exception as error:
            st.error(
                f"**Unexpected error indexing `{document_name}`**:\n"
                f"{str(error)}"
            )
            logger.error(
                "Unexpected error during PDF indexing",
                extra={"extra_data": {"file": document_name, "error": str(error)}},
                exc_info=True,
            )
    
    return pdf_processed
