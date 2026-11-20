import ssl
import os
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic_settings import BaseSettings
from functools import lru_cache

# Load .env into os.environ so LangChain/LangSmith SDK can read tracing config
load_dotenv()

class Settings(BaseSettings):
    
    # LLM Configuration
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    primary_model: str = "openai/gpt-4o-mini"
    fallback_model: str = "openai/gpt-4o-mini"
    # Application
    app_env: str = "development"
    log_level: str = "INFO"
    rate_limit: str = "2/minute"
    cache_ttl_seconds: int = 300
    max_retries: int = 3
    
    
    model_config = {"env_file": ".env", "extra": "ignore"}
    
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"
    
@lru_cache
def get_settings() -> Settings:
    """Cached settings instance - loaded once, reused everywhere."""
    return Settings()


def get_llm():
    """Initialize the LLM used by the tool-enabled workflow."""
    settings = get_settings()
    return ChatOpenAI(
        model=settings.primary_model,
        temperature=0,
        timeout=30,
        max_retries=0,
        max_tokens=3000,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    )


def get_embeddings():
    """Initialize the embeddings model used by the RAG index."""
    settings = get_settings()
    return OpenAIEmbeddings(
        model="openai/text-embedding-3-small",
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    )


llm = get_llm()
embeddings = get_embeddings()

