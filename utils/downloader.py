"""
Image Downloader and Artifact Management Module.
Downloads and persists rendered outputs from Replicate API responses into the application storage.
"""

import os
import time
import uuid
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union
import requests

logger = logging.getLogger("Replicate.Downloader")


@dataclass
class GeneratedImage:
    """Represents a successfully downloaded and stored generated image artifact."""
    path: str
    url: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    image_bytes: Optional[bytes] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert artifact metadata to dictionary."""
        return {
            "path": self.path,
            "url": self.url,
            "metadata": self.metadata
        }


class ImageDownloader:
    """Handles downloading and saving generated images from Replicate output streams or URLs."""

    def __init__(self, output_dir: Optional[str] = None):
        if output_dir:
            self.output_dir = os.path.abspath(output_dir)
        else:
            # Default to standard server uploads tryon previews directory
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            self.output_dir = os.path.abspath(
                os.path.join(base_dir, "server", "uploads", "tryon_previews")
            )
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_filename(self, extension: str = "webp") -> str:
        """Generate a structured timestamped filename: generated_YYYYMMDD_HHMMSS_<uid>.<ext>."""
        clean_ext = extension.lstrip(".").lower()
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        rand_suffix = uuid.uuid4().hex[:6]
        return f"generated_{now_str}_{rand_suffix}.{clean_ext}"

    def download_and_save(
        self,
        replicate_output_item: Any,
        output_format: str = "webp",
        metadata: Optional[Dict[str, Any]] = None,
        custom_filename: Optional[str] = None
    ) -> GeneratedImage:
        """
        Download output item from Replicate (which can be a FileOutput with .read()/.url, a URL string, or bytes)
        and persist it to the output directory.

        Args:
            replicate_output_item: Replicate output object, URL string, or raw bytes.
            output_format: File format extension (e.g. 'webp', 'png', 'jpg').
            metadata: Metadata dictionary to attach.
            custom_filename: Optional filename override.

        Returns:
            GeneratedImage: Populated artifact instance.
        """
        start_time = time.time()
        filename = custom_filename or self.generate_filename(output_format)
        target_path = os.path.join(self.output_dir, filename)
        image_url = ""
        image_bytes: bytes = b""

        logger.info(f"Downloading Replicate generated output artifact to: '{target_path}'")

        # 1. Check if output item has read() method (Replicate FileOutput)
        if hasattr(replicate_output_item, "read") and callable(replicate_output_item.read):
            try:
                image_bytes = replicate_output_item.read()
            except Exception as e:
                logger.error(f"Failed to read data via .read(): {e}")

        # 2. Check if output item has a .url attribute
        if hasattr(replicate_output_item, "url"):
            image_url = str(replicate_output_item.url)
        elif isinstance(replicate_output_item, str) and (
            replicate_output_item.startswith("http://") or replicate_output_item.startswith("https://")
        ):
            image_url = replicate_output_item

        # 3. If image_bytes not populated yet, download via HTTP from URL
        if not image_bytes and image_url:
            logger.info(f"Fetching image binary data from Replicate URL: {image_url}")
            try:
                res = requests.get(image_url, timeout=30.0)
                if res.status_code == 200:
                    image_bytes = res.content
                else:
                    raise IOError(f"HTTP request to image URL failed with status {res.status_code}")
            except Exception as e:
                logger.error(f"Error downloading image from {image_url}: {e}")
                raise

        # 4. If output item is already bytes
        if not image_bytes and isinstance(replicate_output_item, bytes):
            image_bytes = replicate_output_item

        if not image_bytes:
            raise ValueError("Could not extract non-empty image data from Replicate output item.")

        # Persist to disk
        with open(target_path, "wb") as f:
            f.write(image_bytes)

        duration = round(time.time() - start_time, 2)
        logger.info(
            f"Successfully saved generated image '{filename}' ({len(image_bytes)} bytes) in {duration}s"
        )

        meta = metadata.copy() if metadata else {}
        meta.update({
            "saved_filename": filename,
            "saved_path": target_path,
            "bytes_length": len(image_bytes),
            "download_duration_s": duration
        })

        # Derive relative web url if inside server/uploads
        web_url = image_url
        if "server" in target_path and "uploads" in target_path:
            rel_part = target_path.split("uploads")[-1].replace("\\", "/")
            web_url = f"/uploads{rel_part}"

        return GeneratedImage(
            path=target_path,
            url=web_url,
            metadata=meta,
            image_bytes=image_bytes
        )
