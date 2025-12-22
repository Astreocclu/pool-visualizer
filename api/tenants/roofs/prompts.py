"""
Roofs/Solar Visualizer - AI Prompts
Texas-focused roofing and solar visualization pipeline.

Pipeline: cleanup -> roof_material -> solar_panels -> gutters_trim -> quality_check
"""

from api.tenants.roofs import config


def get_cleanup_prompt() -> str:
    """Step 1: Clean the image and enhance for roof visualization."""
    return """Photorealistic image editing. Prepare this house for roof replacement visualization.

WEATHER AND LIGHTING:
Make the weather conditions ideal for roof inspection: bright, clear Texas daylight.
Optimal lighting angle to show roof texture and planes clearly.

REMOVE ONLY THESE TEMPORARY ITEMS:
- Ladders, tools, or construction equipment on roof
- Holiday decorations and lights
- Debris, leaves, branches on roof surface
- Temporary tarps or patches
- Satellite dishes (unless explicitly preserved)
- TV antennas

PRESERVE EXACTLY AS-IS:
- House structure and all architectural details
- All windows and doors
- Chimneys (shape and position)
- Existing vents and skylights (positions only)
- Gutters and downspouts
- Landscaping and trees
- Adjacent structures and fencing

PERSPECTIVE ADJUSTMENT:
Create a perspective ideal for roof material assessment:
- Elevated viewpoint showing at least two roof planes
- Clear view of roof edges and transitions
- Include eave-to-ridge visibility where possible
- Maintain natural architectural lines

OUTPUT: Clean, well-lit house image with optimal roof visibility.
Output at the highest resolution possible."""


def get_roof_material_prompt(selections: dict) -> str:
    """Step 2: Replace roof material with selected options."""
    material = next(
        (m for m in config.ROOF_MATERIALS if m['id'] == selections.get('roof_material', 'asphalt_architectural')),
        config.ROOF_MATERIALS[1]
    )
    color = next(
        (c for c in config.ROOF_COLORS if c['id'] == selections.get('roof_color', 'charcoal')),
        config.ROOF_COLORS[0]
    )

    # Texas-specific hints based on material
    texas_hints = {
        'asphalt': """
TEXAS CLIMATE CONSIDERATIONS:
- UV-resistant granules with realistic color variation
- Class 4 impact-rated appearance (hail resistance)
- Algae-resistant strips visible on lower courses
- Proper starter strips at eaves and rakes""",
        'tile': """
TEXAS CLIMATE CONSIDERATIONS:
- Authentic Mediterranean/Spanish profile for Austin/SA markets
- Natural terracotta color variation typical of aged tile
- High-wind rated installation (hurricane clips not visible but implied)
- Proper underlayment visible at edges""",
        'metal': """
TEXAS CLIMATE CONSIDERATIONS:
- Matte or low-gloss finish to reduce glare
- Standing seam joints running parallel to slope
- Thermal expansion gaps at transitions
- Proper flashing at all penetrations""",
    }

    material_type = 'asphalt' if 'asphalt' in material['id'] else \
                   'tile' if 'tile' in material['id'] or 'clay' in material['id'] or 'concrete' in material['id'] else \
                   'metal' if 'metal' in material['id'] else 'asphalt'
    texas_specific = texas_hints.get(material_type, texas_hints['asphalt'])

    return f"""Photorealistic inpainting. Replace the existing roof with new roofing material.

ROOF SPECIFICATIONS:
- Material: {material['prompt_hint']}
- Color: {color['prompt_hint']}

DIMENSIONAL ACCURACY:
- Maintain exact roof pitch, angles, and geometry from original
- Preserve all valleys, hips, ridges, and dormers
- Keep existing roof penetrations in same locations
- Match existing flashing details at walls and edges

MATERIAL REALISM:
- Show proper alignment and installation pattern for {material['name']}
- Include appropriate shadow lines between courses/panels
- Add realistic texture grain and surface variation
- Install proper ridge caps and edge treatments
- Natural weathering appropriate for 1-year-old installation
{texas_specific}

COLOR AND FINISH:
- {color['prompt_hint']} color across entire roof surface
- Realistic sun reflection appropriate for material type
- Subtle variation within color family for authenticity

CRITICAL INTEGRATION:
- Roof must look INSTALLED, not pasted or floating
- Shadows must match sun direction in image
- Scale must be correct relative to house size
- Seamless transition to existing gutters and fascia
- Match architectural style of home

PRESERVE EXACTLY:
- All walls, windows, doors unchanged
- Chimneys (update only flashing, not structure)
- Gutters and downspouts (unless specified otherwise)
- Landscaping and surroundings
- House foundation and yard

OUTPUT: Photorealistic roof replacement showing new {material['name']} perfectly integrated.
Output at the highest resolution possible."""


