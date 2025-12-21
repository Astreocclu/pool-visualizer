"""
Windows Visualizer - AI Prompts
Layered rendering pipeline for window replacement visualization.

Pipeline: cleanup → window_frame → grilles_glass → trim → doors → patio_enclosure → quality_check
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

PERSPECTIVE ADJUSTMENT:
Create a perspective ideal for window replacement visualization:
- Front or 3/4 view showing the main facade
- Angle that clearly shows all window openings on visible walls
- Minimize extreme angles that distort window proportions
- Ensure window planes are clearly visible for accurate rendering

OUTPUT: Clean, well-lit house exterior image with all windows clearly visible.
Output at the highest resolution possible."""


def get_window_frame_prompt(selections: dict) -> str:
    """Step 2: Replace/install window frames and doors."""
    from api.tenants.windows import config

    project_type = next(
        (p for p in config.PROJECT_TYPES if p['id'] == selections.get('project_type', 'replace_existing')),
        config.PROJECT_TYPES[0]
    )
    door_type = next(
        (d for d in config.DOOR_TYPES if d['id'] == selections.get('door_type', 'none')),
        config.DOOR_TYPES[0]
    )
    window_type = next(
        (w for w in config.WINDOW_TYPES if w['id'] == selections.get('window_type', 'double_hung')),
        config.WINDOW_TYPES[1]
    )
    window_style = next(
        (s for s in config.WINDOW_STYLES if s['id'] == selections.get('window_style', 'modern')),
        config.WINDOW_STYLES[0]
    )
    frame_material = next(
        (m for m in config.FRAME_MATERIALS if m['id'] == selections.get('frame_material', 'vinyl')),
        config.FRAME_MATERIALS[0]
    )
    frame_color = next(
        (c for c in config.FRAME_COLORS if c['id'] == selections.get('frame_color', 'white')),
        config.FRAME_COLORS[0]
    )

    # Build door section if applicable
    door_section = ""
    if door_type['id'] != 'none':
        door_section = f"""
DOOR INSTALLATION:
- Door type: {door_type['prompt_hint']}
- Frame material: {frame_material['prompt_hint']}
- Frame color: {frame_color['prompt_hint']}
- Position: Install at main patio/entrance opening
- For accordion/bi-fold: Show panels in partially open position to demonstrate folding capability
"""

    # Build project context
    project_context = {
        'replace_existing': "Replace ALL existing windows and doors with new ones.",
        'new_opening': "Create new window and door openings in the walls where specified.",
        'enclose_patio': "Enclose the patio/porch area with new windows and doors, creating a sunroom effect.",
    }.get(project_type['id'], "Replace existing windows and doors.")

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

PRESERVE EXACTLY:
- House structure beyond installation areas
- Roof, siding, landscaping
- Original lighting and atmosphere

OUTPUT: Photorealistic image with new windows{' and doors' if door_type['id'] != 'none' else ''} installed.
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


