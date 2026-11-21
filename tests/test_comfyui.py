"""
Unit and Integration Tests for ComfyUI API Refactoring.
Tests WorkflowLoader, WorkflowUpdater, ComfyUIClient, JobPoller, OutputParser,
and ComfyUIModel provider integration.
"""

import os
import json
import pytest
from unittest.mock import MagicMock, patch

from server.services.comfyui.config import ComfyUIConfig
from server.services.comfyui.workflow_loader import WorkflowLoader
from server.services.comfyui.workflow_updater import WorkflowUpdater
from server.services.comfyui.api_client import ComfyUIClient
from server.services.comfyui.job_poller import JobPoller
from server.services.comfyui.output_parser import OutputParser
from server.services.comfyui.model_provider import ComfyUIModel
from server.services.comfyui.exceptions import (
    WorkflowNotFoundError,
    InvalidWorkflowError,
    ComfyUINetworkError,
    ComfyUIExecutionError,
    ComfyUITimeoutError,
    MissingOutputImageError,
)
from server.services.tryon_genai import TryonModelFactory


# ============================================================================
# 1. WorkflowLoader Tests
# ============================================================================

def test_workflow_loader_success():
    """Test loading the existing sd1.5.json workflow."""
    workflow = WorkflowLoader.load("workflow/sd1.5.json")
    assert isinstance(workflow, dict)
    assert len(workflow) > 0
    # Check essential nodes from sd1.5.json
    assert "11" in workflow  # Positive prompt node
    assert "27" in workflow  # KSamplerAdvanced node
    assert "28" in workflow  # Negative prompt node
    assert "29" in workflow  # EmptyLatentImage node
    assert "18" in workflow  # SaveImage node


def test_workflow_loader_not_found():
    """Test that loading a non-existent file raises WorkflowNotFoundError."""
    with pytest.raises(WorkflowNotFoundError):
        WorkflowLoader.load("non_existent_path_to_workflow_123.json")


