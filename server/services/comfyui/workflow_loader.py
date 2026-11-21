"""
ComfyUI Workflow Loader.
Dynamically loads and validates ComfyUI workflow JSON definitions from disk.
"""

import os
import json
import logging
from typing import Dict, Any

from server.services.comfyui.exceptions import (
    WorkflowNotFoundError,
    InvalidWorkflowError
)

logger = logging.getLogger("ComfyUI.WorkflowLoader")


class WorkflowLoader:
    """Handles dynamic loading and schema validation of ComfyUI workflow JSON files."""

    @staticmethod
    def resolve_workflow_path(path_or_filename: str) -> str:
        """
        Resolve workflow path against potential locations (absolute, CWD, or project root).
        """
        if not path_or_filename:
            raise WorkflowNotFoundError("Workflow path is empty or unspecified.")

        # If already an existing absolute path
        if os.path.isabs(path_or_filename) and os.path.isfile(path_or_filename):
            return os.path.abspath(path_or_filename)

        # Check relative to current working directory
        cwd_path = os.path.abspath(path_or_filename)
        if os.path.isfile(cwd_path):
            return cwd_path

        # Check relative to project root
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        root_path = os.path.abspath(os.path.join(base_dir, path_or_filename.lstrip("/\\")))
        if os.path.isfile(root_path):
            return root_path

        raise WorkflowNotFoundError(
            f"Workflow file could not be found at '{path_or_filename}' "
            f"(checked CWD: '{cwd_path}', Project Root: '{root_path}')"
        )

    @classmethod
    def load(cls, workflow_path: str) -> Dict[str, Any]:
        """
        Dynamically read and parse workflow JSON from disk.

        Args:
            workflow_path: Relative or absolute path to workflow JSON.

        Returns:
            Dict containing the parsed ComfyUI workflow graph.

        Raises:
            WorkflowNotFoundError: When file is not found.
            InvalidWorkflowError: When JSON is invalid or missing required structure.
        """
        resolved_path = cls.resolve_workflow_path(workflow_path)
        logger.info(f"Loading ComfyUI workflow from: {resolved_path}")

        try:
            with open(resolved_path, "r", encoding="utf-8") as f:
                workflow = json.load(f)
        except json.JSONDecodeError as err:
            raise InvalidWorkflowError(
                f"Failed to parse workflow JSON from '{resolved_path}': {err}"
            ) from err
        except OSError as err:
            raise WorkflowNotFoundError(
                f"I/O error reading workflow file '{resolved_path}': {err}"
            ) from err

        if not isinstance(workflow, dict) or not workflow:
            raise InvalidWorkflowError(
                f"Workflow definition in '{resolved_path}' must be a non-empty dictionary of nodes."
            )

        logger.info(
            f"Workflow loaded successfully from '{resolved_path}' with {len(workflow)} nodes."
        )
        return workflow
