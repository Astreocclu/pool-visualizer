"""
Pipeline Step Registry - Maps step types to handler functions.

Usage:
    from api.services.pipeline_registry import execute_step, get_handler

    result = execute_step('cleanup', step_config, context)
"""
import logging
from typing import Dict, Any, Callable, Optional
from PIL import Image

from api.services.reference_service import get_reference_image

logger = logging.getLogger(__name__)


# Type alias for step handlers
StepHandler = Callable[[str, Dict[str, Any], Dict[str, Any]], Dict[str, Any]]


def cleanup_handler(
    step_name: str,
    step_config: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Handler for cleanup steps.

    Context expected:
        - visualizer: ScreenVisualizer instance
        - image: Current PIL Image
        - prompts: Prompts module

    Returns:
        - image: Cleaned image
    """
    visualizer = context['visualizer']
    image = context['image']
    prompts = context['prompts']

    cleanup_prompt = prompts.get_cleanup_prompt()
    clean_image = visualizer._call_gemini_edit(image, cleanup_prompt, step_name=step_name)

    logger.info(f"Pipeline Step: {step_name} complete.")
    return {'image': clean_image, 'clean_image': clean_image}


def insertion_handler(
    step_name: str,
    step_config: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Handler for insertion steps (screens, pools, etc).

    Context expected:
        - visualizer: ScreenVisualizer instance
        - image: Current PIL Image
        - prompts: Prompts module
        - scope: Dict of enabled features
        - options: Product options (color, mesh_type, etc)

    Returns:
        - image: Image with insertion, or unchanged if scope not enabled
    """
    visualizer = context['visualizer']
    image = context['image']
    prompts = context['prompts']
    scope = context.get('scope', {})
    options = context.get('options', {})

    scope_key = step_config.get('scope_key')

    # Skip if scope not enabled for this step
    if scope_key and not scope.get(scope_key, False):
        logger.info(f"Pipeline Step: {step_name} skipped (scope not enabled)")
        return {'image': image}

    feature_name = step_config.get('feature_name', step_name)

    # Get insertion prompt using standard interface
    if not hasattr(prompts, 'get_insertion_prompt'):
        raise ValueError(
            f"Prompts module missing get_insertion_prompt(). "
            f"Each tenant's prompts.py must implement this function."
        )
    prompt = prompts.get_insertion_prompt(feature_name, options)

    result_image = visualizer._call_gemini_edit(image, prompt, step_name=step_name)

    logger.info(f"Pipeline Step: {step_name} complete.")
    return {'image': result_image}


def quality_check_handler(
    step_name: str,
    step_config: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Handler for quality check steps.

    Context expected:
        - visualizer: ScreenVisualizer instance
        - clean_image: Reference clean image
        - image: Current/final PIL Image
        - prompts: Prompts module
        - scope: Dict of enabled features

    Returns:
        - score: Quality score 0-1
        - reason: Explanation string
    """
    visualizer = context['visualizer']
    clean_image = context.get('clean_image', context['image'])
    current_image = context['image']
    prompts = context['prompts']
    scope = context.get('scope')

    quality_prompt = prompts.get_quality_check_prompt(scope)

    # Pass both clean (reference) and current (final) images
    quality_result = visualizer._call_gemini_json(
        [clean_image, current_image],
        quality_prompt
    )

    score = quality_result.get('score', 0.95)
    reason = quality_result.get('reason', 'AI quality check completed.')

    logger.info(f"Quality Check: Score={score}, Reason={reason}")
    return {'score': score, 'reason': reason}


def reference_insertion_handler(
    step_name: str,
    step_config: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Handler for reference-based insertion steps.

    Uses reference images from ReferenceImage model if available,
    falls back to text-only insertion if not found.

    Context expected:
        - visualizer: ScreenVisualizer instance
        - image: Current PIL Image (cleaned)
        - prompts: Prompts module
        - scope: Dict of enabled features
        - options: Product options (color, mesh_type, etc)
        - tenant_id: Current tenant identifier

    Step config expected:
        - scope_key: Key in scope dict to check
        - feature_name: Name of feature for prompt
        - reference_category: Which option category to use for reference lookup

    Returns:
        - image: Image with insertion
    """
    visualizer = context['visualizer']
    image = context['image']
    prompts = context['prompts']
    scope = context.get('scope', {})
    options = context.get('options', {})
    tenant_id = context.get('tenant_id', 'pools')

    scope_key = step_config.get('scope_key')

    # Skip if scope not enabled
    if scope_key and not scope.get(scope_key, False):
        logger.info(f"Pipeline Step: {step_name} skipped (scope not enabled)")
        return {'image': image}

    feature_name = step_config.get('feature_name', step_name)
    reference_category = step_config.get('reference_category')

    # Try to get reference image
    reference_image = None
    if reference_category and reference_category in options:
        option_value = options[reference_category]
        reference_image = get_reference_image(tenant_id, reference_category, option_value)

    if reference_image:
        # Use reference-based insertion
        logger.info(f"Pipeline Step: {step_name} using reference image for {reference_category}")

        if hasattr(prompts, 'get_reference_insertion_prompt'):
            prompt = prompts.get_reference_insertion_prompt(feature_name, options)
        else:
            # Fallback prompt for reference insertion
            prompt = f"Place the product from the reference image onto {feature_name} in this photo. Match perspective and lighting naturally."

        result_image = visualizer._call_gemini_edit_with_reference(
            image, reference_image, prompt, step_name=step_name
        )
    else:
        # Fall back to text-only insertion
        logger.info(f"Pipeline Step: {step_name} falling back to text insertion (no reference)")
        prompt = prompts.get_insertion_prompt(feature_name, options)
        result_image = visualizer._call_gemini_edit(image, prompt, step_name=step_name)

    logger.info(f"Pipeline Step: {step_name} complete.")
    return {'image': result_image}


# Registry mapping step types to handlers
STEP_HANDLERS: Dict[str, StepHandler] = {
    'cleanup': cleanup_handler,
    'insertion': insertion_handler,
    'reference_insertion': reference_insertion_handler,
    'quality_check': quality_check_handler,
}


def get_handler(step_type: str) -> Optional[StepHandler]:
    """Get handler function for a step type."""
    return STEP_HANDLERS.get(step_type)


def register_handler(step_type: str, handler: StepHandler) -> None:
    """Register a custom handler for a step type."""
    STEP_HANDLERS[step_type] = handler
    logger.info(f"Registered custom handler for step type: {step_type}")


def execute_step(
    step_name: str,
    step_config: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a pipeline step using the registered handler.

    Args:
        step_name: Name of the step
        step_config: Configuration for the step (type, feature_name, etc)
        context: Execution context (visualizer, image, prompts, etc)

    Returns:
        Handler result dict (varies by step type)

    Raises:
        ValueError: If no handler found for step type
    """
    step_type = step_config.get('type')

    if not step_type:
        raise ValueError(f"Step config missing 'type' for step: {step_name}")

    handler = get_handler(step_type)

    if not handler:
        raise ValueError(f"No handler registered for step type: {step_type}")

    return handler(step_name, step_config, context)
