# Glass Doors & Windows + Roofs Tenants Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extend the windows tenant to support sliding glass doors and accordion doors, and create a new roofs tenant with full material catalog and solar panel visualization.

**Architecture:** Two separate tenant wizards accessible via different routes (`/upload/windows` and `/upload/roofs`). Each tenant has its own config, prompts, and frontend wizard. Tenant switching via `ACTIVE_TENANT` env var for backend; frontend uses route-based separation.

**Tech Stack:** Django 4.0, DRF, React 19.1, Zustand, Google Gemini API

---

## Part 1: Extend Windows Tenant to "Glass Doors & Windows"

### Task 1: Add PROJECT_TYPES and DOOR_TYPES to Windows Config

**Files:**
- Modify: `api/tenants/windows/config.py`

**Step 1: Add PROJECT_TYPES after VERTICAL_DISPLAY_NAME**

Add this code after line 9 (`VERTICAL_DISPLAY_NAME = ...`):

```python
PROJECT_TYPES = [
    {
        'id': 'replace_existing',
        'name': 'Replace Existing',
        'prompt_hint': 'replacing existing windows and doors',
        'description': 'Replace current windows and/or doors with new ones',
    },
    {
        'id': 'new_opening',
        'name': 'Create New Opening',
        'prompt_hint': 'creating new window or door openings in walls',
        'description': 'Add new windows or doors where none exist',
    },
    {
        'id': 'enclose_patio',
        'name': 'Enclose Patio',
        'prompt_hint': 'enclosing patio or porch with glass doors and windows',
        'description': 'Convert open patio/porch to enclosed sunroom',
        'popular': True,
    },
]

DOOR_TYPES = [
    {
        'id': 'none',
        'name': 'Windows Only',
        'prompt_hint': '',
        'description': 'No doors, windows only',
    },
    {
        'id': 'sliding_glass',
        'name': 'Sliding Glass Door',
        'prompt_hint': 'sliding glass patio door with large glass panels',
        'description': 'Standard sliding glass door for patio access',
        'popular': True,
    },
    {
        'id': 'accordion',
        'name': 'Accordion Door',
        'prompt_hint': 'accordion folding glass door system with multiple panels',
        'description': 'Multi-panel folding door that opens completely',
        'popular': True,
    },
    {
        'id': 'bi_fold',
        'name': 'Bi-Fold Door',
        'prompt_hint': 'bi-fold glass door with panels that fold in pairs',
        'description': 'Panels fold in pairs for wide opening',
    },
    {
        'id': 'french',
        'name': 'French Door',
        'prompt_hint': 'french doors with glass panels and traditional styling',
        'description': 'Classic hinged double doors with glass',
    },
]
```

**Step 2: Update VERTICAL_DISPLAY_NAME**

Change line 9 from:
```python
VERTICAL_DISPLAY_NAME = "Window Replacement"
```
to:
```python
VERTICAL_DISPLAY_NAME = "Glass Doors & Windows"
```

**Step 3: Update get_config() to include new options**

In the `get_config()` function (around line 225), add to the return dict:

```python
'project_types': PROJECT_TYPES,
'door_types': DOOR_TYPES,
```

**Step 4: Verify changes**

Run: `cd /home/reid/command-center/testhome/pools-visualizer && source venv/bin/activate && python3 -c "from api.tenants.windows.config import get_config; c = get_config(); print('project_types:', len(c.get('project_types', []))); print('door_types:', len(c.get('door_types', [])))"`

Expected:
```
project_types: 3
door_types: 5
```

**Step 5: Commit**

```bash
git add api/tenants/windows/config.py
git commit -m "feat(windows): add project types and door types to config"
```

---

### Task 2: Update Windows Prompts for Door Handling

**Files:**
- Modify: `api/tenants/windows/prompts.py`

**Step 1: Read current prompts file**

First, read the file to understand the current structure.

**Step 2: Update get_window_frame_prompt to handle doors**

Find the `get_window_frame_prompt` function and update it to include door handling. The function should:

1. Get the door_type from selections
2. If door_type is not 'none', include door installation in the prompt
3. Adjust prompt based on project_type

Replace the function with:

```python
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
```

**Step 3: Verify prompts load**

Run: `cd /home/reid/command-center/testhome/pools-visualizer && source venv/bin/activate && python3 -c "from api.tenants.windows.prompts import get_window_frame_prompt; p = get_window_frame_prompt({'door_type': 'sliding_glass', 'project_type': 'enclose_patio'}); print('Has door section:', 'DOOR INSTALLATION' in p)"`

Expected: `Has door section: True`

**Step 4: Commit**

```bash
git add api/tenants/windows/prompts.py
git commit -m "feat(windows): add door handling to prompts"
```

---

### Task 3: Add Zustand Store Keys for Windows

**Files:**
- Modify: `frontend/src/store/visualizationStore.js`

**Step 1: Add new keys to initial state**

Find the initial state object and add:

```javascript
project_type: null,
door_type: null,
```

**Step 2: Add setters in the store actions**

Add these setter functions:

```javascript
setProjectType: (project_type) => set({ selections: { ...get().selections, project_type } }),
setDoorType: (door_type) => set({ selections: { ...get().selections, door_type } }),
```

**Step 3: Update resetSelections to include new keys**

In the `resetSelections` function, add:

```javascript
project_type: null,
door_type: null,
```

**Step 4: Verify store compiles**

Run: `cd /home/reid/command-center/testhome/pools-visualizer/frontend && npm run build 2>&1 | head -20`

Expected: No errors related to store

**Step 5: Commit**

```bash
git add frontend/src/store/visualizationStore.js
git commit -m "feat(store): add project_type and door_type keys"
```

---

### Task 4: Create ProjectTypeStep Component

**Files:**
- Create: `frontend/src/components/UploadWizard/ProjectTypeStep.js`

**Step 1: Create the component**

