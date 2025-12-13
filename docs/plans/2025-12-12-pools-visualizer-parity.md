# Pools Visualizer Parity Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Update pools tenant prompts to match the quality and structure of boss tenant prompts - simple, specific, positive prompts with proper quality checking.

**Architecture:** The pools tenant already has the correct config structure. We're only updating `prompts.py` to have the same prompt quality as boss: clear cleanup instructions, photorealistic insertion prompts with specific visual details, and a robust quality check that returns JSON scores.

**Tech Stack:** Python, Django, pytest

---

## Gap Analysis

| Component | Boss (Working) | Pools (Needs Update) |
|-----------|---------------|---------------------|
| Cleanup prompt | Sunny weather, clean debris, preserve structures | Generic "prepare area" - needs specificity |
| Insertion prompt | Photorealistic, specific materials, lighting/shadows | Basic shape/surface - needs visual details |
| Quality check | JSON output, hallucination detection, scope-aware | No JSON, no scoring, no scope awareness |
| Tests | Basic interface tests | Same - adequate |

---

## Task 1: Update Cleanup Prompt

**Files:**
- Modify: `api/tenants/pools/prompts.py:7-12`
- Test: `api/tenants/pools/tests/test_prompts.py`

**Step 1: Write the failing test**

Add to `api/tenants/pools/tests/test_prompts.py`:

```python
def test_cleanup_prompt_has_weather_instruction():
    """Cleanup prompt should specify sunny weather like boss tenant."""
    result = prompts.get_cleanup_prompt()
    assert 'sunny' in result.lower() or 'clear' in result.lower()


def test_cleanup_prompt_preserves_structures():
    """Cleanup prompt should preserve permanent structures."""
    result = prompts.get_cleanup_prompt()
    assert 'permanent' in result.lower() or 'preserve' in result.lower() or 'keep' in result.lower()
```

**Step 2: Run test to verify it fails**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/pools/tests/test_prompts.py -v`

Expected: FAIL - current prompt doesn't mention sunny or preserve

**Step 3: Update cleanup prompt**

Replace `get_cleanup_prompt()` in `api/tenants/pools/prompts.py`:

```python
def get_cleanup_prompt() -> str:
    """
    Step 1: The Foundation.
    Focus: Clean image and enhance to ideal sunny conditions.
    """
    return """Please clean this image of any debris, furniture, and temporary items.
Make the weather conditions ideal and sunny with clear blue sky.
Keep all permanent structures exactly as they are.
Remove any existing pool or water features to prepare for new pool insertion."""
```

**Step 4: Run test to verify it passes**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/pools/tests/test_prompts.py -v`

Expected: PASS

**Step 5: Commit**

```bash
cd /home/reid/testhome/boss-security-visualizer
git add api/tenants/pools/prompts.py api/tenants/pools/tests/test_prompts.py
git commit -m "feat(pools): update cleanup prompt to match boss quality"
```

---

## Task 2: Update Pool Insertion Prompt

**Files:**
- Modify: `api/tenants/pools/prompts.py:15-28`
- Test: `api/tenants/pools/tests/test_prompts.py`

**Step 1: Write the failing test**

Add to `api/tenants/pools/tests/test_prompts.py`:

```python
def test_pool_insertion_prompt_is_photorealistic():
    """Pool insertion prompt should specify photorealistic rendering."""
    result = prompts.get_insertion_prompt('pool', {'pool_shape': 'rectangle', 'pool_surface': 'pebble_tec_blue'})
    assert 'photorealistic' in result.lower()


def test_pool_insertion_prompt_mentions_lighting():
    """Pool insertion prompt should mention lighting and shadows."""
    result = prompts.get_insertion_prompt('pool', {'pool_shape': 'rectangle', 'pool_surface': 'pebble_tec_blue'})
    assert 'lighting' in result.lower() or 'shadow' in result.lower()
```

