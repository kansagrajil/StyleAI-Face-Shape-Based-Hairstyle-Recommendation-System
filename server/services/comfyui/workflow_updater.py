"""
ComfyUI Workflow Parameter Updater.
Modifies workflow node inputs at runtime before job submission (positive/negative prompts,
seed, steps, CFG scale, sampler, scheduler, dimensions, batch size, etc.).
"""

import copy
import random
import logging
from typing import Dict, Any, Optional

from server.services.comfyui.exceptions import InvalidWorkflowError

logger = logging.getLogger("ComfyUI.WorkflowUpdater")


class WorkflowUpdater:
    """Updates ComfyUI graph node inputs dynamically with runtime parameters."""

    @staticmethod
    def _generate_seed() -> int:
        """Generate a random 64-bit integer seed."""
        return random.randint(1, 1125899906842624)

    @classmethod
    def update(
        cls,
        workflow: Dict[str, Any],
        positive_prompt: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        steps: Optional[int] = None,
        cfg: Optional[float] = None,
        sampler_name: Optional[str] = None,
        scheduler: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        batch_size: Optional[int] = None,
        filename_prefix: Optional[str] = None,
        ckpt_name: Optional[str] = None,
        **extra_inputs
    ) -> Dict[str, Any]:
        """
        Produce a modified copy of the workflow with updated runtime parameters.

        Args:
            workflow: Original workflow dict.
            positive_prompt: Text description for positive conditioning.
            negative_prompt: Text description for negative conditioning.
            seed: Seed integer (-1 or None for random).
            steps: Diffusion step count.
            cfg: Classifier-Free Guidance scale.
            sampler_name: Name of sampler (e.g. 'euler', 'dpmpp_2m').
            scheduler: Name of scheduler (e.g. 'simple', 'karras').
            width: Latent image width.
            height: Latent image height.
            batch_size: Number of images per batch.
            filename_prefix: Prefix for output files.
            ckpt_name: Optional checkpoint filename override.

        Returns:
            New dictionary representing updated workflow.
        """
        if not isinstance(workflow, dict) or not workflow:
            raise InvalidWorkflowError("Cannot update an empty or invalid workflow.")

        updated = copy.deepcopy(workflow)

        # 1. Locate primary sampler node (KSampler or KSamplerAdvanced)
        sampler_node_id = None
        sampler_node = None
        for nid, node in updated.items():
            if isinstance(node, dict) and node.get("class_type") in ("KSampler", "KSamplerAdvanced"):
                sampler_node_id = nid
                sampler_node = node
                break

        # 2. Determine positive and negative prompt node IDs
        pos_node_id = None
        neg_node_id = None

        if sampler_node and "inputs" in sampler_node:
            s_inputs = sampler_node["inputs"]
            if "positive" in s_inputs and isinstance(s_inputs["positive"], (list, tuple)) and len(s_inputs["positive"]) > 0:
                pos_node_id = str(s_inputs["positive"][0])
            if "negative" in s_inputs and isinstance(s_inputs["negative"], (list, tuple)) and len(s_inputs["negative"]) > 0:
                neg_node_id = str(s_inputs["negative"][0])

        # Fallback search by class_type if not found via sampler connection
        if not pos_node_id or not neg_node_id:
            clip_nodes = [
                nid for nid, node in updated.items()
                if isinstance(node, dict) and node.get("class_type") == "CLIPTextEncode"
            ]
            if not pos_node_id and len(clip_nodes) > 0:
                pos_node_id = clip_nodes[0]
            if not neg_node_id and len(clip_nodes) > 1:
                neg_node_id = clip_nodes[1]

        # 3. Apply Positive Prompt
        if positive_prompt is not None and pos_node_id and pos_node_id in updated:
            updated[pos_node_id].setdefault("inputs", {})["text"] = str(positive_prompt)
            logger.debug(f"Updated positive prompt in node {pos_node_id}")

        # 4. Apply Negative Prompt
        if negative_prompt is not None and neg_node_id and neg_node_id in updated:
            updated[neg_node_id].setdefault("inputs", {})["text"] = str(negative_prompt)
            logger.debug(f"Updated negative prompt in node {neg_node_id}")

        # 5. Apply Sampler settings (seed, steps, cfg, sampler_name, scheduler)
        if sampler_node:
            s_inputs = sampler_node.setdefault("inputs", {})

            # Seed
            actual_seed = cls._generate_seed() if (seed is None or seed < 0) else int(seed)
            if "noise_seed" in s_inputs:
                s_inputs["noise_seed"] = actual_seed
            elif "seed" in s_inputs:
                s_inputs["seed"] = actual_seed
            else:
                s_inputs["noise_seed"] = actual_seed

            if steps is not None:
                s_inputs["steps"] = int(steps)
            if cfg is not None:
                s_inputs["cfg"] = float(cfg)
            if sampler_name is not None:
                s_inputs["sampler_name"] = str(sampler_name)
            if scheduler is not None:
                s_inputs["scheduler"] = str(scheduler)

            logger.debug(
                f"Updated sampler node {sampler_node_id}: seed={actual_seed}, "
                f"steps={s_inputs.get('steps')}, cfg={s_inputs.get('cfg')}, "
                f"sampler={s_inputs.get('sampler_name')}, scheduler={s_inputs.get('scheduler')}"
            )

        # 6. Apply Latent Dimensions & Batch Size (EmptyLatentImage)
        for nid, node in updated.items():
            if isinstance(node, dict) and node.get("class_type") == "EmptyLatentImage":
                l_inputs = node.setdefault("inputs", {})
                if width is not None:
                    l_inputs["width"] = int(width)
                if height is not None:
                    l_inputs["height"] = int(height)
                if batch_size is not None:
                    l_inputs["batch_size"] = int(batch_size)
                logger.debug(
                    f"Updated latent node {nid}: width={l_inputs.get('width')}, "
                    f"height={l_inputs.get('height')}, batch_size={l_inputs.get('batch_size')}"
                )

        # 7. Apply Checkpoint Override if provided
        if ckpt_name:
            for nid, node in updated.items():
                if isinstance(node, dict) and node.get("class_type") == "CheckpointLoaderSimple":
                    node.setdefault("inputs", {})["ckpt_name"] = str(ckpt_name)
                    logger.debug(f"Updated checkpoint loader node {nid} to {ckpt_name}")

        # 8. Apply Output Filename Prefix
        prefix = filename_prefix or "ComfyUI"
        for nid, node in updated.items():
            if isinstance(node, dict) and node.get("class_type") == "SaveImage":
                node.setdefault("inputs", {})["filename_prefix"] = prefix
                logger.debug(f"Updated SaveImage node {nid} prefix: {prefix}")

        # 9. Apply any extra custom node input overrides
        for key, val in extra_inputs.items():
            # Format node_id.input_name = val
            if "." in key:
                target_nid, target_input = key.split(".", 1)
                if target_nid in updated and "inputs" in updated[target_nid]:
                    updated[target_nid]["inputs"][target_input] = val

        return updated