```javascript
import React, { useEffect, useState } from 'react';
import { Home, PlusSquare, Sun } from 'lucide-react';
import useVisualizationStore from '../../store/visualizationStore';

const PROJECT_TYPES = [
  {
    id: 'replace_existing',
    name: 'Replace Existing',
    description: 'Replace current windows and/or doors with new ones',
    icon: Home,
  },
  {
    id: 'new_opening',
    name: 'Create New Opening',
    description: 'Add new windows or doors where none exist',
    icon: PlusSquare,
  },
  {
    id: 'enclose_patio',
    name: 'Enclose Patio',
    description: 'Convert open patio/porch to enclosed sunroom',
    icon: Sun,
    popular: true,
  },
];

const ProjectTypeStep = ({ nextStep }) => {
  const { selections, setProjectType } = useVisualizationStore();
  const [selected, setSelected] = useState(selections.project_type || null);

  useEffect(() => {
    if (selections.project_type) {
      setSelected(selections.project_type);
    }
  }, [selections.project_type]);

  const handleSelect = (typeId) => {
    setSelected(typeId);
    setProjectType(typeId);
  };

  const handleNext = () => {
    if (selected) {
      nextStep();
    }
  };

  return (
    <div className="wizard-step">
      <h2 className="step-title">What type of project is this?</h2>
      <p className="step-subtitle">Select your project type to get started</p>

      <div className="options-grid three-column">
        {PROJECT_TYPES.map((type) => {
          const IconComponent = type.icon;
          return (
            <div
              key={type.id}
              className={`option-card ${selected === type.id ? 'selected' : ''}`}
              onClick={() => handleSelect(type.id)}
            >
              {type.popular && <span className="popular-badge">Popular</span>}
              <div className="option-icon">
                <IconComponent size={32} />
              </div>
              <h3 className="option-name">{type.name}</h3>
              <p className="option-description">{type.description}</p>
            </div>
          );
        })}
      </div>

      <div className="wizard-navigation">
        <button
          className="nav-button primary"
          onClick={handleNext}
          disabled={!selected}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default ProjectTypeStep;
```

**Step 2: Verify component compiles**

Run: `cd /home/reid/command-center/testhome/pools-visualizer/frontend && npm run build 2>&1 | grep -i error | head -5`

Expected: No errors

**Step 3: Commit**

```bash
git add frontend/src/components/UploadWizard/ProjectTypeStep.js
git commit -m "feat(wizard): add ProjectTypeStep component"
```

---

### Task 5: Create DoorTypeStep Component

**Files:**
- Create: `frontend/src/components/UploadWizard/DoorTypeStep.js`

**Step 1: Create the component**

```javascript
import React, { useEffect, useState } from 'react';
import { Square, Columns, FoldVertical, DoorOpen } from 'lucide-react';
import useVisualizationStore from '../../store/visualizationStore';

const DOOR_TYPES = [
  {
    id: 'none',
    name: 'Windows Only',
    description: 'No doors, windows only',
    icon: Square,
  },
  {
    id: 'sliding_glass',
    name: 'Sliding Glass Door',
    description: 'Standard sliding glass door for patio access',
    icon: Columns,
    popular: true,
  },
  {
    id: 'accordion',
    name: 'Accordion Door',
    description: 'Multi-panel folding door that opens completely',
    icon: FoldVertical,
    popular: true,
  },
  {
    id: 'bi_fold',
    name: 'Bi-Fold Door',
    description: 'Panels fold in pairs for wide opening',
    icon: FoldVertical,
  },
  {
    id: 'french',
    name: 'French Door',
    description: 'Classic hinged double doors with glass',
    icon: DoorOpen,
  },
];

const DoorTypeStep = ({ nextStep, prevStep }) => {
  const { selections, setDoorType } = useVisualizationStore();
  const [selected, setSelected] = useState(selections.door_type || null);

  useEffect(() => {
    if (selections.door_type) {
      setSelected(selections.door_type);
    }
  }, [selections.door_type]);

  const handleSelect = (typeId) => {
    setSelected(typeId);
    setDoorType(typeId);
  };

  const handleNext = () => {
    if (selected) {
      nextStep();
    }
  };

  return (
    <div className="wizard-step">
      <h2 className="step-title">Select Door Type</h2>
      <p className="step-subtitle">Choose the type of door for your project (or windows only)</p>

      <div className="options-grid">
        {DOOR_TYPES.map((type) => {
          const IconComponent = type.icon;
          return (
            <div
              key={type.id}
              className={`option-card ${selected === type.id ? 'selected' : ''}`}
              onClick={() => handleSelect(type.id)}
            >
              {type.popular && <span className="popular-badge">Popular</span>}
              <div className="option-icon">
                <IconComponent size={32} />
              </div>
              <h3 className="option-name">{type.name}</h3>
              <p className="option-description">{type.description}</p>
            </div>
          );
        })}
      </div>

      <div className="wizard-navigation">
        <button className="nav-button secondary" onClick={prevStep}>
          Back
        </button>
        <button
          className="nav-button primary"
          onClick={handleNext}
          disabled={!selected}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default DoorTypeStep;
```

**Step 2: Commit**

```bash
git add frontend/src/components/UploadWizard/DoorTypeStep.js
git commit -m "feat(wizard): add DoorTypeStep component"
```

---

### Task 6: Update WindowsUploadPage to 8 Steps

**Files:**
- Modify: `frontend/src/pages/WindowsUploadPage.js`

**Step 1: Add imports for new components**

Add after line 6:

```javascript
import ProjectTypeStep from '../components/UploadWizard/ProjectTypeStep';
import DoorTypeStep from '../components/UploadWizard/DoorTypeStep';
```

**Step 2: Update step count in progress bar**

Change line 66-67 from:
```javascript
style={{ width: `${((step - 1) / 5) * 100}%` }}
```
to:
```javascript
style={{ width: `${((step - 1) / 7) * 100}%` }}
```

Change line 69 from:
```javascript
{[1, 2, 3, 4, 5, 6].map(s => (
```
to:
```javascript
{[1, 2, 3, 4, 5, 6, 7, 8].map(s => (
```

**Step 3: Update step rendering**

Replace the step rendering section (lines 77-118) with:

```javascript
{step === 1 && (
  <ProjectTypeStep nextStep={nextStep} />
)}
{step === 2 && (
  <DoorTypeStep nextStep={nextStep} prevStep={prevStep} />
)}
{step === 3 && (
  <WindowTypeStep nextStep={nextStep} prevStep={prevStep} />
)}
{step === 4 && (
  <FrameMaterialStep nextStep={nextStep} prevStep={prevStep} />
)}
{step === 5 && (
  <GrillePatternStep nextStep={nextStep} prevStep={prevStep} />
)}
{step === 6 && (
  <HardwareTrimStep nextStep={nextStep} prevStep={prevStep} />
)}
{step === 7 && (
  <Step4Upload
    formData={formData}
    setFormData={setFormData}
    nextStep={nextStep}
    prevStep={prevStep}
  />
)}
{step === 8 && (
  <Step5Review
    formData={formData}
    selections={selections}
    prevStep={prevStep}
    handleSubmit={handleSubmit}
    isSubmitting={isSubmitting}
    error={error}
  />
)}
```

**Step 4: Update handleSubmit to include new fields**

In the `handleSubmit` function, update `selectionsPayload` to include:

```javascript
const selectionsPayload = {
  project_type: selections.project_type,
  door_type: selections.door_type,
  window_type: selections.window_type,
  window_style: selections.window_style,
  frame_material: selections.frame_material,
  frame_color: selections.frame_color,
  grille_pattern: selections.grille_pattern,
  glass_option: selections.glass_option,
  hardware_finish: selections.hardware_finish,
  trim_style: selections.trim_style,
};
```

**Step 5: Verify build**

Run: `cd /home/reid/command-center/testhome/pools-visualizer/frontend && npm run build`

Expected: Build succeeds

**Step 6: Commit**

```bash
git add frontend/src/pages/WindowsUploadPage.js
git commit -m "feat(windows): update wizard to 8 steps with project type and doors"
```

---

## Part 2: Create Roofs Tenant

### Task 7: Create Roofs Tenant __init__.py

**Files:**
- Create: `api/tenants/roofs/__init__.py`

**Step 1: Create the file**

```python
"""
Roofs Tenant - Roof replacement and solar panel visualization.
"""
from .config import RoofsTenantConfig

__all__ = ['RoofsTenantConfig']
```

**Step 2: Commit**

```bash
git add api/tenants/roofs/__init__.py
git commit -m "feat(roofs): create roofs tenant package"
```

---

### Task 8: Create Roofs Config

**Files:**
- Create: `api/tenants/roofs/config.py`

**Step 1: Create the full config file**

