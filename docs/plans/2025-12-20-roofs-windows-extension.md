# Roofs/Solar Tenant + Windows Extension Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create roofs/solar tenant and extend windows tenant with doors/patio enclosure scopes.

**Architecture:** Multi-tenant system with scope-based conditional pipeline steps. Each tenant has config.py (options, pricing, pipeline) and prompts.py (layered AI prompts). Follows established pools tenant pattern.

**Tech Stack:** Django 4.0, Python 3.10, pytest

---

## Phase 1: Cleanup Old Information

### Task 1: Fix Parent CLAUDE.md Port Reference

**Files:**
- Modify: `/home/reid/testhome/CLAUDE.md` (line ~15)

**Step 1: Read current file and identify the issue**

Current line shows:
```markdown
| [pools-visualizer](./pools-visualizer/) | 8001 | pools_db.sqlite3 | Active |
```

Should be:
```markdown
| [pools-visualizer](./pools-visualizer/) | 8006 | db.sqlite3 | Active |
```

**Step 2: Make the edit**

Change port from `8001` to `8006` and database from `pools_db.sqlite3` to `db.sqlite3`.

**Step 3: Verify the change**

Run: `grep "pools-visualizer" /home/reid/testhome/CLAUDE.md`
Expected: Line shows port 8006

**Step 4: Commit**

```bash
git add /home/reid/testhome/CLAUDE.md
git commit -m "docs: fix pools-visualizer port reference (8001 → 8006)"
```

---

### Task 2: Clean Up Legacy Security Screen Prompts

**Files:**
- Modify: `api/visualizer/prompts.py`

**Step 1: Read current file**

Run: `cat api/visualizer/prompts.py`

This file contains legacy security screen prompts copied from boss. These should be removed or replaced with a redirect to the proper tenant prompts.

**Step 2: Replace with tenant redirect**

Replace entire file content with:

```python
"""
Pool Visualizer - Prompts
-------------------------
DEPRECATED: This file exists for backwards compatibility.
Use tenant-specific prompts instead:
  - api/tenants/pools/prompts.py
  - api/tenants/windows/prompts.py
  - api/tenants/roofs/prompts.py
"""

def get_cleanup_prompt():
    """Redirect to pools tenant."""
    from api.tenants.pools import prompts
    return prompts.get_cleanup_prompt()


def get_screen_insertion_prompt(feature_type: str, options: dict):
    """Redirect to pools tenant."""
    from api.tenants.pools import prompts
    return prompts.get_screen_insertion_prompt(feature_type, options)


def get_quality_check_prompt(scope: dict = None):
    """Redirect to pools tenant."""
    from api.tenants.pools import prompts
    return prompts.get_quality_check_prompt(scope)
```

**Step 3: Run existing tests to ensure no breakage**

Run: `cd /home/reid/testhome/pools-visualizer && source venv/bin/activate && python3 -m pytest api/tests/ -v --tb=short -x`
Expected: Tests pass (or identify which tests need updating)

**Step 4: Commit**

```bash
git add api/visualizer/prompts.py
git commit -m "refactor: replace legacy prompts with tenant redirects"
```

---

## Phase 2: Create Roofs/Solar Tenant

### Task 3: Create Roofs Tenant Directory Structure

**Files:**
- Create: `api/tenants/roofs/__init__.py`

**Step 1: Create the __init__.py**

```python
"""Roofs/Solar tenant package."""
from .config import RoofsTenantConfig, get_config, get_full_config_with_pricing

__all__ = ['RoofsTenantConfig', 'get_config', 'get_full_config_with_pricing']
```

**Step 2: Verify file exists**

Run: `ls -la api/tenants/roofs/`
Expected: Shows `__init__.py`

**Step 3: Commit**

```bash
git add api/tenants/roofs/__init__.py
git commit -m "feat(roofs): create tenant package structure"
```

---

### Task 4: Create Roofs Config - Part 1 (Materials & Colors)

**Files:**
- Create: `api/tenants/roofs/config.py`

**Step 1: Write the config file with materials and colors**

```python
"""
Roofs/Solar Vertical Configuration
Port: 8006 (same as pools - tenant switching via ACTIVE_TENANT)
Pipeline: cleanup -> roof_material -> solar_panels -> finishing -> quality_check
"""
from api.tenants.base import BaseTenantConfig

VERTICAL_NAME = "roofs"
VERTICAL_DISPLAY_NAME = "Roof Replacement & Solar"

ROOF_MATERIALS = [
    {
        'id': 'asphalt_3tab',
        'name': '3-Tab Asphalt Shingles',
        'price_per_sqft': 4.50,
        'prompt_hint': 'basic 3-tab asphalt shingle roof with flat appearance',
        'description': 'Budget-friendly, 15-20 year lifespan',
    },
    {
        'id': 'asphalt_architectural',
        'name': 'Architectural Shingles',
        'price_per_sqft': 5.50,
        'prompt_hint': 'dimensional architectural asphalt shingles with shadow lines and depth',
        'description': 'Most popular, 25-30 year lifespan, Class 4 hail rating available',
        'popular': True,
    },
    {
        'id': 'tile_clay',
        'name': 'Clay Tile',
        'price_per_sqft': 18.00,
        'prompt_hint': 'Mediterranean-style barrel clay tile roof with natural terracotta color variation',
        'description': 'Traditional Texas/Spanish style, 50+ year lifespan, excellent heat resistance',
    },
    {
        'id': 'tile_concrete',
        'name': 'Concrete Tile',
        'price_per_sqft': 12.50,
        'prompt_hint': 'concrete tile roof with Spanish S-profile or flat shake pattern',
        'description': 'Durable alternative to clay, 40+ year lifespan, high wind resistance',
    },
    {
        'id': 'metal_standing_seam',
        'name': 'Standing Seam Metal',
        'price_per_sqft': 14.00,
        'prompt_hint': 'modern standing seam metal roof with vertical ribs and concealed fasteners',
        'description': 'Contemporary look, 50+ year lifespan, excellent for solar integration',
        'popular': True,
    },
    {
        'id': 'metal_corrugated',
        'name': 'Corrugated Metal',
        'price_per_sqft': 9.50,
        'prompt_hint': 'corrugated metal roof with exposed fasteners and rustic appearance',
        'description': 'Hill Country/ranch style, 40+ year lifespan',
    },
    {
        'id': 'slate',
        'name': 'Natural Slate',
        'price_per_sqft': 25.00,
        'prompt_hint': 'natural slate stone roof with subtle color variation and textured surface',
        'description': 'Premium natural stone, 75-100+ year lifespan',
    },
    {
        'id': 'wood_shake',
        'name': 'Cedar Wood Shake',
        'price_per_sqft': 11.00,
        'prompt_hint': 'natural cedar wood shake roof with rustic weathered texture',
        'description': 'Rustic aesthetic, 25-30 year lifespan, requires maintenance',
    },
    {
        'id': 'tpo_flat',
        'name': 'TPO/Single-Ply Membrane',
        'price_per_sqft': 8.50,
        'prompt_hint': 'white TPO membrane on flat or low-slope roof section',
        'description': 'For flat/commercial sections, energy-efficient, 20-30 year lifespan',
    },
]

ROOF_COLORS = [
    {'id': 'charcoal', 'name': 'Charcoal', 'prompt_hint': 'dark charcoal gray', 'thermal_hint': 'Absorbs heat - pair with radiant barrier'},
    {'id': 'weathered_wood', 'name': 'Weathered Wood', 'prompt_hint': 'multi-tone brown weathered wood appearance', 'thermal_hint': 'Medium heat absorption'},
    {'id': 'desert_tan', 'name': 'Desert Tan', 'prompt_hint': 'light desert tan/sand color', 'thermal_hint': 'Good solar reflectance for Texas heat'},
    {'id': 'slate_gray', 'name': 'Slate Gray', 'prompt_hint': 'medium slate gray', 'thermal_hint': 'Moderate heat absorption'},
    {'id': 'terracotta', 'name': 'Terracotta', 'prompt_hint': 'warm terracotta orange-red', 'thermal_hint': 'Traditional Texas clay color'},
    {'id': 'white', 'name': 'White/Cool Roof', 'prompt_hint': 'bright white reflective', 'thermal_hint': 'Maximum solar reflectance - Energy Star rated'},
    {'id': 'black', 'name': 'Black', 'prompt_hint': 'deep black', 'thermal_hint': 'Maximum heat absorption - requires excellent ventilation'},
    {'id': 'bronze', 'name': 'Bronze', 'prompt_hint': 'metallic bronze finish', 'thermal_hint': 'For metal roofs - medium reflectance'},
    {'id': 'galvalume', 'name': 'Galvalume Silver', 'prompt_hint': 'silver galvanized metal finish', 'thermal_hint': 'High reflectance - industrial aesthetic'},
]
```

