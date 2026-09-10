"""
Abstract Base Class for Multi-Agent System (MAS) Framework Adapters.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class MASAdapter(ABC):
    """
    Abstract interface for integrating Multi-Agent System frameworks
    (e.g., MetaGPT, ChatDev, MARE) with SpecForge AI.
    """

    @abstractmethod
    def prepare_task_input(
        self, annotated_spec: Optional[Dict[str, Any]], task_description: str
    ) -> Any:
        """
        Transform task description and SpecForge's annotated spec into the input
        format expected by the target MAS framework.

        If annotated_spec is None, return baseline task description.
        """
        pass

    @abstractmethod
    def run(self, prepared_input: Any, output_dir: str) -> Dict[str, Any]:
        """
        Invoke the MAS framework and write raw logs/traces to output_dir.

        Returns a dictionary containing:
          - "status": "completed" | "failed_to_run"
          - "raw_trace_path": str (path to raw log/trace file)
          - "duration_seconds": float
        """
        pass

    @abstractmethod
    def get_framework_name(self) -> str:
        """Return the short framework identifier (e.g. 'metagpt')."""
        pass
