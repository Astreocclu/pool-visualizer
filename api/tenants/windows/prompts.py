"""
Windows Visualizer - AI Prompts
Layered rendering pipeline for window replacement visualization.

Pipeline: cleanup → window_frame → grilles_glass → trim → quality_check
"""

from api.tenants.windows import config


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

OUTPUT: Clean, well-lit house exterior image with all windows clearly visible.
Output at the highest resolution possible."""


def get_window_frame_prompt(selections: dict) -> str:
    """Step 2: Replace all window frames with selected options."""
    window_type = next(
        (w for w in config.WINDOW_TYPES if w['id'] == selections.get('window_type', 'double_hung')),
        config.WINDOW_TYPES[1]
    )
    window_style = next(
        (s for s in config.WINDOW_STYLES if s['id'] == selections.get('window_style', 'traditional')),
        config.WINDOW_STYLES[1]
    )
    frame_material = next(
        (m for m in config.FRAME_MATERIALS if m['id'] == selections.get('frame_material', 'vinyl')),
        config.FRAME_MATERIALS[0]
    )
    frame_color = next(
        (c for c in config.FRAME_COLORS if c['id'] == selections.get('frame_color', 'white')),
        config.FRAME_COLORS[0]
    )

    return f"""Photorealistic inpainting. Replace ALL windows on this house with new windows.

WINDOW SPECIFICATIONS:
- Type: {window_type['prompt_hint']}
- Style: {window_style['prompt_hint']}
- Frame material: {frame_material['prompt_hint']}
- Frame color: {frame_color['prompt_hint']}

WINDOW REPLACEMENT REQUIREMENTS:
- Replace EVERY visible window on the house
- Maintain exact window opening sizes and positions from original image
- Keep windows properly aligned and level
- Window frames should be appropriate width for the material (vinyl slightly thicker than aluminum)
- Glass should appear clean and new with subtle reflections
- Maintain consistent style across all windows on the house

WINDOW REALISM:
- Frames must look like actual {frame_material['name']} material with authentic texture
- {frame_color['name']} color should be uniform and professional
- Glass should have realistic reflections (sky, trees, neighboring structures)
- Subtle depth to frame profile appropriate to {window_type['name']} windows
- No distortion or warping of window frames
- Proper weatherseals visible where appropriate

CRITICAL INTEGRATION:
- Windows must look INSTALLED in the wall, not floating or pasted on
- Maintain the relationship between window and surrounding siding/trim
- Shadows cast correctly based on frame depth and sun position
- Scale must match the house architecture
- Preserve all non-window elements (doors, siding, roof, landscaping)
- Windows should look consistent with each other in terms of reflection and lighting

PRESERVE EXACTLY:
- House siding, doors, roof, and all architectural features
- Landscaping, walkways, driveways
- All structures outside the window replacements
- Original lighting conditions and atmosphere

OUTPUT: Photorealistic image with all windows replaced with new {window_type['name']} windows.
Output at the highest resolution possible."""


def get_grilles_glass_prompt(selections: dict) -> str:
    """Step 3: Add grille patterns and glass effects to all windows."""
    grille_pattern = next(
        (g for g in config.GRILLE_PATTERNS if g['id'] == selections.get('grille_pattern', 'none')),
        config.GRILLE_PATTERNS[0]
    )
    glass_option = next(
        (g for g in config.GLASS_OPTIONS if g['id'] == selections.get('glass_option', 'clear')),
        config.GLASS_OPTIONS[0]
    )

    # Skip this step if no visible changes needed
    if grille_pattern['id'] == 'none' and glass_option['id'] in ['clear', 'low_e']:
        return None

    features = []
    if grille_pattern['id'] != 'none':
        features.append(f"Grille pattern: {grille_pattern['prompt_hint']}")
    if glass_option['id'] not in ['clear', 'low_e']:
        features.append(f"Glass type: {glass_option['prompt_hint']}")

    if not features:
        return None

    features_text = "\n".join(f"- {f}" for f in features)

    return f"""Photorealistic inpainting. Add grilles and glass effects to all windows.

FEATURES TO ADD:
{features_text}

GRILLE REQUIREMENTS (if applicable):
- Apply grilles consistently to ALL windows on the house
- Grilles should appear as thin, precise bars matching the window frame color
- Pattern should be geometrically accurate and symmetrical
- Grilles should appear to be between the glass panes or on the surface
- No warping or distortion of grille lines
- Proper depth and shadow to show grille dimension

GLASS REQUIREMENTS (if applicable):
- Apply glass effect consistently to ALL windows
- Frosted/obscure glass should still show subtle light transmission
- Maintain realistic reflections appropriate to the glass type
- Privacy glass should obscure interior view while allowing light
- Textured glass should show consistent pattern

PRESERVE EXACTLY:
- Window frames and their material/color exactly as rendered
- All architectural features, siding, doors
- Landscaping and structures
- Original lighting and atmosphere

