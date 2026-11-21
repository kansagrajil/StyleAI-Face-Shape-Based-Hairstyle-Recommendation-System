"""
ComfyUI Configuration Module.
Stores configurable parameters (API endpoint, API key, timeout, polling interval, workflow path)
from environment variables with production-ready fallback defaults.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ComfyUIConfig:
    """Configuration settings for ComfyUI API interactions."""

    api_url: str = field(
        default_factory=lambda: os.getenv("COMFYUI_API_URL", "http://127.0.0.1:8188").rstrip("/")
    )
    api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("COMFYUI_API_KEY") or None
    )
    workflow_path: str = field(
        default_factory=lambda: os.getenv("COMFYUI_WORKFLOW_PATH", "workflow/sd1.5.json")
    )
    timeout: float = field(
        default_factory=lambda: float(os.getenv("COMFYUI_TIMEOUT", "180.0"))
    )
    poll_interval: float = field(
        default_factory=lambda: float(os.getenv("COMFYUI_POLL_INTERVAL", "1.0"))
    )

    # Inference defaults for SD 1.5
    default_steps: int = 20
    default_cfg: float = 8.0
    default_sampler_name: str = "euler"
    default_scheduler: str = "simple"
    default_width: int = 512
    default_height: int = 512
    default_batch_size: int = 1

    @classmethod
    def from_env(cls, **overrides) -> "ComfyUIConfig":
        """Instantiate config using environment variables with optional keyword overrides."""
        config = cls()
        for key, value in overrides.items():
            if hasattr(config, key) and value is not None:
                setattr(config, key, value)
        return config
