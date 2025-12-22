# Reference Image System - All Tenants Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add optional Reference Image System support to all tenants (pools, windows, roofs, screens)

**Architecture:** Add opt-in flag to BaseTenantConfig, add `get_reference_insertion_prompt()` to each tenant's prompts.py. Pipeline checks flag at runtime.

**Tech Stack:** Django, Python, existing tenant system

---

## Task 1: Add opt-in flag to BaseTenantConfig

**Files:**
- Modify: `api/tenants/base.py`

**Step 1: Add the flag**

Add class attribute after the class docstring:

```python
class BaseTenantConfig(ABC):
    """Base class all tenant configs must implement."""

    # Opt-in for Reference Image System
    supports_reference_images: bool = False
```

**Step 2: Verify**

Run: `cd /home/reid/command-center/testhome/testhome-visualizer && source venv/bin/activate && python3 manage.py check`
Expected: "System check identified no issues"

**Step 3: Commit**

```bash
git add api/tenants/base.py
git commit -m "feat(tenants): add supports_reference_images opt-in flag to BaseTenantConfig"
```

---

## Task 2: Add get_reference_insertion_prompt to pools tenant

**Files:**
- Modify: `api/tenants/pools/prompts.py`
- Modify: `api/tenants/pools/config.py`

**Step 1: Add prompt function to prompts.py**

Add at the end of the file:

```python
def get_reference_insertion_prompt(feature_type: str, options: dict) -> str:
    """
    Generate prompt for reference-based insertion.
    Uses contractor's reference image as the visual guide.
    """
    # Get relevant option for this feature
    if feature_type == 'pool':
        product_desc = f"{options.get('pool_shape', 'rectangular')} pool with {options.get('interior_finish', 'plaster')} finish"
    elif feature_type == 'deck':
        product_desc = f"{options.get('deck_material', 'travertine')} deck in {options.get('deck_color', 'cream')}"
    else:
        product_desc = feature_type

    return f"""You are given TWO images:
1. REFERENCE IMAGE (first): Shows the exact {feature_type} product to install
2. TARGET IMAGE (second): Customer's backyard photo

TASK: Install the {feature_type} from the reference image into the target backyard.

PRODUCT DETAILS: {product_desc}

REQUIREMENTS:
- Match the exact appearance and style from the reference
- Adjust perspective and scale to fit naturally in the target
- Maintain realistic lighting, shadows, and reflections
- Keep the installation looking professional
- Blend seamlessly with existing landscaping

OUTPUT: A photorealistic composite showing the reference product installed in the customer's backyard."""
```

**Step 2: Enable flag in config.py**

Add after the class definition line in PoolsTenantConfig:

```python
class PoolsTenantConfig(BaseTenantConfig):
    """Pools vertical tenant configuration."""

    supports_reference_images = True  # Add this line
    tenant_id = 'pools'
```

**Step 3: Verify**

Run: `source venv/bin/activate && python3 manage.py shell -c "from api.tenants.pools.prompts import get_reference_insertion_prompt; print(get_reference_insertion_prompt('pool', {'pool_shape': 'kidney'}))"`
Expected: Outputs the prompt text

**Step 4: Commit**

```bash
git add api/tenants/pools/
git commit -m "feat(pools): add Reference Image System support"
```

---

## Task 3: Add get_reference_insertion_prompt to windows tenant

**Files:**
- Modify: `api/tenants/windows/prompts.py`
- Modify: `api/tenants/windows/config.py`

**Step 1: Read current windows prompts.py**

Check current structure before adding.

**Step 2: Add prompt function to prompts.py**

Add at the end of the file:

```python
def get_reference_insertion_prompt(feature_type: str, options: dict) -> str:
    """
    Generate prompt for reference-based insertion.
    Uses contractor's reference image as the visual guide.
    """
    frame_color = options.get('frame_color', options.get('color', 'white'))
    style = options.get('window_style', 'double-hung')

    return f"""You are given TWO images:
1. REFERENCE IMAGE (first): Shows the exact {feature_type} product to install
2. TARGET IMAGE (second): Customer's home photo

TASK: Install the {feature_type} from the reference image onto the appropriate locations in the target image.

PRODUCT DETAILS: {style} windows with {frame_color} frames

REQUIREMENTS:
- Match the exact appearance, color ({frame_color}), and style from the reference
- Adjust perspective and scale to fit naturally in the target
- Maintain realistic lighting and shadows
- Keep the installation looking professional and flush-mounted
- Replace existing windows in appropriate locations

OUTPUT: A photorealistic composite showing the reference windows installed on the customer's home."""
```