def get_doors_prompt(selections: dict) -> str:
    """Step 5: Install doors if selected."""
    from api.tenants.windows import config

    door_type = next(
        (d for d in config.DOOR_TYPES if d['id'] == selections.get('door_type', 'none')),
        config.DOOR_TYPES[0]
    )

    # Skip if no door selected
    if door_type['id'] == 'none':
        return None

    frame_material = next(
        (m for m in config.FRAME_MATERIALS if m['id'] == selections.get('frame_material', 'vinyl')),
        config.FRAME_MATERIALS[0]
    )
    frame_color = next(
        (c for c in config.FRAME_COLORS if c['id'] == selections.get('frame_color', 'white')),
        config.FRAME_COLORS[0]
    )

    # Build door-specific installation details
    door_details = {
        'sliding_glass': """
SLIDING GLASS DOOR SPECIFICATIONS:
- Type: Sliding glass patio door with large glass panels
- Track system: Heavy-duty aluminum track at top and bottom
- Panels: 2-4 panels depending on width, one or more slide
- Hardware: Recessed pull handles, keyed lock
- Threshold: Low-profile aluminum threshold with weather seal
- Installation: Show door in partially open position to demonstrate sliding action
- Glass: Large unobstructed panels for maximum view
""",
        'french': """
FRENCH DOOR SPECIFICATIONS:
- Type: Traditional hinged double doors with glass panels
- Operation: Both doors open outward or inward with active/passive configuration
- Panels: Multiple glass panels (lites) in each door with decorative muntins
- Hardware: Traditional lever handles, deadbolt lock, decorative hinges
- Installation: Show doors in elegant closed position with astragal between panels
- Style: Classic divided-lite design with clean, symmetrical appearance
- Threshold: Standard door threshold with weather stripping
""",
        'accordion': """
ACCORDION FOLDING DOOR SPECIFICATIONS:
- Type: Multi-panel folding glass door system (typically 4-8 panels)
- Track system: Heavy-duty top-hung track with bottom guide
- Operation: Panels fold accordion-style, stacking to one or both sides
- Hardware: Continuous hinge system between panels, locking handle
- Installation: Show door in partially folded position (50-75% open) to demonstrate folding capability
- Panels: Each panel 2-3 feet wide, all panels same size
- Opening: Can open up to 90% of the wall when fully folded
- Frame: Minimal frame profile for maximum glass area
""",
        'bifold': """
BI-FOLD DOOR SPECIFICATIONS:
- Type: Paired folding glass door panels (typically 4-6 panels total)
- Track system: Top-mounted track with pivot hinges
- Operation: Panels fold in pairs, connected by hinges
- Hardware: Pivot hardware at top and bottom, central locking mechanism
- Installation: Show door partially open (one pair folded) to demonstrate bi-fold action
- Configuration: Panels fold to one or both sides in pairs
- Frame: Sturdy frame to support paired panel weight
- Opening: Creates wide opening when fully folded (80-85% of wall width)
""",
    }.get(door_type['id'], '')

    return f"""Photorealistic inpainting. Install {door_type['name']} in the designated patio/entrance opening.

{door_details}

DOOR FRAME REQUIREMENTS:
- Frame material: {frame_material['prompt_hint']}
- Frame color: {frame_color['prompt_hint']} (matching existing window frames)
- Frame should be solid and professionally installed
- Proper weather sealing and flashing details
- Frame thickness appropriate to door type and material

GLASS REQUIREMENTS:
- Large glass panels for maximum light and view
- Tempered safety glass (required for doors)
- Subtle reflections showing sky and surrounding environment
- Clean, professional appearance
- For multi-panel doors: Consistent spacing between panels

INSTALLATION REALISM:
- Door must look structurally sound and professionally installed
- Proper integration with house exterior (siding, trim, foundation)
- Realistic shadows cast by door frame and panels
- Appropriate clearance from ground/deck surface
- Weather seals and threshold details visible
- Hardware should appear functional and properly positioned

PRESERVE EXACTLY:
- All windows and their current state
- House structure, siding, roof
- Landscaping and existing features
- Original lighting and atmosphere
- Any trim or enclosures already installed

OUTPUT: Photorealistic image with {door_type['name']} professionally installed.
Output at the highest resolution possible."""


