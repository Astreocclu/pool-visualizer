# Windows Visualizer Vertical Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a "windows" tenant to the pools-visualizer project to support window replacement visualization.

**Architecture:** Create a new tenant under `api/tenants/windows/` mirroring the pools tenant structure. Add corresponding frontend wizard steps. The AI pipeline will process house exterior images to visualize new windows.

**Tech Stack:** Django 4.0, React 19.1, Zustand, Google Gemini AI, ReportLab PDF

---

## Task 1: Create Windows Tenant Backend Structure

**Files:**
- Create: `api/tenants/windows/__init__.py`
- Create: `api/tenants/windows/config.py`
- Modify: `api/tenants/__init__.py:15-16,84-85`

**Step 1: Create the windows tenant directory and __init__.py**

```bash
mkdir -p api/tenants/windows
```

```python
# api/tenants/windows/__init__.py
"""Windows Visualization Tenant"""
from .config import WindowsTenantConfig

__all__ = ['WindowsTenantConfig']
```

**Step 2: Create config.py with window options**

```python
# api/tenants/windows/config.py
"""
Windows Vertical Configuration
Port: 8006
Pipeline: cleanup → window_frame → grilles_glass → trim → quality_check
"""
from api.tenants.base import BaseTenantConfig

VERTICAL_NAME = "windows"
VERTICAL_DISPLAY_NAME = "Window Replacement"

WINDOW_TYPES = [
    {
        'id': 'single_hung',
        'name': 'Single Hung',
        'description': 'Bottom sash slides up, top is fixed',
        'base_price': 350,
        'prompt_hint': 'single-hung window with bottom sash that slides vertically',
    },
    {
        'id': 'double_hung',
        'name': 'Double Hung',
        'description': 'Both sashes slide up and down',
        'base_price': 450,
        'prompt_hint': 'double-hung window with both sashes operable',
        'popular': True,
    },
    {
        'id': 'casement',
        'name': 'Casement',
        'description': 'Hinged on side, swings outward',
        'base_price': 500,
        'prompt_hint': 'casement window with side hinges that swings outward',
    },
    {
        'id': 'slider',
        'name': 'Slider',
        'description': 'Sash slides horizontally',
        'base_price': 400,
        'prompt_hint': 'horizontal sliding window',
    },
    {
        'id': 'picture',
        'name': 'Picture',
        'description': 'Fixed, non-operable for views',
        'base_price': 300,
        'prompt_hint': 'large fixed picture window for maximum light and views',
    },
]

WINDOW_STYLES = [
    {'id': 'modern', 'name': 'Modern', 'prompt_hint': 'clean modern minimalist style'},
    {'id': 'traditional', 'name': 'Traditional', 'prompt_hint': 'traditional classic style'},
    {'id': 'colonial', 'name': 'Colonial', 'prompt_hint': 'colonial style with symmetrical design'},
    {'id': 'craftsman', 'name': 'Craftsman', 'prompt_hint': 'craftsman style with detailed woodwork'},
]

FRAME_MATERIALS = [
    {'id': 'vinyl', 'name': 'Vinyl', 'price_multiplier': 1.0, 'prompt_hint': 'vinyl frame with smooth finish'},
    {'id': 'wood', 'name': 'Wood', 'price_multiplier': 1.5, 'prompt_hint': 'natural wood frame'},
    {'id': 'fiberglass', 'name': 'Fiberglass', 'price_multiplier': 1.3, 'prompt_hint': 'fiberglass composite frame'},
    {'id': 'aluminum', 'name': 'Aluminum', 'price_multiplier': 1.2, 'prompt_hint': 'aluminum metal frame'},
]

FRAME_COLORS = [
    {'id': 'white', 'name': 'White', 'prompt_hint': 'bright white'},
    {'id': 'tan', 'name': 'Tan/Almond', 'prompt_hint': 'warm tan/almond color'},
    {'id': 'brown', 'name': 'Brown', 'prompt_hint': 'rich brown'},
    {'id': 'black', 'name': 'Black', 'prompt_hint': 'modern black'},
    {'id': 'bronze', 'name': 'Bronze', 'prompt_hint': 'bronze metallic finish'},
]

GRILLE_PATTERNS = [
    {'id': 'none', 'name': 'No Grilles', 'price_add': 0, 'prompt_hint': ''},
    {'id': 'colonial', 'name': 'Colonial', 'price_add': 150, 'prompt_hint': 'colonial grid pattern with 6 or 9 panes'},
    {'id': 'prairie', 'name': 'Prairie', 'price_add': 175, 'prompt_hint': 'prairie style with border grilles only'},
    {'id': 'craftsman', 'name': 'Craftsman', 'price_add': 200, 'prompt_hint': 'craftsman style with top grilles only'},
    {'id': 'diamond', 'name': 'Diamond', 'price_add': 225, 'prompt_hint': 'diamond/diagonal grille pattern'},
]

GLASS_OPTIONS = [
    {'id': 'clear', 'name': 'Clear', 'price_add': 0, 'prompt_hint': 'clear transparent glass'},
    {'id': 'low_e', 'name': 'Low-E', 'price_add': 50, 'prompt_hint': 'clear glass with low-e coating'},
    {'id': 'frosted', 'name': 'Frosted', 'price_add': 75, 'prompt_hint': 'frosted privacy glass'},
    {'id': 'obscure', 'name': 'Obscure', 'price_add': 75, 'prompt_hint': 'obscure textured privacy glass'},
    {'id': 'rain', 'name': 'Rain', 'price_add': 100, 'prompt_hint': 'rain pattern decorative glass'},
]

HARDWARE_STYLES = [
    {'id': 'standard', 'name': 'Standard', 'prompt_hint': 'standard hardware'},
    {'id': 'modern', 'name': 'Modern Lever', 'prompt_hint': 'modern lever-style hardware'},
    {'id': 'classic', 'name': 'Classic Crank', 'prompt_hint': 'classic crank-out hardware'},
]

HARDWARE_FINISHES = [
    {'id': 'white', 'name': 'White', 'prompt_hint': 'white finish'},
    {'id': 'brushed_nickel', 'name': 'Brushed Nickel', 'prompt_hint': 'brushed nickel finish'},
    {'id': 'oil_rubbed_bronze', 'name': 'Oil-Rubbed Bronze', 'prompt_hint': 'oil-rubbed bronze finish'},
    {'id': 'brass', 'name': 'Brass', 'prompt_hint': 'polished brass finish'},
]

TRIM_STYLES = [
    {'id': 'standard', 'name': 'Standard', 'price_add': 0, 'prompt_hint': 'standard flat trim'},
    {'id': 'craftsman', 'name': 'Craftsman', 'price_add': 100, 'prompt_hint': 'craftsman style trim with header'},
    {'id': 'colonial', 'name': 'Colonial', 'price_add': 75, 'prompt_hint': 'colonial profiled trim'},
    {'id': 'modern', 'name': 'Modern Flat', 'price_add': 50, 'prompt_hint': 'minimal modern flat trim'},
]

PIPELINE_STEPS = ['cleanup', 'window_frame', 'grilles_glass', 'trim', 'quality_check']

PRIMARY_COLOR = "#2E7D32"  # Forest Green
SECONDARY_COLOR = "#66BB6A"


class WindowsTenantConfig(BaseTenantConfig):
    """Windows vertical tenant configuration."""

    tenant_id = 'windows'
    display_name = VERTICAL_DISPLAY_NAME

    def get_pipeline_steps(self):
        return PIPELINE_STEPS

    def get_step_config(self, step_name):
        configs = {
            'cleanup': {'type': 'cleanup', 'progress_weight': 20, 'description': 'Preparing image'},
            'window_frame': {'type': 'insertion', 'scope_key': None, 'feature_name': 'windows', 'progress_weight': 35, 'description': 'Adding windows'},
            'grilles_glass': {'type': 'insertion', 'scope_key': 'grille_pattern', 'feature_name': 'grilles', 'progress_weight': 20, 'description': 'Adding grilles and glass'},
            'trim': {'type': 'insertion', 'scope_key': 'trim_style', 'feature_name': 'trim', 'progress_weight': 15, 'description': 'Adding trim'},
            'quality_check': {'type': 'quality_check', 'progress_weight': 10, 'description': 'Quality check'},
        }
        return configs.get(step_name, {})

    def get_prompts_module(self):
        from api.tenants.windows import prompts
        return prompts

    def get_schema(self):
        return get_config()

    def get_mesh_choices(self):
        return []

    def get_frame_color_choices(self):
        return [(c['id'], c['name']) for c in FRAME_COLORS]

    def get_mesh_color_choices(self):
        return []

    def get_opacity_choices(self):
        return []


def get_config():
    """Return config dict for API responses. Excludes pricing data."""
    return {
        'name': VERTICAL_NAME,
        'display_name': VERTICAL_DISPLAY_NAME,
        'window_types': [
            {k: v for k, v in wt.items() if k not in ['base_price']}
            for wt in WINDOW_TYPES
        ],
        'window_styles': WINDOW_STYLES,
        'frame_materials': [
            {k: v for k, v in fm.items() if k != 'price_multiplier'}
            for fm in FRAME_MATERIALS
        ],
        'frame_colors': FRAME_COLORS,
        'grille_patterns': [
            {k: v for k, v in gp.items() if k != 'price_add'}
            for gp in GRILLE_PATTERNS
        ],
        'glass_options': [
            {k: v for k, v in go.items() if k != 'price_add'}
            for go in GLASS_OPTIONS
        ],
        'hardware_styles': HARDWARE_STYLES,
        'hardware_finishes': HARDWARE_FINISHES,
        'trim_styles': [
            {k: v for k, v in ts.items() if k != 'price_add'}
            for ts in TRIM_STYLES
        ],
        'pipeline_steps': PIPELINE_STEPS,
        'primary_color': PRIMARY_COLOR,
        'secondary_color': SECONDARY_COLOR,
    }
```

