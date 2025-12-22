# Testhome Visualizer Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rename pools-visualizer to testhome-visualizer, add screens tenant (from boss), port Reference Image System, fresh database on port 8000.

**Architecture:** Rename directory in place, add missing models (TenantConfig, PromptOverride, ReferenceImage), create api/services/ with reference_service.py and pipeline_registry.py, copy boss tenant as screens tenant with renamed references.

**Tech Stack:** Django 4.0, Python 3, SQLite (fresh), google-genai

---

## Task 1: Backup and Rename Directory

**Files:**
- Rename: `/home/reid/testhome/pools-visualizer/` → `/home/reid/testhome/testhome-visualizer/`

**Step 1: Verify no processes running**

Run: `lsof -i :8006 | grep python || echo "Port clear"`
Expected: "Port clear" OR list of processes to kill

**Step 2: Kill any running servers**

Run: `pkill -f "pools-visualizer" || true`
Expected: Processes killed or nothing to kill

**Step 3: Rename directory**

Run: `mv /home/reid/testhome/pools-visualizer /home/reid/testhome/testhome-visualizer`
Expected: No error

**Step 4: Verify rename**

Run: `ls -la /home/reid/testhome/testhome-visualizer/manage.py`
Expected: File exists

**Step 5: Update working directory**

Run: `cd /home/reid/testhome/testhome-visualizer && pwd`
Expected: `/home/reid/testhome/testhome-visualizer`

---

## Task 2: Add Missing Models to models.py

**Files:**
- Modify: `api/models.py`

**Step 1: Read current models.py end**

Run: `tail -50 api/models.py`
Expected: See Lead model as last model

**Step 2: Add upload helpers and new models**

Add after the Lead model class (around line 586):

```python
# =============================================================================
# WHITE-LABEL CONFIGURATION MODELS
# =============================================================================

def upload_to_reference_images(instance, filename):
    """Generate upload path for reference images."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('reference_images', instance.tenant_id, filename)


def upload_to_reference_thumbnails(instance, filename):
    """Generate upload path for reference image thumbnails."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}_thumb.{ext}"
    return os.path.join('reference_images', instance.tenant_id, 'thumbs', filename)


class TenantConfig(models.Model):
    """
    Cached tenant configuration from YAML.

    YAML files in api/tenants/{tenant}/config.yaml are the source of truth.
    This model caches the config for runtime performance and API access.
    """
    tenant_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique tenant identifier (e.g., 'screens', 'pools')"
    )
    display_name = models.CharField(
        max_length=100,
        help_text="Human-readable tenant name"
    )
    product_categories = models.JSONField(
        default=list,
        help_text="Product category definitions for dynamic forms"
    )
    pipeline_steps = models.JSONField(
        default=list,
        help_text="Ordered list of pipeline step names"
    )
    step_configs = models.JSONField(
        default=dict,
        help_text="Configuration for each pipeline step"
    )
    branding = models.JSONField(
        default=dict,
        help_text="Branding config (colors, logo path)"
    )
    config_version = models.PositiveIntegerField(
        default=1,
        help_text="Version number, incremented on sync"
    )
    synced_from_yaml_at = models.DateTimeField(
        auto_now=True,
        help_text="When config was last synced from YAML"
    )

    class Meta:
        verbose_name = "Tenant Config"
        verbose_name_plural = "Tenant Configs"

    def __str__(self):
        return f"{self.display_name} (v{self.config_version})"


class PromptOverride(models.Model):
    """
    Database override for AI prompts.

    Code prompts in api/tenants/{tenant}/prompts.py are the defaults.
    This model allows runtime override without redeployment.
    """
    tenant_id = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Tenant this override applies to"
    )
    step_name = models.CharField(
        max_length=50,
        help_text="Pipeline step name (e.g., 'cleanup', 'doors', 'quality_check')"
    )
    prompt_text = models.TextField(
        help_text="Override prompt text (supports {variable} substitution)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this override is active"
    )
    version = models.PositiveIntegerField(
        default=1,
        help_text="Version number for this override"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="User who created this override"
    )

    class Meta:
        verbose_name = "Prompt Override"
        verbose_name_plural = "Prompt Overrides"
        unique_together = ['tenant_id', 'step_name', 'version']
        ordering = ['-version']

    def __str__(self):
        status = "active" if self.is_active else "inactive"
        return f"{self.tenant_id}/{self.step_name} v{self.version} ({status})"


class ReferenceImage(models.Model):
    """
    Reference images for product options.

    These images can be uploaded by non-technical users to show
    examples of different product options (e.g., mesh colors, pool surfaces).
    """
    tenant_id = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Tenant this image belongs to"
    )
    category = models.CharField(
        max_length=50,
        help_text="Product category key (e.g., 'mesh_type', 'pool_shape')"
    )
    option_value = models.CharField(
        max_length=50,
        help_text="Option value this image represents (e.g., 'black', 'rectangle')"
    )
    image = models.ImageField(
        upload_to=upload_to_reference_images,
        help_text="Full-size reference image"
    )
    thumbnail = models.ImageField(
        upload_to=upload_to_reference_thumbnails,
        null=True,
        blank=True,
        help_text="Auto-generated thumbnail"
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional description of this reference image"
    )
    embedding = models.JSONField(
        null=True,
        blank=True,
        help_text="AI embedding vector for similarity matching (future use)"
    )
    uploaded_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="User who uploaded this image"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reference Image"
        verbose_name_plural = "Reference Images"
        unique_together = ['tenant_id', 'category', 'option_value']
        ordering = ['tenant_id', 'category', 'option_value']

    def __str__(self):
        return f"{self.tenant_id}/{self.category}/{self.option_value}"
```

