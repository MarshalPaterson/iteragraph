import os
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

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
            self.client = weaviate.Client(
                url=self.url,
                auth_client_secret=weaviate.AuthApiKey(self.api_key) if self.api_key else None
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
            self.client.data_object.create(
                class_name="ResearchMemory",
                data_object={"content": content, "metadata": metadata or {}}
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


vector_store = VectorStore()