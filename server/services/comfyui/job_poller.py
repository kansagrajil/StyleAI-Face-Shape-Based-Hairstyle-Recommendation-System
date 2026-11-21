"""
ComfyUI Job Poller.
Monitors workflow execution progress asynchronously via polling until completion or timeout.
"""

import time
import logging
from typing import Dict, Any, Optional

from server.services.comfyui.api_client import ComfyUIClient
from server.services.comfyui.exceptions import (
    ComfyUITimeoutError,
    ComfyUIExecutionError
)

logger = logging.getLogger("ComfyUI.JobPoller")


class JobPoller:
    """Polls ComfyUI job execution status and awaits completion."""

    def __init__(self, client: ComfyUIClient, poll_interval: float = 1.0, timeout: float = 180.0):
        self.client = client
        self.poll_interval = max(0.2, poll_interval)
        self.timeout = timeout

    def wait_for_completion(self, prompt_id: str) -> Dict[str, Any]:
        """
        Poll ComfyUI /history/{prompt_id} until the job completes, fails, or times out.

        Args:
            prompt_id: The job identifier returned from submit_prompt.

        Returns:
            Dict containing the completed prompt entry from /history response.

        Raises:
            ComfyUITimeoutError: When execution exceeds the timeout limit.
            ComfyUIExecutionError: When a node execution fails in ComfyUI.
        """
        start_time = time.time()
        logger.info(
            f"Starting polling for Job ID: {prompt_id} "
            f"(interval={self.poll_interval}s, timeout={self.timeout}s)"
        )

        while True:
            elapsed = time.time() - start_time
            if elapsed > self.timeout:
                logger.error(
                    f"Job ID {prompt_id} timed out after {elapsed:.1f}s (timeout={self.timeout}s)"
                )
                raise ComfyUITimeoutError(
                    f"ComfyUI generation for Job ID '{prompt_id}' timed out after {elapsed:.1f}s"
                )

            try:
                history_data = self.client.get_history(prompt_id)
            except Exception as e:
                logger.warning(f"Transient error querying history for {prompt_id}: {e}")
                time.sleep(self.poll_interval)
                continue

            # Check if prompt_id is present in history
            if prompt_id in history_data:
                prompt_info = history_data[prompt_id]
                status_info = prompt_info.get("status", {})
                completed = status_info.get("completed", False)
                status_str = status_info.get("status_str", "")

                # Check for execution failure messages
                messages = status_info.get("messages", [])
                for msg in messages:
                    if isinstance(msg, list) and len(msg) > 0 and msg[0] == "execution_error":
                        err_details = msg[1] if len(msg) > 1 else "Unknown execution error"
                        logger.error(f"ComfyUI job {prompt_id} encountered execution error: {err_details}")
                        raise ComfyUIExecutionError(f"ComfyUI execution error: {err_details}")

                if completed or status_str == "success":
                    logger.info(
                        f"Job ID {prompt_id} completed successfully in {elapsed:.1f}s "
                        f"(status='{status_str}')"
                    )
                    return prompt_info

            logger.debug(f"Job ID {prompt_id} still processing... (elapsed: {elapsed:.1f}s)")
            time.sleep(self.poll_interval)