**Step 2: Verify syntax**

Run: `cd /home/reid/testhome/pools-visualizer && source venv/bin/activate && python3 -c "from api.tenants.roofs import config; print(len(config.ROOF_MATERIALS))"`
Expected: `9`

**Step 3: Commit**

```bash
git add api/tenants/roofs/config.py
git commit -m "feat(roofs): add roof materials and colors config"
```

---

### Task 5: Create Roofs Config - Part 2 (Solar Options)

**Files:**
- Modify: `api/tenants/roofs/config.py` (append)

**Step 1: Append solar configuration**

Add after ROOF_COLORS:

```python
SOLAR_PANEL_TYPES = [
    {
        'id': 'none',
        'name': 'No Solar',
        'prompt_hint': '',
        'price_per_watt': 0,
    },
    {
        'id': 'standard_mono',
        'name': 'Standard Monocrystalline',
        'prompt_hint': 'standard monocrystalline solar panels with blue-black cells and silver frames',
        'price_per_watt': 2.80,
        'description': 'Most common, 20-22% efficiency',
        'popular': True,
    },
    {
        'id': 'allblack_mono',
        'name': 'All-Black Monocrystalline',
        'prompt_hint': 'premium all-black solar panels with black cells, frames, and backsheet',
        'price_per_watt': 3.20,
        'description': 'Sleek aesthetic, 20-22% efficiency',
    },
    {
        'id': 'polycrystalline',
        'name': 'Polycrystalline',
        'prompt_hint': 'blue polycrystalline solar panels with visible crystal pattern',
        'price_per_watt': 2.40,
        'description': 'Budget option, 15-17% efficiency',
    },
    {
        'id': 'solar_tiles',
        'name': 'Solar Roof Tiles',
        'prompt_hint': 'integrated solar roof tiles that blend seamlessly with regular roofing',
        'price_per_sqft': 25.00,
        'description': 'Tesla-style integrated solar, premium aesthetic',
    },
]

SOLAR_COVERAGE = [
    {'id': 'partial', 'name': 'Partial (30%)', 'prompt_hint': 'solar panels covering approximately 30% of south-facing roof', 'coverage_pct': 30},
    {'id': 'half', 'name': 'Half (50%)', 'prompt_hint': 'solar panels covering approximately half of available roof space', 'coverage_pct': 50},
    {'id': 'full', 'name': 'Maximum (80%+)', 'prompt_hint': 'solar panels covering most available roof space with required setbacks', 'coverage_pct': 80, 'popular': True},
]

SOLAR_MOUNTING = [
    {
        'id': 'flush',
        'name': 'Flush Mount',
        'prompt_hint': 'flush-mounted panels parallel to roof surface with minimal gap',
        'description': 'Lower profile, better wind resistance, slightly less efficient',
    },
    {
        'id': 'tilted',
        'name': 'Tilted Mount',
        'prompt_hint': 'tilted mounting brackets angling panels 25-30 degrees for optimal Texas sun exposure',
        'description': '15-20% more energy production, higher profile',
        'popular': True,
    },
]

BATTERY_OPTIONS = [
    {'id': 'none', 'name': 'No Battery', 'prompt_hint': '', 'price_add': 0},
    {
        'id': 'powerwall',
        'name': 'Tesla Powerwall',
        'prompt_hint': 'Tesla Powerwall battery unit mounted on exterior garage wall',
        'price_add': 11500,
        'popular': True,
    },
    {
        'id': 'enphase',
        'name': 'Enphase Battery',
        'prompt_hint': 'Enphase IQ battery system mounted on exterior wall',
        'price_add': 10000,
    },
    {
        'id': 'generac',
        'name': 'Generac PWRcell',
        'prompt_hint': 'Generac PWRcell battery cabinet mounted in garage or exterior',
        'price_add': 12000,
    },
]

INVERTER_LOCATIONS = [
    {'id': 'garage_wall', 'name': 'Garage Wall', 'prompt_hint': 'inverter mounted on interior garage wall near electrical panel'},
    {'id': 'exterior_wall', 'name': 'Exterior Wall', 'prompt_hint': 'weatherproof inverter on shaded exterior wall'},
    {'id': 'side_yard', 'name': 'Side Yard Ground Mount', 'prompt_hint': 'ground-mounted inverter enclosure in side yard'},
]
```

**Step 2: Verify syntax**

Run: `python3 -c "from api.tenants.roofs import config; print(len(config.SOLAR_PANEL_TYPES))"`
Expected: `5`

**Step 3: Commit**

```bash
git add api/tenants/roofs/config.py
git commit -m "feat(roofs): add solar panel configuration options"
```

---

### Task 6: Create Roofs Config - Part 3 (Finishing & Pipeline)

**Files:**
- Modify: `api/tenants/roofs/config.py` (append)

**Step 1: Append finishing options and tenant class**

Add after INVERTER_LOCATIONS:

```python
FINISHING_OPTIONS = {
    'gutters': [
        {'id': 'keep_existing', 'name': 'Keep Existing', 'prompt_hint': ''},
        {'id': 'white_aluminum', 'name': 'White Aluminum', 'prompt_hint': 'new white seamless aluminum gutters and downspouts'},
        {'id': 'bronze_aluminum', 'name': 'Bronze Aluminum', 'prompt_hint': 'new bronze seamless aluminum gutters matching roof color'},
        {'id': 'copper', 'name': 'Copper', 'prompt_hint': 'copper gutters and downspouts that will develop natural patina'},
        {'id': 'color_match', 'name': 'Color-Matched', 'prompt_hint': 'gutters color-matched to roof material'},
    ],
    'skylights': [
        {'id': 'none', 'name': 'None', 'prompt_hint': ''},
        {'id': 'single', 'name': 'Single Skylight', 'prompt_hint': 'one velux-style skylight on main roof plane'},
        {'id': 'multiple', 'name': 'Multiple Skylights', 'prompt_hint': 'multiple skylights strategically placed for natural light'},
        {'id': 'tubular', 'name': 'Tubular Skylights', 'prompt_hint': 'small tubular sun tunnels for interior lighting'},
    ],
    'ventilation': [
        {'id': 'standard', 'name': 'Standard Box Vents', 'prompt_hint': 'standard roof box vents'},
        {'id': 'ridge', 'name': 'Ridge Vent', 'prompt_hint': 'continuous ridge vent along roof peak'},
        {'id': 'solar_powered', 'name': 'Solar-Powered Vents', 'prompt_hint': 'solar-powered attic exhaust fans'},
    ],
    'trim_fascia': [
        {'id': 'keep_existing', 'name': 'Keep Existing', 'prompt_hint': ''},
        {'id': 'painted_white', 'name': 'Painted White', 'prompt_hint': 'freshly painted white fascia and trim'},
        {'id': 'painted_match', 'name': 'Color-Matched', 'prompt_hint': 'fascia and trim painted to complement roof color'},
        {'id': 'aluminum_wrap', 'name': 'Aluminum Wrap', 'prompt_hint': 'maintenance-free aluminum fascia wrap'},
    ],
}

EXTERIOR_PAINT = [
    {'id': 'none', 'name': 'Keep Existing', 'prompt_hint': ''},
    {'id': 'white_modern', 'name': 'Modern White', 'prompt_hint': 'fresh white exterior paint with dark charcoal trim accents'},
    {'id': 'gray_contemporary', 'name': 'Gray Contemporary', 'prompt_hint': 'light gray exterior with white trim'},
    {'id': 'warm_beige', 'name': 'Texas Beige', 'prompt_hint': 'warm beige/tan exterior paint typical of Texas homes'},
    {'id': 'sage_green', 'name': 'Sage Green', 'prompt_hint': 'muted sage green exterior with cream trim'},
    {'id': 'navy_blue', 'name': 'Navy Blue', 'prompt_hint': 'deep navy blue exterior with bright white trim'},
]

PIPELINE_STEPS = ['cleanup', 'roof_material', 'solar_panels', 'finishing', 'quality_check']

PRIMARY_COLOR = "#8B4513"  # Saddle Brown
SECONDARY_COLOR = "#D2691E"  # Chocolate


class RoofsTenantConfig(BaseTenantConfig):
    """Roofs/Solar vertical tenant configuration."""

    tenant_id = 'roofs'
    display_name = VERTICAL_DISPLAY_NAME

    def get_pipeline_steps(self):
        return PIPELINE_STEPS

    def get_step_config(self, step_name):
        configs = {
            'cleanup': {
                'type': 'cleanup',
                'progress_weight': 15,
                'description': 'Preparing image',
            },
            'roof_material': {
                'type': 'insertion',
                'scope_key': None,  # Always runs
                'feature_name': 'roof',
                'progress_weight': 35,
                'description': 'Installing new roof',
            },
            'solar_panels': {
                'type': 'insertion',
                'scope_key': 'solar',
                'feature_name': 'solar_panels',
                'progress_weight': 25,
                'description': 'Adding solar panels',
            },
            'finishing': {
                'type': 'insertion',
                'scope_key': 'finishing',
                'feature_name': 'finishing',
                'progress_weight': 15,
                'description': 'Adding finishing touches',
            },
            'quality_check': {
                'type': 'quality_check',
                'progress_weight': 10,
                'description': 'Quality check',
            },
        }
        return configs.get(step_name, {})

    def get_prompts_module(self):
        from api.tenants.roofs import prompts
        return prompts

    def get_schema(self):
        return get_config()

    def get_mesh_choices(self):
        return []

    def get_frame_color_choices(self):
        return []

    def get_mesh_color_choices(self):
        return []

    def get_opacity_choices(self):
        return []


def get_config():
    """Return config dict for API responses. Excludes pricing data."""
    return {
        'name': VERTICAL_NAME,
        'display_name': VERTICAL_DISPLAY_NAME,
        'roof_materials': [
            {k: v for k, v in mat.items() if 'price' not in k}
            for mat in ROOF_MATERIALS
        ],
        'roof_colors': ROOF_COLORS,
        'solar_panel_types': [
            {k: v for k, v in panel.items() if 'price' not in k}
            for panel in SOLAR_PANEL_TYPES
        ],
        'solar_coverage': SOLAR_COVERAGE,
        'solar_mounting': SOLAR_MOUNTING,
        'battery_options': [
            {k: v for k, v in opt.items() if 'price' not in k}
            for opt in BATTERY_OPTIONS
        ],
        'inverter_locations': INVERTER_LOCATIONS,
        'finishing_options': FINISHING_OPTIONS,
        'exterior_paint': EXTERIOR_PAINT,
        'pipeline_steps': PIPELINE_STEPS,
        'primary_color': PRIMARY_COLOR,
        'secondary_color': SECONDARY_COLOR,
    }


def get_full_config_with_pricing():
    """Return full config including pricing. For internal/admin use only."""
    return {
        'name': VERTICAL_NAME,
        'display_name': VERTICAL_DISPLAY_NAME,
        'roof_materials': ROOF_MATERIALS,
        'roof_colors': ROOF_COLORS,
        'solar_panel_types': SOLAR_PANEL_TYPES,
        'solar_coverage': SOLAR_COVERAGE,
        'solar_mounting': SOLAR_MOUNTING,
        'battery_options': BATTERY_OPTIONS,
        'inverter_locations': INVERTER_LOCATIONS,
        'finishing_options': FINISHING_OPTIONS,
        'exterior_paint': EXTERIOR_PAINT,
        'pipeline_steps': PIPELINE_STEPS,
    }
```

**Step 2: Verify full config loads**

Run: `python3 -c "from api.tenants.roofs.config import RoofsTenantConfig; c = RoofsTenantConfig(); print(c.tenant_id, len(c.get_pipeline_steps()))"`
Expected: `roofs 5`

**Step 3: Commit**

```bash
git add api/tenants/roofs/config.py
git commit -m "feat(roofs): add finishing options and tenant config class"
```

---

### Task 7: Create Roofs Prompts - Cleanup & Roof Material

**Files:**
- Create: `api/tenants/roofs/prompts.py`

**Step 1: Write cleanup and roof_material prompts**

```python
"""
Roofs/Solar Visualizer - AI Prompts
Texas-focused roofing and solar visualization pipeline.

Pipeline: cleanup -> roof_material -> solar_panels -> finishing -> quality_check
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
        (m for m in config.ROOF_MATERIALS if m['id'] == selections.get('material', 'asphalt_architectural')),
        config.ROOF_MATERIALS[1]
    )
    color = next(
        (c for c in config.ROOF_COLORS if c['id'] == selections.get('color', 'charcoal')),
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
                   'tile' if 'tile' in material['id'] else \
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
- {color['thermal_hint']}
- Consistent color across entire roof surface
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
```

**Step 2: Verify syntax**

Run: `python3 -c "from api.tenants.roofs.prompts import get_cleanup_prompt, get_roof_material_prompt; print(len(get_cleanup_prompt()), len(get_roof_material_prompt({})))"`
Expected: Two numbers (prompt lengths)

**Step 3: Commit**