```python
"""
Roofs Vertical Configuration
Port: 8008
Pipeline: cleanup → roof_material → solar_panels → gutters_trim → quality_check
"""
from api.tenants.base import BaseTenantConfig

VERTICAL_NAME = "roofs"
VERTICAL_DISPLAY_NAME = "Roofs & Solar"

ROOF_MATERIALS = [
    {
        'id': 'asphalt_3tab',
        'name': 'Asphalt - 3-Tab',
        'price_per_sqft': 3.50,
        'prompt_hint': 'traditional 3-tab asphalt shingles',
        'description': 'Affordable, classic look, 15-20 year lifespan',
    },
    {
        'id': 'asphalt_architectural',
        'name': 'Asphalt - Architectural',
        'price_per_sqft': 4.75,
        'prompt_hint': 'dimensional architectural asphalt shingles with shadow lines',
        'description': 'Premium look, 30 year lifespan',
        'popular': True,
    },
    {
        'id': 'metal_standing_seam',
        'name': 'Metal - Standing Seam',
        'price_per_sqft': 9.50,
        'prompt_hint': 'standing seam metal roof with vertical ribs',
        'description': 'Modern, durable, 50+ year lifespan',
        'popular': True,
    },
    {
        'id': 'metal_corrugated',
        'name': 'Metal - Corrugated',
        'price_per_sqft': 6.50,
        'prompt_hint': 'corrugated metal roofing panels',
        'description': 'Industrial/farmhouse look, 40+ year lifespan',
    },
    {
        'id': 'clay_tile',
        'name': 'Clay Tile',
        'price_per_sqft': 15.00,
        'prompt_hint': 'traditional barrel clay roof tiles',
        'description': 'Mediterranean style, 100+ year lifespan',
    },
    {
        'id': 'concrete_tile',
        'name': 'Concrete Tile',
        'price_per_sqft': 10.50,
        'prompt_hint': 'flat or curved concrete roof tiles',
        'description': 'Durable, fire-resistant, 50+ year lifespan',
    },
    {
        'id': 'slate',
        'name': 'Natural Slate',
        'price_per_sqft': 22.00,
        'prompt_hint': 'natural slate roofing tiles',
        'description': 'Premium natural stone, 100+ year lifespan',
    },
    {
        'id': 'wood_shake',
        'name': 'Wood Shake',
        'price_per_sqft': 12.50,
        'prompt_hint': 'cedar wood shake shingles',
        'description': 'Rustic natural look, 30 year lifespan',
    },
    {
        'id': 'tpo_flat',
        'name': 'TPO (Flat Roof)',
        'price_per_sqft': 5.50,
        'prompt_hint': 'white TPO membrane flat roof',
        'description': 'For flat/low-slope roofs, 20-30 year lifespan',
    },
]

ROOF_COLORS = [
    {'id': 'charcoal', 'name': 'Charcoal', 'prompt_hint': 'charcoal gray'},
    {'id': 'black', 'name': 'Black', 'prompt_hint': 'black'},
    {'id': 'brown', 'name': 'Brown', 'prompt_hint': 'brown'},
    {'id': 'tan', 'name': 'Tan', 'prompt_hint': 'tan/beige'},
    {'id': 'terracotta', 'name': 'Terracotta', 'prompt_hint': 'terracotta red'},
    {'id': 'slate_gray', 'name': 'Slate Gray', 'prompt_hint': 'slate gray'},
    {'id': 'weathered_wood', 'name': 'Weathered Wood', 'prompt_hint': 'weathered wood brown'},
    {'id': 'green', 'name': 'Forest Green', 'prompt_hint': 'forest green'},
    {'id': 'blue', 'name': 'Colonial Blue', 'prompt_hint': 'colonial blue'},
    {'id': 'white', 'name': 'White', 'prompt_hint': 'white'},
]

SOLAR_OPTIONS = [
    {
        'id': 'none',
        'name': 'No Solar',
        'prompt_hint': '',
        'description': 'Roof only, no solar panels',
    },
    {
        'id': 'partial',
        'name': 'Partial Coverage',
        'prompt_hint': 'solar panel array covering approximately 30% of south-facing roof',
        'description': 'Solar panels on part of the roof',
        'popular': True,
    },
    {
        'id': 'full_south',
        'name': 'Full South Roof',
        'prompt_hint': 'solar panel array covering entire south-facing roof plane',
        'description': 'Maximize solar on south-facing roof',
    },
    {
        'id': 'full_all',
        'name': 'Maximum Coverage',
        'prompt_hint': 'solar panel arrays covering all suitable roof planes',
        'description': 'Solar panels on all viable roof areas',
    },
]

GUTTER_OPTIONS = [
    {
        'id': 'none',
        'name': 'No Gutters',
        'prompt_hint': '',
        'description': 'No gutter system',
    },
    {
        'id': 'standard',
        'name': 'Standard Gutters',
        'prompt_hint': 'K-style aluminum gutters with downspouts',
        'description': 'Standard aluminum gutter system',
        'popular': True,
    },
    {
        'id': 'seamless',
        'name': 'Seamless Gutters',
        'prompt_hint': 'seamless aluminum gutters with downspouts',
        'description': 'Premium seamless gutter system',
    },
    {
        'id': 'copper',
        'name': 'Copper Gutters',
        'prompt_hint': 'copper half-round gutters with copper downspouts',
        'description': 'Premium copper gutter system',
    },
]

PIPELINE_STEPS = ['cleanup', 'roof_material', 'solar_panels', 'gutters_trim', 'quality_check']

PRIMARY_COLOR = "#D84315"  # Deep Orange
SECONDARY_COLOR = "#FF7043"


class RoofsTenantConfig(BaseTenantConfig):
    """Roofs vertical tenant configuration."""

    tenant_id = 'roofs'
    display_name = VERTICAL_DISPLAY_NAME

    def get_pipeline_steps(self):
        return PIPELINE_STEPS

    def get_step_config(self, step_name):
        configs = {
            'cleanup': {'type': 'cleanup', 'progress_weight': 15, 'description': 'Preparing image'},
            'roof_material': {'type': 'insertion', 'scope_key': None, 'feature_name': 'roof', 'progress_weight': 45, 'description': 'Installing roofing material'},
            'solar_panels': {'type': 'insertion', 'scope_key': 'solar_option', 'feature_name': 'solar', 'progress_weight': 20, 'description': 'Adding solar panels'},
            'gutters_trim': {'type': 'insertion', 'scope_key': 'gutter_option', 'feature_name': 'gutters', 'progress_weight': 15, 'description': 'Installing gutters'},
            'quality_check': {'type': 'quality_check', 'progress_weight': 5, 'description': 'Quality check'},
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
        return [(color['id'], color['name']) for color in ROOF_COLORS]

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
            {k: v for k, v in mat.items() if k != 'price_per_sqft'}
            for mat in ROOF_MATERIALS
        ],
        'roof_colors': ROOF_COLORS,
        'solar_options': SOLAR_OPTIONS,
        'gutter_options': GUTTER_OPTIONS,
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
        'solar_options': SOLAR_OPTIONS,
        'gutter_options': GUTTER_OPTIONS,
        'pipeline_steps': PIPELINE_STEPS,
    }
```

**Step 2: Verify config loads**

Run: `cd /home/reid/command-center/testhome/pools-visualizer && source venv/bin/activate && python3 -c "from api.tenants.roofs.config import RoofsTenantConfig; c = RoofsTenantConfig(); print('tenant_id:', c.tenant_id); print('steps:', c.get_pipeline_steps())"`

Expected:
```
tenant_id: roofs
steps: ['cleanup', 'roof_material', 'solar_panels', 'gutters_trim', 'quality_check']
```

**Step 3: Commit**

```bash
git add api/tenants/roofs/config.py
git commit -m "feat(roofs): create roofs tenant config with materials, colors, solar, gutters"
```

---

### Task 9: Create Roofs Prompts

**Files:**
- Create: `api/tenants/roofs/prompts.py`

**Step 1: Create the prompts file**