**Step 2: Run test to verify it fails**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/pools/tests/test_prompts.py::test_pool_insertion_prompt_is_photorealistic -v`

Expected: FAIL - current prompt doesn't say "photorealistic"

**Step 3: Update pool insertion prompt**

Replace `get_pool_insertion_prompt()` in `api/tenants/pools/prompts.py`:

```python
def get_pool_insertion_prompt(feature_type: str, options: dict) -> str:
    """
    Generates a focused inpainting prompt for pool features.

    Args:
        feature_type: 'pool' or 'deck'
        options: Dict with pool_shape, pool_surface, deck_material, water_feature
    """
    pool_shape = options.get('pool_shape', 'rectangle')
    pool_surface = options.get('pool_surface', 'pebble_tec_blue')
    deck_material = options.get('deck_material', 'travertine')
    water_feature = options.get('water_feature', 'none')

    # Map surface to visual description
    surface_desc = {
        'white_plaster': 'smooth white plaster with light blue water tint',
        'pebble_tec_blue': 'textured pebble finish with deep blue water color',
        'pebble_tec_midnight': 'textured pebble finish with dark midnight blue water'
    }.get(pool_surface, 'textured blue finish')

    if feature_type == 'deck':
        return f"""Photorealistic inpainting. Add a {deck_material} pool deck surrounding the pool area.
Render the deck material with realistic texture and natural weathering.
Ensure lighting and shadows interact naturally with the deck surface.
Maintain seamless integration with the existing landscape."""

    base_prompt = f"""Photorealistic inpainting. Add a {pool_shape} shaped swimming pool with {surface_desc}.
Render realistic water with natural reflections matching the sky and surroundings.
Ensure lighting and shadows interact naturally with the water surface.
The pool should integrate seamlessly with the existing landscape and architecture."""

    if water_feature and water_feature != 'none':
        feature_desc = {
            'waterfall': 'a natural stone waterfall feature cascading into the pool',
            'fountain': 'elegant fountain jets rising from the pool surface',
            'infinity_edge': 'an infinity edge on the far side with water flowing over'
        }.get(water_feature, '')
        if feature_desc:
            base_prompt += f"\nInclude {feature_desc}."

    return base_prompt
```

**Step 4: Run test to verify it passes**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/pools/tests/test_prompts.py -v`

Expected: PASS

**Step 5: Commit**

```bash
cd /home/reid/testhome/boss-security-visualizer
git add api/tenants/pools/prompts.py api/tenants/pools/tests/test_prompts.py
git commit -m "feat(pools): update insertion prompts to be photorealistic with visual details"
```

---

## Task 3: Update Quality Check Prompt

**Files:**
- Modify: `api/tenants/pools/prompts.py:31-39`
- Test: `api/tenants/pools/tests/test_prompts.py`

**Step 1: Write the failing test**

Add to `api/tenants/pools/tests/test_prompts.py`:

```python
def test_quality_check_returns_json_instruction():
    """Quality check prompt should instruct to return JSON."""
    result = prompts.get_quality_check_prompt()
    assert 'json' in result.lower()


def test_quality_check_has_score_instruction():
    """Quality check prompt should mention score between 0 and 1."""
    result = prompts.get_quality_check_prompt()
    assert 'score' in result.lower()
    assert '0' in result and '1' in result
```

**Step 2: Run test to verify it fails**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/pools/tests/test_prompts.py::test_quality_check_returns_json_instruction -v`

Expected: FAIL - current prompt doesn't mention JSON

**Step 3: Update quality check prompt**

Replace `get_quality_check_prompt()` in `api/tenants/pools/prompts.py`:

```python
def get_quality_check_prompt(scope: dict = None) -> str:
    """
    Generates a prompt for the AI to evaluate the realism and consistency
    of the generated pool image compared to the reference.
    """
    base_prompt = """You are a Quality Control AI.
Image 1 is the REFERENCE (Clean State).
Image 2 is the FINAL RESULT (With Pool).

Compare them and check for issues:
1. Is the pool shape consistent and realistic?
2. Does the water have natural reflections and color?
3. Is the perspective consistent with the original image?
4. Are there any floating or disconnected elements?
"""

    if scope and scope.get('deck'):
        base_prompt += """
CONTEXT: Pool with Deck Installation.
- Verify deck integrates naturally with pool edge.
- Check deck material looks realistic and properly textured.
"""

    if scope and scope.get('water_feature') and scope.get('water_feature') != 'none':
        base_prompt += """
CONTEXT: Water Feature Included.
- Verify water feature looks natural and physically plausible.
- Check water flow direction and splash patterns are realistic.
"""

    base_prompt += """
Rate the quality on a scale of 0.0 to 1.0.
- If the pool looks unrealistic or floating, score MUST be below 0.5.
- If photorealism is poor (bad reflections, wrong shadows), score MUST be below 0.7.

Return ONLY a JSON object with the following structure:
{
    "score": float,
    "reason": "string"
}
"""
    return base_prompt
