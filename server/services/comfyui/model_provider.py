"""
ComfyUI Model Provider.
Implements the BaseTryonModel interface to integrate ComfyUI seamlessly into the
StyleAI hairstyle try-on pipeline with dynamic workflow loading, parameter updating,
asynchronous job execution, polling, and output retrieval.
"""

import time
import logging
from typing import Dict, Any, Optional

from server.services.comfyui.config import ComfyUIConfig
from server.services.comfyui.workflow_loader import WorkflowLoader
from server.services.comfyui.workflow_updater import WorkflowUpdater
from server.services.comfyui.api_client import ComfyUIClient
from server.services.comfyui.job_poller import JobPoller
from server.services.comfyui.output_parser import OutputParser
from server.services.comfyui.exceptions import ComfyUIError

logger = logging.getLogger("ComfyUI.ModelProvider")


class ComfyUIModel:
    """
    ComfyUI implementation of the virtual try-on generator.
    Coordinates workflow loading, dynamic parameter injection, asynchronous execution,
    polling, and image retrieval while adhering to BaseTryonModel contract.
    """

    MODEL_NAME = "ComfyUI/SD1.5"

    def __init__(
        self,
        config: Optional[ComfyUIConfig] = None,
        workflow_path: Optional[str] = None,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        overrides = {}
        if workflow_path:
            overrides["workflow_path"] = workflow_path
        if api_url:
            overrides["api_url"] = api_url
        if api_key:
            overrides["api_key"] = api_key

        self.config = config or ComfyUIConfig.from_env(**overrides)
        self.model_name = self.MODEL_NAME

        # Modular components
        self.client = ComfyUIClient(self.config)
        self.poller = JobPoller(
            client=self.client,
            poll_interval=self.config.poll_interval,
            timeout=self.config.timeout
        )
        self.parser = OutputParser(self.client)

    def generate_preview(
        self,
        user_image_path: str,
        hairstyle_data: Dict[str, Any],
        face_shape: str,
        prompt_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute image generation workflow via ComfyUI.

        Args:
            user_image_path: Path to user's face portrait.
            hairstyle_data: Dictionary containing hairstyle attributes.
            face_shape: Recognized face shape.
            prompt_data: Dict with positive_prompt, negative_prompt, and optional overrides.

        Returns:
            dict: {
                'success': bool,
                'preview_bytes': bytes (if success),
                'model_version': str,
                'error': str (if failed)
            }
        """
        start_time = time.time()
        logger.info(f"Starting ComfyUI generation using workflow: '{self.config.workflow_path}'")

        try:
            # 1. Dynamically load workflow JSON
            workflow_graph = WorkflowLoader.load(self.config.workflow_path)

            # 2. Extract prompts and parameters from prompt_data
            positive_prompt = prompt_data.get("positive_prompt") or prompt_data.get("prompt", "")
            negative_prompt = prompt_data.get("negative_prompt", "")

            # Runtime hyperparameters (use prompt_data overrides or config defaults)
            seed = prompt_data.get("seed")
            steps = prompt_data.get("steps", self.config.default_steps)
            cfg = prompt_data.get("cfg", self.config.default_cfg)
            sampler_name = prompt_data.get("sampler_name", self.config.default_sampler_name)
            scheduler = prompt_data.get("scheduler", self.config.default_scheduler)
            width = prompt_data.get("width", self.config.default_width)
            height = prompt_data.get("height", self.config.default_height)
            batch_size = prompt_data.get("batch_size", self.config.default_batch_size)
            filename_prefix = prompt_data.get("filename_prefix", "ComfyUI_TryOn")

            # 3. Update workflow at runtime
            updated_workflow = WorkflowUpdater.update(
                workflow=workflow_graph,
                positive_prompt=positive_prompt,
                negative_prompt=negative_prompt,
                seed=seed,
                steps=steps,
                cfg=cfg,
                sampler_name=sampler_name,
                scheduler=scheduler,
                width=width,
                height=height,
                batch_size=batch_size,
                filename_prefix=filename_prefix
            )

            # 4. Submit workflow to ComfyUI API
            prompt_id = self.client.submit_prompt(updated_workflow)

            # 5. Poll status until job completion
            prompt_info = self.poller.wait_for_completion(prompt_id)

            # 6. Parse outputs and download rendered image
            image_bytes = self.parser.get_primary_image_bytes(prompt_info)

            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.info(f"ComfyUI generation completed successfully in {elapsed_ms}ms (Job ID: {prompt_id})")

            return {
                "success": True,
                "preview_bytes": image_bytes,
                "model_version": self.model_name,
                "job_id": prompt_id,
                "processing_time_ms": elapsed_ms
            }

        except ComfyUIError as err:
            logger.error(f"ComfyUI error during preview generation: {err}")
            return {
                "success": False,
                "error": f"ComfyUI Error: {str(err)}",
                "model_version": self.model_name
            }
        except Exception as err:
            logger.exception(f"Unexpected error during ComfyUI preview generation: {err}")
            return {
                "success": False,
                "error": f"Internal Error: {str(err)}",
                "model_version": self.model_name
            }