**Step 3: Verify syntax**

Run: `cd /home/reid/testhome/testhome-visualizer && source venv/bin/activate && python3 -c "from api.models import TenantConfig, PromptOverride, ReferenceImage; print('Models OK')"`
Expected: "Models OK"

**Step 4: Commit**

```bash
git add api/models.py
git commit -m "feat: add TenantConfig, PromptOverride, ReferenceImage models

- TenantConfig caches tenant YAML for runtime
- PromptOverride allows runtime prompt changes
- ReferenceImage stores product reference images"
```

---

## Task 3: Create Fresh Database

**Files:**
- Delete: `db.sqlite3`
- Create: `db.sqlite3` (via migrate)

**Step 1: Delete old database**

Run: `cd /home/reid/testhome/testhome-visualizer && rm -f db.sqlite3`
Expected: No error

**Step 2: Create migrations**

Run: `cd /home/reid/testhome/testhome-visualizer && source venv/bin/activate && python3 manage.py makemigrations`
Expected: Migration created for new models

**Step 3: Apply migrations**

Run: `cd /home/reid/testhome/testhome-visualizer && source venv/bin/activate && python3 manage.py migrate`
Expected: All migrations applied

**Step 4: Create superuser**

Run: `cd /home/reid/testhome/testhome-visualizer && source venv/bin/activate && echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python3 manage.py shell`
Expected: User created

**Step 5: Commit**

```bash
git add api/migrations/
git commit -m "chore: add migration for white-label models"
```

---

## Task 4: Create api/services/ Directory and reference_service.py

**Files:**
- Create: `api/services/__init__.py`
- Create: `api/services/reference_service.py`

**Step 1: Create directory**

Run: `mkdir -p /home/reid/testhome/testhome-visualizer/api/services`
Expected: Directory created

**Step 2: Create __init__.py**

Create `api/services/__init__.py`:

```python
"""Services package for testhome-visualizer."""
```

**Step 3: Create reference_service.py**

Create `api/services/reference_service.py`:

```python
"""
Reference Image Service - Fetches reference images for product options.
"""
import logging
from typing import Dict, Optional
from PIL import Image

from api.models import ReferenceImage

logger = logging.getLogger(__name__)


def get_reference_image(
    tenant_id: str,
    category: str,
    option_value: str
) -> Optional[Image.Image]:
    """
    Fetch a reference image for a specific tenant/category/option.

    Args:
        tenant_id: Tenant identifier (e.g., 'screens', 'pools')
        category: Product category key (e.g., 'mesh_type', 'frame_color')
        option_value: Option value (e.g., 'black', 'bronze')

    Returns:
        PIL Image if found, None otherwise
    """
    ref = ReferenceImage.objects.filter(
        tenant_id=tenant_id,
        category=category,
        option_value=option_value
    ).first()

    if not ref:
        logger.debug(f"No reference image for {tenant_id}/{category}/{option_value}")
        return None

    try:
        return Image.open(ref.image.path)
    except Exception as e:
        logger.error(f"Failed to load reference image: {e}")
        return None


def get_reference_images_for_options(
    tenant_id: str,
    options: Dict[str, str]
) -> Dict[str, Image.Image]:
    """
    Fetch all reference images for a set of product options.

    Args:
        tenant_id: Tenant identifier
        options: Dict mapping category to option_value

    Returns:
        Dict mapping category to PIL Image (only includes found images)
    """
    result = {}
    for category, option_value in options.items():
        img = get_reference_image(tenant_id, category, option_value)
        if img:
            result[category] = img
    return result
```

**Step 4: Verify import**

Run: `cd /home/reid/testhome/testhome-visualizer && source venv/bin/activate && python3 -c "from api.services.reference_service import get_reference_image; print('OK')"`
Expected: "OK"

**Step 5: Commit**

```bash
git add api/services/
git commit -m "feat: add reference_service for fetching reference images

- get_reference_image() fetches single ref by tenant/category/option
- get_reference_images_for_options() fetches all refs for options dict"
```

---

## Task 5: Create pipeline_registry.py

**Files:**
- Create: `api/services/pipeline_registry.py`

**Step 1: Create pipeline_registry.py**

Create `api/services/pipeline_registry.py`:

```python
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
```

**Step 2: Verify import**

Run: `cd /home/reid/testhome/testhome-visualizer && source venv/bin/activate && python3 -c "from api.services.pipeline_registry import execute_step, STEP_HANDLERS; print(f'Handlers: {list(STEP_HANDLERS.keys())}')"`
Expected: "Handlers: ['cleanup', 'insertion', 'reference_insertion', 'quality_check']"

**Step 3: Commit**

```bash
git add api/services/pipeline_registry.py
git commit -m "feat: add pipeline_registry with step handlers

- cleanup_handler, insertion_handler, quality_check_handler
- reference_insertion_handler with fallback to text insertion
- execute_step() routes to correct handler by type"
```

---

## Task 6: Add _call_gemini_edit_with_reference to ScreenVisualizer

**Files:**
- Modify: `api/visualizer/services.py`

**Step 1: Read current services.py to find insertion point**

Run: `grep -n "_call_gemini_edit" api/visualizer/services.py | head -5`
Expected: Line numbers for _call_gemini_edit method

**Step 2: Add new method after _call_gemini_edit**

Add after the `_call_gemini_edit` method (find it first, add after its closing):

```python
    def _call_gemini_edit_with_reference(
        self,
        target_image: Image.Image,
        reference_image: Image.Image,
        prompt: str,
        step_name: str = "unknown"
    ) -> Image.Image:
        """
        Call Gemini with a reference image for compositing.

        Args:
            target_image: The cleaned customer photo
            reference_image: The reference product image to composite
            prompt: Instructions for compositing
            step_name: Name for logging

        Returns:
            PIL Image with reference composited onto target
        """
        try:
            config_args = {
                "response_modalities": ["TEXT", "IMAGE"],
            }

            if hasattr(types, 'ThinkingConfig'):
                config_args['thinking_config'] = types.ThinkingConfig(include_thoughts=True)

            if hasattr(types, 'ImageGenerationConfig'):
                config_args['image_generation_config'] = types.ImageGenerationConfig(
                    guidance_scale=70,
                    person_generation="dont_generate_people"
                )

            # Retry logic
            max_retries = 4
            for attempt in range(max_retries):
                try:
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=[reference_image, target_image, prompt],  # Reference first
                        config=types.GenerateContentConfig(**config_args)
                    )
                    break
                except Exception as e:
                    if "429" in str(e) and attempt < max_retries - 1:
                        wait_time = 10 * (attempt + 1)
                        logger.warning(f"Rate limited, waiting {wait_time}s (attempt {attempt + 1})")
                        time.sleep(wait_time)
                    else:
                        raise e

            # Log thinking if available
            self._log_thinking(step_name, prompt, response)

            # Log usage
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = response.usage_metadata
                thinking_tokens = getattr(usage, 'thoughts_token_count', 0) or 0
                total_tokens = getattr(usage, 'total_token_count', 0) or 0
                logger.info(f"Gemini Usage [{step_name}] - Thinking: {thinking_tokens}, Total: {total_tokens}")

            # Extract image from response
            result_image = None
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        result_image = Image.open(io.BytesIO(image_data))
                        break

            if result_image is None:
                raise ValueError(f"No image in Gemini response for step {step_name}")

            return result_image

        except Exception as e:
            logger.error(f"Reference edit failed for step {step_name}: {e}")
            raise
```

