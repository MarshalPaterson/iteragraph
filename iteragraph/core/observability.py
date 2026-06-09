import os
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class Observability:
    def __init__(self):
        self.enabled = os.getenv("PHOENIX_ENABLED", "false").lower() == "true"
        self.endpoint = os.getenv("PHOENIX_ENDPOINT", "http://localhost:6006")
        self.tracer = None
        
        if self.enabled:
            self._init_phoenix()

    def _init_phoenix(self):
        try:
            import phoenix as px
            px.launch_app(endpoint=self.endpoint)
            self.tracer = px
            logger.info(f"Phoenix observability enabled at {self.endpoint}")
        except Exception as e:
            logger.warning(f"Phoenix initialization failed: {e}")
            self.enabled = False

    @contextmanager
    def trace(self, name: str, attributes: Optional[Dict] = None):
        if self.enabled:
            logger.debug(f"Tracing: {name}")
        try:
            yield
        finally:
            if self.enabled:
                logger.debug(f"Completed: {name}")

    def record_evaluation(self, task: str, result: str, groundness: float):
        if self.enabled:
            logger.info(f"Eval: task={task}, groundness={groundness:.2f}")


observability = Observability()