```python
"""
Roofs Visualizer - AI Prompts
Layered rendering pipeline for roof replacement and solar installation.

Pipeline: cleanup → roof_material → solar_panels → gutters_trim → quality_check
"""

from api.tenants.roofs import config


def get_cleanup_prompt() -> str:
    """Step 1: Clean the image and prepare for roof visualization."""
    return """Photorealistic image editing. Prepare this house exterior for roof visualization.

WEATHER AND LIGHTING:
Make conditions ideal: sunny day with clear blue sky, good natural lighting to highlight roof details.

REMOVE ONLY THESE ITEMS:
- Debris, leaves, moss on existing roof
- Temporary tarps or covers
- Construction materials and ladders
- Satellite dishes and antennas (will be repositioned)
- Tree branches directly overhanging roof

PRESERVE EXACTLY:
- House structure and all walls
- All windows and doors
- Existing roof SHAPE and pitch (we will replace material only)
- Chimneys, skylights, roof vents
- Landscaping and property features
- Garage and outbuildings

ROOF VISIBILITY:
- Ensure all roof planes are clearly visible
- Maintain accurate roof geometry
- Keep all roof penetrations in original positions

OUTPUT: Clean, well-lit house exterior with roof clearly visible.
Output at highest resolution possible."""


def get_roof_material_prompt(selections: dict) -> str:
    """Step 2: Replace roof material with selected option."""
    roof_material = next(
        (r for r in config.ROOF_MATERIALS if r['id'] == selections.get('roof_material', 'asphalt_architectural')),
        config.ROOF_MATERIALS[1]
    )
    roof_color = next(
        (c for c in config.ROOF_COLORS if c['id'] == selections.get('roof_color', 'charcoal')),
        config.ROOF_COLORS[0]
    )

    return f"""Photorealistic inpainting. Replace the entire roof with new roofing material.

ROOF SPECIFICATIONS:
- Material: {roof_material['prompt_hint']}
- Color: {roof_color['prompt_hint']}

INSTALLATION REQUIREMENTS:
- Replace ALL existing roofing material on every roof plane
- Maintain exact roof shape, pitch, valleys, and ridges
- Keep chimneys, skylights, vents in exact positions
- Show proper material patterns:
  - For shingles: overlapping rows with proper exposure
  - For metal: standing seams or panel joints
  - For tile: interlocking pattern with correct spacing
  - For slate: natural variation in color/texture

MATERIAL REALISM:
- {roof_material['name']} must look authentic with proper texture
- {roof_color['name']} color should be consistent with subtle natural variation
- Appropriate reflectivity for material type
- Proper shadowing based on roof angles and sun position

INTEGRATION:
- Roof edges must align perfectly with fascia boards
- Ridge caps should match material style
- Flashing visible at all penetrations and valleys
- Drip edge along all eaves

PRESERVE EXACTLY:
- House walls, windows, doors
- Landscaping and surroundings
- Original lighting atmosphere

OUTPUT: Photorealistic image with new {roof_material['name']} roof in {roof_color['name']}.
Output at highest resolution possible."""


def get_solar_panels_prompt(selections: dict) -> str:
    """Step 3: Add solar panels if selected."""
    solar_option = next(
        (s for s in config.SOLAR_OPTIONS if s['id'] == selections.get('solar_option', 'none')),
        config.SOLAR_OPTIONS[0]
    )

    if solar_option['id'] == 'none':
        return None

    return f"""Photorealistic inpainting. Install solar panels on the roof.

SOLAR SPECIFICATIONS:
- Coverage: {solar_option['prompt_hint']}

INSTALLATION REQUIREMENTS:
- Mount panels on optimal roof sections (prefer south-facing)
- Panels aligned in neat, parallel rows
- Proper spacing between panels (6-12 inches)
- Mounting rails visible beneath panels
- Conduit running along roof edge to inverter location

PANEL APPEARANCE:
- Black monocrystalline panels with visible grid lines
- Aluminum frame around each panel
- Subtle blue/purple tint when light hits at angle
- Glass surface showing realistic reflections

SHADOW AND LIGHTING:
- Panels cast realistic shadows on roof surface
- Shadow direction matches sun position
- Slight gap shadow beneath panels from mounting hardware

PRESERVE EXACTLY:
- New roof material exactly as rendered
- All chimneys, vents, skylights (panels avoid these)
- House structure below roofline
- Landscaping and surroundings

OUTPUT: Photorealistic image with solar panel installation.
Output at highest resolution possible."""


def get_gutters_trim_prompt(selections: dict) -> str:
    """Step 4: Add gutters if selected."""
    gutter_option = next(
        (g for g in config.GUTTER_OPTIONS if g['id'] == selections.get('gutter_option', 'none')),
        config.GUTTER_OPTIONS[0]
    )

    if gutter_option['id'] == 'none':
        return None

    return f"""Photorealistic inpainting. Install gutter system on the house.

GUTTER SPECIFICATIONS:
- Type: {gutter_option['prompt_hint']}

INSTALLATION REQUIREMENTS:
- Gutters along all eaves where water would drain
- Proper slope toward downspouts (not visible but affects placement)
- Downspouts at corners and every 30-40 feet
- Downspout elbows directing water away from foundation

GUTTER APPEARANCE:
- Clean, professionally installed look
- Color coordinated with fascia/trim
- Visible mounting brackets at regular intervals
- Seamless joints (for seamless option)

DOWNSPOUT ROUTING:
- Downspouts follow wall contours
- Elbows at top and bottom
- Extensions at ground level

PRESERVE EXACTLY:
- Roof with new material and solar panels
- House structure, windows, doors
- Landscaping

OUTPUT: Photorealistic image with complete gutter system.
Output at highest resolution possible."""


def get_quality_check_prompt(scope: dict = None) -> str:
    """Step 5: Quality check the final result."""
    return """You are a Quality Control AI for roof replacement visualization.

IMAGE 1: REFERENCE (original house)
IMAGE 2: FINAL RESULT (house with new roof)

EVALUATE:

1. ROOF MATERIAL ACCURACY
   - Is the selected material accurately represented?
   - Is color consistent with selection?
   - Does material have authentic texture?

2. GEOMETRY PRESERVATION
   - Is roof shape/pitch preserved from original?
   - Are all penetrations (chimneys, vents) in correct positions?
   - Are valleys and ridges properly rendered?

3. INSTALLATION REALISM
   - Does roof look professionally installed?
   - Are flashing details correct?
   - Do materials scale properly?

4. SOLAR PANELS (if present)
   - Are panels properly positioned?
   - Do they follow roof contours?
   - Is mounting hardware realistic?

5. GUTTERS (if present)
   - Are gutters properly mounted?
   - Are downspouts logically placed?

6. PRESERVATION
   - Are house walls, windows intact?
   - Is landscaping preserved?
   - Any artifacts or distortions?

SCORING:
- 0.0-0.4: FAIL - Major issues
- 0.5-0.6: POOR - Obvious problems
- 0.7-0.8: GOOD - Minor imperfections
- 0.9-1.0: EXCELLENT - Highly realistic

RETURN ONLY VALID JSON:
{
    "score": <float 0.0-1.0>,
    "issues": [<list of issues>],
    "recommendation": "<PASS or REGENERATE>"
}

Score below 0.6 should recommend REGENERATE."""


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
        return get_quality_check_prompt()
    else:
        raise ValueError(f"Unknown pipeline step: {step}")
```

**Step 2: Verify prompts load**