**Step 3: Verify method exists**

Run: `cd /home/reid/testhome/testhome-visualizer && source venv/bin/activate && python3 -c "from api.visualizer.services import ScreenVisualizer; print(hasattr(ScreenVisualizer, '_call_gemini_edit_with_reference'))"`
Expected: "True"

**Step 4: Commit**

```bash
git add api/visualizer/services.py
git commit -m "feat: add _call_gemini_edit_with_reference method

- Passes [reference, target, prompt] to Nano Banana Pro
- Same retry logic and config as _call_gemini_edit
- Reference image passed first per API docs"
```

---

## Task 7: Create Screens Tenant (Copy from Boss)

**Files:**
- Create: `api/tenants/screens/__init__.py`
- Create: `api/tenants/screens/config.py`
- Create: `api/tenants/screens/prompts.py`

**Step 1: Create screens directory**

Run: `mkdir -p /home/reid/testhome/testhome-visualizer/api/tenants/screens`
Expected: Directory created

**Step 2: Create __init__.py**

Create `api/tenants/screens/__init__.py`:

```python
"""Screens (Security Screens) tenant package."""
from .config import ScreensTenantConfig

__all__ = ['ScreensTenantConfig']
```

**Step 3: Create config.py**

Create `api/tenants/screens/config.py`:

```python
"""Security Screens tenant configuration."""
from typing import List, Tuple, Dict, Any
from ..base import BaseTenantConfig


class ScreensTenantConfig(BaseTenantConfig):

    @property
    def tenant_id(self) -> str:
        return "screens"

    @property
    def display_name(self) -> str:
        return "Security Screens"

    def get_product_schema(self) -> List[Dict[str, Any]]:
        """
        Product categories for Security Screens.

        Note: No 'opacity' category - mesh density and color determine visibility.
        """
        return [
            {
                "key": "mesh_type",
                "label": "Mesh Type",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "10x10_standard", "label": "10x10 Standard"},
                    {"value": "12x12_standard", "label": "12x12 Standard"},
                    {"value": "12x12_american", "label": "12x12 American"},
                ]
            },
            {
                "key": "frame_color",
                "label": "Frame Color",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "black", "label": "Black"},
                    {"value": "dark_bronze", "label": "Dark Bronze"},
                    {"value": "stucco", "label": "Stucco"},
                    {"value": "white", "label": "White"},
                    {"value": "almond", "label": "Almond"},
                ]
            },
            {
                "key": "mesh_color",
                "label": "Mesh Color",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "black", "label": "Black (Recommended)"},
                    {"value": "stucco", "label": "Stucco"},
                    {"value": "bronze", "label": "Bronze"},
                ]
            },
        ]

    def get_pipeline_steps(self) -> List[str]:
        # Order: doors -> windows -> patio (patio last as largest envelope)
        return ['cleanup', 'doors', 'windows', 'patio', 'quality_check']

    def get_prompts_module(self):
        from . import prompts
        return prompts

    def get_step_config(self, step_name: str) -> Dict[str, Any]:
        configs = {
            'cleanup': {
                'type': 'cleanup',
                'description': 'Cleaning',
                'progress_weight': 30
            },
            'patio': {
                'type': 'insertion',
                'feature_name': 'patio enclosure',
                'scope_key': 'patio',
                'description': 'Building Patio',
                'progress_weight': 50
            },
            'windows': {
                'type': 'insertion',
                'feature_name': 'windows',
                'scope_key': 'windows',
                'description': 'Building Windows',
                'progress_weight': 60
            },
            'doors': {
                'type': 'insertion',
                'feature_name': 'entry doors',
                'scope_key': 'doors',
                'description': 'Building Doors',
                'progress_weight': 70
            },
            'quality_check': {
                'type': 'quality_check',
                'description': 'Checking Quality',
                'progress_weight': 90
            }
        }
        return configs.get(step_name, {})
```