**Step 3: Register the windows tenant**

In `api/tenants/__init__.py`, add after line 15:

```python
from .windows.config import WindowsTenantConfig
```

And add after line 85 (after `register_tenant(PoolsTenantConfig())`):

```python
register_tenant(WindowsTenantConfig())
```

**Step 4: Verify import works**

Run: `cd /home/reid/command-center/testhome/pools-visualizer && source venv/bin/activate && python3 -c "from api.tenants.windows.config import WindowsTenantConfig; print('OK')"`

Expected: `OK`

**Step 5: Commit**

```bash
git add api/tenants/windows/ api/tenants/__init__.py
git commit -m "feat(windows): add windows tenant config and registration"
```

---

## Task 2: Create Windows Prompts Module

**Files:**
- Create: `api/tenants/windows/prompts.py`

**Step 1: Create prompts.py with window-specific AI prompts**

```python
# api/tenants/windows/prompts.py
"""
Windows Visualizer - AI Prompts
Layered rendering pipeline for window replacement visualization.

Pipeline: cleanup → window_frame → grilles_glass → trim → quality_check
"""

from api.tenants.windows import config


def get_cleanup_prompt() -> str:
    """Step 1: Clean the image and prepare for window visualization."""
    return """Photorealistic image editing. Prepare this house exterior for window visualization.

WEATHER AND LIGHTING:
Make the weather conditions ideal: clear day with good natural lighting, no harsh shadows.

PRESERVE EXACTLY AS-IS:
- House structure and all architectural features
- Siding, brick, stone - all exterior materials
- Roof and gutters
- Doors and entryways
- Landscaping, trees, shrubs
- Driveway, walkways, hardscape
- Any decorative elements

CLEAN UP ONLY:
- Remove any window reflections that obscure the frame
- Slight enhancement of lighting for clarity
- Remove temporary items (ladders, tools, construction materials)

PERSPECTIVE:
- Maintain the existing perspective
- Ensure window openings are clearly visible
- Optimize visibility of windows to be replaced

OUTPUT: Clean, well-lit house exterior image ready for window visualization.
Output at the highest resolution possible."""


def get_window_frame_prompt(selections: dict) -> str:
    """Step 2: Render new window frames with selected options."""
    window_type = next(
        (wt for wt in config.WINDOW_TYPES if wt['id'] == selections.get('window_type', 'double_hung')),
        config.WINDOW_TYPES[1]
    )
    style = next(
        (s for s in config.WINDOW_STYLES if s['id'] == selections.get('window_style', 'traditional')),
        config.WINDOW_STYLES[1]
    )
    material = next(
        (m for m in config.FRAME_MATERIALS if m['id'] == selections.get('frame_material', 'vinyl')),
        config.FRAME_MATERIALS[0]
    )
    color = next(
        (c for c in config.FRAME_COLORS if c['id'] == selections.get('frame_color', 'white')),
        config.FRAME_COLORS[0]
    )

    return f"""Photorealistic inpainting. Replace the windows on this house with new windows.

WINDOW SPECIFICATIONS:
- Type: {window_type['prompt_hint']}
- Style: {style['prompt_hint']}
- Frame Material: {material['prompt_hint']}
- Frame Color: {color['prompt_hint']}

WINDOW REPLACEMENT REQUIREMENTS:
- Replace ALL visible windows with the new style
- Maintain exact window opening sizes and positions
- Frames should look professionally installed
- Consistent style across all windows
- Proper depth and shadow for realism

CRITICAL INTEGRATION:
- Windows must look INSTALLED, not pasted on
- Shadows and reflections match lighting in scene
- Frame edges crisp and properly aligned
- Glass should show slight reflections of sky/surroundings
- Maintain architectural harmony with house style

PRESERVE EXACTLY:
- House structure, siding, brick
- Roof, gutters, trim (will be updated in later step)
- Doors, landscaping
- Overall lighting and atmosphere

OUTPUT: Photorealistic image with new window frames installed.
Output at the highest resolution possible."""


def get_grilles_glass_prompt(selections: dict) -> str:
    """Step 3: Add grille patterns and glass effects."""
    grille = next(
        (g for g in config.GRILLE_PATTERNS if g['id'] == selections.get('grille_pattern', 'none')),
        config.GRILLE_PATTERNS[0]
    )
    glass = next(
        (g for g in config.GLASS_OPTIONS if g['id'] == selections.get('glass_option', 'clear')),
        config.GLASS_OPTIONS[0]
    )

    if grille['id'] == 'none' and glass['id'] in ['clear', 'low_e']:
        return None  # Skip if no visible changes needed

    grille_text = ""
    if grille['prompt_hint']:
        grille_text = f"""
GRILLE PATTERN:
- Add {grille['prompt_hint']} to all windows
- Grilles should be between-the-glass or SDL style
- Consistent pattern across all windows
- Color matches frame color
"""

    glass_text = ""
    if glass['id'] not in ['clear', 'low_e']:
        glass_text = f"""
GLASS TREATMENT:
- Apply {glass['prompt_hint']} effect to window panes
- Effect should be subtle and realistic
- Maintain some visibility/light transmission
"""

    return f"""Photorealistic inpainting. Add grille patterns and glass effects to the windows.

{grille_text}
{glass_text}

REQUIREMENTS:
- Grilles proportional to window size
- Glass effects applied uniformly
- Maintain realistic reflections
- Keep frames and structure exactly as rendered

PRESERVE EXACTLY:
- Window frames and positions
- House exterior
- All landscaping and surroundings

OUTPUT: Photorealistic image with grilles and glass effects.
Output at the highest resolution possible."""


def get_trim_prompt(selections: dict) -> str:
    """Step 4: Add exterior trim around windows."""
    trim = next(
        (t for t in config.TRIM_STYLES if t['id'] == selections.get('trim_style', 'standard')),
        config.TRIM_STYLES[0]
    )
    frame_color = next(
        (c for c in config.FRAME_COLORS if c['id'] == selections.get('frame_color', 'white')),
        config.FRAME_COLORS[0]
    )

    if trim['id'] == 'standard':
        return None  # Standard trim already implied

    return f"""Photorealistic inpainting. Add exterior trim around the windows.

TRIM SPECIFICATIONS:
- Style: {trim['prompt_hint']}
- Color: {frame_color['prompt_hint']} (matching window frames)

TRIM REQUIREMENTS:
- Apply trim around all window frames
- Consistent width and profile on all windows
- Professional installation appearance
- Proper shadow and depth
- Trim should complement house architecture

PRESERVE EXACTLY:
- Windows exactly as rendered
- House structure and siding
- All other architectural elements

OUTPUT: Photorealistic image with exterior window trim.
Output at the highest resolution possible."""


def get_quality_check_prompt(scope: dict = None) -> str:
    """Step 5: Quality check comparing original to final result."""
    return """You are a Quality Control AI for window visualization. You will receive two images.

IMAGE 1: The REFERENCE image (original house exterior)
IMAGE 2: The FINAL RESULT (house with new windows)

EVALUATE THE VISUALIZATION:

1. WINDOW PLACEMENT
   - Are windows in the exact same positions as original?
   - Are window sizes consistent with openings?
   - Is alignment proper (level, plumb)?

2. WINDOW REALISM
   - Do frames look professionally installed?
   - Are glass reflections natural?
   - Is frame depth and shadow realistic?

3. STYLE CONSISTENCY
   - Are all windows the same style?
   - Do grilles match across all windows?
   - Does trim look consistent?

4. ARCHITECTURAL HARMONY
   - Do new windows suit the house style?
   - Is color coordination appropriate?
   - Does the result look like a real renovation?

5. INTEGRATION
   - Do windows look INSTALLED vs. pasted?
   - Are edges clean and crisp?
   - Is lighting/shadow consistent?

6. PRESERVATION
   - Is house structure intact?
   - Are doors, siding, roof unchanged?
   - Is landscaping preserved?

SCORING GUIDE:
- 0.0 to 0.4: FAIL - Major issues (wrong positions, floating frames, style inconsistency)
- 0.5 to 0.6: POOR - Usable but obvious issues (slight misalignment, unnatural reflections)
- 0.7 to 0.8: GOOD - Minor imperfections only (subtle edge issues)
- 0.9 to 1.0: EXCELLENT - Highly realistic, professional appearance

RETURN ONLY VALID JSON:
{
    "score": <float between 0.0 and 1.0>,
    "issues": [<list of specific issues found, empty if none>],
    "recommendation": "<PASS or REGENERATE>"
}

A score below 0.6 should recommend REGENERATE.
Be strict - homeowners making $10K-50K decisions based on this visualization."""


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
```