Run: `cd /home/reid/command-center/testhome/pools-visualizer && source venv/bin/activate && python3 -c "from api.tenants.roofs.prompts import get_prompt; p = get_prompt('roof_material', {'roof_material': 'metal_standing_seam', 'roof_color': 'charcoal'}); print('Has metal:', 'standing seam' in p)"`

Expected: `Has metal: True`

**Step 3: Commit**

```bash
git add api/tenants/roofs/prompts.py
git commit -m "feat(roofs): create roofs prompts for 5-step pipeline"
```

---

### Task 10: Register Roofs Tenant

**Files:**
- Modify: `api/tenants/__init__.py`

**Step 1: Add import for RoofsTenantConfig**

Add after line 16:

```python
from .roofs.config import RoofsTenantConfig
```

**Step 2: Register roofs tenant**

Add after line 87:

```python
register_tenant(RoofsTenantConfig())
```

**Step 3: Verify registration**

Run: `cd /home/reid/command-center/testhome/pools-visualizer && source venv/bin/activate && python3 -c "from api.tenants import get_all_tenants; print('Tenants:', list(get_all_tenants().keys()))"`

Expected: `Tenants: ['pools', 'windows', 'roofs']`

**Step 4: Commit**

```bash
git add api/tenants/__init__.py
git commit -m "feat(tenants): register roofs tenant"
```

---

### Task 11: Add Roofs Store Keys

**Files:**
- Modify: `frontend/src/store/visualizationStore.js`

**Step 1: Add roofs keys to initial state**

Add these to the selections initial state:

```javascript
roof_material: null,
roof_color: null,
solar_option: null,
gutter_option: null,
```

**Step 2: Add setters**

```javascript
setRoofMaterial: (roof_material) => set({ selections: { ...get().selections, roof_material } }),
setRoofColor: (roof_color) => set({ selections: { ...get().selections, roof_color } }),
setSolarOption: (solar_option) => set({ selections: { ...get().selections, solar_option } }),
setGutterOption: (gutter_option) => set({ selections: { ...get().selections, gutter_option } }),
```

**Step 3: Update resetSelections**

Add to the reset object:

```javascript
roof_material: null,
roof_color: null,
solar_option: null,
gutter_option: null,
```

**Step 4: Commit**

```bash
git add frontend/src/store/visualizationStore.js
git commit -m "feat(store): add roofs tenant state keys"
```

---

### Task 12: Create RoofMaterialStep Component

**Files:**
- Create: `frontend/src/components/UploadWizard/RoofMaterialStep.js`

**Step 1: Create the component**

```javascript
import React, { useEffect, useState } from 'react';
import useVisualizationStore from '../../store/visualizationStore';

const ROOF_MATERIALS = [
  { id: 'asphalt_3tab', name: 'Asphalt - 3-Tab', description: 'Affordable, classic look' },
  { id: 'asphalt_architectural', name: 'Asphalt - Architectural', description: 'Premium look, 30 year lifespan', popular: true },
  { id: 'metal_standing_seam', name: 'Metal - Standing Seam', description: 'Modern, durable, 50+ years', popular: true },
  { id: 'metal_corrugated', name: 'Metal - Corrugated', description: 'Industrial/farmhouse look' },
  { id: 'clay_tile', name: 'Clay Tile', description: 'Mediterranean style, 100+ years' },
  { id: 'concrete_tile', name: 'Concrete Tile', description: 'Durable, fire-resistant' },
  { id: 'slate', name: 'Natural Slate', description: 'Premium stone, 100+ years' },
  { id: 'wood_shake', name: 'Wood Shake', description: 'Rustic natural look' },
  { id: 'tpo_flat', name: 'TPO (Flat Roof)', description: 'For flat/low-slope roofs' },
];

const RoofMaterialStep = ({ nextStep }) => {
  const { selections, setRoofMaterial } = useVisualizationStore();
  const [selected, setSelected] = useState(selections.roof_material || null);

  useEffect(() => {
    if (selections.roof_material) {
      setSelected(selections.roof_material);
    }
  }, [selections.roof_material]);

  const handleSelect = (materialId) => {
    setSelected(materialId);
    setRoofMaterial(materialId);
  };

  return (
    <div className="wizard-step">
      <h2 className="step-title">Select Roofing Material</h2>
      <p className="step-subtitle">Choose the type of roofing for your home</p>

      <div className="options-grid">
        {ROOF_MATERIALS.map((material) => (
          <div
            key={material.id}
            className={`option-card ${selected === material.id ? 'selected' : ''}`}
            onClick={() => handleSelect(material.id)}
          >
            {material.popular && <span className="popular-badge">Popular</span>}
            <h3 className="option-name">{material.name}</h3>
            <p className="option-description">{material.description}</p>
          </div>
        ))}
      </div>

      <div className="wizard-navigation">
        <button
          className="nav-button primary"
          onClick={nextStep}
          disabled={!selected}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default RoofMaterialStep;
```

**Step 2: Commit**

```bash
git add frontend/src/components/UploadWizard/RoofMaterialStep.js
git commit -m "feat(wizard): add RoofMaterialStep component"
```

---

### Task 13: Create RoofColorStep Component

**Files:**
- Create: `frontend/src/components/UploadWizard/RoofColorStep.js`

**Step 1: Create the component**

