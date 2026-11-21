"""
Image Generator Service.
Provides a clean, modular service layer over image generation providers,
managing image-to-image transformations, style transfer, and inpainting.
"""

import logging
from pathlib import Path
from typing import Any, BinaryIO, Dict, Optional, Union

from providers.replicate_provider import ReplicateImageProvider
from utils.downloader import GeneratedImage

logger = logging.getLogger("Services.ImageGenerator")


class ImageGenerator:
    """High-level service for executing image-to-image and text-to-image workflows."""

    def __init__(self, provider: Optional[ReplicateImageProvider] = None):
        self.provider = provider or ReplicateImageProvider()

    def edit_image(
        self,
        prompt: str,
        input_image: Union[str, Path, bytes, BinaryIO],
        selected_image: Union[str, Path, bytes, BinaryIO, None] = None,
        negative_prompt: Optional[str] = None,
        mask: Union[str, Path, bytes, BinaryIO, None] = None,
        **kwargs
    ) -> GeneratedImage:
        """
        Execute an Image-to-Image transformation or inpainting request.

        Args:
            prompt: Text instruction detailing the desired modification.
            input_image: Existing portrait or source image.
            selected_image: Optional reference hairstyle image.
            negative_prompt: Elements to avoid.
            mask: Inpainting mask.
            **kwargs: Extra parameters (e.g. quality, aspect_ratio, compression).

        Returns:
            GeneratedImage: The resulting saved image artifact.
        """
        logger.info(f"ImageGenerator: executing Image-to-Image with prompt: '{prompt[:50]}...'")
        return self.provider.generate_image(
            prompt=prompt,
            input_image=input_image,
            selected_image=selected_image,
            negative_prompt=negative_prompt,
            mask=mask,
            **kwargs
        )

    def generate_from_text(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        **kwargs
    ) -> GeneratedImage:
        """
        Fallback Text-to-Image generation when no input image is provided.

        Args:
            prompt: Text prompt.
            negative_prompt: Negative guidance.
            **kwargs: Extra parameters.

        Returns:
            GeneratedImage: Resulting image artifact.
        """
        logger.info(f"ImageGenerator: executing Text-to-Image with prompt: '{prompt[:50]}...'")
        return self.provider.generate_image(
            prompt=prompt,
            input_image=None,
            negative_prompt=negative_prompt,
            **kwargs
        )