```bash
git add api/tenants/roofs/prompts.py
git commit -m "feat(roofs): add cleanup and roof_material prompts"
```

---

### Task 8: Create Roofs Prompts - Solar Panels

**Files:**
- Modify: `api/tenants/roofs/prompts.py` (append)

**Step 1: Append solar_panels prompt**

Add after `get_roof_material_prompt`:

```python
def get_solar_panels_prompt(selections: dict) -> str:
    """Step 3: Add solar panels to the roof (conditional)."""
    panel_type = next(
        (p for p in config.SOLAR_PANEL_TYPES if p['id'] == selections.get('solar_type', 'none')),
        config.SOLAR_PANEL_TYPES[0]
    )

    if panel_type['id'] == 'none':
        return None

    coverage = next(
        (c for c in config.SOLAR_COVERAGE if c['id'] == selections.get('solar_coverage', 'half')),
        config.SOLAR_COVERAGE[1]
    )
    mounting = next(
        (m for m in config.SOLAR_MOUNTING if m['id'] == selections.get('solar_mounting', 'flush')),
        config.SOLAR_MOUNTING[0]
    )
    battery = next(
        (b for b in config.BATTERY_OPTIONS if b['id'] == selections.get('battery', 'none')),
        config.BATTERY_OPTIONS[0]
    )
    inverter = next(
        (i for i in config.INVERTER_LOCATIONS if i['id'] == selections.get('inverter_location', 'garage_wall')),
        config.INVERTER_LOCATIONS[0]
    )

    battery_text = ""
    if battery['prompt_hint']:
        battery_text = f"""
BATTERY STORAGE:
- {battery['prompt_hint']}
- Proper clearances around unit
- Conduit connection to main electrical panel"""

    inverter_text = f"""
INVERTER & ELECTRICAL:
- {inverter['prompt_hint']}
- Conduit routing from roof edge down to inverter
- Utility disconnect box near main panel
- AC wiring conduit painted to match house"""

    return f"""Photorealistic inpainting. Install solar panel system on the new roof.

SOLAR SYSTEM SPECIFICATIONS:
- Panel type: {panel_type['prompt_hint']}
- Coverage: {coverage['prompt_hint']}
- Mounting: {mounting['prompt_hint']}

PANEL PLACEMENT REQUIREMENTS:
- Primary placement on south-facing roof planes
- Secondary on west/east planes if south insufficient
- Maintain fire setbacks: 36" from ridge, 18" from edges
- Leave 18" access pathways along roof edges
- Avoid shading from chimneys, vents, trees

MOUNTING SYSTEM:
- {mounting['prompt_hint']}
- Rail system visible under panels (black or silver aluminum)
- Flashings integrated with roof material
- Panel spacing: 0.5-1" between panels for thermal expansion
- Proper tilt angle for Central Texas latitude (25-30°)

ELECTRICAL COMPONENTS:
{inverter_text}
{battery_text}

VISUAL REALISM:
- Photovoltaic cells visible through tempered glass
- Anti-reflective coating showing slight blue/black sheen
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
```

**Step 2: Verify syntax**

Run: `python3 -c "from api.tenants.roofs.prompts import get_solar_panels_prompt; p = get_solar_panels_prompt({'solar_type': 'standard_mono'}); print('Has prompt' if p else 'None')"`
Expected: `Has prompt`

**Step 3: Commit**

```bash
git add api/tenants/roofs/prompts.py
git commit -m "feat(roofs): add solar_panels prompt with Texas considerations"
```

---

### Task 9: Create Roofs Prompts - Finishing & Quality Check

**Files:**
- Modify: `api/tenants/roofs/prompts.py` (append)

**Step 1: Append finishing and quality_check prompts**

Add after `get_solar_panels_prompt`:

```python
def get_finishing_prompt(selections: dict) -> str:
    """Step 4: Add finishing touches (gutters, paint, skylights, etc.)."""
    gutter = next(
        (g for g in config.FINISHING_OPTIONS['gutters'] if g['id'] == selections.get('gutters', 'keep_existing')),
        config.FINISHING_OPTIONS['gutters'][0]
    )
    skylight = next(
        (s for s in config.FINISHING_OPTIONS['skylights'] if s['id'] == selections.get('skylights', 'none')),
        config.FINISHING_OPTIONS['skylights'][0]
    )
    vent = next(
        (v for v in config.FINISHING_OPTIONS['ventilation'] if v['id'] == selections.get('ventilation', 'standard')),
        config.FINISHING_OPTIONS['ventilation'][0]
    )
    trim = next(
        (t for t in config.FINISHING_OPTIONS['trim_fascia'] if t['id'] == selections.get('trim_fascia', 'keep_existing')),
        config.FINISHING_OPTIONS['trim_fascia'][0]
    )
    paint = next(
        (p for p in config.EXTERIOR_PAINT if p['id'] == selections.get('exterior_paint', 'none')),
        config.EXTERIOR_PAINT[0]
    )

    additions = []
    if gutter['prompt_hint']:
        additions.append(f"GUTTERS: {gutter['prompt_hint']}")
    if skylight['prompt_hint']:
        additions.append(f"SKYLIGHTS: {skylight['prompt_hint']}")
    if vent['prompt_hint']:
        additions.append(f"VENTILATION: {vent['prompt_hint']}")
    if trim['prompt_hint']:
        additions.append(f"TRIM/FASCIA: {trim['prompt_hint']}")
    if paint['prompt_hint']:
        additions.append(f"EXTERIOR PAINT: {paint['prompt_hint']}")

    if not additions:
        return None

    additions_text = "\n".join(f"- {a}" for a in additions)

    return f"""Photorealistic inpainting. Add finishing touches to complete the roof project.

FINISHING ADDITIONS:
{additions_text}

GUTTER REQUIREMENTS (if applicable):
- Seamless design with proper slope toward downspouts
- Appropriate bracket spacing (24-36")
- Downspouts routed to drainage areas
- Color matching roof or trim as specified

SKYLIGHT REQUIREMENTS (if applicable):
- Proper flashing integrated with roof material
- Low-profile frame matching modern standards
- Realistic glass reflection showing sky

EXTERIOR PAINT REQUIREMENTS (if applicable):
- Apply evenly to all exterior walls
- Maintain architectural details and trim profiles
- Proper sheen: semi-gloss on trim, satin on siding
- Clean lines at foundation, windows, doors
- Color coordination with new roof

INTEGRATION:
- All additions must look professionally installed
- Maintain consistency with roof and house style
- Proper shadow casting for all new elements

PRESERVE EXACTLY:
- New roof material exactly as installed
- Solar panels (if installed) unchanged
- Windows, doors, and structural details
- Landscaping and surroundings

OUTPUT: Photorealistic final image with all finishing touches.
Output at the highest resolution possible."""


def get_quality_check_prompt(scope: dict = None) -> str:
    """Step 5: Quality check comparing clean image to final result."""
    return """You are a Quality Control AI for roof/solar visualization. You will receive two images.

IMAGE 1: The REFERENCE image (original house before roof work)
IMAGE 2: The FINAL RESULT (house with new roof and optional solar/finishes)

EVALUATE THE VISUALIZATION:

1. ROOF MATERIAL INTEGRATION
   - Does the new roof follow exact pitch and angles of original?
   - Are valleys, hips, and ridges properly aligned?
   - Do penetrations (vents, chimneys) have correct flashing?
   - Is material texture realistic for the selected type?
   - Is color consistent across all roof planes?

2. SOLAR INSTALLATION (if present)
   - Are panels properly spaced with fire setbacks?
   - Does mounting style match selection (flush vs tilted)?
   - Is inverter/battery equipment visible and realistic?
   - Are conduit runs logical and clean?
   - Is panel coverage appropriate for selected level?

3. PERSPECTIVE AND SCALE
   - Does the roof maintain original perspective exactly?
   - Is scale correct relative to house and surroundings?
   - Do shadows from roof/panels match sun direction?
   - Are architectural proportions preserved?

4. TEXAS-SPECIFIC CHECKS
   - Does material show appropriate heat/UV characteristics?
   - Are hail/wind considerations addressed (proper fastening)?
   - Is color appropriate for thermal performance claimed?
   - Are solar panels angled for Texas latitude (~30°)?

5. FINISHING TOUCHES (if present)
   - Are gutters properly sloped and attached?
   - Do skylights have realistic flashing?
   - Is exterior paint evenly applied?
   - Are trim/fascia cleanly finished?

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
Solar installations require permit-ready accuracy.

RETURN ONLY VALID JSON:
{
    "score": <float between 0.0 and 1.0>,
    "issues": [<list of specific issues found, empty if none>],
    "recommendation": "<PASS or REGENERATE>"
}

Solar installations: score below 0.7 should REGENERATE.
Roof-only projects: score below 0.6 should REGENERATE."""


def get_prompt(step: str, selections: dict = None) -> str:
    """Get prompt for a specific pipeline step."""
    selections = selections or {}

    if step == 'cleanup':
        return get_cleanup_prompt()
    elif step == 'roof_material':
        return get_roof_material_prompt(selections)
    elif step == 'solar_panels':
        return get_solar_panels_prompt(selections)
    elif step == 'finishing':
        return get_finishing_prompt(selections)
    elif step == 'quality_check':
        return get_quality_check_prompt()
    else:
        raise ValueError(f"Unknown pipeline step: {step}")


# Compatibility alias for tenant registry
def get_screen_insertion_prompt(feature_type: str, options: dict) -> str:
    """Compatibility wrapper for tenant pipeline."""
    return get_roof_material_prompt(options)
```

