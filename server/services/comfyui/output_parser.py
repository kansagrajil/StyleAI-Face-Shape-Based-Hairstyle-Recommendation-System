"""
ComfyUI Output Parser & Image Downloader.
Extracts output image metadata from completed job history and downloads the binary image artifacts.
"""

import logging
from typing import Dict, Any, List, Optional

from server.services.comfyui.api_client import ComfyUIClient
from server.services.comfyui.exceptions import MissingOutputImageError

logger = logging.getLogger("ComfyUI.OutputParser")


class OutputParser:
    """Parses outputs from ComfyUI job history and downloads generated images."""

    def __init__(self, client: ComfyUIClient):
        self.client = client

    def extract_image_items(self, prompt_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Locate all output image references from the node outputs dictionary.

        Args:
            prompt_info: The dictionary for the completed prompt from /history/{prompt_id}.

        Returns:
            List of dicts with keys: 'filename', 'subfolder', 'type'.
        """
        outputs = prompt_info.get("outputs", {})
        images = []

        for node_id, node_output in outputs.items():
            if isinstance(node_output, dict) and "images" in node_output:
                for img_item in node_output["images"]:
                    if isinstance(img_item, dict) and "filename" in img_item:
                        images.append({
                            "filename": img_item["filename"],
                            "subfolder": img_item.get("subfolder", ""),
                            "type": img_item.get("type", "output"),
                            "node_id": node_id
                        })

        return images

    def get_primary_image_bytes(self, prompt_info: Dict[str, Any]) -> bytes:
        """
        Extract the first available output image and fetch its raw bytes.

        Args:
            prompt_info: The dictionary for the completed prompt.

        Returns:
            bytes: Downloaded image content.

        Raises:
            MissingOutputImageError: If no output image was generated or downloaded.
        """
        image_items = self.extract_image_items(prompt_info)
        if not image_items:
            logger.error(f"No output images found in prompt history outputs: {prompt_info.get('outputs')}")
            raise MissingOutputImageError(
                "ComfyUI completed execution but did not produce any output images."
            )

        primary = image_items[0]
        filename = primary["filename"]
        subfolder = primary["subfolder"]
        folder_type = primary["type"]

        logger.info(
            f"Retrieving output image '{filename}' from node {primary.get('node_id')} "
            f"(subfolder='{subfolder}', type='{folder_type}')"
        )

        image_bytes = self.client.fetch_image_bytes(
            filename=filename,
            subfolder=subfolder,
            folder_type=folder_type
        )

        if not image_bytes:
            raise MissingOutputImageError(f"Fetched image '{filename}' was empty.")

        logger.info(f"Retrieved primary output image '{filename}' ({len(image_bytes)} bytes)")
        return image_bytes