**Step 4: Create prompts.py**

Create `api/tenants/screens/prompts.py`:

```python
"""
Security Screens Visualizer - Prompts
-------------------------------------
Simplified, atomic prompts for the Nano Banana Pro pipeline.
Focused on visual descriptions, not physical attributes.
"""

def get_cleanup_prompt():
    """
    Step 1: The Foundation.
    Focus: Clean image and enhance to ideal sunny conditions.
    """
    return """Please clean this image of any debris, furniture, and temporary items.
Make the weather conditions ideal and sunny with clear blue sky.
Keep all permanent structures exactly as they are."""

def get_screen_insertion_prompt(feature_type: str, options: dict):
    """
    Generates a focused inpainting prompt for a specific feature.

    Args:
        feature_type (str): "windows", "patio enclosure", or "entry doors"
        options (dict): Contains 'color', 'mesh_type', etc.
    """
    # Extract options with defaults
    color = options.get('color', 'Black')
    mesh_type = options.get('mesh_type', 'Standard')

    # Map mesh density to visual opacity description
    opacity_desc = "Semi-transparent mesh"  # Default
    if "privacy" in mesh_type.lower():
        opacity_desc = "Opaque, solid block"
    elif "standard" in mesh_type.lower():
        opacity_desc = "Semi-transparent mesh"
    elif "solar" in mesh_type.lower():
        opacity_desc = "Tinted transparency"

    base_prompt = f"Photorealistic inpainting. Install {color} security screens on the {feature_type}. Render the screen material as a heavy-duty {color} mesh with {opacity_desc}. Maintain flush mounting frames. Ensure lighting and shadows interact naturally with the new mesh texture."

    if feature_type == "patio enclosure":
        base_prompt += """

In your text response, state EXACTLY:
- OPENING WIDTH: [X] feet
- MULLION COUNT: [Y]
- POSITIONS: [list]"""
        base_prompt += " IMPORTANT: Install visible vertical aluminum structural mullions (support posts) every 5 feet across the screen span - these mullions are essential and must be clearly visible."
        base_prompt += " Focus EXCLUSIVELY on enclosing the open patio/porch areas. Leave all standard windows and other openings in their original state."

    return base_prompt

def get_quality_check_prompt(scope: dict = None):
    """
    Generates a prompt for the AI to evaluate the realism and consistency.
    """
    base_prompt = """
    You are a Quality Control AI.
    Image 1 is the REFERENCE (Clean State).
    Image 2 is the FINAL RESULT (With Screens).

    Compare them and check for "hallucinations":
    1. Did windows turn into doors?
    2. Did new structural elements appear that weren't in the reference?
    3. Is the perspective consistent?
    """

    if scope and scope.get('patio'):
        base_prompt += """
    CONTEXT: The user requested a Patio Enclosure.
    - Allow filling of existing structural voids/openings with screen material.
    - Do NOT allow the removal or conversion of existing glass windows or load-bearing walls.
    """
    else:
        base_prompt += """
    CONTEXT: Standard Screen Installation.
    - Any structural change (window->door, new opening) is a HALLUCINATION.
    """

    if scope and not scope.get('windows'):
        base_prompt += """
    NEGATIVE CONSTRAINT: Windows were NOT requested.
    - Verify that standard windows remain untouched/unscreened.
    - If unrequested window screens are present, score MUST be below 0.5.
    """

    base_prompt += """
    Rate the quality on a scale of 0.0 to 1.0.
    - If forbidden hallucinations exist, score MUST be below 0.5.
    - If photorealism is poor, score MUST be below 0.7.

    Return ONLY a JSON object with the following structure:
    {
        "score": float,
        "reason": "string"
    }
    """
    return base_prompt

def get_insertion_prompt(feature_type: str, options: dict) -> str:
    """
    Generic insertion prompt interface for pipeline_registry.
    Routes to the existing get_screen_insertion_prompt.
    """
    return get_screen_insertion_prompt(feature_type, options)

def get_reference_insertion_prompt(feature_type: str, options: dict) -> str:
    """
    Generate prompt for reference-based insertion.
    Uses contractor's reference image as the visual guide.
    """
    color = options.get('color', options.get('mesh_color', 'Black'))

    return f"""You are given TWO images:
1. REFERENCE IMAGE (first): Shows the exact {feature_type} product to install
2. TARGET IMAGE (second): Customer's home photo

TASK: Install the {feature_type} from the reference image onto the appropriate locations in the target image.

REQUIREMENTS:
- Match the exact appearance, color ({color}), and style from the reference
- Adjust perspective and scale to fit naturally in the target
- Maintain realistic lighting and shadows
- Keep the installation looking professional and flush-mounted
- Do NOT add the reference product to inappropriate locations

OUTPUT: A photorealistic composite showing the reference product installed on the customer's home."""
```