**Step 2: Test full prompts module**

Run: `python3 -c "from api.tenants.roofs import prompts; print([s for s in ['cleanup', 'roof_material', 'solar_panels', 'finishing', 'quality_check'] if prompts.get_prompt(s, {'solar_type': 'standard_mono'})])"`
Expected: List of all 5 step names

**Step 3: Commit**

```bash
git add api/tenants/roofs/prompts.py
git commit -m "feat(roofs): add finishing and quality_check prompts"
```

---

### Task 10: Register Roofs Tenant

**Files:**
- Modify: `api/tenants/__init__.py`

**Step 1: Read current file**

Run: `cat api/tenants/__init__.py`

**Step 2: Add roofs import and registration**

Add to imports:
```python
from .roofs.config import RoofsTenantConfig
```

Add to `TENANT_CONFIGS` dict:
```python
'roofs': RoofsTenantConfig(),
```

**Step 3: Verify registration**

Run: `python3 -c "from api.tenants import TENANT_CONFIGS; print('roofs' in TENANT_CONFIGS)"`
Expected: `True`

**Step 4: Commit**

```bash
git add api/tenants/__init__.py
git commit -m "feat(roofs): register tenant in tenant registry"
```

---

## Phase 3: Extend Windows Tenant

### Task 11: Add Door Types to Windows Config

**Files:**
- Modify: `api/tenants/windows/config.py`

**Step 1: Read current file to find insertion point**

Run: `grep -n "TRIM_STYLES" api/tenants/windows/config.py`

**Step 2: Add door configuration after TRIM_STYLES**

Insert after TRIM_STYLES definition:

```python
DOOR_TYPES = [
    {
        'id': 'sliding_glass',
        'name': 'Sliding Glass Door',
        'prompt_hint': 'sliding glass patio door with smooth-gliding panels',
        'description': 'Wide opening to patio/yard, panels slide horizontally',
        'width_options': ['6ft', '8ft', '10ft', '12ft'],
    },
    {
        'id': 'french',
        'name': 'French Doors',
        'prompt_hint': 'French doors with divided glass lites and elegant hardware',
        'description': 'Traditional hinged double doors with glass panels',
        'width_options': ['5ft', '6ft'],
    },
    {
        'id': 'accordion',
        'name': 'Accordion/Folding Glass Door',
        'prompt_hint': 'multi-panel accordion folding glass door system that stacks to one side',
        'description': 'Folds completely open, creates seamless indoor-outdoor transition',
        'width_options': ['10ft', '12ft', '16ft', '20ft'],
        'popular': True,
    },
    {
        'id': 'bifold',
        'name': 'Bi-Fold Glass Door',
        'prompt_hint': 'bi-fold glass door system with panels folding in pairs',
        'description': 'Similar to accordion but folds in pairs',
        'width_options': ['8ft', '12ft', '16ft'],
    },
]

PATIO_ENCLOSURE_TYPES = [
    {
        'id': 'three_season',
        'name': 'Three-Season Sunroom',
        'prompt_hint': 'glass-enclosed sunroom with single-pane windows and screen options',
        'description': 'Usable spring through fall, not climate controlled',
    },
    {
        'id': 'four_season',
        'name': 'Four-Season Sunroom',
        'prompt_hint': 'fully insulated glass sunroom with double-pane windows',
        'description': 'Year-round comfort with HVAC connection',
        'popular': True,
    },
    {
        'id': 'screen_room',
        'name': 'Screen Room',
        'prompt_hint': 'screened patio enclosure with aluminum frame and mesh panels',
        'description': 'Bug protection while maintaining outdoor feel',
    },
    {
        'id': 'glass_walls',
        'name': 'Retractable Glass Walls',
        'prompt_hint': 'floor-to-ceiling retractable glass wall panels that open completely',
        'description': 'Transforms patio into enclosed space when needed',
    },
]

ENCLOSURE_GLASS_TYPES = [
    {'id': 'single_clear', 'name': 'Single-Pane Clear', 'prompt_hint': 'single-pane clear glass'},
    {'id': 'double_clear', 'name': 'Double-Pane Clear', 'prompt_hint': 'insulated double-pane clear glass'},
    {'id': 'double_lowe', 'name': 'Double-Pane Low-E', 'prompt_hint': 'energy-efficient double-pane Low-E glass'},
    {'id': 'tinted', 'name': 'Tinted Glass', 'prompt_hint': 'tinted glass for sun control'},
]
```

**Step 3: Verify syntax**

Run: `python3 -c "from api.tenants.windows import config; print(len(config.DOOR_TYPES))"`
Expected: `4`

**Step 4: Commit**

```bash
git add api/tenants/windows/config.py
git commit -m "feat(windows): add door types and patio enclosure config"
```

---

### Task 12: Update Windows Pipeline Steps

**Files:**
- Modify: `api/tenants/windows/config.py`

**Step 1: Update PIPELINE_STEPS**

Change from:
```python
PIPELINE_STEPS = ['cleanup', 'window_frame', 'grilles_glass', 'trim', 'quality_check']
```

