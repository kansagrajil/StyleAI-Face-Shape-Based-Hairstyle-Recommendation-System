"""
Replicate Image Provider (OpenAI GPT-Image-2.5-Flare).
Implements Image-to-Image editing (primary) and Text-to-Image (fallback) generation
using the official Replicate Python SDK.
"""

import os
import io
import time
import base64
import logging
import mimetypes
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Union

from utils.downloader import GeneratedImage, ImageDownloader

logger = logging.getLogger("Replicate.Provider")


# ============================================================================
# Custom Exceptions Hierarchy
# ============================================================================

class ReplicateProviderError(Exception):
    """Base exception for all Replicate provider errors."""
    pass


class ReplicateConfigError(ReplicateProviderError):
    """Raised when configuration or REPLICATE_API_TOKEN is missing or invalid."""
    pass


class InvalidPromptError(ReplicateProviderError):
    """Raised when an invalid or empty prompt is provided."""
    pass


class InvalidImageError(ReplicateProviderError):
    """Raised when an input image or mask is unreadable, empty, or missing."""
    pass


class ReplicateAPIError(ReplicateProviderError):
    """Raised when the Replicate API encounters a runtime or model execution error."""
    pass


class ReplicateTimeoutError(ReplicateProviderError):
    """Raised when the generation request exceeds the allotted timeout limit."""
    pass


class ReplicateNetworkError(ReplicateProviderError):
    """Raised when a network failure occurs communicating with Replicate."""
    pass


# ============================================================================
# Data URI Helper
# ============================================================================

def to_data_uri(
    file_input: Union[str, Path, bytes, BinaryIO, None],
    default_mime: str = "image/jpeg"
) -> Optional[str]:
    """
    Convert a file path, Path object, raw bytes, or BinaryIO stream into a base64 Data URI.
    If already a Data URI or HTTP/HTTPS URL, returns it as-is.

    Example output: 'data:image/jpeg;base64,/9j/4AAQSkZJRg...'
    """
    if file_input is None:
        return None

    if isinstance(file_input, str):
        cleaned = file_input.strip()
        if cleaned.startswith("data:image/") or cleaned.startswith("http://") or cleaned.startswith("https://"):
            return cleaned
        p = Path(cleaned)
        if not p.exists():
            raise InvalidImageError(f"Image file not found at: '{cleaned}'")
        if p.stat().st_size == 0:
            raise InvalidImageError(f"Image file at '{cleaned}' is empty (0 bytes).")
        mime, _ = mimetypes.guess_type(p)
        mime = mime or default_mime
        raw_bytes = p.read_bytes()
        b64 = base64.b64encode(raw_bytes).decode("utf-8")
        return f"data:{mime};base64,{b64}"

    if isinstance(file_input, Path):
        if not file_input.exists():
            raise InvalidImageError(f"Image file not found at: '{file_input}'")
        if file_input.stat().st_size == 0:
            raise InvalidImageError(f"Image file at '{file_input}' is empty (0 bytes).")
        mime, _ = mimetypes.guess_type(file_input)
        mime = mime or default_mime
        raw_bytes = file_input.read_bytes()
        b64 = base64.b64encode(raw_bytes).decode("utf-8")
        return f"data:{mime};base64,{b64}"

    if isinstance(file_input, bytes):
        if len(file_input) == 0:
            raise InvalidImageError("Image bytes provided are empty.")
        if file_input.startswith(b"\x89PNG"):
            mime = "image/png"
        elif file_input.startswith(b"RIFF") and b"WEBP" in file_input[:16]:
            mime = "image/webp"
        else:
            mime = default_mime
        b64 = base64.b64encode(file_input).decode("utf-8")
        return f"data:{mime};base64,{b64}"

    if hasattr(file_input, "read"):
        raw_bytes = file_input.read()
        if hasattr(file_input, "seek"):
            try:
                file_input.seek(0)
            except Exception:
                pass
        if not raw_bytes or len(raw_bytes) == 0:
            raise InvalidImageError("Image stream provided is empty.")
        if raw_bytes.startswith(b"\x89PNG"):
            mime = "image/png"
        elif raw_bytes.startswith(b"RIFF") and b"WEBP" in raw_bytes[:16]:
            mime = "image/webp"
        else:
            mime = default_mime
        b64 = base64.b64encode(raw_bytes).decode("utf-8")
        return f"data:{mime};base64,{b64}"

    raise InvalidImageError(
        f"Unsupported image input type: {type(file_input)}. Expected Path, str, bytes, or BinaryIO."
    )


# ============================================================================
# Replicate Image Provider
# ============================================================================

