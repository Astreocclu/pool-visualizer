"""
Roofs Vertical AI Prompts
Generates prompts for each step in the 5-step pipeline.
"""


def get_cleanup_prompt():
    """Step 1: Remove existing roof/solar for clean slate."""
    return """Remove the existing roof and any solar panels from this house image.

Replace the roof area with a neutral gray placeholder that maintains the exact roof shape and pitch.
Keep the house structure, walls, windows, gutters, and all other elements unchanged.
The goal is to prepare a clean canvas for the new roof installation."""


def get_roof_material_prompt(selections):
    """Step 2: Install new roof material in selected color."""
    material = selections.get('roof_material', 'asphalt_architectural')
    material_hint = selections.get('roof_material_hint', 'dimensional architectural asphalt shingles')
    color = selections.get('roof_color', 'charcoal')
    color_hint = selections.get('roof_color_hint', 'charcoal gray')

    return f"""Install a new {material_hint} roof in {color_hint} color on this house.

The roof should:
- Match the existing roof shape, pitch, and architecture perfectly
- Show realistic texture and detail for {material_hint}
- Use {color_hint} as the primary color
- Include proper shingle/tile overlap patterns and shadow lines
- Look professionally installed with clean lines
- Maintain all existing architectural details (dormers, valleys, ridges, eaves)

Make the roof look photorealistic and professionally installed."""


def get_solar_panels_prompt(selections):
    """Step 3: Add solar panels (conditional - only if solar_option != 'none')."""
    solar_option = selections.get('solar_option', 'none')

    if solar_option == 'none':
        return None  # Skip this step

    solar_hint = selections.get('solar_option_hint', '')

    return f"""Add {solar_hint} to this house.

The solar installation should:
- Use modern black monocrystalline solar panels with realistic grid lines
- {solar_hint}
- Mount panels flush to the roof surface with proper racking
- Maintain consistent spacing and alignment in neat rows
- Avoid shaded areas, roof vents, and chimneys
- Look professionally installed with clean wiring runs
- Show realistic reflections and panel texture

Make the solar installation look professional and photorealistic."""


def get_gutters_trim_prompt(selections):
    """Step 4: Add gutters and trim (conditional - only if gutter_option != 'none')."""
    gutter_option = selections.get('gutter_option', 'none')

    if gutter_option == 'none':
        return None  # Skip this step

    gutter_hint = selections.get('gutter_option_hint', '')

    return f"""Install {gutter_hint} on this house.

The gutter system should:
- {gutter_hint}
- Run along all roof edges that drain water
- Include properly placed downspouts at corners
- Match the roof lines and architectural style
- Show realistic shadows and highlights
- Look professionally installed with clean joints

Make the gutter installation look professional and photorealistic."""


def get_quality_check_prompt():
    """Step 5: Final quality check and refinement."""
    return """Perform final quality check and refinement on this roof/solar installation image.

Ensure:
- All roof materials look realistic with proper texture and lighting
- Solar panels (if present) are properly aligned and realistic
- Gutters (if present) are properly installed
- Shadows and lighting are consistent across all elements
- No artifacts, blurring, or unrealistic elements
- The overall composition looks professional and photorealistic
- All architectural details are preserved

Make any final adjustments needed for a polished, professional result."""


def get_prompt(step, selections):
    """
    Router function to get the prompt for a specific pipeline step.

    Args:
        step: Pipeline step name ('cleanup', 'roof_material', 'solar_panels', 'gutters_trim', 'quality_check')
        selections: User selections dict containing roof_material, roof_color, solar_option, gutter_option, etc.

    Returns:
        Prompt string for the step, or None if step should be skipped
    """
    if step == 'cleanup':
        return get_cleanup_prompt()
    elif step == 'roof_material':
        return get_roof_material_prompt(selections)
    elif step == 'solar_panels':
        return get_solar_panels_prompt(selections)
    elif step == 'gutters_trim':
        return get_gutters_trim_prompt(selections)
    elif step == 'quality_check':
        return get_quality_check_prompt()
    else:
        return None
