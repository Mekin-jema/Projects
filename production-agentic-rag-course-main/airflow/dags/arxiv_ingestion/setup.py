import logging

from sqlalchemy import text

from .common import get_cached_services

logger = logging.getLogger(__name__)


def setup_environment():
    """Setup environment and verify all required dependencies.

    Verifies the database and OpenSearch connections, then ensures
    the hybrid search index and RRF pipeline are available.
    """
    logger.info("Setting up environment for arXiv paper ingestion")

    try:
        # Get cached service instances.
        # Services are created only when the cache is empty.
        (
            arxiv_client,
            _pdf_parser,
            database,
            _metadata_fetcher,
            opensearch_client,
        ) = get_cached_services()

        # ------------------------------------------------------------------
        # Verify database connection
        # ------------------------------------------------------------------
        with database.get_session() as session:
            session.execute(text("SELECT 1"))
            logger.info("Database connection verified")

        # ------------------------------------------------------------------
        # Verify OpenSearch connection
        # ------------------------------------------------------------------
        try:
            health = opensearch_client.client.cluster.health()
            status = health["status"]

            if status in ["green", "yellow", "red"]:
                logger.info(
                    f"OpenSearch client connected "
                    f"(cluster status: {status})"
                )
            else:
                raise Exception(
                    f"OpenSearch cluster unhealthy: {status}"
                )

        except Exception as e:
            raise Exception(
                f"OpenSearch client connection failed: {e}"
            )

        # ------------------------------------------------------------------
        # Setup OpenSearch hybrid search resources
        # ------------------------------------------------------------------
        setup_results = opensearch_client.setup_indices(force=False)

        if setup_results.get("hybrid_index"):
            logger.info(
                "Hybrid search index created with vector support"
            )
        else:
            logger.info(
                "Hybrid search index already exists"
            )

        if setup_results.get("rrf_pipeline"):
            logger.info(
                "RRF pipeline created successfully"
            )
        else:
            logger.info(
                "RRF pipeline already exists"
            )

        logger.info("Hybrid search setup completed")

        # ------------------------------------------------------------------
        # Verify arXiv client
        # ------------------------------------------------------------------
        logger.info(
            f"arXiv client ready: {arxiv_client.base_url}"
        )

        # ------------------------------------------------------------------
        # Docling PDF parser
        # ------------------------------------------------------------------
        # TODO: Verify that the required Docling models are actually
        # cached and available locally instead of assuming they are cached.
        logger.info(
            "PDF parser service initialized (Docling model cache not yet verified)"
        )

        # ------------------------------------------------------------------
        # Environment setup completed
        # ------------------------------------------------------------------
        logger.info(
            "Environment setup completed successfully"
        )

        return {
            "status": "success",
            "message": "Environment setup completed",
        }

    except Exception as e:
        error_msg = f"Environment setup failed: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)