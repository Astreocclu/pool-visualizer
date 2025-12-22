"""
Pools Visualizer - AI Prompts
Layered rendering pipeline for swimming pool visualization.

Pipeline: cleanup → pool_shell → deck → water_features → finishing → quality_check
"""

from api.tenants.pools import config


def get_cleanup_prompt() -> str:
    """Step 1: Clean the image and enhance to ideal conditions."""
    return """Photorealistic image editing. Prepare this backyard for pool visualization.

WEATHER AND LIGHTING:
Make the weather conditions ideal: sunny day with clear blue sky, good natural lighting, no clouds.

REMOVE ONLY THESE TEMPORARY ITEMS:
- Pool toys, floats, inflatables
- Garden hoses
- Yard tools and equipment
- Children's toys and play equipment
- Temporary furniture covers
- Trash cans and debris
- Construction materials
- Vehicles visible in yard

PRESERVE EXACTLY AS-IS:
- House and all architectural features
- Fence and gates (all sides)
- Trees, shrubs, plants, landscaping
- Permanent outdoor furniture
- Patios, walkways, existing hardscape
- Lighting fixtures
- Ground elevation and terrain
- Property boundaries

PERSPECTIVE ADJUSTMENT:
Always create a perspective ideal for a designer to create a 3D render of a pool.
- Slightly elevated viewpoint (as if standing on a raised deck or second floor)
- Angle that shows the full yard footprint clearly
- Minimize extreme foreshortening
- Ensure ground plane is clearly visible for pool placement

OUTPUT: Clean, sunny backyard image with optimal perspective for pool visualization.
Output at the highest resolution possible."""


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


def get_deck_prompt(selections: dict) -> str:
    """Step 3: Add deck/surround around the pool."""
    material = next((m for m in config.DECK_MATERIALS if m['id'] == selections.get('deck_material', 'travertine')), config.DECK_MATERIALS[0])
    color = next((c for c in config.DECK_COLORS if c['id'] == selections.get('deck_color', 'cream')), config.DECK_COLORS[0])

    return f"""Photorealistic inpainting. Add a pool deck around the installed pool.

DECK SPECIFICATIONS:
- Material: {material['prompt_hint']}
- Color: {color['prompt_hint']}
- Coverage: 4-6 feet width surrounding the entire pool perimeter

DECK REQUIREMENTS:
- Natural material texture authentic to {material['name']}
- Realistic color variation within the {color['name']} palette
- Subtle drainage slope away from house (barely visible)
- Clean expansion joints where appropriate for the material
- Non-slip texture appearance
- Smooth transition to existing hardscape where they meet

INTEGRATION:
- Deck connects logically to any existing patio or walkways
- Natural shadow patterns from surrounding objects on deck surface
- Appropriate weathering (subtle, not dirty or damaged)
- Match the perspective established in the scene

PRESERVE EXACTLY:
- The pool exactly as rendered in previous step
- All landscaping beyond the deck footprint
- House, fence, and all structures
- Original lighting and atmosphere

OUTPUT: Photorealistic image with completed pool deck.
Output at the highest resolution possible."""


def get_water_features_prompt(selections: dict) -> str:
    """Step 4: Add selected water features."""
    selected_features = selections.get('water_features', [])

    if not selected_features:
        return None

    features = [f for f in config.WATER_FEATURES if f['id'] in selected_features]

    if not features:
        return None

    features_text = "\n".join(f"- {f['prompt_hint']}" for f in features)

    return f"""Photorealistic inpainting. Add water features to the pool.

WATER FEATURES TO ADD:
{features_text}

REQUIREMENTS FOR EACH FEATURE:
- Realistic water flow with proper physics
- Natural splash and spray patterns where water meets pool
- Proper lighting interaction (reflections, caustics from moving water)
- Materials and colors matching existing pool finishes
- Seamless integration with pool edge, coping, and deck

POSITIONING:
- Place features in visually balanced, architecturally logical positions
- Waterfall: typically at the deep end or raised bond beam
- Bubblers/jets: typically on tanning ledge or shallow end
- Fire bowls: on deck corners or raised pedestals
- Scuppers: on raised wall section

PRESERVE EXACTLY:
- Pool shape and water color exactly as rendered
- Deck material and color exactly as rendered
- All landscaping, structures, lighting

OUTPUT: Photorealistic image with water features installed.
Output at the highest resolution possible."""


def get_finishing_prompt(selections: dict) -> str:
    """Step 5: Add finishing touches (lighting, landscaping, furniture)."""
    lighting = next(
        (l for l in config.FINISHING_OPTIONS['lighting'] if l['id'] == selections.get('lighting', 'none')),
        config.FINISHING_OPTIONS['lighting'][0]
    )
    landscaping = next(
        (l for l in config.FINISHING_OPTIONS['landscaping'] if l['id'] == selections.get('landscaping', 'none')),
        config.FINISHING_OPTIONS['landscaping'][0]
    )
    furniture = next(
        (f for f in config.FINISHING_OPTIONS['furniture'] if f['id'] == selections.get('furniture', 'none')),
        config.FINISHING_OPTIONS['furniture'][0]
    )

    additions = []
    if lighting['prompt_hint']:
        additions.append(lighting['prompt_hint'])
    if landscaping['prompt_hint']:
        additions.append(landscaping['prompt_hint'])
    if furniture['prompt_hint']:
        additions.append(furniture['prompt_hint'])

    if not additions:
        return None

    additions_text = "\n".join(f"- {a}" for a in additions)

    return f"""Photorealistic inpainting. Add finishing touches to the pool scene.

ADDITIONS:
{additions_text}

REQUIREMENTS:
- All additions must look natural and professionally placed
- Furniture positioned for practical use (facing pool, in shade where logical)
- Landscaping appropriate for Texas climate
- Lighting fixtures consistent with home's architectural style
- All items at proper scale for the space

PRESERVE EXACTLY:
- Pool, water features, and deck exactly as rendered
- Existing landscaping not being enhanced
- House, fence, and all structures
- Original lighting conditions and atmosphere

OUTPUT: Photorealistic final image with all finishing touches.
Output at the highest resolution possible."""


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


def get_prompt(step: str, selections: dict = None) -> str:
    """Get prompt for a specific pipeline step."""
    selections = selections or {}

    if step == 'cleanup':
        return get_cleanup_prompt()
    elif step == 'pool_shell':
        return get_pool_shell_prompt(selections)
    elif step == 'deck':
        return get_deck_prompt(selections)
    elif step == 'water_features':
        return get_water_features_prompt(selections)
    elif step == 'finishing':
        return get_finishing_prompt(selections)
    elif step == 'quality_check':
        return get_quality_check_prompt(selections)
    else:
        raise ValueError(f"Unknown pipeline step: {step}")


# Compatibility aliases for tenant registry
def get_screen_insertion_prompt(feature_type: str, options: dict) -> str:
    """Compatibility wrapper for tenant pipeline."""
    return get_pool_shell_prompt(options)


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
