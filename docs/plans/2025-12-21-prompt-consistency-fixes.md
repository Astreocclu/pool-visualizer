# Prompt Consistency Fixes Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Standardize AI prompt patterns across all three tenants (pools, windows, roofs) for consistency and maintainability.

**Architecture:** Four targeted fixes: (1) Add perspective adjustment to windows cleanup, (2) Add regional hints to pools and windows like roofs has, (3) Standardize get_prompt() signature to match pools pattern, (4) Make pools/roofs quality_check actually use scope parameter like windows does.

**Tech Stack:** Python, Django tenant system

---

## Task 1: Add Perspective Adjustment to Windows Cleanup

**Files:**
- Modify: `api/tenants/windows/prompts.py:11-44`

**Step 1: Add PERSPECTIVE ADJUSTMENT section to windows cleanup prompt**

In `get_cleanup_prompt()`, add after WINDOW VISIBILITY section (before OUTPUT):

```python
def get_cleanup_prompt() -> str:
    """Step 1: Clean the image and enhance to ideal conditions."""
    return """Photorealistic image editing. Prepare this house exterior for window visualization.

WEATHER AND LIGHTING:
Make the weather conditions ideal: sunny day with clear blue sky, good natural lighting, no harsh shadows.

REMOVE ONLY THESE TEMPORARY ITEMS:
- Garden hoses and yard equipment
- Yard tools and equipment
- Children's toys and play equipment
- Temporary furniture covers
- Trash cans and debris
- Construction materials
- Vehicles visible in frame

PRESERVE EXACTLY AS-IS:
- House structure, siding, and all architectural features
- All existing windows and their openings (frames can be old/damaged)
- Doors and entryways
- Roof, gutters, downspouts
- Landscaping (trees, shrubs, plants, grass)
- Walkways, driveways, hardscape
- Lighting fixtures
- Fence and property boundaries

WINDOW VISIBILITY:
- Ensure all window openings are clearly visible
- Preserve the exact size and position of each window
- Keep window trim and surrounding siding intact
- Remove any obstructions blocking window views

PERSPECTIVE ADJUSTMENT:
Create a perspective ideal for window replacement visualization:
- Front or 3/4 view showing the main facade
- Angle that clearly shows all window openings on visible walls
- Minimize extreme angles that distort window proportions
- Ensure window planes are clearly visible for accurate rendering

OUTPUT: Clean, well-lit house exterior image with all windows clearly visible.
Output at the highest resolution possible."""
```

**Step 2: Verify the change**

Run: `cd /home/reid/command-center/testhome/pools-visualizer && source venv/bin/activate && python3 -c "from api.tenants.windows.prompts import get_cleanup_prompt; p = get_cleanup_prompt(); assert 'PERSPECTIVE ADJUSTMENT' in p; print('OK')"`

Expected: `OK`

**Step 3: Commit**

```bash
git add api/tenants/windows/prompts.py
git commit -m "fix(windows): add perspective adjustment to cleanup prompt"
```

---

## Task 2: Add Regional Hints to Pools Prompts

**Files:**
- Modify: `api/tenants/pools/prompts.py:49-104`

**Step 1: Add Texas climate hints to pool_shell_prompt**

Update `get_pool_shell_prompt()` to include regional considerations after WATER APPEARANCE:

```python
def get_pool_shell_prompt(selections: dict) -> str:
    """Step 2: Render the pool shell with selected options."""
    size = next((s for s in config.POOL_SIZES if s['id'] == selections.get('size', 'classic')), config.POOL_SIZES[1])
    shape = next((s for s in config.POOL_SHAPES if s['id'] == selections.get('shape', 'rectangle')), config.POOL_SHAPES[0])
    finish = next((f for f in config.INTERIOR_FINISHES if f['id'] == selections.get('finish', 'pebble_blue')), config.INTERIOR_FINISHES[1])

    features = []
    if selections.get('tanning_ledge', True):
        features.append(config.BUILT_IN_FEATURES['tanning_ledge']['prompt_hint'])
        lounger_count = selections.get('lounger_count', 2)
        if lounger_count > 0:
            features.append(config.BUILT_IN_FEATURES['ledge_loungers']['prompt_hint'].format(count=lounger_count))

    if selections.get('attached_spa', False):
        features.append(config.BUILT_IN_FEATURES['attached_spa']['prompt_hint'])

    features_text = ""
    if features:
        features_text = f"""
BUILT-IN FEATURES:
Include these built-in features as part of the pool structure:
{chr(10).join('- ' + f for f in features)}
"""

    return f"""Photorealistic inpainting. Install a swimming pool in this backyard.

POOL SPECIFICATIONS:
- Size: {size['prompt_hint']}
- Shape: {shape['prompt_hint']} pool
- Interior finish: {finish['prompt_hint']}

POOL STRUCTURE REQUIREMENTS:
- Position pool in the most logical open area of the yard
- Minimum 5 feet apparent setback from house
- Minimum 3 feet apparent setback from fence lines
- Pool coping (rounded bull-nose edge) around entire perimeter
- Waterline tile visible at the surface level
- Depth transition visible through water (shallow to deep end)
- Pool equipment pad area (subtle, near fence)
{features_text}
WATER APPEARANCE:
- Crystal clear water with realistic color from the {finish['water_color']} finish
- Light refraction patterns (caustics) visible on pool floor
- Subtle surface reflections matching sky and surroundings
- Water level approximately 6 inches below coping
- Natural depth shadows on pool walls visible through water

TEXAS CLIMATE CONSIDERATIONS:
- Pool designed for 100°F+ summer temperatures
- Pebble/quartz finishes that resist Texas sun bleaching
- Coping materials appropriate for barefoot use in extreme heat
- Equipment placement accounting for full sun exposure

CRITICAL INTEGRATION:
- Pool must look INSTALLED, not floating or pasted on
- Shadows cast correctly based on sun position in image
- Scale must be realistic relative to house and yard
- Match the perspective established in the cleaned image
- Preserve all structures, fence, trees outside pool footprint

OUTPUT: Photorealistic image showing installed pool shell.
Output at the highest resolution possible."""
```

**Step 2: Verify the change**

Run: `python3 -c "from api.tenants.pools.prompts import get_pool_shell_prompt; p = get_pool_shell_prompt({}); assert 'TEXAS CLIMATE' in p; print('OK')"`

Expected: `OK`

**Step 3: Commit**

```bash
git add api/tenants/pools/prompts.py
git commit -m "fix(pools): add Texas climate hints to pool_shell prompt"
```

---

## Task 3: Add Regional Hints to Windows Prompts

**Files:**
- Modify: `api/tenants/windows/prompts.py:47-117`

**Step 1: Add Texas climate hints to window_frame_prompt**

Update `get_window_frame_prompt()` to add regional section before OUTPUT:

Find the line `OUTPUT: Photorealistic image with new windows` (around line 115) and insert before it:

```python
TEXAS CLIMATE CONSIDERATIONS:
- Windows rated for intense UV exposure and 100°F+ temperatures
- Low-E glass appropriate for Texas sun and heat reduction
- Frame materials that resist warping in extreme heat
- Energy-efficient glazing for high cooling loads
```

The full return statement ending should become:

```python
    return f"""Photorealistic inpainting. {project_context}

WINDOW SPECIFICATIONS:
- Window type: {window_type['prompt_hint']}
- Style: {window_style['prompt_hint']}
- Frame material: {frame_material['prompt_hint']}
- Frame color: {frame_color['prompt_hint']}
{door_section}
INSTALLATION REQUIREMENTS:
- All windows must have identical frame style and color
- Maintain proper window proportions relative to wall size
- Frames should look solid and professionally installed
- Glass should show subtle reflections of sky/surroundings
- For new openings: Show clean cuts with proper headers

TEXAS CLIMATE CONSIDERATIONS:
- Windows rated for intense UV exposure and 100°F+ temperatures
- Low-E glass appropriate for Texas sun and heat reduction
- Frame materials that resist warping in extreme heat
- Energy-efficient glazing for high cooling loads

PRESERVE EXACTLY:
- House structure beyond installation areas
- Roof, siding, landscaping
- Original lighting and atmosphere

OUTPUT: Photorealistic image with new windows{' and doors' if door_type['id'] != 'none' else ''} installed.
Output at the highest resolution possible."""
```