class ReplicateImageProvider:
    """
    Image generation and editing provider utilizing Replicate's
    'openai/gpt-image-2.5-flare' model. Prioritizes Image-to-Image editing
    while seamlessly falling back to Text-to-Image.
    """

    MODEL_NAME = "openai/gpt-image-2.5-flare"

    DEFAULT_PARAMETERS = {
        "quality": "low",
        "background": "auto",
        "moderation": "auto",
        "aspect_ratio": "3:2",
        "output_format": "webp",
        "number_of_images": 1,
        "output_compression": 90
    }

    def __init__(
        self,
        api_token: Optional[str] = None,
        model_name: Optional[str] = None,
        output_dir: Optional[str] = None,
        downloader: Optional[ImageDownloader] = None
    ):
        """
        Initialize Replicate provider with API credentials and configuration.

        Args:
            api_token: Optional API token override. If omitted, loads from REPLICATE_API_TOKEN.
            model_name: Optional model identifier override.
            output_dir: Directory where generated artifacts are stored.
            downloader: Optional ImageDownloader instance.
        """
        # Prefer env token if explicit api_token looks like a placeholder
        env_token = os.getenv("REPLICATE_API_TOKEN") or os.getenv("REPLICATE_API_KEY")
        if api_token and not str(api_token).startswith("r8_") and env_token and env_token.startswith("r8_"):
            api_token = env_token

        self.api_token = (
            api_token
            or env_token
        )
        self.model_name = model_name or os.getenv("REPLICATE_MODEL", self.MODEL_NAME)
        self.downloader = downloader or ImageDownloader(output_dir=output_dir)

        # Set environment variable for the Replicate SDK client
        if self.api_token:
            os.environ["REPLICATE_API_TOKEN"] = self.api_token

        logger.info(
            f"Initialized ReplicateImageProvider with model '{self.model_name}' "
            f"(Token configured: {bool(self.api_token)})"
        )

    def _prepare_input_file(
        self,
        file_input: Union[str, Path, bytes, BinaryIO, None],
        field_name: str = "image"
    ) -> Optional[BinaryIO]:
        """
        Convert file path, bytes, or BinaryIO into an open binary stream.
        Maintained for backwards-compatibility.
        """
        if file_input is None:
            return None

        if isinstance(file_input, (str, Path)):
            path_str = str(file_input)
            if not os.path.exists(path_str):
                raise InvalidImageError(f"{field_name.capitalize()} file not found at: '{path_str}'")
            if os.path.getsize(path_str) == 0:
                raise InvalidImageError(f"{field_name.capitalize()} file at '{path_str}' is empty (0 bytes).")
            try:
                return open(path_str, "rb")
            except Exception as e:
                raise InvalidImageError(f"Failed to open {field_name} file '{path_str}': {e}") from e

        if isinstance(file_input, bytes):
            if len(file_input) == 0:
                raise InvalidImageError(f"{field_name.capitalize()} bytes provided are empty.")
            return io.BytesIO(file_input)

        if hasattr(file_input, "read"):
            return file_input

        raise InvalidImageError(
            f"Unsupported type for {field_name}: {type(file_input)}. Expected Path, str, bytes, or BinaryIO."
        )

    def generate_image(
        self,
        prompt: str,
        input_image: Union[str, Path, bytes, BinaryIO, None] = None,
        selected_image: Union[str, Path, bytes, BinaryIO, None] = None,
        negative_prompt: Optional[str] = None,
        mask: Union[str, Path, bytes, BinaryIO, None] = None,
        **kwargs
    ) -> GeneratedImage:
        """
        Generate or edit an image using Replicate SDK.
        Prioritizes Image-to-Image editing when input_image is supplied.
        Encodes user portrait and selected hairstyle image as base64 Data URIs
        and submits them in the input_images parameter expected by Replicate.

        Args:
            prompt: Text instruction describing the desired edit or image.
            input_image: Existing user portrait or primary image to edit.
            selected_image: Optional reference hairstyle image to apply.
            negative_prompt: Optional negative guidance.
            mask: Optional binary mask for inpainting.
            **kwargs: Overrides for quality, aspect_ratio, output_format, etc.

        Returns:
            GeneratedImage: Artifact with local path, URL, and metadata.

        Raises:
            ReplicateConfigError: When API token is not configured.
            InvalidPromptError: When prompt is empty.
            InvalidImageError: When input image is invalid.
            ReplicateAPIError: When Replicate execution fails.
        """
        start_time = time.time()

        # 1. Validate credentials & inputs
        if not self.api_token:
            raise ReplicateConfigError(
                "REPLICATE_API_TOKEN is not set. Please add it to your .env file or pass it to ReplicateImageProvider."
            )

        if not prompt or not str(prompt).strip():
            raise InvalidPromptError("Prompt string cannot be empty.")

        clean_prompt = str(prompt).strip()

        # 2. Build model input parameters
        input_payload: Dict[str, Any] = self.DEFAULT_PARAMETERS.copy()
        default_quality = os.getenv("REPLICATE_QUALITY", self.DEFAULT_PARAMETERS.get("quality", "low"))
        input_payload["quality"] = default_quality
        input_payload.update(kwargs)
        input_payload["prompt"] = clean_prompt

        if negative_prompt:
            input_payload["negative_prompt"] = str(negative_prompt).strip()

        # 3. Handle Image-to-Image vs Text-to-Image with Base64 Data URIs
        mode = "text-to-image"
        input_images_list: List[str] = []

        if input_image is not None:
            user_data_uri = to_data_uri(input_image)
            # ONLY 1 image of the uploaded person goes with the request
            input_images_list.append(user_data_uri)
            input_payload["image"] = user_data_uri
            input_payload["input_image"] = user_data_uri
            mode = "image-to-image"

        if input_images_list:
            input_payload["input_images"] = input_images_list

        if mask is not None:
            mask_data_uri = to_data_uri(mask)
            input_payload["mask"] = mask_data_uri
            mode = "inpainting"

        # Log request parameters (summarizing base64 payloads to keep logs readable)
        logged_payload = {}
        for k, v in input_payload.items():
            if isinstance(v, str) and v.startswith("data:image/"):
                logged_payload[k] = f"<data_uri mime={v.split(';')[0]} len={len(v)}>"
            elif isinstance(v, list) and k == "input_images":
                logged_payload[k] = [
                    (f"<data_uri mime={img.split(';')[0]} len={len(img)}>" if isinstance(img, str) and img.startswith("data:image/") else str(img))
                    for img in v
                ]
            elif hasattr(v, "read"):
                logged_payload[k] = f"<{type(v).__name__}>"
            else:
                logged_payload[k] = v

        logger.info(
            f"Starting Replicate generation [{mode}] with model '{self.model_name}': "
            f"params={logged_payload}"
        )

        # 4. Invoke Replicate SDK
        try:
            import replicate
        except ImportError as e:
            raise ReplicateConfigError(
                "The 'replicate' Python package is required. Install it with: pip install replicate"
            ) from e

        try:
            output = replicate.run(
                self.model_name,
                input=input_payload
            )
        except Exception as e:
            err_msg = str(e)
            logger.error(f"Replicate API execution failed: {err_msg}")
            if "timeout" in err_msg.lower():
                raise ReplicateTimeoutError(f"Replicate request timed out: {err_msg}") from e
            if "connection" in err_msg.lower() or "network" in err_msg.lower():
                raise ReplicateNetworkError(f"Network error during Replicate API call: {err_msg}") from e
            raise ReplicateAPIError(f"Replicate API error: {err_msg}") from e

        # 5. Validate and parse output
        if not output:
            raise ReplicateAPIError("Replicate model completed but returned an empty output list.")

        output_item = output[0] if isinstance(output, (list, tuple)) else output
        duration = round(time.time() - start_time, 2)
        logger.info(f"Replicate generation completed successfully in {duration}s")

        # 6. Download and save output artifact
        output_fmt = input_payload.get("output_format", "webp")
        metadata = {
            "provider": "replicate",
            "model": self.model_name,
            "mode": mode,
            "prompt": clean_prompt,
            "generation_duration_s": duration,
            "parameters": {
                k: (f"<data_uri len={len(v)}>" if isinstance(v, str) and v.startswith("data:image/") else (
                    [f"<data_uri len={len(i)}>" if isinstance(i, str) and i.startswith("data:image/") else i for i in v]
                    if isinstance(v, list) else v
                ))
                for k, v in input_payload.items()
                if not hasattr(v, "read")
            }
        }

        generated_image = self.downloader.download_and_save(
            replicate_output_item=output_item,
            output_format=output_fmt,
            metadata=metadata
        )

        return generated_image

    # ========================================================================
    # Compatibility with Application Interface (BaseTryonModel)
    # ========================================================================

    def generate_preview(
        self,
        user_image_path: str,
        hairstyle_data: Dict[str, Any],
        face_shape: str,
        prompt_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Adapter method satisfying the BaseTryonModel interface in StyleAI.

        Args:
            user_image_path: Path to user's face photo.
            hairstyle_data: Metadata dict for chosen hairstyle.
            face_shape: Detected face shape.
            prompt_data: Prompt data including positive/negative prompts and reference images.

        Returns:
            dict: {
                'success': bool,
                'preview_bytes': bytes,
                'preview_url': str,
                'preview_path': str,
                'model_version': str,
                'metadata': dict,
                'error': str (if failed)
            }
        """
        positive_prompt = prompt_data.get("positive_prompt") or prompt_data.get("prompt", "")
        negative_prompt = prompt_data.get("negative_prompt", "")
        mask = prompt_data.get("mask")

        try:
            extra_params = {
                k: v for k, v in prompt_data.items()
                if k not in ("positive_prompt", "negative_prompt", "prompt", "mask", "landmarks", "selected_image", "selected_image_url")
            }

            # Only the 1 uploaded image of the person goes with the request
            generated = self.generate_image(
                prompt=positive_prompt,
                input_image=user_image_path,
                negative_prompt=negative_prompt,
                mask=mask,
                **extra_params
            )

            return {
                "success": True,
                "preview_bytes": generated.image_bytes,
                "preview_url": generated.url,
                "preview_path": generated.path,
                "model_version": self.model_name,
                "metadata": generated.metadata
            }

        except ReplicateProviderError as e:
            logger.error(f"Replicate preview generation error: {e}")
            return {
                "success": False,
                "error": f"Replicate Error: {str(e)}",
                "model_version": self.model_name
            }
        except Exception as e:
            logger.exception(f"Unexpected error in Replicate preview generation: {e}")
            return {
                "success": False,
                "error": f"Internal Error: {str(e)}",
                "model_version": self.model_name
            }