To:
```python
PIPELINE_STEPS = ['cleanup', 'window_frame', 'grilles_glass', 'trim', 'doors', 'patio_enclosure', 'quality_check']
```

**Step 2: Update get_step_config in WindowsTenantConfig**

Add new step configs:
```python
'doors': {
    'type': 'insertion',
    'scope_key': 'doors',
    'feature_name': 'doors',
    'progress_weight': 10,
    'description': 'Installing doors',
},
'patio_enclosure': {
    'type': 'insertion',
    'scope_key': 'patio_enclosure',
    'feature_name': 'patio_enclosure',
    'progress_weight': 10,
    'description': 'Building patio enclosure',
},
```

**Step 3: Update get_config() to include new options**

Add to return dict:
```python
'door_types': DOOR_TYPES,
'patio_enclosure_types': PATIO_ENCLOSURE_TYPES,
'enclosure_glass_types': ENCLOSURE_GLASS_TYPES,
```

**Step 4: Verify changes**

Run: `python3 -c "from api.tenants.windows.config import WindowsTenantConfig; c = WindowsTenantConfig(); print(len(c.get_pipeline_steps()))"`
Expected: `7`

**Step 5: Commit**

```bash
git add api/tenants/windows/config.py
git commit -m "feat(windows): update pipeline with doors and patio_enclosure steps"
```

---

### Task 13: Add Door Prompts to Windows

**Files:**
- Modify: `api/tenants/windows/prompts.py`

**Step 1: Read current file to find insertion point**

Run: `grep -n "def get_quality_check_prompt" api/tenants/windows/prompts.py`

**Step 2: Add door prompt before quality_check**

Insert before `get_quality_check_prompt`:

```python
def get_doors_prompt(selections: dict) -> str:
    """Step 5: Add or replace doors (conditional)."""
    from api.tenants.windows import config

    door_type = next(
        (d for d in config.DOOR_TYPES if d['id'] == selections.get('door_type')),
        None
    )

    if not door_type:
        return None

    frame_material = next(
        (m for m in config.FRAME_MATERIALS if m['id'] == selections.get('frame_material', 'vinyl')),
        config.FRAME_MATERIALS[0]
    )
    frame_color = next(
        (c for c in config.FRAME_COLORS if c['id'] == selections.get('frame_color', 'white')),
        config.FRAME_COLORS[0]
    )
    glass = next(
        (g for g in config.GLASS_OPTIONS if g['id'] == selections.get('glass_option', 'clear')),
        config.GLASS_OPTIONS[0]
    )

    door_width = selections.get('door_width', door_type['width_options'][0])

    return f"""Photorealistic inpainting. Install new door system on this house.

DOOR SPECIFICATIONS:
- Type: {door_type['prompt_hint']}
- Width: {door_width}
- Frame material: {frame_material['prompt_hint']}
- Frame color: {frame_color['prompt_hint']}
- Glass: {glass['prompt_hint']}

INSTALLATION REQUIREMENTS:
- Position door in logical location (back of house facing patio/yard typical)
- Replace existing door opening or create new opening where architecturally appropriate
- Door frame must integrate with surrounding wall/siding
- Proper threshold and step detail
- Hardware (handles, locks) matching {frame_color['name']} finish

DOOR REALISM:
- Glass panels showing realistic reflections
- Frame material authentic to {frame_material['name']}
- Proper weatherstripping visible
- Track system visible for sliding/folding types
- Professional installation appearance

FOR ACCORDION/FOLDING DOORS:
- Show panels in partially open or fully stacked position
- Track system integrated with ceiling/header
- Each panel clearly visible with proper hinges
- Floor track or suspended system as appropriate

INTEGRATION:
- Door must look INSTALLED, not floating
- Shadows cast correctly from door depth
- Consistent with house architectural style
- Match existing window frames if visible

PRESERVE EXACTLY:
- All windows and trim exactly as rendered
- House structure outside door area
- Landscaping visible through door glass
- Interior glimpse should be realistic

OUTPUT: Photorealistic door installation integrated with house.
Output at the highest resolution possible."""
```

**Step 3: Verify syntax**

Run: `python3 -c "from api.tenants.windows.prompts import get_doors_prompt; print('OK' if get_doors_prompt({'door_type': 'sliding_glass'}) else 'None')"`
Expected: `OK`

**Step 4: Commit**

```bash
git add api/tenants/windows/prompts.py
git commit -m "feat(windows): add doors prompt"
```

---

### Task 14: Add Patio Enclosure Prompt to Windows

**Files:**
- Modify: `api/tenants/windows/prompts.py`

**Step 1: Add patio_enclosure prompt after doors prompt**

```python
def get_patio_enclosure_prompt(selections: dict) -> str:
    """Step 6: Add patio/sunroom enclosure (conditional)."""
    from api.tenants.windows import config

    enclosure_type = next(
        (e for e in config.PATIO_ENCLOSURE_TYPES if e['id'] == selections.get('enclosure_type')),
        None
    )

    if not enclosure_type:
        return None

    frame_color = next(
        (c for c in config.FRAME_COLORS if c['id'] == selections.get('frame_color', 'white')),
        config.FRAME_COLORS[0]
    )
    glass = next(
        (g for g in config.ENCLOSURE_GLASS_TYPES if g['id'] == selections.get('enclosure_glass', 'double_clear')),
        config.ENCLOSURE_GLASS_TYPES[1]
    )

    enclosure_specifics = ""
    if enclosure_type['id'] == 'screen_room':
        enclosure_specifics = """
SCREEN ROOM SPECIFICS:
- Aluminum frame with visible structural posts every 4-5 feet
- Screen mesh panels (standard fiberglass or pet-resistant)
- Solid knee wall or full-height screens
- Screen door for entry
- Roof: existing patio cover or new aluminum roof panels"""
    elif enclosure_type['id'] == 'glass_walls':
        enclosure_specifics = """
RETRACTABLE GLASS WALL SPECIFICS:
- Floor-to-ceiling glass panels (typically 3-4 feet wide each)
- Panels stack to one side when open
- Overhead track system with concealed hardware
- No vertical mullions when closed (frameless appearance)
- Weatherproof seals at floor and ceiling"""
    else:
        enclosure_specifics = f"""
SUNROOM SPECIFICS:
- Full glass wall enclosure with aluminum or vinyl frame
- Vertical mullions every 3-4 feet for structural support
- {glass['prompt_hint']}
- Insulated roof or glass roof panels
- Proper drainage and weatherproofing"""

    return f"""Photorealistic inpainting. Enclose the existing patio/porch with {enclosure_type['name']}.

ENCLOSURE SPECIFICATIONS:
- Type: {enclosure_type['prompt_hint']}
- Frame color: {frame_color['prompt_hint']}
- Glass/panels: {glass['prompt_hint']}

STRUCTURAL REQUIREMENTS:
- Enclose the existing patio/porch footprint exactly
- Connect to existing house walls and roofline
- Foundation: use existing patio slab
- Maintain any existing columns or structural supports
- Proper door entry (at least one access point)
{enclosure_specifics}

VISUAL REALISM:
- Frame material consistent with house style
- Glass showing realistic reflections (sky, trees, interior glimpse)
- Proper shadows from frame structure
- Weatherproof appearance at all joints
- Professional construction quality

INTEGRATION:
- Seamless connection to house exterior
- Roof ties into existing roofline or extends naturally
- Electrical (if visible): exterior lights, ceiling fan
- Consistent with neighborhood/HOA standards

PRESERVE EXACTLY:
- All windows on main house unchanged
- House structure outside enclosure
- Landscaping beyond enclosure footprint
- Existing patio furniture (if requested preserved)

FOCUS: Enclose ONLY the patio/porch area. Do NOT modify the main house structure.

OUTPUT: Photorealistic patio enclosure integrated with existing home.
Output at the highest resolution possible."""
```