**Step 2: Verify the change**

Run: `python3 -c "from api.tenants.windows.prompts import get_window_frame_prompt; p = get_window_frame_prompt({}); assert 'TEXAS CLIMATE' in p; print('OK')"`

Expected: `OK`

**Step 3: Commit**

```bash
git add api/tenants/windows/prompts.py
git commit -m "fix(windows): add Texas climate hints to window_frame prompt"
```

---

## Task 4: Standardize get_prompt() Signature in Windows

**Files:**
- Modify: `api/tenants/windows/prompts.py:554-574`

**Step 1: Update get_prompt() to match pools pattern**

Change from:
```python
def get_prompt(step: str, selections: dict = None, scope: dict = None) -> str:
    """Get prompt for a specific pipeline step."""
    selections = selections or {}
    scope = scope or {}
```

To:
```python
def get_prompt(step: str, selections: dict = None) -> str:
    """Get prompt for a specific pipeline step."""
    selections = selections or {}
```

And update the quality_check call from:
```python
    elif step == 'quality_check':
        return get_quality_check_prompt(scope)
```

To:
```python
    elif step == 'quality_check':
        return get_quality_check_prompt(selections)
```

**Step 2: Update get_quality_check_prompt() to use selections**

Change function signature from:
```python
def get_quality_check_prompt(scope: dict = None) -> str:
```

To:
```python
def get_quality_check_prompt(selections: dict = None) -> str:
```

And update the body to derive scope from selections:
```python
def get_quality_check_prompt(selections: dict = None) -> str:
    """Step 7: Quality check comparing original to final result."""
    selections = selections or {}

    # Derive scope from selections
    scope = {
        'doors': selections.get('door_type') and selections.get('door_type') != 'none',
        'patio_enclosure': selections.get('enclosure_type') and selections.get('enclosure_type') != 'none',
    }

    # Build additional checks based on scope
    additional_checks = []
    # ... rest unchanged
```

**Step 3: Verify the change**

Run: `python3 -c "from api.tenants.windows.prompts import get_prompt; p = get_prompt('cleanup'); print('OK')"`

Expected: `OK`

**Step 4: Commit**

```bash
git add api/tenants/windows/prompts.py
git commit -m "fix(windows): standardize get_prompt signature to match pools"
```

---

## Task 5: Make Pools quality_check Use Scope from Selections

**Files:**
- Modify: `api/tenants/pools/prompts.py:235-289`

**Step 1: Update get_quality_check_prompt to derive scope from selections**

Change from:
```python
def get_quality_check_prompt(scope: dict = None) -> str:
    """Step 6: Quality check comparing clean image to final result."""
    return """You are a Quality Control AI...
```