**Step 2: Verify prompts module imports correctly**

Run: `cd /home/reid/command-center/testhome/pools-visualizer && source venv/bin/activate && python3 -c "from api.tenants.windows import prompts; print(prompts.get_cleanup_prompt()[:50])"`

Expected: First 50 chars of cleanup prompt

**Step 3: Commit**

```bash
git add api/tenants/windows/prompts.py
git commit -m "feat(windows): add AI prompts for window visualization pipeline"
```

---

## Task 3: Create Frontend Window Type Step

**Files:**
- Create: `frontend/src/components/UploadWizard/WindowTypeStep.js`

**Step 1: Create the WindowTypeStep component**

```javascript
// frontend/src/components/UploadWizard/WindowTypeStep.js
import { ArrowLeft, ArrowRight } from 'lucide-react';
import useVisualizationStore from '../../store/visualizationStore';

const WINDOW_TYPES = [
    { id: 'single_hung', name: 'Single Hung', description: 'Bottom sash slides up, top is fixed' },
    { id: 'double_hung', name: 'Double Hung', description: 'Both sashes slide up and down', popular: true },
    { id: 'casement', name: 'Casement', description: 'Hinged on side, swings outward' },
    { id: 'slider', name: 'Slider', description: 'Sash slides horizontally' },
    { id: 'picture', name: 'Picture', description: 'Fixed, non-operable for views' },
];

const WINDOW_STYLES = [
    { id: 'modern', name: 'Modern' },
    { id: 'traditional', name: 'Traditional' },
    { id: 'colonial', name: 'Colonial' },
    { id: 'craftsman', name: 'Craftsman' },
];

const WindowTypeStep = ({ nextStep, prevStep }) => {
    const { selections, setSelection } = useVisualizationStore();

    return (
        <div className="wizard-step fade-in">
            <div className="step-header">
                <h2>Window Type & Style</h2>
                <p className="step-subtitle">Choose your window type and architectural style</p>
            </div>

            <section>
                <h3>Select Window Type</h3>
                <div className="size-grid">
                    {WINDOW_TYPES.map(type => (
                        <div
                            key={type.id}
                            className={`size-card ${selections.window_type === type.id ? 'selected' : ''} ${type.popular ? 'popular' : ''}`}
                            onClick={() => setSelection('window_type', type.id)}
                        >
                            {type.popular && <span className="popular-badge">Popular</span>}
                            <h4>{type.name}</h4>
                            <p className="description">{type.description}</p>
                        </div>
                    ))}
                </div>
            </section>

            <section>
                <h3>Select Architectural Style</h3>
                <div className="shape-grid">
                    {WINDOW_STYLES.map(style => (
                        <div
                            key={style.id}
                            className={`shape-card ${selections.window_style === style.id ? 'selected' : ''}`}
                            onClick={() => setSelection('window_style', style.id)}
                        >
                            <span>{style.name}</span>
                        </div>
                    ))}
                </div>
            </section>

            <div className="wizard-actions">
                {prevStep && (
                    <button className="btn-back" onClick={prevStep}>
                        <ArrowLeft size={18} /> Back
                    </button>
                )}
                <button
                    className="btn-next"
                    onClick={nextStep}
                    disabled={!selections.window_type || !selections.window_style}
                >
                    Next Step <ArrowRight size={18} />
                </button>
            </div>
        </div>
    );
};

export default WindowTypeStep;
```