def test_workflow_loader_invalid_json(tmp_path):
    """Test that malformed JSON raises InvalidWorkflowError."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{ unquoted_invalid_json: true, ", encoding="utf-8")
    with pytest.raises(InvalidWorkflowError):
        WorkflowLoader.load(str(bad_file))


def test_workflow_loader_empty_json(tmp_path):
    """Test that empty JSON dictionary raises InvalidWorkflowError."""
    empty_file = tmp_path / "empty.json"
    empty_file.write_text("{}", encoding="utf-8")
    with pytest.raises(InvalidWorkflowError):
        WorkflowLoader.load(str(empty_file))


# ============================================================================
# 2. WorkflowUpdater Tests
# ============================================================================

def test_workflow_updater_modifies_nodes():
    """Test that WorkflowUpdater correctly updates prompts, sampler, and dimensions."""
    original = WorkflowLoader.load("workflow/sd1.5.json")
    
    updated = WorkflowUpdater.update(
        workflow=original,
        positive_prompt="A sleek modern undercut hairstyle",
        negative_prompt="blurry, distorted, low quality",
        seed=424242,
        steps=25,
        cfg=7.5,
        sampler_name="dpmpp_2m",
        scheduler="karras",
        width=768,
        height=768,
        batch_size=1,
        filename_prefix="Custom_Test_Prefix"
    )

    # Verify original was not mutated
    assert original["11"]["inputs"]["text"] != "A sleek modern undercut hairstyle"

    # Verify positive prompt in node 11
    assert updated["11"]["inputs"]["text"] == "A sleek modern undercut hairstyle"

    # Verify negative prompt in node 28
    assert updated["28"]["inputs"]["text"] == "blurry, distorted, low quality"

    # Verify sampler inputs in node 27
    s_inputs = updated["27"]["inputs"]
    assert s_inputs["noise_seed"] == 424242
    assert s_inputs["steps"] == 25
    assert s_inputs["cfg"] == 7.5
    assert s_inputs["sampler_name"] == "dpmpp_2m"
    assert s_inputs["scheduler"] == "karras"

    # Verify latent dimensions in node 29
    l_inputs = updated["29"]["inputs"]
    assert l_inputs["width"] == 768
    assert l_inputs["height"] == 768
    assert l_inputs["batch_size"] == 1

    # Verify SaveImage prefix in node 18
    assert updated["18"]["inputs"]["filename_prefix"] == "Custom_Test_Prefix"


def test_workflow_updater_random_seed():
    """Test that seed=None generates a positive random seed."""
    original = WorkflowLoader.load("workflow/sd1.5.json")
    updated = WorkflowUpdater.update(workflow=original, seed=None)
    assert updated["27"]["inputs"]["noise_seed"] > 0


# ============================================================================
# 3. ComfyUIClient Tests
# ============================================================================

def test_api_client_submit_prompt_success():
    """Test submitting prompt workflow via mock HTTP POST."""
    client = ComfyUIClient(ComfyUIConfig(api_url="http://mock-comfyui:8188"))
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"prompt_id": "test-uuid-1234", "number": 1}

    with patch.object(client.session, "post", return_value=mock_response) as mock_post:
        prompt_id = client.submit_prompt({"node": {}})
        assert prompt_id == "test-uuid-1234"
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "http://mock-comfyui:8188/prompt" in args[0]
        assert kwargs["json"]["client_id"] == client.client_id


def test_api_client_submit_prompt_node_error():
    """Test that ComfyUI node validation errors raise ComfyUIExecutionError."""
    client = ComfyUIClient(ComfyUIConfig(api_url="http://mock-comfyui:8188"))
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "node_errors": {"27": ["Invalid checkpoint name"]}
    }

    with patch.object(client.session, "post", return_value=mock_response):
        with pytest.raises(ComfyUIExecutionError) as exc_info:
            client.submit_prompt({"node": {}})
        assert "node validation error" in str(exc_info.value)


def test_api_client_fetch_image_bytes():
    """Test downloading binary image data via mock /view endpoint."""
    client = ComfyUIClient(ComfyUIConfig(api_url="http://mock-comfyui:8188"))
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"fake_png_binary_data_12345"

    with patch.object(client.session, "get", return_value=mock_response) as mock_get:
        img_bytes = client.fetch_image_bytes("test_image.png")
        assert img_bytes == b"fake_png_binary_data_12345"
        mock_get.assert_called_once()


# ============================================================================
# 4. JobPoller Tests
# ============================================================================

def test_job_poller_success():
    """Test job poller successfully awaits completion."""
    client = ComfyUIClient(ComfyUIConfig(api_url="http://mock-comfyui:8188"))
    poller = JobPoller(client=client, poll_interval=0.01, timeout=2.0)

    mock_history = {
        "job-1": {
            "status": {"completed": True, "status_str": "success"},
            "outputs": {"18": {"images": [{"filename": "out.png", "subfolder": "", "type": "output"}]}}
        }
    }

    with patch.object(client, "get_history", return_value=mock_history):
        result = poller.wait_for_completion("job-1")
        assert result["status"]["completed"] is True


def test_job_poller_timeout():
    """Test job poller raises ComfyUITimeoutError on timeout."""
    client = ComfyUIClient(ComfyUIConfig(api_url="http://mock-comfyui:8188"))
    poller = JobPoller(client=client, poll_interval=0.01, timeout=0.05)

    # Empty history simulates ongoing processing
    with patch.object(client, "get_history", return_value={}):
        with pytest.raises(ComfyUITimeoutError):
            poller.wait_for_completion("job-timeout")


def test_job_poller_execution_error():
    """Test job poller detects node execution error."""
    client = ComfyUIClient(ComfyUIConfig(api_url="http://mock-comfyui:8188"))
    poller = JobPoller(client=client, poll_interval=0.01, timeout=2.0)

    mock_history = {
        "job-err": {
            "status": {
                "completed": False,
                "messages": [["execution_error", {"node_id": "27", "exception_type": "CUDA out of memory"}]]
            }
        }
    }

    with patch.object(client, "get_history", return_value=mock_history):
        with pytest.raises(ComfyUIExecutionError):
            poller.wait_for_completion("job-err")


# ============================================================================
# 5. OutputParser Tests
# ============================================================================

def test_output_parser_extracts_image():
    """Test parsing outputs and downloading primary image."""
    client = ComfyUIClient(ComfyUIConfig(api_url="http://mock-comfyui:8188"))
    parser = OutputParser(client)

    prompt_info = {
        "outputs": {
            "18": {
                "images": [
                    {"filename": "rendered_hair.png", "subfolder": "test_folder", "type": "output"}
                ]
            }
        }
    }

    with patch.object(client, "fetch_image_bytes", return_value=b"test_image_bytes"):
        data = parser.get_primary_image_bytes(prompt_info)
        assert data == b"test_image_bytes"


def test_output_parser_missing_images():
    """Test that empty outputs raise MissingOutputImageError."""
    client = ComfyUIClient(ComfyUIConfig(api_url="http://mock-comfyui:8188"))
    parser = OutputParser(client)

    prompt_info = {"outputs": {}}
    with pytest.raises(MissingOutputImageError):
        parser.get_primary_image_bytes(prompt_info)


# ============================================================================
# 6. ComfyUIModel End-to-End & Factory Integration Tests
# ============================================================================

def test_comfyui_model_generate_preview_mocked():
    """Test end-to-end preview generation through ComfyUIModel with mocked API."""
    model = ComfyUIModel(workflow_path="workflow/sd1.5.json")

    mock_history = {
        "job-mock-999": {
            "status": {"completed": True, "status_str": "success"},
            "outputs": {
                "18": {
                    "images": [{"filename": "style_out.png", "subfolder": "", "type": "output"}]
                }
            }
        }
    }

    with patch.object(model.client, "submit_prompt", return_value="job-mock-999"), \
         patch.object(model.client, "get_history", return_value=mock_history), \
         patch.object(model.client, "fetch_image_bytes", return_value=b"mocked_tryon_image_bytes"):

        result = model.generate_preview(
            user_image_path="test.jpg",
            hairstyle_data={"name": "Textured Crop", "category": "modern"},
            face_shape="oval",
            prompt_data={
                "positive_prompt": "100% Identity-Preserved Hair Style Try-On: Textured Crop",
                "negative_prompt": "blurry, low quality"
            }
        )

        assert result["success"] is True
        assert result["preview_bytes"] == b"mocked_tryon_image_bytes"
        assert result["job_id"] == "job-mock-999"
        assert result["model_version"] == "ComfyUI/SD1.5"


def test_tryon_model_factory_integration():
    """Test that TryonModelFactory creates ComfyUIModel as default or by name."""
    provider_default = TryonModelFactory.get_provider("comfyui")
    assert isinstance(provider_default, ComfyUIModel)

    provider_alias = TryonModelFactory.get_provider("sd1.5")
    assert isinstance(provider_alias, ComfyUIModel)


def test_tryon_service_uses_comfyui():
    """Test that TryonService instantiates ComfyUI provider when requested."""
    from server.services.tryon_service import TryonService
    service = TryonService(provider_type="comfyui")
    assert isinstance(service.provider, ComfyUIModel)