To:
```python
def get_quality_check_prompt(selections: dict = None) -> str:
    """Step 6: Quality check comparing clean image to final result."""
    selections = selections or {}

    # Derive scope from selections
    has_water_features = bool(selections.get('water_features'))
    has_spa = selections.get('attached_spa', False)
    has_tanning_ledge = selections.get('tanning_ledge', True)

    # Build feature-specific checks
    feature_checks = ""
    if has_water_features or has_spa or has_tanning_ledge:
        feature_checks = """
6. FEATURES
   - Do water features have realistic water flow?
   - Are built-ins (tanning ledge, spa) properly integrated?
   - Does furniture/landscaping look natural?"""

    return f"""You are a Quality Control AI for pool visualization. You will receive two images.

IMAGE 1: The REFERENCE image (clean backyard before pool)
IMAGE 2: The FINAL RESULT (backyard with pool and all features)

EVALUATE THE VISUALIZATION:

1. POOL PLACEMENT
   - Is the pool positioned logically in the yard?
   - Are setbacks from house and fence realistic?
   - Does the pool fit the space without looking cramped or tiny?

2. POOL REALISM
   - Does the pool shape have consistent, natural edges?
   - Is the water color realistic for the selected finish?
   - Are water reflections and caustics natural?
   - Does the water appear level (not tilted)?

3. PERSPECTIVE & SCALE
   - Does the pool match the perspective of the original image?
   - Is the pool scaled correctly relative to the house?
   - Do shadows fall in the correct direction?

4. INTEGRATION
   - Does the pool look INSTALLED vs. pasted/floating?
   - Does the deck connect naturally to existing hardscape?
   - Are transitions between materials smooth?

5. PRESERVATION
   - Are the house, fence, and trees intact?
   - Is existing landscaping preserved outside work area?
   - Are there any unwanted artifacts or deletions?
{feature_checks}
SCORING GUIDE:
- 0.0 to 0.4: FAIL - Major issues (floating pool, impossible geometry, wrong perspective, significant artifacts)
- 0.5 to 0.6: POOR - Usable but obvious issues (minor floating, perspective slightly off, unnatural edges)
- 0.7 to 0.8: GOOD - Minor imperfections only (subtle edge issues, minor reflection problems)
- 0.9 to 1.0: EXCELLENT - Highly realistic, no obvious issues

RETURN ONLY VALID JSON:
{{
    "score": <float between 0.0 and 1.0>,
    "issues": [<list of specific issues found, empty if none>],
    "recommendation": "<PASS or REGENERATE>"
}}

A score below 0.6 should recommend REGENERATE.
Be strict - homeowners will pay $50K-150K based on this visualization."""
```

**Step 2: Update get_prompt() to pass selections to quality_check**

Change line 307 from:
```python
    elif step == 'quality_check':
        return get_quality_check_prompt()
```

To:
```python
    elif step == 'quality_check':
        return get_quality_check_prompt(selections)
```

**Step 3: Verify the change**

Run: `python3 -c "from api.tenants.pools.prompts import get_prompt; p = get_prompt('quality_check', {'water_features': ['waterfall']}); assert 'FEATURES' in p; print('OK')"`

Expected: `OK`

**Step 4: Commit**

```bash
git add api/tenants/pools/prompts.py
git commit -m "fix(pools): make quality_check derive scope from selections"
```

---

## Task 6: Make Roofs quality_check Use Scope from Selections

**Files:**
- Modify: `api/tenants/roofs/prompts.py:235-313`

**Step 1: Update get_quality_check_prompt to derive scope from selections**

Change from:
```python
def get_quality_check_prompt(scope: dict = None) -> str:
    """Step 5: Quality check comparing clean image to final result."""
    return """You are a Quality Control AI...
```