**Step 2: Commit**

```bash
git add frontend/src/components/UploadWizard/WindowTypeStep.js
git commit -m "feat(windows): add WindowTypeStep wizard component"
```

---

## Task 4: Create Frontend Frame Material Step

**Files:**
- Create: `frontend/src/components/UploadWizard/FrameMaterialStep.js`

**Step 1: Create the FrameMaterialStep component**

```javascript
// frontend/src/components/UploadWizard/FrameMaterialStep.js
import { ArrowLeft, ArrowRight } from 'lucide-react';
import useVisualizationStore from '../../store/visualizationStore';

const FRAME_MATERIALS = [
    { id: 'vinyl', name: 'Vinyl', description: 'Low maintenance, energy efficient' },
    { id: 'wood', name: 'Wood', description: 'Classic beauty, paintable' },
    { id: 'fiberglass', name: 'Fiberglass', description: 'Strong, durable, low expansion' },
    { id: 'aluminum', name: 'Aluminum', description: 'Slim profiles, modern look' },
];

const FRAME_COLORS = [
    { id: 'white', name: 'White' },
    { id: 'tan', name: 'Tan/Almond' },
    { id: 'brown', name: 'Brown' },
    { id: 'black', name: 'Black' },
    { id: 'bronze', name: 'Bronze' },
];

const FrameMaterialStep = ({ nextStep, prevStep }) => {
    const { selections, setSelection } = useVisualizationStore();

    return (
        <div className="wizard-step fade-in">
            <div className="step-header">
                <h2>Frame Material & Color</h2>
                <p className="step-subtitle">Choose your frame material and finish color</p>
            </div>

            <section>
                <h3>Select Frame Material</h3>
                <div className="size-grid">
                    {FRAME_MATERIALS.map(material => (
                        <div
                            key={material.id}
                            className={`size-card ${selections.frame_material === material.id ? 'selected' : ''}`}
                            onClick={() => setSelection('frame_material', material.id)}
                        >
                            <h4>{material.name}</h4>
                            <p className="description">{material.description}</p>
                        </div>
                    ))}
                </div>
            </section>

            <section>
                <h3>Select Frame Color</h3>
                <div className="shape-grid">
                    {FRAME_COLORS.map(color => (
                        <div
                            key={color.id}
                            className={`shape-card ${selections.frame_color === color.id ? 'selected' : ''}`}
                            onClick={() => setSelection('frame_color', color.id)}
                        >
                            <span>{color.name}</span>
                        </div>
                    ))}
                </div>
            </section>

            <div className="wizard-actions">
                <button className="btn-back" onClick={prevStep}>
                    <ArrowLeft size={18} /> Back
                </button>
                <button
                    className="btn-next"
                    onClick={nextStep}
                    disabled={!selections.frame_material || !selections.frame_color}
                >
                    Next Step <ArrowRight size={18} />
                </button>
            </div>
        </div>
    );
};

export default FrameMaterialStep;
```