```

**Step 4: Run test to verify it passes**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/pools/tests/test_prompts.py -v`

Expected: PASS

**Step 5: Commit**

```bash
cd /home/reid/testhome/boss-security-visualizer
git add api/tenants/pools/prompts.py api/tenants/pools/tests/test_prompts.py
git commit -m "feat(pools): update quality check to return JSON scores like boss tenant"
```

---

## Task 4: Run Full Test Suite

**Files:**
- Test: All tenant tests

**Step 1: Run all pools tests**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/pools/tests/ -v`

Expected: All tests PASS

**Step 2: Run all tenant tests to verify no regressions**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/ -v`

Expected: All 34+ tests PASS

**Step 3: Commit test additions**

```bash
cd /home/reid/testhome/boss-security-visualizer
git add api/tenants/pools/tests/test_prompts.py
git commit -m "test(pools): add comprehensive prompt quality tests"
```

---

## Task 5: Update Documentation

**Files:**
- Modify: `docs/PROMPTING-LOGIC-DEEP-DIVE.md`

**Step 1: Update the pools section in the deep dive doc**

Edit the POOLS TENANT section in `docs/PROMPTING-LOGIC-DEEP-DIVE.md` to reflect the new prompts:

```markdown
### POOLS TENANT

**File**: `api/tenants/pools/prompts.py`

**Pipeline Order**: cleanup → pool_insertion → deck_insertion → quality_check

#### Cleanup Prompt
```
Please clean this image of any debris, furniture, and temporary items.
Make the weather conditions ideal and sunny with clear blue sky.
Keep all permanent structures exactly as they are.
Remove any existing pool or water features to prepare for new pool insertion.
```

#### Pool Insertion Prompt
```
Photorealistic inpainting. Add a {pool_shape} shaped swimming pool with {surface_desc}.
Render realistic water with natural reflections matching the sky and surroundings.
Ensure lighting and shadows interact naturally with the water surface.
The pool should integrate seamlessly with the existing landscape and architecture.

[If water_feature specified]: Include {feature_desc}.
```

#### Deck Insertion Prompt
```
Photorealistic inpainting. Add a {deck_material} pool deck surrounding the pool area.
Render the deck material with realistic texture and natural weathering.
Ensure lighting and shadows interact naturally with the deck surface.
Maintain seamless integration with the existing landscape.
```

#### Quality Check Prompt
```
You are a Quality Control AI.
Image 1 is the REFERENCE (Clean State).
Image 2 is the FINAL RESULT (With Pool).

Compare them and check for issues:
1. Is the pool shape consistent and realistic?
2. Does the water have natural reflections and color?
3. Is the perspective consistent with the original image?
4. Are there any floating or disconnected elements?

[Context varies by scope - deck, water feature]

Rate quality 0.0 to 1.0...
Return ONLY a JSON object with score and reason
```
```

**Step 2: Commit documentation**

```bash
cd /home/reid/testhome/boss-security-visualizer
git add docs/PROMPTING-LOGIC-DEEP-DIVE.md
git commit -m "docs: update pools tenant prompts in deep dive doc"
```

---

## Summary

After completing all tasks:

1. **Cleanup prompt** - Now matches boss: sunny weather, preserve structures, specific cleanup
2. **Pool insertion prompt** - Now photorealistic with visual details, lighting, shadows
3. **Deck insertion prompt** - New dedicated prompt for deck feature
4. **Quality check** - Now returns JSON scores with hallucination detection
5. **Tests** - Comprehensive coverage of prompt quality requirements
6. **Docs** - Updated to reflect new prompts

The pools tenant will now produce the same quality of AI output as the boss tenant.