OUTPUT: Photorealistic image with grilles and glass effects applied.
Output at the highest resolution possible."""


def get_trim_prompt(selections: dict) -> str:
    """Step 4: Add exterior trim around windows."""
    trim_style = next(
        (t for t in config.TRIM_STYLES if t['id'] == selections.get('trim_style', 'standard')),
        config.TRIM_STYLES[0]
    )
    frame_color = next(
        (c for c in config.FRAME_COLORS if c['id'] == selections.get('frame_color', 'white')),
        config.FRAME_COLORS[0]
    )

    # Skip if standard trim
    if trim_style['id'] == 'standard':
        return None

    return f"""Photorealistic inpainting. Add exterior trim around all windows.

TRIM SPECIFICATIONS:
- Style: {trim_style['prompt_hint']}
- Color: {frame_color['prompt_hint']} (matching window frames)

TRIM REQUIREMENTS:
- Apply trim consistently around ALL windows on the house
- Trim should frame each window with appropriate width for the style
- Craftsman trim: wider, more substantial molding with clean lines
- Colonial trim: traditional molding with decorative edge detail
- Modern trim: minimal, flat profile
- Trim color should match the window frame color
- Proper depth and shadow showing trim projection from siding
- Clean, professional installation appearance

INTEGRATION:
- Trim should integrate naturally with house siding
- Corners should be properly mitered at 45-degree angles
- Consistent reveal/spacing around window frames
- Appropriate to the house architectural style
- Shadows cast correctly based on trim depth and sun position

PRESERVE EXACTLY:
- Window frames, grilles, and glass exactly as rendered
- House siding, doors, roof, and all other features
- Landscaping and structures
- Original lighting and atmosphere

OUTPUT: Photorealistic image with exterior window trim installed.
Output at the highest resolution possible."""


def get_quality_check_prompt(scope: dict = None) -> str:
    """Step 5: Quality check comparing original to final result."""
    return """You are a Quality Control AI for window replacement visualization. You will receive two images.

IMAGE 1: The REFERENCE image (original house before window replacement)
IMAGE 2: The FINAL RESULT (house with new windows installed)

EVALUATE THE VISUALIZATION:

1. WINDOW PLACEMENT
   - Are all windows maintained in their original positions?
   - Are window sizes consistent with the original openings?
   - Are windows properly aligned and level?
   - Is the spacing between windows preserved?

2. WINDOW REALISM
   - Do the window frames look like authentic material (not painted/flat)?
   - Is the frame color uniform and professional across all windows?
   - Are glass reflections realistic and consistent?
   - Do windows have proper depth and dimension?
   - Are all windows the same style and type?

3. INTEGRATION
   - Do windows look INSTALLED vs. pasted/floating on the wall?
   - Is the relationship with surrounding siding natural?
   - Are shadows cast correctly based on frame depth?
   - Do windows match the house architectural style?

4. GRILLES & GLASS (if applicable)
   - Are grille patterns consistent across all windows?
   - Are grille lines straight, symmetrical, and properly spaced?
   - Does glass treatment (frosted, textured, etc.) look realistic?
   - Are privacy glass effects appropriate?

5. TRIM (if applicable)
   - Is trim applied consistently around all windows?
   - Are trim corners properly mitered?
   - Does trim color match window frames?
   - Is trim depth and shadow realistic?

6. PRESERVATION
   - Are house siding, doors, and roof intact?
   - Is landscaping preserved outside work area?
   - Are there any unwanted artifacts or deletions?
   - Are reflections in glass appropriate (showing sky, trees, etc.)?

SCORING GUIDE:
- 0.0 to 0.4: FAIL - Major issues (floating windows, wrong sizes, inconsistent styles, significant artifacts)
- 0.5 to 0.6: POOR - Usable but obvious issues (misaligned windows, unrealistic materials, poor reflections)
- 0.7 to 0.8: GOOD - Minor imperfections only (subtle reflection issues, minor alignment variations)
- 0.9 to 1.0: EXCELLENT - Highly realistic, no obvious issues

RETURN ONLY VALID JSON:
{
    "score": <float between 0.0 and 1.0>,
    "issues": [<list of specific issues found, empty if none>],
    "recommendation": "<PASS or REGENERATE>"
}

A score below 0.6 should recommend REGENERATE.
Be strict - homeowners will make purchasing decisions based on this visualization."""


def get_prompt(step: str, selections: dict = None) -> str:
    """Get prompt for a specific pipeline step."""
    selections = selections or {}

    if step == 'cleanup':
        return get_cleanup_prompt()
    elif step == 'window_frame':
        return get_window_frame_prompt(selections)
    elif step == 'grilles_glass':
        return get_grilles_glass_prompt(selections)
    elif step == 'trim':
        return get_trim_prompt(selections)
    elif step == 'quality_check':
        return get_quality_check_prompt()
    else:
        raise ValueError(f"Unknown pipeline step: {step}")


# Compatibility aliases for tenant registry
def get_screen_insertion_prompt(feature_type: str, options: dict) -> str:
    """Compatibility wrapper for tenant pipeline."""
    return get_window_frame_prompt(options)
