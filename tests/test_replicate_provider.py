"""
Unit and Integration Tests for Replicate Provider (OpenAI GPT-Image-2.5-Flare).
Tests ReplicateImageProvider (Image-to-Image, Text-to-Image, inpainting), ImageDownloader,
ImageGenerator service, error handling, and TryonModelFactory integration.
"""

import os
import io
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from providers.replicate_provider import (
    ReplicateImageProvider,
    ReplicateConfigError,
    InvalidPromptError,
    InvalidImageError,
    ReplicateAPIError,
    ReplicateTimeoutError,
    ReplicateNetworkError,
)
from utils.downloader import GeneratedImage, ImageDownloader
from services.image_generator import ImageGenerator
from server.services.tryon_genai import TryonModelFactory
from server.services.tryon_service import TryonService


# ============================================================================
# Helper Mock Class for Replicate Output
# ============================================================================

class MockReplicateFileOutput:
    """Simulates a Replicate FileOutput object having .read() and .url attributes."""
    def __init__(self, data: bytes = b"mock_generated_webp_bytes", url: str = "https://replicate.delivery/pbxt/test.webp"):
        self.data = data
        self.url = url

    def read(self) -> bytes:
        return self.data


# ============================================================================
# 1. Initialization and Configuration Tests
# ============================================================================

def test_replicate_provider_init_with_token():
    """Test initialization with explicit token."""
    provider = ReplicateImageProvider(api_token="r8_test_token_12345")
    assert provider.api_token == "r8_test_token_12345"
    assert provider.model_name == "openai/gpt-image-2.5-flare"


def test_replicate_provider_init_from_env(monkeypatch):
    """Test initialization loading from REPLICATE_API_TOKEN environment variable."""
    monkeypatch.setenv("REPLICATE_API_TOKEN", "r8_env_token_67890")
    provider = ReplicateImageProvider()
    assert provider.api_token == "r8_env_token_67890"


def test_replicate_provider_missing_token(monkeypatch):
    """Test that missing API token raises ReplicateConfigError on generation."""
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)
    monkeypatch.delenv("REPLICATE_API_KEY", raising=False)
    provider = ReplicateImageProvider(api_token=None)
    with pytest.raises(ReplicateConfigError):
        provider.generate_image(prompt="test prompt")


# ============================================================================
# 2. Input Validation Tests
# ============================================================================

def test_replicate_provider_empty_prompt():
    """Test that empty or whitespace prompt raises InvalidPromptError."""
    provider = ReplicateImageProvider(api_token="r8_dummy")
    with pytest.raises(InvalidPromptError):
        provider.generate_image(prompt="")
    with pytest.raises(InvalidPromptError):
        provider.generate_image(prompt="   ")


def test_replicate_provider_nonexistent_image():
    """Test that nonexistent input image path raises InvalidImageError."""
    provider = ReplicateImageProvider(api_token="r8_dummy")
    with pytest.raises(InvalidImageError):
        provider.generate_image(prompt="test prompt", input_image="nonexistent_file_path_123.jpg")


def test_replicate_provider_empty_image(tmp_path):
    """Test that empty 0-byte image file raises InvalidImageError."""
    empty_file = tmp_path / "empty.jpg"
    empty_file.write_bytes(b"")
    provider = ReplicateImageProvider(api_token="r8_dummy")
    with pytest.raises(InvalidImageError):
        provider.generate_image(prompt="test prompt", input_image=str(empty_file))


def test_replicate_provider_empty_bytes():
    """Test that empty byte array raises InvalidImageError."""
    provider = ReplicateImageProvider(api_token="r8_dummy")
    with pytest.raises(InvalidImageError):
        provider.generate_image(prompt="test prompt", input_image=b"")


# ============================================================================
# 3. Image-to-Image Generation Tests (Primary Workflow)
# ============================================================================