**Step 3: Enable flag in config.py**

Add `supports_reference_images = True` to WindowsTenantConfig.

**Step 4: Verify**

Run: `source venv/bin/activate && python3 manage.py shell -c "from api.tenants.windows.prompts import get_reference_insertion_prompt; print('OK')"`
Expected: "OK"

**Step 5: Commit**

```bash
git add api/tenants/windows/
git commit -m "feat(windows): add Reference Image System support"
```

---

## Task 4: Add get_reference_insertion_prompt to roofs tenant

**Files:**
- Modify: `api/tenants/roofs/prompts.py`
- Modify: `api/tenants/roofs/config.py`

**Step 1: Read current roofs prompts.py**

Check current structure before adding.

**Step 2: Add prompt function to prompts.py**

Add at the end of the file:

```python
def get_reference_insertion_prompt(feature_type: str, options: dict) -> str:
    """
    Generate prompt for reference-based insertion.
    Uses contractor's reference image as the visual guide.
    """
    material = options.get('roofing_material', options.get('material', 'shingle'))
    color = options.get('roof_color', options.get('color', 'charcoal'))

    return f"""You are given TWO images:
1. REFERENCE IMAGE (first): Shows the exact {feature_type} material/product
2. TARGET IMAGE (second): Customer's home photo

TASK: Replace the roof in the target image with the roofing material shown in the reference.

PRODUCT DETAILS: {material} roofing in {color}

REQUIREMENTS:
- Match the exact texture, color ({color}), and pattern from the reference
- Maintain the existing roof shape and architecture
- Adjust for proper perspective and scale
- Ensure realistic lighting and shadows on the new roof
- Keep gutters, vents, and other roof features appropriately placed

OUTPUT: A photorealistic composite showing the reference roofing material on the customer's home."""
```

**Step 3: Enable flag in config.py**

Add `supports_reference_images = True` to RoofsTenantConfig.

**Step 4: Verify**

Run: `source venv/bin/activate && python3 manage.py shell -c "from api.tenants.roofs.prompts import get_reference_insertion_prompt; print('OK')"`
Expected: "OK"

**Step 5: Commit**

```bash
git add api/tenants/roofs/
git commit -m "feat(roofs): add Reference Image System support"
```

---

## Task 5: Enable flag for screens tenant (already has prompts)

**Files:**
- Modify: `api/tenants/screens/config.py`

**Step 1: Add flag**

The screens tenant already has `get_reference_insertion_prompt()` in prompts.py. Just add the flag:

```python
class ScreensTenantConfig(BaseTenantConfig):

    supports_reference_images = True  # Add this line

    @property
    def tenant_id(self) -> str:
```

**Step 2: Verify**

Run: `source venv/bin/activate && python3 manage.py shell -c "from api.tenants import get_tenant_config; print(get_tenant_config('screens').supports_reference_images)"`
Expected: "True"

**Step 3: Commit**

```bash
git add api/tenants/screens/config.py
git commit -m "feat(screens): enable supports_reference_images flag"
```

---

## Task 6: Final verification

**Step 1: Verify all tenants**

```bash
source venv/bin/activate && python3 manage.py shell -c "
from api.tenants import get_all_tenants
for tid, config in get_all_tenants().items():
    has_flag = getattr(config, 'supports_reference_images', False)
    prompts = config.get_prompts_module()
    has_prompt = hasattr(prompts, 'get_reference_insertion_prompt')
    print(f'{tid}: flag={has_flag}, prompt={has_prompt}')
"
```

Expected output:
```
pools: flag=True, prompt=True
windows: flag=True, prompt=True
roofs: flag=True, prompt=True
screens: flag=True, prompt=True
```

**Step 2: Django check**

Run: `python3 manage.py check`
Expected: "System check identified no issues"

**Step 3: Summary commit (optional)**

If not already committed individually:
```bash
git add -A
git commit -m "feat: add Reference Image System support to all tenants"
```

---

## Summary

| Tenant | supports_reference_images | get_reference_insertion_prompt |
|--------|---------------------------|-------------------------------|
| pools | ✓ | ✓ (new) |
| windows | ✓ | ✓ (new) |
| roofs | ✓ | ✓ (new) |
| screens | ✓ | ✓ (existing) |

All tenants can now opt-in to Reference Image System. Contractors can upload reference images via Django admin, and the pipeline will use them for AI compositing when available.