def get_patio_enclosure_prompt(selections: dict) -> str:
    """Step 6: Add patio enclosure if selected."""
    from api.tenants.windows import config

    enclosure_type = next(
        (e for e in config.PATIO_ENCLOSURE_TYPES if e['id'] == selections.get('enclosure_type', 'none')),
        config.PATIO_ENCLOSURE_TYPES[0]
    )

    # Skip if no enclosure selected
    if enclosure_type['id'] == 'none':
        return None

    frame_material = next(
        (m for m in config.FRAME_MATERIALS if m['id'] == selections.get('frame_material', 'vinyl')),
        config.FRAME_MATERIALS[0]
    )
    frame_color = next(
        (c for c in config.FRAME_COLORS if c['id'] == selections.get('frame_color', 'white')),
        config.FRAME_COLORS[0]
    )
    enclosure_glass = next(
        (g for g in config.ENCLOSURE_GLASS_TYPES if g['id'] == selections.get('enclosure_glass_type', 'double_pane')),
        config.ENCLOSURE_GLASS_TYPES[1]
    )

    # Build enclosure-specific details
    enclosure_details = {
        'three_season': f"""
THREE-SEASON SUNROOM SPECIFICATIONS:
- Type: Three-season sunroom with combination of glass windows and screen panels
- Frame: {frame_material['prompt_hint']} frame structure, {frame_color['prompt_hint']} color
- Windows: {enclosure_glass['prompt_hint']} in operable and fixed configurations
- Screens: Removable or retractable screen panels for ventilation
- Roof: Insulated roof panels or glass roof sections
- Foundation: Connect to existing concrete patio slab or deck
- Usage: Designed for spring, summer, and fall use (not climate controlled)

STRUCTURAL INTEGRATION:
- Attach to existing house wall with proper ledger and flashing
- Posts/columns every 6-8 feet for structural support
- Knee walls (2-3 feet) with windows above, or floor-to-ceiling glass
- Gable or shed roof matching house roofline angle
""",
        'four_season': f"""
FOUR-SEASON SUNROOM SPECIFICATIONS:
- Type: Fully insulated, climate-controlled sunroom addition
- Frame: {frame_material['prompt_hint']} thermal-break frame, {frame_color['prompt_hint']} color
- Windows: {enclosure_glass['prompt_hint']} for energy efficiency
- Roof: Fully insulated roof system with interior ceiling finish
- Foundation: Insulated foundation walls on existing slab or new foundation
- HVAC: Visible supply/return vents for heating and cooling
- Usage: Year-round comfort, true room addition

STRUCTURAL INTEGRATION:
- Attach to house with proper structural connection and insulation
- Support posts/columns integrated into wall design
- Insulated knee walls (2-3 feet) with large windows above
- Cathedral or flat ceiling with proper insulation and finish
- Proper roofing that matches or complements house
""",
        'screen_room': f"""
SCREEN ROOM SPECIFICATIONS:
- Type: Screened patio enclosure with aluminum frame
- Frame: Aluminum frame structure, {frame_color['prompt_hint']} color (powder-coated)
- Screens: High-quality fiberglass or aluminum mesh, charcoal or gray color
- Screen panels: Floor-to-ceiling or with kickplate at bottom
- Roof: Insulated aluminum roof panels or open to existing patio cover
- Foundation: Attach to existing concrete patio slab
- Door: Screen door with aluminum frame and self-closing mechanism

STRUCTURAL INTEGRATION:
- Aluminum posts every 6-8 feet
- Attach to house wall with aluminum mounting brackets
- Screen panels in aluminum channels (top, bottom, sides)
- Simple, functional design focused on bug protection
- Minimal sightlines for maximum view
""",
        'glass_walls': f"""
RETRACTABLE GLASS WALL SPECIFICATIONS:
- Type: Modern sliding/folding glass panel system
- Frame: {frame_material['prompt_hint']} minimal frame, {frame_color['prompt_hint']} color
- Glass: {enclosure_glass['prompt_hint']}, floor-to-ceiling panels
- Operation: Panels slide and stack to one or both sides (show partially open)
- Track: Top-mounted track system with bottom guide
- Panels: Frameless or minimal-frame glass panels, each 3-4 feet wide
- Opening: Opens completely to merge indoor and outdoor spaces

STRUCTURAL INTEGRATION:
- Header beam integrated into house wall or patio structure
- Support posts at corners and intervals (if needed)
- Panels stack neatly when open (show 2-3 panels stacked)
- Modern, clean aesthetic with minimal visible hardware
- Proper weather sealing when closed
""",
    }.get(enclosure_type['id'], '')

    return f"""Photorealistic inpainting. Add {enclosure_type['name']} enclosing the patio area.

{enclosure_details}

INSTALLATION REQUIREMENTS:
- Structure must attach to existing house wall
- Use existing patio slab as foundation (no excavation)
- Maintain proper scale and proportion relative to house
- Structure should look professionally designed and permitted
- Proper roofline integration with house architecture
- Support posts/columns properly sized and positioned

GLASS/SCREEN REQUIREMENTS:
- Consistent material throughout the enclosure
- Realistic reflections in glass (showing sky, trees, surroundings)
- For screens: Fine mesh texture, slightly transparent appearance
- Clean, professional installation appearance
- Proper spacing and alignment of panels

INTEGRATION WITH HOUSE:
- Enclosure must look like an intentional addition, not an afterthought
- Siding/trim connection points should be clean and professional
- Roof should complement existing house roof
- Color scheme should harmonize with house exterior
- Appropriate architectural style for the house

PRESERVE EXACTLY:
- All windows and doors already installed
- House structure, siding, and roof beyond attachment points
- Landscaping outside the enclosure area
- Original lighting and atmosphere
- Existing trim and features

OUTPUT: Photorealistic image with {enclosure_type['name']} professionally installed around patio.
Output at the highest resolution possible."""


