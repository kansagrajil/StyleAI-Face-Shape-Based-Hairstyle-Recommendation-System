"""
Custom exception hierarchy for ComfyUI integration.
"""


class ComfyUIError(Exception):
    """Base exception for all ComfyUI-related errors."""
    pass


class WorkflowNotFoundError(ComfyUIError):
    """Raised when the workflow JSON file does not exist."""
    pass


class InvalidWorkflowError(ComfyUIError):
    """Raised when the workflow JSON is malformed or missing required nodes."""
    pass


class ComfyUINetworkError(ComfyUIError):
    """Raised when communication with the ComfyUI API fails."""
    pass


class ComfyUIExecutionError(ComfyUIError):
    """Raised when ComfyUI encounters a node execution failure or error prompt."""
    pass


class ComfyUITimeoutError(ComfyUIError):
    """Raised when generation does not complete within the allotted timeout."""
    pass


class MissingOutputImageError(ComfyUIError):
    """Raised when generation completes but no output image is found or retrieved."""
    pass