```javascript
import React, { useEffect, useState } from 'react';
import useVisualizationStore from '../../store/visualizationStore';

const ROOF_COLORS = [
  { id: 'charcoal', name: 'Charcoal', hex: '#36454F' },
  { id: 'black', name: 'Black', hex: '#1a1a1a' },
  { id: 'brown', name: 'Brown', hex: '#5C4033' },
  { id: 'tan', name: 'Tan', hex: '#D2B48C' },
  { id: 'terracotta', name: 'Terracotta', hex: '#E2725B' },
  { id: 'slate_gray', name: 'Slate Gray', hex: '#708090' },
  { id: 'weathered_wood', name: 'Weathered Wood', hex: '#8B7355' },
  { id: 'green', name: 'Forest Green', hex: '#228B22' },
  { id: 'blue', name: 'Colonial Blue', hex: '#4169E1' },
  { id: 'white', name: 'White', hex: '#F5F5F5' },
];

const RoofColorStep = ({ nextStep, prevStep }) => {
  const { selections, setRoofColor } = useVisualizationStore();
  const [selected, setSelected] = useState(selections.roof_color || null);

  useEffect(() => {
    if (selections.roof_color) {
      setSelected(selections.roof_color);
    }
  }, [selections.roof_color]);

  const handleSelect = (colorId) => {
    setSelected(colorId);
    setRoofColor(colorId);
  };

  return (
    <div className="wizard-step">
      <h2 className="step-title">Select Roof Color</h2>
      <p className="step-subtitle">Choose the color for your new roof</p>

      <div className="color-options-grid">
        {ROOF_COLORS.map((color) => (
          <div
            key={color.id}
            className={`color-option ${selected === color.id ? 'selected' : ''}`}
            onClick={() => handleSelect(color.id)}
          >
            <div
              className="color-swatch"
              style={{ backgroundColor: color.hex }}
            />
            <span className="color-name">{color.name}</span>
          </div>
        ))}
      </div>

      <div className="wizard-navigation">
        <button className="nav-button secondary" onClick={prevStep}>
          Back
        </button>
        <button
          className="nav-button primary"
          onClick={nextStep}
          disabled={!selected}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default RoofColorStep;
```

**Step 2: Commit**

```bash
git add frontend/src/components/UploadWizard/RoofColorStep.js
git commit -m "feat(wizard): add RoofColorStep component"
```

---

### Task 14: Create SolarOptionStep Component

**Files:**
- Create: `frontend/src/components/UploadWizard/SolarOptionStep.js`

**Step 1: Create the component**

```javascript
import React, { useEffect, useState } from 'react';
import { Sun, Zap } from 'lucide-react';
import useVisualizationStore from '../../store/visualizationStore';

const SOLAR_OPTIONS = [
  { id: 'none', name: 'No Solar', description: 'Roof only, no solar panels', icon: null },
  { id: 'partial', name: 'Partial Coverage', description: 'Solar on part of the roof', icon: Sun, popular: true },
  { id: 'full_south', name: 'Full South Roof', description: 'Maximize solar on south-facing', icon: Zap },
  { id: 'full_all', name: 'Maximum Coverage', description: 'Solar on all viable areas', icon: Zap },
];

const SolarOptionStep = ({ nextStep, prevStep }) => {
  const { selections, setSolarOption } = useVisualizationStore();
  const [selected, setSelected] = useState(selections.solar_option || null);

  useEffect(() => {
    if (selections.solar_option) {
      setSelected(selections.solar_option);
    }
  }, [selections.solar_option]);

  const handleSelect = (optionId) => {
    setSelected(optionId);
    setSolarOption(optionId);
  };

  return (
    <div className="wizard-step">
      <h2 className="step-title">Solar Panel Options</h2>
      <p className="step-subtitle">Would you like to add solar panels?</p>

      <div className="options-grid">
        {SOLAR_OPTIONS.map((option) => {
          const IconComponent = option.icon;
          return (
            <div
              key={option.id}
              className={`option-card ${selected === option.id ? 'selected' : ''}`}
              onClick={() => handleSelect(option.id)}
            >
              {option.popular && <span className="popular-badge">Popular</span>}
              {IconComponent && (
                <div className="option-icon">
                  <IconComponent size={32} />
                </div>
              )}
              <h3 className="option-name">{option.name}</h3>
              <p className="option-description">{option.description}</p>
            </div>
          );
        })}
      </div>

      <div className="wizard-navigation">
        <button className="nav-button secondary" onClick={prevStep}>
          Back
        </button>
        <button
          className="nav-button primary"
          onClick={nextStep}
          disabled={!selected}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default SolarOptionStep;
```

**Step 2: Commit**

```bash
git add frontend/src/components/UploadWizard/SolarOptionStep.js
git commit -m "feat(wizard): add SolarOptionStep component"
```

---

### Task 15: Create GutterOptionStep Component

**Files:**
- Create: `frontend/src/components/UploadWizard/GutterOptionStep.js`

**Step 1: Create the component**

```javascript
import React, { useEffect, useState } from 'react';
import useVisualizationStore from '../../store/visualizationStore';

const GUTTER_OPTIONS = [
  { id: 'none', name: 'No Gutters', description: 'No gutter system' },
  { id: 'standard', name: 'Standard Gutters', description: 'Aluminum K-style gutters', popular: true },
  { id: 'seamless', name: 'Seamless Gutters', description: 'Premium seamless system' },
  { id: 'copper', name: 'Copper Gutters', description: 'Premium copper half-round' },
];

const GutterOptionStep = ({ nextStep, prevStep }) => {
  const { selections, setGutterOption } = useVisualizationStore();
  const [selected, setSelected] = useState(selections.gutter_option || null);

  useEffect(() => {
    if (selections.gutter_option) {
      setSelected(selections.gutter_option);
    }
  }, [selections.gutter_option]);

  const handleSelect = (optionId) => {
    setSelected(optionId);
    setGutterOption(optionId);
  };

  return (
    <div className="wizard-step">
      <h2 className="step-title">Gutter Options</h2>
      <p className="step-subtitle">Select a gutter system for your new roof</p>

      <div className="options-grid">
        {GUTTER_OPTIONS.map((option) => (
          <div
            key={option.id}
            className={`option-card ${selected === option.id ? 'selected' : ''}`}
            onClick={() => handleSelect(option.id)}
          >
            {option.popular && <span className="popular-badge">Popular</span>}
            <h3 className="option-name">{option.name}</h3>
            <p className="option-description">{option.description}</p>
          </div>
        ))}
      </div>

      <div className="wizard-navigation">
        <button className="nav-button secondary" onClick={prevStep}>
          Back
        </button>
        <button
          className="nav-button primary"
          onClick={nextStep}
          disabled={!selected}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default GutterOptionStep;
```

**Step 2: Commit**