**Step 2: Commit**

```bash
git add frontend/src/components/UploadWizard/FrameMaterialStep.js
git commit -m "feat(windows): add FrameMaterialStep wizard component"
```

---

## Task 5: Create Frontend Grille Pattern Step

**Files:**
- Create: `frontend/src/components/UploadWizard/GrillePatternStep.js`

**Step 1: Create the GrillePatternStep component**

```javascript
// frontend/src/components/UploadWizard/GrillePatternStep.js
import { ArrowLeft, ArrowRight } from 'lucide-react';
import useVisualizationStore from '../../store/visualizationStore';

const GRILLE_PATTERNS = [
    { id: 'none', name: 'No Grilles', description: 'Clean, unobstructed view' },
    { id: 'colonial', name: 'Colonial', description: '6 or 9 pane grid pattern' },
    { id: 'prairie', name: 'Prairie', description: 'Border grilles only' },
    { id: 'craftsman', name: 'Craftsman', description: 'Top section grilles only' },
    { id: 'diamond', name: 'Diamond', description: 'Diagonal pattern' },
];

const GLASS_OPTIONS = [
    { id: 'clear', name: 'Clear', description: 'Maximum light and visibility' },
    { id: 'low_e', name: 'Low-E', description: 'Energy efficient coating' },
    { id: 'frosted', name: 'Frosted', description: 'Privacy with diffused light' },
    { id: 'obscure', name: 'Obscure', description: 'Textured privacy glass' },
    { id: 'rain', name: 'Rain', description: 'Decorative rain pattern' },
];

const GrillePatternStep = ({ nextStep, prevStep }) => {
    const { selections, setSelection } = useVisualizationStore();

    return (
        <div className="wizard-step fade-in">
            <div className="step-header">
                <h2>Grilles & Glass</h2>
                <p className="step-subtitle">Choose grille pattern and glass type</p>
            </div>

            <section>
                <h3>Select Grille Pattern</h3>
                <div className="size-grid">
                    {GRILLE_PATTERNS.map(pattern => (
                        <div
                            key={pattern.id}
                            className={`size-card ${selections.grille_pattern === pattern.id ? 'selected' : ''}`}
                            onClick={() => setSelection('grille_pattern', pattern.id)}
                        >
                            <h4>{pattern.name}</h4>
                            <p className="description">{pattern.description}</p>
                        </div>
                    ))}
                </div>
            </section>

            <section>
                <h3>Select Glass Type</h3>
                <div className="size-grid">
                    {GLASS_OPTIONS.map(glass => (
                        <div
                            key={glass.id}
                            className={`size-card ${selections.glass_option === glass.id ? 'selected' : ''}`}
                            onClick={() => setSelection('glass_option', glass.id)}
                        >
                            <h4>{glass.name}</h4>
                            <p className="description">{glass.description}</p>
                        </div>
                    ))}
                </div>
            </section>

            <div className="wizard-actions">
                <button className="btn-back" onClick={prevStep}>
                    <ArrowLeft size={18} /> Back
                </button>
                <button
                    className="btn-next"
                    onClick={nextStep}
                    disabled={!selections.grille_pattern || !selections.glass_option}
                >
                    Next Step <ArrowRight size={18} />
                </button>
            </div>
        </div>
    );
};

export default GrillePatternStep;
```