def test_replicate_provider_img2img_file_path(tmp_path):
    """Test primary Image-to-Image editing using a file path with base64 Data URIs."""
    test_img = tmp_path / "portrait.jpg"
    test_img.write_bytes(b"dummy_portrait_jpg_data")

    out_dir = tmp_path / "output"
    provider = ReplicateImageProvider(api_token="r8_test", output_dir=str(out_dir))

    mock_out = [MockReplicateFileOutput(b"rendered_hair_edit_bytes", "https://replicate.delivery/pbxt/edit.webp")]

    with patch("replicate.run", return_value=mock_out) as mock_run:
        result = provider.generate_image(
            prompt="Add modern taper fade hairstyle while preserving facial identity",
            input_image=str(test_img),
            quality="low",
            aspect_ratio="1:1"
        )

        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert args[0] == "openai/gpt-image-2.5-flare"
        payload = kwargs["input"]
        assert payload["prompt"] == "Add modern taper fade hairstyle while preserving facial identity"
        assert payload["quality"] == "low"
        assert payload["aspect_ratio"] == "1:1"
        assert "image" in payload
        assert payload["image"].startswith("data:image/")
        assert "input_images" in payload
        assert isinstance(payload["input_images"], list)
        assert len(payload["input_images"]) == 1
        assert payload["input_images"][0].startswith("data:image/")

        # Verify output artifact
        assert isinstance(result, GeneratedImage)
        assert os.path.exists(result.path)
        assert result.metadata["mode"] == "image-to-image"
        assert result.metadata["model"] == "openai/gpt-image-2.5-flare"
        assert result.image_bytes == b"rendered_hair_edit_bytes"


def test_replicate_provider_img2img_single_user_image_only(tmp_path):
    """Test Image-to-Image strictly sends only 1 image (user portrait) in input_images."""
    user_img = tmp_path / "user_portrait.jpg"
    user_img.write_bytes(b"user_face_bytes_data")

    provider = ReplicateImageProvider(api_token="r8_test", output_dir=str(tmp_path))
    mock_out = [MockReplicateFileOutput(b"transformed_hair_bytes")]

    with patch("replicate.run", return_value=mock_out) as mock_run:
        result = provider.generate_image(
            prompt="Transform hairstyle to Lob with Face Framing",
            input_image=str(user_img),
            quality="low"
        )

        mock_run.assert_called_once()
        payload = mock_run.call_args[1]["input"]
        assert payload["quality"] == "low"
        assert "input_images" in payload
        assert len(payload["input_images"]) == 1
        assert payload["input_images"][0].startswith("data:image/")
        assert payload["image"] == payload["input_images"][0]
        assert "style_image" not in payload
        assert result.metadata["mode"] == "image-to-image"


def test_replicate_provider_default_quality_low():
    """Test that ReplicateImageProvider defaults to quality='low' when unspecified."""
    provider = ReplicateImageProvider(api_token="r8_test")
    mock_out = [MockReplicateFileOutput(b"dummy")]

    with patch("replicate.run", return_value=mock_out) as mock_run:
        provider.generate_image(prompt="test prompt")
        mock_run.assert_called_once()
        payload = mock_run.call_args[1]["input"]
        assert payload["quality"] == "low"


def test_replicate_provider_img2img_bytes():
    """Test Image-to-Image editing using raw image bytes converted to Data URI."""
    provider = ReplicateImageProvider(api_token="r8_test")
    mock_out = [MockReplicateFileOutput(b"bytes_result")]

    with patch("replicate.run", return_value=mock_out) as mock_run:
        result = provider.generate_image(
            prompt="Restyle hair",
            input_image=b"raw_jpg_data_stream_123"
        )

        mock_run.assert_called_once()
        payload = mock_run.call_args[1]["input"]
        assert "image" in payload
        assert payload["image"].startswith("data:image/")
        assert "input_images" in payload
        assert payload["input_images"][0].startswith("data:image/")
        assert result.metadata["mode"] == "image-to-image"


def test_replicate_provider_inpainting_mask(tmp_path):
    """Test Image-to-Image inpainting when a mask is provided as Data URI."""
    test_img = tmp_path / "face.jpg"
    test_img.write_bytes(b"face_bytes")
    test_mask = tmp_path / "hair_mask.png"
    test_mask.write_bytes(b"\x89PNG\r\n\x1a\n" + b"mask_bytes")

    provider = ReplicateImageProvider(api_token="r8_test", output_dir=str(tmp_path))
    mock_out = [MockReplicateFileOutput(b"inpaint_result")]

    with patch("replicate.run", return_value=mock_out) as mock_run:
        result = provider.generate_image(
            prompt="Fill masked scalp area with voluminous curls",
            input_image=str(test_img),
            mask=str(test_mask)
        )

        mock_run.assert_called_once()
        payload = mock_run.call_args[1]["input"]
        assert "image" in payload
        assert payload["image"].startswith("data:image/")
        assert "mask" in payload
        assert payload["mask"].startswith("data:image/png")
        assert result.metadata["mode"] == "inpainting"


# ============================================================================
# 4. Text-to-Image Fallback Tests
# ============================================================================

