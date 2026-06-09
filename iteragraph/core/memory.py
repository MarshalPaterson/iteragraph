import os
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    content: str
    metadata: Dict[str, Any]


class VectorStore:
    def __init__(self):
        self.url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        self.api_key = os.getenv("WEAVIATE_API_KEY", "")
        self.client = None
        self._init_client()

    def _init_client(self):
        try:
            import weaviate
            from weaviate.auth import AuthApiKey

            parsed = urlparse(self.url)
            host = parsed.hostname or "localhost"
            port = parsed.port or 8080
            secure = parsed.scheme == "https"

            self.client = weaviate.connect_to_custom(
                http_host=host,
                http_port=port,
                http_secure=secure,
                grpc_host=host,
                grpc_port=50051,
                grpc_secure=secure,
                auth_credentials=AuthApiKey(self.api_key) if self.api_key else None,
            )
            logger.info(f"Connected to Weaviate at {self.url}")
        except Exception as e:
            logger.warning(f"Weaviate unavailable: {e}")
            self.client = None

    def add_memory(self, content: str, metadata: Optional[Dict] = None) -> bool:
        if not self.client:
            logger.warning("Weaviate not initialized, skipping memory add")
            return False

        try:
            self.client.data.insert(
                data_object={"content": content, "metadata": metadata or {}},
                class_name="ResearchMemory",
            )
            return True
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            return False

    def search(self, query: str, limit: int = 5) -> List[str]:
        if not self.client:
            return []

        try:
            results = self.client.query.get(
                "ResearchMemory",
                ["content"]
            ).with_near_text({"concepts": [query]}).with_limit(limit).do()
            return [r["content"] for r in results.get("data", {}).get("Get", {}).get("ResearchMemory", [])]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def close(self):
        if self.client:
            self.client.close()


vector_store = VectorStore()