**Step 2: Commit**

```bash
git add frontend/src/components/UploadWizard/GrillePatternStep.js
git commit -m "feat(windows): add GrillePatternStep wizard component"
```

---

## Task 6: Create Frontend Hardware & Trim Step

**Files:**
- Create: `frontend/src/components/UploadWizard/HardwareTrimStep.js`

**Step 1: Create the HardwareTrimStep component**

```javascript
// frontend/src/components/UploadWizard/HardwareTrimStep.js
import { ArrowLeft, ArrowRight } from 'lucide-react';
import useVisualizationStore from '../../store/visualizationStore';

const HARDWARE_FINISHES = [
    { id: 'white', name: 'White' },
    { id: 'brushed_nickel', name: 'Brushed Nickel' },
    { id: 'oil_rubbed_bronze', name: 'Oil-Rubbed Bronze' },
    { id: 'brass', name: 'Brass' },
];

const TRIM_STYLES = [
    { id: 'standard', name: 'Standard', description: 'Simple flat trim' },
    { id: 'craftsman', name: 'Craftsman', description: 'Bold with header detail' },
    { id: 'colonial', name: 'Colonial', description: 'Classic profiled trim' },
    { id: 'modern', name: 'Modern Flat', description: 'Minimal, sleek profile' },
];

const HardwareTrimStep = ({ nextStep, prevStep }) => {
    const { selections, setSelection } = useVisualizationStore();

    return (
        <div className="wizard-step fade-in">
            <div className="step-header">
                <h2>Hardware & Trim</h2>
                <p className="step-subtitle">Choose hardware finish and exterior trim style</p>
            </div>

            <section>
                <h3>Select Hardware Finish</h3>
                <div className="shape-grid">
                    {HARDWARE_FINISHES.map(finish => (
                        <div
                            key={finish.id}
                            className={`shape-card ${selections.hardware_finish === finish.id ? 'selected' : ''}`}
                            onClick={() => setSelection('hardware_finish', finish.id)}
                        >
                            <span>{finish.name}</span>
                        </div>
                    ))}
                </div>
            </section>

            <section>
                <h3>Select Exterior Trim Style</h3>
                <div className="size-grid">
                    {TRIM_STYLES.map(trim => (
                        <div
                            key={trim.id}
                            className={`size-card ${selections.trim_style === trim.id ? 'selected' : ''}`}
                            onClick={() => setSelection('trim_style', trim.id)}
                        >
                            <h4>{trim.name}</h4>
                            <p className="description">{trim.description}</p>
                        </div>
                    ))}
                </div>
            </section>

            <div className="wizard-actions">
                <button className="btn-back" onClick={prevStep}>
                    <ArrowLeft size={18} /> Back
                </button>
                <button
                    className="btn-next"
                    onClick={nextStep}
                    disabled={!selections.hardware_finish || !selections.trim_style}
                >
                    Generate Visualization <ArrowRight size={18} />
                </button>
            </div>
        </div>
    );
};

export default HardwareTrimStep;
```