def test_replicate_provider_text_to_image_fallback():
    """Test that when input_image is None, it cleanly falls back to text-to-image."""
    provider = ReplicateImageProvider(api_token="r8_test")
    mock_out = [MockReplicateFileOutput(b"t2i_result")]

    with patch("replicate.run", return_value=mock_out) as mock_run:
        result = provider.generate_image(
            prompt="A cinematic portrait of a woman with long layered waves",
            input_image=None
        )

        mock_run.assert_called_once()
        payload = mock_run.call_args[1]["input"]
        assert "image" not in payload
        assert "mask" not in payload
        assert result.metadata["mode"] == "text-to-image"


# ============================================================================
# 5. Downloader and Output Saving Tests
# ============================================================================

def test_downloader_custom_directory_and_naming(tmp_path):
    """Test ImageDownloader saves generated images with timestamped naming."""
    out_dir = tmp_path / "custom_output"
    downloader = ImageDownloader(output_dir=str(out_dir))

    mock_item = MockReplicateFileOutput(b"saved_test_image_data")
    artifact = downloader.download_and_save(mock_item, output_format="webp")

    assert os.path.isfile(artifact.path)
    assert artifact.path.endswith(".webp")
    assert "generated_" in os.path.basename(artifact.path)
    with open(artifact.path, "rb") as f:
        assert f.read() == b"saved_test_image_data"


# ============================================================================
# 6. Error Handling Tests
# ============================================================================

def test_replicate_provider_api_error():
    """Test Replicate execution failure raises ReplicateAPIError."""
    provider = ReplicateImageProvider(api_token="r8_test")
    with patch("replicate.run", side_effect=RuntimeError("CUDA execution failed")):
        with pytest.raises(ReplicateAPIError) as exc_info:
            provider.generate_image(prompt="generate hair")
        assert "CUDA execution failed" in str(exc_info.value)


def test_replicate_provider_timeout_error():
    """Test Replicate timeout raises ReplicateTimeoutError."""
    provider = ReplicateImageProvider(api_token="r8_test")
    with patch("replicate.run", side_effect=Exception("Request timeout while waiting")):
        with pytest.raises(ReplicateTimeoutError):
            provider.generate_image(prompt="generate hair")


def test_replicate_provider_empty_output():
    """Test that an empty output list from Replicate raises ReplicateAPIError."""
    provider = ReplicateImageProvider(api_token="r8_test")
    with patch("replicate.run", return_value=[]):
        with pytest.raises(ReplicateAPIError) as exc:
            provider.generate_image(prompt="generate hair")
        assert "empty output list" in str(exc.value)


# ============================================================================
# 7. Service Layer and Factory Integration Tests
# ============================================================================

def test_image_generator_service_edit_image(tmp_path):
    """Test ImageGenerator service delegates to provider edit_image."""
    test_img = tmp_path / "face.jpg"
    test_img.write_bytes(b"dummy")

    provider = ReplicateImageProvider(api_token="r8_test", output_dir=str(tmp_path))
    service = ImageGenerator(provider=provider)

    mock_out = [MockReplicateFileOutput(b"edited_img")]
    with patch("replicate.run", return_value=mock_out):
        res = service.edit_image("Change hair to bob cut", input_image=str(test_img))
        assert res.metadata["mode"] == "image-to-image"


def test_image_generator_service_text_generation(tmp_path):
    """Test ImageGenerator service generate_from_text fallback."""
    provider = ReplicateImageProvider(api_token="r8_test", output_dir=str(tmp_path))
    service = ImageGenerator(provider=provider)

    mock_out = [MockReplicateFileOutput(b"t2i_img")]
    with patch("replicate.run", return_value=mock_out):
        res = service.generate_from_text("Generate blonde pixie cut")
        assert res.metadata["mode"] == "text-to-image"


def test_tryon_model_factory_replicate_registration():
    """Test that TryonModelFactory instantiates ReplicateImageProvider as default or by name."""
    provider_default = TryonModelFactory.get_provider("replicate")
    assert isinstance(provider_default, ReplicateImageProvider)

    provider_by_model = TryonModelFactory.get_provider("openai/gpt-image-2.5-flare")
    assert isinstance(provider_by_model, ReplicateImageProvider)

    provider_alias = TryonModelFactory.get_provider("gpt-image-2.5-flare")
    assert isinstance(provider_alias, ReplicateImageProvider)