**Step 2: Verify syntax**

Run: `python3 -c "from api.tenants.windows.prompts import get_patio_enclosure_prompt; print('OK' if get_patio_enclosure_prompt({'enclosure_type': 'four_season'}) else 'None')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add api/tenants/windows/prompts.py
git commit -m "feat(windows): add patio_enclosure prompt"
```

---

### Task 15: Update Windows get_prompt Router

**Files:**
- Modify: `api/tenants/windows/prompts.py`

**Step 1: Update get_prompt function**

Find the existing `get_prompt` function and update to include new steps:

```python
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
    elif step == 'doors':
        return get_doors_prompt(selections)
    elif step == 'patio_enclosure':
        return get_patio_enclosure_prompt(selections)
    elif step == 'quality_check':
        return get_quality_check_prompt()
    else:
        raise ValueError(f"Unknown pipeline step: {step}")
```

**Step 2: Verify all steps work**

Run: `python3 -c "from api.tenants.windows import prompts; [print(s, ':', 'OK' if prompts.get_prompt(s, {'door_type': 'sliding_glass', 'enclosure_type': 'four_season'}) else 'None/Skip') for s in ['cleanup', 'window_frame', 'doors', 'patio_enclosure', 'quality_check']]"`

Expected: All print OK or None/Skip appropriately

**Step 3: Commit**

```bash
git add api/tenants/windows/prompts.py
git commit -m "feat(windows): update get_prompt router for doors and enclosure steps"
```

---

### Task 16: Update Windows Quality Check for New Scopes

**Files:**
- Modify: `api/tenants/windows/prompts.py`

**Step 1: Update get_quality_check_prompt to include door and enclosure checks**

Replace the function with enhanced version:

```python
def get_quality_check_prompt(scope: dict = None) -> str:
    """Step 7: Quality check comparing original to final result."""
    scope = scope or {}

    door_checks = ""
    if scope.get('doors'):
        door_checks = """
5. DOOR INSTALLATION (if present)
   - Is door positioned logically for house layout?
   - Does door frame integrate with wall/siding?
   - Are glass reflections realistic and consistent?
   - Is hardware (handles, locks) appropriate?
   - For folding/sliding: is track system visible and realistic?
"""

    enclosure_checks = ""
    if scope.get('patio_enclosure'):
        enclosure_checks = """
6. PATIO ENCLOSURE (if present)
   - Does enclosure connect seamlessly to house?
   - Are structural posts/mullions properly spaced?
   - Is roof integrated with existing roofline?
   - Does glass/screen show realistic reflections/transparency?
   - Is the enclosure footprint matching original patio?
"""

    return f"""You are a Quality Control AI for window/door visualization. You will receive two images.

IMAGE 1: The REFERENCE image (original house before work)
IMAGE 2: The FINAL RESULT (house with new windows, doors, and/or enclosures)

EVALUATE THE VISUALIZATION:

1. WINDOW PLACEMENT
   - Are all windows maintained in original positions?
   - Are window sizes consistent with original openings?
   - Are windows properly aligned and level?

2. WINDOW REALISM
   - Do frames look like authentic material?
   - Is frame color uniform and professional?
   - Are glass reflections realistic and consistent?
   - Do windows have proper depth and dimension?

3. INTEGRATION
   - Do windows look INSTALLED vs. pasted/floating?
   - Is relationship with siding natural?
   - Are shadows cast correctly?

4. GRILLES & TRIM (if applicable)
   - Are grille patterns consistent across windows?
   - Is trim applied consistently and mitered properly?
{door_checks}
{enclosure_checks}
7. PRESERVATION
   - Are house siding, roof intact?
   - Is landscaping preserved?
   - Are there any unwanted artifacts?

SCORING GUIDE:
- 0.0-0.4: FAIL - Major issues (floating elements, impossible geometry)
- 0.5-0.6: POOR - Obvious issues (misalignment, unrealistic materials)
- 0.7-0.8: GOOD - Minor issues (subtle reflection problems)
- 0.9-1.0: EXCELLENT - Highly realistic, professional appearance

RETURN ONLY VALID JSON:
{{
    "score": <float between 0.0 and 1.0>,
    "issues": [<list of specific issues found, empty if none>],
    "recommendation": "<PASS or REGENERATE>"
}}

A score below 0.6 should recommend REGENERATE."""
```

**Step 2: Verify quality check works with scope**

Run: `python3 -c "from api.tenants.windows.prompts import get_quality_check_prompt; print('doors' in get_quality_check_prompt({'doors': True}))"`
Expected: `True`

**Step 3: Commit**

```bash
git add api/tenants/windows/prompts.py
git commit -m "feat(windows): enhance quality_check for doors and enclosures"
```

---

## Phase 4: Testing & Verification

### Task 17: Write Basic Tests for Roofs Tenant

**Files:**
- Create: `api/tenants/roofs/tests/test_config.py`

**Step 1: Create test file**

```python
"""Tests for roofs tenant configuration."""
import pytest
from api.tenants.roofs.config import (
    RoofsTenantConfig,
    get_config,
    get_full_config_with_pricing,
    ROOF_MATERIALS,
    SOLAR_PANEL_TYPES,
)


class TestRoofsConfig:
    """Test roofs configuration."""

    def test_tenant_id(self):
        config = RoofsTenantConfig()
        assert config.tenant_id == 'roofs'

    def test_display_name(self):
        config = RoofsTenantConfig()
        assert config.display_name == 'Roof Replacement & Solar'

    def test_pipeline_steps(self):
        config = RoofsTenantConfig()
        steps = config.get_pipeline_steps()
        assert steps == ['cleanup', 'roof_material', 'solar_panels', 'finishing', 'quality_check']

    def test_step_configs_exist(self):
        config = RoofsTenantConfig()
        for step in config.get_pipeline_steps():
            step_config = config.get_step_config(step)
            assert step_config, f"Missing config for step: {step}"
            assert 'type' in step_config

    def test_roof_materials_have_required_fields(self):
        for material in ROOF_MATERIALS:
            assert 'id' in material
            assert 'name' in material
            assert 'prompt_hint' in material

    def test_solar_panel_types_have_required_fields(self):
        for panel in SOLAR_PANEL_TYPES:
            assert 'id' in panel
            assert 'name' in panel

    def test_get_config_excludes_pricing(self):
        config = get_config()
        for material in config['roof_materials']:
            assert 'price_per_sqft' not in material

    def test_get_full_config_includes_pricing(self):
        config = get_full_config_with_pricing()
        # At least one material should have pricing
        has_pricing = any('price_per_sqft' in m for m in config['roof_materials'])
        assert has_pricing
```

**Step 2: Run test**

Run: `cd /home/reid/testhome/pools-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/roofs/tests/test_config.py -v`
Expected: All tests pass