**Step 2: Commit**

```bash
git add frontend/src/components/UploadWizard/HardwareTrimStep.js
git commit -m "feat(windows): add HardwareTrimStep wizard component"
```

---

## Task 7: Update Visualization Store for Windows

**Files:**
- Modify: `frontend/src/store/visualizationStore.js:55-77`

**Step 1: Add windows selections to initialState**

Replace the `selections` object in `initialState` (lines 55-77) with:

```javascript
  selections: {
    // === POOLS SELECTIONS ===
    // Screen 1: Size & Shape
    size: 'classic',
    shape: 'rectangle',

    // Screen 2: Finish & Built-ins
    finish: 'pebble_blue',
    tanning_ledge: true,
    lounger_count: 2,
    attached_spa: false,

    // Screen 3: Deck
    deck_material: 'travertine',
    deck_color: 'cream',

    // Screen 4: Water Features
    water_features: [],

    // Screen 5: Finishing Touches
    lighting: 'none',
    landscaping: 'none',
    furniture: 'none',

    // === WINDOWS SELECTIONS ===
    // Screen 1: Window Type & Style
    window_type: 'double_hung',
    window_style: 'traditional',

    // Screen 2: Frame Material & Color
    frame_material: 'vinyl',
    frame_color: 'white',

    // Screen 3: Grilles & Glass
    grille_pattern: 'none',
    glass_option: 'clear',

    // Screen 4: Hardware & Trim
    hardware_finish: 'white',
    trim_style: 'standard',
  }
```

**Step 2: Verify store still works**

Run: `cd /home/reid/command-center/testhome/pools-visualizer/frontend && npm run build 2>&1 | head -20`

Expected: Build succeeds or only unrelated warnings

**Step 3: Commit**

```bash
git add frontend/src/store/visualizationStore.js
git commit -m "feat(windows): add windows selections to visualization store"
```