def test_tryon_service_uses_replicate_default():
    """Test that TryonService defaults to ReplicateImageProvider."""
    service = TryonService()
    assert isinstance(service.provider, ReplicateImageProvider)


def test_generate_preview_adapter(tmp_path):
    """Test that generate_preview adapter fulfills application contract."""
    test_img = tmp_path / "portrait.jpg"
    test_img.write_bytes(b"portrait_bytes")

    provider = ReplicateImageProvider(api_token="r8_test", output_dir=str(tmp_path))
    mock_out = [MockReplicateFileOutput(b"preview_bytes_data", "https://replicate.delivery/pbxt/preview.webp")]

    with patch("replicate.run", return_value=mock_out):
        result = provider.generate_preview(
            user_image_path=str(test_img),
            hairstyle_data={"name": "Classic Bob", "category": "classic"},
            face_shape="oval",
            prompt_data={"positive_prompt": "Classic Bob on oval face", "negative_prompt": "blurry"}
        )

        assert result["success"] is True
        assert result["preview_bytes"] == b"preview_bytes_data"
        assert result["model_version"] == "openai/gpt-image-2.5-flare"
        assert "preview_path" in result
        assert "preview_url" in result


def test_generate_preview_adapter_single_image_only(tmp_path):
    """Test that generate_preview strictly passes only 1 image (user portrait) to Replicate."""
    user_img = tmp_path / "user.jpg"
    user_img.write_bytes(b"user_bytes")

    provider = ReplicateImageProvider(api_token="r8_test", output_dir=str(tmp_path))
    mock_out = [MockReplicateFileOutput(b"generated_style_bytes")]

    with patch("replicate.run", return_value=mock_out) as mock_run:
        result = provider.generate_preview(
            user_image_path=str(user_img),
            hairstyle_data={"name": "Lob with Face Framing", "category": "trending"},
            face_shape="round",
            prompt_data={
                "positive_prompt": "Transform hairstyle of the person in the photo into a photorealistic Lob with Face Framing",
                "negative_prompt": "blurry"
            }
        )

        assert result["success"] is True
        mock_run.assert_called_once()
        payload = mock_run.call_args[1]["input"]
        assert len(payload["input_images"]) == 1
        assert payload["input_images"][0].startswith("data:image/")
        assert payload["image"] == payload["input_images"][0]
        assert "style_image" not in payload


def test_hairstyle_prompt_builder_top_recommendations():
    """Test specialized prompts for top recommended hairstyles mentioned by user."""
    from server.services.hairstyle_prompts import build_hairstyle_prompt

    # 1. Lob with Face Framing
    lob_doc = {
        'name': 'Lob with Face Framing',
        'description': 'A long bob (lob) with face-framing layers that hit just below the chin, adding length to round faces.',
        'hair_length': 'medium',
        'category': 'trending',
        'tags': ['lob', 'medium', 'face-framing', 'flattering']
    }
    lob_p = build_hairstyle_prompt(lob_doc, face_shape='round')
    assert "Lob with Face Framing" in lob_p['positive_prompt']
    assert "face-framing" in lob_p['positive_prompt']
    assert "round face shape" in lob_p['positive_prompt']
    assert "Keep the exact same person" in lob_p['positive_prompt']
    assert "reference image" not in lob_p['positive_prompt']

    # 2. Soft Waves with Side Part
    waves_doc = {
        'name': 'Soft Waves with Side Part',
        'description': 'Soft, flowing waves with a side part soften strong jawlines and add feminine movement.',
        'hair_length': 'medium',
        'category': 'classic',
        'tags': ['waves', 'medium', 'soft', 'feminine']
    }
    waves_p = build_hairstyle_prompt(waves_doc, face_shape='square')
    assert "Soft Waves with Side Part" in waves_p['positive_prompt']
    assert "side part" in waves_p['positive_prompt']
    assert "square face shape" in waves_p['positive_prompt']
    assert "reference image" not in waves_p['positive_prompt']

    # 3. Layered Shag
    shag_doc = {
        'name': 'Layered Shag',
        'description': 'A modern shag cut with lots of layers that break up angular features and add texture.',
        'hair_length': 'medium',
        'category': 'edgy',
        'tags': ['shag', 'medium', 'textured', 'trendy']
    }
    shag_p = build_hairstyle_prompt(shag_doc, face_shape='square')
    assert "Layered Shag" in shag_p['positive_prompt']
    assert "shag" in shag_p['positive_prompt'].lower()
    assert "square face shape" in shag_p['positive_prompt']
    assert "reference image" not in shag_p['positive_prompt']