```bash
git add frontend/src/components/UploadWizard/GutterOptionStep.js
git commit -m "feat(wizard): add GutterOptionStep component"
```

---

### Task 16: Create RoofsUploadPage

**Files:**
- Create: `frontend/src/pages/RoofsUploadPage.js`

**Step 1: Create the page**

```javascript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Check } from 'lucide-react';
import { createVisualizationRequest } from '../services/api';
import useVisualizationStore from '../store/visualizationStore';
import RoofMaterialStep from '../components/UploadWizard/RoofMaterialStep';
import RoofColorStep from '../components/UploadWizard/RoofColorStep';
import SolarOptionStep from '../components/UploadWizard/SolarOptionStep';
import GutterOptionStep from '../components/UploadWizard/GutterOptionStep';
import Step4Upload from '../components/UploadWizard/Step4Upload';
import Step5Review from '../components/UploadWizard/Step5Review';
import './UploadPage.css';

const RoofsUploadPage = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    image: null
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { selections } = useVisualizationStore();

  const nextStep = () => setStep(prev => prev + 1);
  const prevStep = () => setStep(prev => prev - 1);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      const data = new FormData();
      const selectionsPayload = {
        roof_material: selections.roof_material,
        roof_color: selections.roof_color,
        solar_option: selections.solar_option,
        gutter_option: selections.gutter_option,
      };
      data.append('scope', JSON.stringify(selectionsPayload));
      data.append('original_image', formData.image);

      const response = await createVisualizationRequest(data);
      navigate(`/results/${response.id}`);
    } catch (err) {
      console.error('Submit error:', err);
      const errorMsg = err.message || err.data?.detail || JSON.stringify(err.data) || 'Unknown error';
      setError(`Failed: ${errorMsg}`);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="upload-page">
      <div className="wizard-progress-bar">
        <div className="progress-track">
          <div
            className="progress-fill"
            style={{ width: `${((step - 1) / 5) * 100}%` }}
          />
        </div>
        <div className="steps-indicator">
          {[1, 2, 3, 4, 5, 6].map(s => (
            <div
              key={s}
              className={`step-dot ${s <= step ? 'active' : ''} ${s === step ? 'current' : ''}`}
            >
              {s < step ? <Check size={12} /> : s}
            </div>
          ))}
        </div>
      </div>

      {step === 1 && (
        <RoofMaterialStep nextStep={nextStep} />
      )}
      {step === 2 && (
        <RoofColorStep nextStep={nextStep} prevStep={prevStep} />
      )}
      {step === 3 && (
        <SolarOptionStep nextStep={nextStep} prevStep={prevStep} />
      )}
      {step === 4 && (
        <GutterOptionStep nextStep={nextStep} prevStep={prevStep} />
      )}
      {step === 5 && (
        <Step4Upload
          formData={formData}
          setFormData={setFormData}
          nextStep={nextStep}
          prevStep={prevStep}
        />
      )}
      {step === 6 && (
        <Step5Review
          formData={formData}
          selections={selections}
          prevStep={prevStep}
          handleSubmit={handleSubmit}
          isSubmitting={isSubmitting}
          error={error}
        />
      )}
    </div>
  );
};

export default RoofsUploadPage;
```

**Step 2: Commit**

```bash
git add frontend/src/pages/RoofsUploadPage.js
git commit -m "feat(roofs): create RoofsUploadPage with 6-step wizard"
```

---

### Task 17: Add Roofs Route to App.js

**Files:**
- Modify: `frontend/src/App.js`

**Step 1: Add import**

Add after line 8:

```javascript
import RoofsUploadPage from './pages/RoofsUploadPage';
```

**Step 2: Add route**

After the `/upload/windows` route block (around line 129), add:

```javascript
<Route path="/upload/roofs" element={
  <ProtectedRoute>
    <RoofsUploadPage />
  </ProtectedRoute>
} />
```

**Step 3: Verify build**

Run: `cd /home/reid/command-center/testhome/pools-visualizer/frontend && npm run build`

Expected: Build succeeds

**Step 4: Commit**

```bash
git add frontend/src/App.js
git commit -m "feat(routing): add /upload/roofs route"
```

---

## Part 3: Testing & Verification

### Task 18: Test Windows Tenant End-to-End

**Steps:**

1. Start backend with windows tenant:
   ```bash
   cd /home/reid/command-center/testhome/pools-visualizer
   source venv/bin/activate
   ACTIVE_TENANT=windows python3 manage.py runserver 8006
   ```

2. In another terminal, start frontend:
   ```bash
   cd /home/reid/command-center/testhome/pools-visualizer/frontend
   PORT=3006 npm start
   ```

3. Navigate to `http://localhost:3006/upload/windows`

4. Verify 8-step wizard:
   - Step 1: Project Type (3 options)
   - Step 2: Door Type (5 options)
   - Steps 3-8: Window options, upload, review

5. Submit test image and verify pipeline runs

---

### Task 19: Test Roofs Tenant End-to-End

**Steps:**

1. Start backend with roofs tenant:
   ```bash
   ACTIVE_TENANT=roofs python3 manage.py runserver 8006
   ```

2. Navigate to `http://localhost:3006/upload/roofs`

3. Verify 6-step wizard:
   - Step 1: Roof Material (9 options)
   - Step 2: Roof Color (10 options)
   - Step 3: Solar Options (4 options)
   - Step 4: Gutter Options (4 options)
   - Step 5: Upload
   - Step 6: Review

4. Submit test image and verify pipeline runs

---

## Summary

**Total Tasks:** 19
**Backend Changes:** 6 files
**Frontend Changes:** 10 files

**Windows Tenant Extensions:**
- Added PROJECT_TYPES (replace/new/enclose)
- Added DOOR_TYPES (none/sliding/accordion/bi-fold/french)
- Updated wizard from 6 to 8 steps
- Updated prompts for door handling

**Roofs Tenant (New):**
- Full config with 9 materials, 10 colors, 4 solar options, 4 gutter options
- 5-step AI pipeline (cleanup → material → solar → gutters → quality)
- 6-step frontend wizard
- Registered in tenant registry