**Step 3: Commit**

```bash
git add api/tenants/roofs/tests/test_config.py
git commit -m "test(roofs): add config tests"
```

---

### Task 18: Write Basic Tests for Roofs Prompts

**Files:**
- Create: `api/tenants/roofs/tests/test_prompts.py`

**Step 1: Create test file**

```python
"""Tests for roofs tenant prompts."""
import pytest
from api.tenants.roofs import prompts


class TestRoofsPrompts:
    """Test roofs prompts."""

    def test_cleanup_prompt_returns_string(self):
        result = prompts.get_cleanup_prompt()
        assert isinstance(result, str)
        assert len(result) > 100
        assert 'Texas' in result or 'roof' in result.lower()

    def test_roof_material_prompt_returns_string(self):
        result = prompts.get_roof_material_prompt({})
        assert isinstance(result, str)
        assert 'ROOF SPECIFICATIONS' in result

    def test_roof_material_prompt_includes_selection(self):
        result = prompts.get_roof_material_prompt({
            'material': 'metal_standing_seam',
            'color': 'bronze'
        })
        assert 'standing seam' in result.lower()
        assert 'bronze' in result.lower()

    def test_solar_panels_prompt_returns_none_when_no_solar(self):
        result = prompts.get_solar_panels_prompt({'solar_type': 'none'})
        assert result is None

    def test_solar_panels_prompt_returns_string_when_solar_selected(self):
        result = prompts.get_solar_panels_prompt({
            'solar_type': 'standard_mono',
            'solar_coverage': 'full',
            'solar_mounting': 'tilted',
        })
        assert isinstance(result, str)
        assert 'solar' in result.lower()

    def test_finishing_prompt_returns_none_when_no_changes(self):
        result = prompts.get_finishing_prompt({
            'gutters': 'keep_existing',
            'skylights': 'none',
            'exterior_paint': 'none',
        })
        assert result is None

    def test_finishing_prompt_returns_string_when_changes_selected(self):
        result = prompts.get_finishing_prompt({
            'gutters': 'copper',
            'skylights': 'single',
        })
        assert isinstance(result, str)
        assert 'copper' in result.lower() or 'GUTTERS' in result

    def test_quality_check_prompt_returns_string(self):
        result = prompts.get_quality_check_prompt()
        assert isinstance(result, str)
        assert 'JSON' in result
        assert 'score' in result.lower()

    def test_get_prompt_router_all_steps(self):
        steps = ['cleanup', 'roof_material', 'quality_check']
        for step in steps:
            result = prompts.get_prompt(step, {})
            assert result is not None, f"Step {step} returned None"

    def test_get_prompt_router_invalid_step(self):
        with pytest.raises(ValueError):
            prompts.get_prompt('invalid_step', {})
```

**Step 2: Run test**

Run: `python3 -m pytest api/tenants/roofs/tests/test_prompts.py -v`
Expected: All tests pass

**Step 3: Commit**

```bash
git add api/tenants/roofs/tests/test_prompts.py
git commit -m "test(roofs): add prompts tests"
```

---

### Task 19: Write Tests for Windows Extensions

**Files:**
- Modify: `api/tenants/windows/tests/test_prompts.py` (or create if doesn't exist)

**Step 1: Add tests for new door and enclosure prompts**

```python
"""Tests for windows tenant door and enclosure prompts."""
import pytest
from api.tenants.windows import prompts


class TestWindowsDoorPrompts:
    """Test door prompts."""

    def test_doors_prompt_returns_none_when_no_door_type(self):
        result = prompts.get_doors_prompt({})
        assert result is None

    def test_doors_prompt_returns_string_when_door_selected(self):
        result = prompts.get_doors_prompt({
            'door_type': 'sliding_glass',
            'door_width': '8ft',
        })
        assert isinstance(result, str)
        assert 'sliding' in result.lower()

    def test_accordion_door_includes_folding_details(self):
        result = prompts.get_doors_prompt({
            'door_type': 'accordion',
            'door_width': '16ft',
        })
        assert 'accordion' in result.lower() or 'folding' in result.lower()


class TestWindowsEnclosurePrompts:
    """Test patio enclosure prompts."""

    def test_enclosure_prompt_returns_none_when_no_type(self):
        result = prompts.get_patio_enclosure_prompt({})
        assert result is None

    def test_enclosure_prompt_returns_string_when_selected(self):
        result = prompts.get_patio_enclosure_prompt({
            'enclosure_type': 'four_season',
        })
        assert isinstance(result, str)
        assert 'sunroom' in result.lower() or 'enclosure' in result.lower()

    def test_screen_room_includes_mesh_details(self):
        result = prompts.get_patio_enclosure_prompt({
            'enclosure_type': 'screen_room',
        })
        assert 'screen' in result.lower()

    def test_glass_walls_includes_retractable_details(self):
        result = prompts.get_patio_enclosure_prompt({
            'enclosure_type': 'glass_walls',
        })
        assert 'retractable' in result.lower() or 'panel' in result.lower()


class TestWindowsGetPromptRouter:
    """Test get_prompt includes new steps."""

    def test_doors_step_in_router(self):
        result = prompts.get_prompt('doors', {'door_type': 'french'})
        assert result is not None

    def test_patio_enclosure_step_in_router(self):
        result = prompts.get_prompt('patio_enclosure', {'enclosure_type': 'three_season'})
        assert result is not None

    def test_quality_check_includes_door_scope(self):
        result = prompts.get_quality_check_prompt({'doors': True})
        assert 'DOOR' in result
```

**Step 2: Run test**

Run: `python3 -m pytest api/tenants/windows/tests/ -v -k "door or enclosure or Door or Enclosure"`
Expected: All new tests pass

**Step 3: Commit**

```bash
git add api/tenants/windows/tests/
git commit -m "test(windows): add door and enclosure prompt tests"
```

---

### Task 20: Run Full Test Suite

**Files:**
- None (verification only)

**Step 1: Run all tenant tests**

Run: `cd /home/reid/testhome/pools-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/ -v --tb=short`
Expected: All tests pass

**Step 2: Run full API test suite**

Run: `python3 -m pytest api/tests/ -v --tb=short -x`
Expected: All tests pass (or document any pre-existing failures)

**Step 3: Final commit**

```bash
git add -A
git commit -m "feat: complete roofs tenant and windows extension implementation"
```

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| 1 | 1-2 | Cleanup old info (port, legacy prompts) |
| 2 | 3-10 | Create roofs/solar tenant (config + prompts) |
| 3 | 11-16 | Extend windows with doors + patio enclosures |
| 4 | 17-20 | Testing and verification |

**Total Tasks:** 20
**Estimated Time:** 2-3 hours for experienced developer

**Key Files Created:**
- `api/tenants/roofs/__init__.py`
- `api/tenants/roofs/config.py`
- `api/tenants/roofs/prompts.py`
- `api/tenants/roofs/tests/test_config.py`
- `api/tenants/roofs/tests/test_prompts.py`

**Key Files Modified:**
- `/home/reid/testhome/CLAUDE.md`
- `api/visualizer/prompts.py`
- `api/tenants/__init__.py`
- `api/tenants/windows/config.py`
- `api/tenants/windows/prompts.py`
- `api/tenants/windows/tests/test_prompts.py`