To:
```python
def get_quality_check_prompt(selections: dict = None) -> str:
    """Step 5: Quality check comparing clean image to final result."""
    selections = selections or {}

    # Derive scope from selections
    has_solar = selections.get('solar_option') and selections.get('solar_option') != 'none'
    has_gutters = selections.get('gutter_option') and selections.get('gutter_option') != 'none'

    solar_section = ""
    if has_solar:
        solar_section = """
2. SOLAR INSTALLATION
   - Are panels properly spaced with fire setbacks?
   - Is mounting style appropriate (flush to roof)?
   - Are conduit runs logical and clean?
   - Is panel coverage appropriate for selected level?"""

    gutter_section = ""
    if has_gutters:
        gutter_section = """
3. GUTTER SYSTEM
   - Are gutters properly sloped toward downspouts?
   - Are downspouts logically positioned?
   - Does gutter style match specification?"""

    return f"""You are a Quality Control AI for roof/solar visualization. You will receive two images.

IMAGE 1: The REFERENCE image (original house before roof work)
IMAGE 2: The FINAL RESULT (house with new roof and optional solar/gutters)

EVALUATE THE VISUALIZATION:

1. ROOF MATERIAL INTEGRATION
   - Does the new roof follow exact pitch and angles of original?
   - Are valleys, hips, and ridges properly aligned?
   - Do penetrations (vents, chimneys) have correct flashing?
   - Is material texture realistic for the selected type?
   - Is color consistent across all roof planes?
{solar_section}{gutter_section}
4. PERSPECTIVE AND SCALE
   - Does the roof maintain original perspective exactly?
   - Is scale correct relative to house and surroundings?
   - Do shadows from roof/panels match sun direction?
   - Are architectural proportions preserved?

5. TEXAS-SPECIFIC CHECKS
   - Does material show appropriate heat/UV characteristics?
   - Are hail/wind considerations addressed (proper fastening)?
   - Is color appropriate for thermal performance?
   - Are solar panels angled for Texas latitude (~30°)?

6. PRESERVATION
   - Are walls, windows, doors completely unchanged?
   - Is landscaping preserved as expected?
   - Are there any unwanted artifacts or deletions?
   - Is the foundation and yard intact?

SCORING GUIDE:
- 0.0-0.4: FAIL - Major issues (wrong perspective, impossible geometry, floating elements)
- 0.5-0.6: POOR - Obvious issues (misaligned materials, unrealistic textures, bad integration)
- 0.7-0.8: GOOD - Minor issues (slight alignment problems, small texture inconsistencies)
- 0.9-1.0: EXCELLENT - Highly realistic, professional installation appearance

CRITICAL: Homeowners invest $15K-$80K based on these visualizations.

RETURN ONLY VALID JSON:
{{
    "score": <float between 0.0 and 1.0>,
    "issues": [<list of specific issues found, empty if none>],
    "recommendation": "<PASS or REGENERATE>"
}}

Score below 0.6 should REGENERATE."""
```

**Step 2: Update get_prompt() to pass selections to quality_check**

Change line 311 from:
```python
    elif step == 'quality_check':
        return get_quality_check_prompt()
```

To:
```python
    elif step == 'quality_check':
        return get_quality_check_prompt(selections)
```

**Step 3: Verify the change**

Run: `python3 -c "from api.tenants.roofs.prompts import get_prompt; p = get_prompt('quality_check', {'solar_option': 'partial'}); assert 'SOLAR INSTALLATION' in p; print('OK')"`

Expected: `OK`

**Step 4: Commit**

```bash
git add api/tenants/roofs/prompts.py
git commit -m "fix(roofs): make quality_check derive scope from selections"
```

---

## Task 7: Final Verification

**Files:**
- Test all three tenant prompts

**Step 1: Verify all prompts import and run**

Run:
```bash
python3 -c "
from api.tenants.pools.prompts import get_prompt as pools_get
from api.tenants.windows.prompts import get_prompt as windows_get
from api.tenants.roofs.prompts import get_prompt as roofs_get

# Test pools
p = pools_get('cleanup')
assert 'PERSPECTIVE ADJUSTMENT' in p
p = pools_get('pool_shell', {})
assert 'TEXAS CLIMATE' in p
p = pools_get('quality_check', {'water_features': ['waterfall']})
assert 'FEATURES' in p

# Test windows
p = windows_get('cleanup')
assert 'PERSPECTIVE ADJUSTMENT' in p
p = windows_get('window_frame', {})
assert 'TEXAS CLIMATE' in p
p = windows_get('quality_check', {'door_type': 'sliding_glass'})
assert 'DOOR INSTALLATION' in p

# Test roofs
p = roofs_get('cleanup')
assert 'PERSPECTIVE ADJUSTMENT' in p
p = roofs_get('roof_material', {})
assert 'TEXAS' in p
p = roofs_get('quality_check', {'solar_option': 'partial'})
assert 'SOLAR INSTALLATION' in p

print('All prompts consistent!')
"
```

Expected: `All prompts consistent!`

**Step 2: Final commit**

```bash
git add -A
git commit -m "chore: verify prompt consistency across all tenants"
```

---

## Summary

| Fix | Pools | Windows | Roofs |
|-----|-------|---------|-------|
| Perspective in cleanup | Already has | Task 1 | Already has |
| Regional hints | Task 2 | Task 3 | Already has |
| get_prompt(step, selections) | Already has | Task 4 | Already has |
| quality_check uses selections | Task 5 | Task 4 | Task 6 |