**Step 5: Verify tenant loads**

Run: `cd /home/reid/testhome/testhome-visualizer && source venv/bin/activate && python3 -c "from api.tenants.screens.config import ScreensTenantConfig; c = ScreensTenantConfig(); print(c.tenant_id, c.display_name)"`
Expected: "screens Security Screens"

**Step 6: Commit**

```bash
git add api/tenants/screens/
git commit -m "feat: add screens tenant (security screens)

- ScreensTenantConfig with mesh/frame/color options
- Pipeline: cleanup -> doors -> windows -> patio -> quality_check
- Prompts for screen insertion and reference compositing"
```

---

## Task 8: Register Screens Tenant

**Files:**
- Modify: `api/tenants/__init__.py`

**Step 1: Read current registry**

Run: `cat api/tenants/__init__.py`
Expected: See current tenant registrations

**Step 2: Add screens tenant import and registration**

Add to the imports section:
```python
from .screens.config import ScreensTenantConfig
```

Add to the registration section (after other tenants):
```python
register_tenant(ScreensTenantConfig())
```

**Step 3: Verify all tenants registered**

Run: `cd /home/reid/testhome/testhome-visualizer && source venv/bin/activate && python3 -c "from api.tenants import TENANT_REGISTRY; print(list(TENANT_REGISTRY.keys()))"`
Expected: List includes 'screens' along with pools, windows, roofs

**Step 4: Commit**

```bash
git add api/tenants/__init__.py
git commit -m "feat: register screens tenant in registry"
```

---

## Task 9: Update Django Admin for ReferenceImage

**Files:**
- Modify: `api/admin.py`

**Step 1: Read current admin.py**

Run: `cat api/admin.py`
Expected: See current admin registrations

**Step 2: Add ReferenceImage admin**

Add imports:
```python
from django.utils.html import format_html
from .models import ReferenceImage
```

Add admin class:
```python
@admin.register(ReferenceImage)
class ReferenceImageAdmin(admin.ModelAdmin):
    """Admin interface for managing reference images."""

    list_display = (
        'tenant_id',
        'category',
        'option_value',
        'thumbnail_preview',
        'description',
        'uploaded_at',
    )
    list_filter = ('tenant_id', 'category')
    search_fields = ('option_value', 'description')
    readonly_fields = ('thumbnail_preview', 'uploaded_at')

    fieldsets = (
        ('Reference Details', {
            'fields': ('tenant_id', 'category', 'option_value')
        }),
        ('Image', {
            'fields': ('image', 'thumbnail', 'thumbnail_preview')
        }),
        ('Metadata', {
            'fields': ('description', 'uploaded_by', 'uploaded_at')
        }),
    )

    def thumbnail_preview(self, obj):
        """Display thumbnail in admin list and detail views."""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: contain;" />',
                obj.thumbnail.url
            )
        elif obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: contain;" />',
                obj.image.url
            )
        return "-"

    thumbnail_preview.short_description = "Preview"
```

**Step 3: Verify admin loads**

Run: `cd /home/reid/testhome/testhome-visualizer && source venv/bin/activate && python3 manage.py check`
Expected: "System check identified no issues."

**Step 4: Commit**

```bash
git add api/admin.py
git commit -m "feat: add ReferenceImage to Django admin

- List view with tenant, category, option, thumbnail
- Filter by tenant and category
- Inline thumbnail preview"
```