---

## Task 8: Update PDF Generator for Windows

**Files:**
- Modify: `api/utils/pdf_generator.py`

**Step 1: Add windows pricing constants after line 21**

```python
# Window pricing estimates
WINDOW_PRICING = {
    'single_hung': 350,
    'double_hung': 450,
    'casement': 500,
    'slider': 400,
    'picture': 300,
    'vinyl_multiplier': 1.0,
    'wood_multiplier': 1.5,
    'fiberglass_multiplier': 1.3,
    'aluminum_multiplier': 1.2,
    'grille_add': 150,
    'decorative_glass_add': 100,
    'trim_upgrade': 75,
    'installation_per_window': 150,
}
```

**Step 2: Add calculate_windows_quote function after calculate_quote**

```python
def calculate_windows_quote(visualization_request, window_count=5):
    """
    Calculate quote based on window selections.
    Assumes 5 windows unless specified.
    """
    options = visualization_request.options or {}
    items = []
    total = 0

    # Window base price
    window_type = options.get('window_type', 'double_hung')
    base_price = WINDOW_PRICING.get(window_type, WINDOW_PRICING['double_hung'])

    # Material multiplier
    material = options.get('frame_material', 'vinyl')
    multiplier = WINDOW_PRICING.get(f'{material}_multiplier', 1.0)

    window_unit_price = int(base_price * multiplier)
    window_total = window_unit_price * window_count

    items.append({
        'name': f'{window_type.replace("_", " ").title()} Windows ({material.title()})',
        'qty': window_count,
        'unit_price': window_unit_price,
        'subtotal': window_total
    })
    total += window_total

    # Grille pattern
    grille = options.get('grille_pattern', 'none')
    if grille != 'none':
        grille_total = WINDOW_PRICING['grille_add'] * window_count
        items.append({
            'name': f'{grille.title()} Grille Pattern',
            'qty': window_count,
            'unit_price': WINDOW_PRICING['grille_add'],
            'subtotal': grille_total
        })
        total += grille_total

    # Decorative glass
    glass = options.get('glass_option', 'clear')
    if glass not in ['clear', 'low_e']:
        glass_total = WINDOW_PRICING['decorative_glass_add'] * window_count
        items.append({
            'name': f'{glass.title()} Glass',
            'qty': window_count,
            'unit_price': WINDOW_PRICING['decorative_glass_add'],
            'subtotal': glass_total
        })
        total += glass_total

    # Trim upgrade
    trim = options.get('trim_style', 'standard')
    if trim != 'standard':
        trim_total = WINDOW_PRICING['trim_upgrade'] * window_count
        items.append({
            'name': f'{trim.title()} Trim Upgrade',
            'qty': window_count,
            'unit_price': WINDOW_PRICING['trim_upgrade'],
            'subtotal': trim_total
        })
        total += trim_total

    # Installation
    install_total = WINDOW_PRICING['installation_per_window'] * window_count
    items.append({
        'name': 'Professional Installation',
        'qty': window_count,
        'unit_price': WINDOW_PRICING['installation_per_window'],
        'subtotal': install_total
    })
    total += install_total

    return {'items': items, 'total': total}
```

**Step 3: Commit**

```bash
git add api/utils/pdf_generator.py
git commit -m "feat(windows): add windows quote calculation to PDF generator"
```

---

## Task 9: Integration - Wire Up Windows Wizard (Manual Step)

**Note to implementer:** This task requires manual integration based on how the UploadPage is structured. The key changes needed:

1. **UploadPage.js** - Add tenant detection and render appropriate wizard steps
2. **App.js** - Add `/windows` routes if needed
3. **API endpoint** - Ensure tenant parameter is passed to backend

This is marked as a manual integration step because the exact implementation depends on:
- How you want to switch between pools/windows (URL, setting, dropdown)
- Whether you want separate routes or a unified wizard

**Suggested approach:**
- Add `?tenant=windows` query param support
- Or add `/windows/upload` route that sets tenant context

**Commit when done:**

```bash
git add -A
git commit -m "feat(windows): integrate windows wizard into upload flow"
```

---

## Summary

| Task | Component | Effort |
|------|-----------|--------|
| 1 | Backend tenant config | ~15 min |
| 2 | AI prompts module | ~20 min |
| 3 | WindowTypeStep | ~10 min |
| 4 | FrameMaterialStep | ~10 min |
| 5 | GrillePatternStep | ~10 min |
| 6 | HardwareTrimStep | ~10 min |
| 7 | Store updates | ~5 min |
| 8 | PDF generator | ~15 min |
| 9 | Integration | ~30 min |

**Total estimated:** ~2 hours

---

Plan complete and saved to `docs/plans/2025-12-19-windows-visualizer.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