def get_solar_panels_prompt(selections: dict) -> str:
    """Step 3: Add solar panels to the roof (conditional)."""
    solar_option = next(
        (s for s in config.SOLAR_OPTIONS if s['id'] == selections.get('solar_option', 'none')),
        config.SOLAR_OPTIONS[0]
    )

    if solar_option['id'] == 'none':
        return None

    return f"""Photorealistic inpainting. Install solar panel system on the new roof.

SOLAR SYSTEM SPECIFICATIONS:
- Coverage: {solar_option['prompt_hint']}

PANEL PLACEMENT REQUIREMENTS:
- Primary placement on south-facing roof planes
- Secondary on west/east planes if south insufficient
- Maintain fire setbacks: 36" from ridge, 18" from edges
- Leave 18" access pathways along roof edges
- Avoid shading from chimneys, vents, trees

MOUNTING SYSTEM:
- Flush-mounted panels parallel to roof surface
- Rail system visible under panels (black or silver aluminum)
- Flashings integrated with roof material
- Panel spacing: 0.5-1" between panels for thermal expansion
- Proper tilt angle for Central Texas latitude (25-30°)

ELECTRICAL COMPONENTS:
- Inverter mounted on exterior garage wall or side of house
- Conduit routing from roof edge down to inverter
- Utility disconnect box near main panel
- AC wiring conduit painted to match house

VISUAL REALISM:
- Modern monocrystalline panels with anti-reflective coating
- Photovoltaic cells visible through tempered glass
- Aluminum frames with proper corner connectors
- Realistic dust pattern for 6-month installation
- Wiring junction boxes at panel groupings

SHADOWS AND LIGHTING:
- Panels cast subtle shadows on roof surface
- Minimal glare (anti-reflective coating)
- Metallic frame sheen matching sun angle

TEXAS CONSIDERATIONS:
- Panels rated for 140+ mph wind loads
- Heat dissipation gaps for 100°F+ operation
- Hail-resistant tempered glass visible

PRESERVE EXACTLY:
- New roof material exactly as installed
- All architectural features unchanged
- Existing landscaping
- House structure and foundation

OUTPUT: Photorealistic solar installation integrated with new roof.
Output at the highest resolution possible."""


def get_gutters_trim_prompt(selections: dict) -> str:
    """Step 4: Add gutters and trim (conditional)."""
    gutter = next(
        (g for g in config.GUTTER_OPTIONS if g['id'] == selections.get('gutter_option', 'none')),
        config.GUTTER_OPTIONS[0]
    )

    if gutter['id'] == 'none':
        return None

    return f"""Photorealistic inpainting. Install new gutter system on this house.

GUTTER SPECIFICATIONS:
- Type: {gutter['prompt_hint']}

GUTTER REQUIREMENTS:
- Install along all roof eaves
- Seamless design with proper slope toward downspouts (1/4" per 10 feet)
- Appropriate bracket spacing (24-36")
- Downspouts at corners and every 30-40 feet of run
- Downspouts routed to drainage areas away from foundation

VISUAL DETAILS:
- Gutter profile matching specification
- Proper end caps and corners
- Clean joints and connections
- Realistic shadows from gutter depth
- Color matching or complementing trim

INTEGRATION:
- Gutters must attach cleanly to fascia board
- Downspouts aligned with house corners
- No gaps or misalignment visible
- Professional installation appearance

PRESERVE EXACTLY:
- New roof material exactly as installed
- Solar panels (if installed) unchanged
- Windows, doors, and structural details
- Landscaping and surroundings

OUTPUT: Photorealistic gutter installation integrated with house.
Output at the highest resolution possible."""


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

    # Adjust numbering based on what sections are present
    perspective_num = 2
    if has_solar:
        perspective_num += 1
    if has_gutters:
        perspective_num += 1

    texas_num = perspective_num + 1
    preservation_num = texas_num + 1

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
{solar_section}
{gutter_section}
{perspective_num}. PERSPECTIVE AND SCALE
   - Does the roof maintain original perspective exactly?
   - Is scale correct relative to house and surroundings?
   - Do shadows from roof/panels match sun direction?
   - Are architectural proportions preserved?

{texas_num}. TEXAS-SPECIFIC CHECKS
   - Does material show appropriate heat/UV characteristics?
   - Are hail/wind considerations addressed (proper fastening)?
   - Is color appropriate for thermal performance?
   - Are solar panels angled for Texas latitude (~30°)?

{preservation_num}. PRESERVATION
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


def get_prompt(step: str, selections: dict = None) -> str:
    """Get prompt for a specific pipeline step."""
    selections = selections or {}

    if step == 'cleanup':
        return get_cleanup_prompt()
    elif step == 'roof_material':
        return get_roof_material_prompt(selections)
    elif step == 'solar_panels':
        return get_solar_panels_prompt(selections)
    elif step == 'gutters_trim':
        return get_gutters_trim_prompt(selections)
    elif step == 'quality_check':
        return get_quality_check_prompt(selections)
    else:
        raise ValueError(f"Unknown pipeline step: {step}")


# Compatibility alias for tenant registry
def get_screen_insertion_prompt(feature_type: str, options: dict) -> str:
    """Compatibility wrapper for tenant pipeline."""
    return get_roof_material_prompt(options)


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