def get_quality_check_prompt(scope: dict = None) -> str:
    """Step 7: Quality check comparing original to final result."""
    scope = scope or {}

    # Build additional checks based on scope
    additional_checks = []

    if scope.get('doors'):
        additional_checks.append("""
7. DOOR INSTALLATION (if applicable)
   - Is door positioned correctly in opening?
   - Does door type match specifications (sliding/french/accordion/bifold)?
   - Is door frame material and color consistent with windows?
   - Do multi-panel doors show proper operation (partially open position)?
   - Are door reflections and glass realistic?
   - Does hardware appear functional and properly positioned?
""")

    if scope.get('patio_enclosure'):
        additional_checks.append("""
8. PATIO ENCLOSURE (if applicable)
   - Does enclosure attach naturally to the house wall?
   - Are support posts/columns properly sized and positioned?
   - Is the roof properly integrated with house architecture?
   - Do glass panels or screens look realistic and professionally installed?
   - Is the enclosure scale appropriate to the patio and house?
   - Does structure look permitted and professionally designed?
""")

    additional_checks_text = '\n'.join(additional_checks) if additional_checks else ''

    return f"""You are a Quality Control AI for window replacement visualization. You will receive two images.

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
{additional_checks_text}
SCORING GUIDE:
- 0.0 to 0.4: FAIL - Major issues (floating windows, wrong sizes, inconsistent styles, significant artifacts)
- 0.5 to 0.6: POOR - Usable but obvious issues (misaligned windows, unrealistic materials, poor reflections)
- 0.7 to 0.8: GOOD - Minor imperfections only (subtle reflection issues, minor alignment variations)
- 0.9 to 1.0: EXCELLENT - Highly realistic, no obvious issues

RETURN ONLY VALID JSON:
{{
    "score": <float between 0.0 and 1.0>,
    "issues": [<list of specific issues found, empty if none>],
    "recommendation": "<PASS or REGENERATE>"
}}

A score below 0.6 should recommend REGENERATE.
Be strict - homeowners will make purchasing decisions based on this visualization."""


def get_prompt(step: str, selections: dict = None, scope: dict = None) -> str:
    """Get prompt for a specific pipeline step."""
    selections = selections or {}
    scope = scope or {}

    if step == 'cleanup':
        return get_cleanup_prompt()
    elif step == 'window_frame':
        return get_window_frame_prompt(selections)
    elif step == 'grilles_glass':
        return get_grilles_glass_prompt(selections)
    elif step == 'trim':
        return get_trim_prompt(selections)
    elif step == 'doors':
        return get_doors_prompt(selections)
    elif step == 'patio_enclosure':
        return get_patio_enclosure_prompt(selections)
    elif step == 'quality_check':
        return get_quality_check_prompt(scope)
    else:
        raise ValueError(f"Unknown pipeline step: {step}")


# Compatibility aliases for tenant registry
def get_screen_insertion_prompt(feature_type: str, options: dict) -> str:
    """Compatibility wrapper for tenant pipeline."""
    return get_window_frame_prompt(options)