---

## Task 10: Update Port Configuration

**Files:**
- Modify: `frontend/src/services/api.js`
- Modify: `CLAUDE.md`

**Step 1: Update frontend API port**

Find and replace in `frontend/src/services/api.js`:
- Change `8006` to `8000`
- Change `3006` to `3000` (frontend port)

**Step 2: Update CLAUDE.md**

Update all port references:
- Backend: 8006 → 8000
- Frontend: 3006 → 3000

**Step 3: Verify frontend config**

Run: `grep -n "800" frontend/src/services/api.js`
Expected: Show 8000 not 8006

**Step 4: Commit**

```bash
git add frontend/src/services/api.js CLAUDE.md
git commit -m "chore: update ports to 8000/3000

- Backend: 8006 -> 8000
- Frontend: 3006 -> 3000"
```

---

## Task 11: Update Parent CLAUDE.md

**Files:**
- Modify: `/home/reid/testhome/CLAUDE.md`

**Step 1: Update projects table**

Change pools-visualizer entry to:
```markdown
| [testhome-visualizer](./testhome-visualizer/) | 8000 | db.sqlite3 | Active |
```

Remove or archive boss-security-visualizer entry.

**Step 2: Update Quick Start section**

Update the testhome-visualizer commands:
```bash
# Testhome Visualizer
cd testhome-visualizer
source venv/bin/activate
python3 manage.py runserver 8000
```

**Step 3: Commit (in testhome-visualizer)**

Note: This file is outside the repo, so just edit it manually.

---

## Task 12: Archive Boss Security Visualizer

**Files:**
- Create: `/home/reid/testhome/boss-security-visualizer/ARCHIVED.md`

**Step 1: Create archive notice**

Create `/home/reid/testhome/boss-security-visualizer/ARCHIVED.md`:

```markdown
# ARCHIVED

This project has been archived as of 2025-12-22.

## Why Archived
The functionality has been migrated to **testhome-visualizer** as the "screens" tenant.

## Where to Find the Code
- **New location:** `/home/reid/testhome/testhome-visualizer/`
- **Screens tenant:** `api/tenants/screens/`

## Do Not Use
This codebase is kept for reference only. All new development should happen in testhome-visualizer.
```

**Step 2: No commit needed (different repo)**

---

## Task 13: Final Verification

**Step 1: Run Django checks**

Run: `cd /home/reid/testhome/testhome-visualizer && source venv/bin/activate && python3 manage.py check`
Expected: "System check identified no issues."

**Step 2: Run migrations check**

Run: `cd /home/reid/testhome/testhome-visualizer && source venv/bin/activate && python3 manage.py showmigrations`
Expected: All migrations applied [X]

**Step 3: Verify all tenants**

Run: `cd /home/reid/testhome/testhome-visualizer && source venv/bin/activate && python3 -c "from api.tenants import TENANT_REGISTRY; [print(f'{k}: {v.display_name}') for k,v in TENANT_REGISTRY.items()]"`
Expected: pools, screens, windows, roofs all listed

**Step 4: Start backend**

Run: `cd /home/reid/testhome/testhome-visualizer && source venv/bin/activate && python3 manage.py runserver 8000`
Expected: Server starts on port 8000

**Step 5: Verify admin accessible**

Visit: http://localhost:8000/admin/
Login: admin / admin
Expected: Can see Reference Images section

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Rename directory | pools-visualizer → testhome-visualizer |
| 2 | Add models | TenantConfig, PromptOverride, ReferenceImage |
| 3 | Fresh database | Delete db.sqlite3, migrate |
| 4 | Reference service | api/services/reference_service.py |
| 5 | Pipeline registry | api/services/pipeline_registry.py |
| 6 | Visualizer method | _call_gemini_edit_with_reference |
| 7 | Screens tenant | api/tenants/screens/* |
| 8 | Register tenant | api/tenants/__init__.py |
| 9 | Admin UI | ReferenceImageAdmin |
| 10 | Port config | 8006→8000, 3006→3000 |
| 11 | Parent docs | testhome/CLAUDE.md |
| 12 | Archive boss | ARCHIVED.md |
| 13 | Verification | Django checks, server test |

**Total: 13 tasks**
