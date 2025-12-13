# Pools Visualizer Full Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement complete pools visualizer with 6-step AI pipeline, 5-screen wizard, comprehensive config with pricing-ready data model, and proper tenant registration.

**Architecture:** Standalone pools-visualizer project at `/home/reid/testhome/pools-visualizer/`. Uses existing Django tenant system with pools-specific config, prompts, and pipeline. Frontend wizard collects all pool customization options that feed into layered AI rendering pipeline.

**Tech Stack:** Django 5.2, React 19, Python 3.10, Gemini AI, SQLite

**Port:** 8006 (already configured)

**CRITICAL:** Pricing data is in config but NOT shown in UI yet.

---

## Task 1: Create Pools Tenant __init__.py

**Files:**
- Create: `api/tenants/pools/__init__.py`

**Step 1: Create the init file**

Create `/home/reid/testhome/pools-visualizer/api/tenants/pools/__init__.py`:

```python
"""Pools Visualizer Tenant Package."""
from . import config
from . import prompts

__all__ = ['config', 'prompts']
```

**Step 2: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add -A && git commit -m "feat(pools): add tenant __init__.py"
```

---

## Task 2: Create Pools config.py

**Files:**
- Create: `api/tenants/pools/config.py`

**Step 1: Create the config file**

Create `/home/reid/testhome/pools-visualizer/api/tenants/pools/config.py` with the full config from the spec:
- POOL_SIZES with dimensions and base_price (hidden from UI)
- POOL_SHAPES with price_multiplier (hidden from UI)
- INTERIOR_FINISHES with water_color and price_add
- BUILT_IN_FEATURES (tanning_ledge, ledge_loungers, attached_spa)
- DECK_MATERIALS with price_per_sqft
- DECK_COLORS
- WATER_FEATURES with price_add
- FINISHING_OPTIONS (lighting, landscaping, furniture)
- PIPELINE_STEPS
- PoolsTenantConfig class extending BaseTenantConfig
- get_config() that excludes pricing
- get_full_config_with_pricing() for admin use

**Step 2: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add -A && git commit -m "feat(pools): add comprehensive config with pricing-ready data model"
```

---

## Task 3: Create Pools prompts.py

**Files:**
- Create: `api/tenants/pools/prompts.py`

**Step 1: Create the prompts file**

Create `/home/reid/testhome/pools-visualizer/api/tenants/pools/prompts.py` with:
- get_cleanup_prompt() - Clean backyard, sunny weather, preserve structures
- get_pool_shell_prompt(selections) - Pool size, shape, finish, built-ins
- get_deck_prompt(selections) - Deck material and color
- get_water_features_prompt(selections) - Returns None if no features selected
- get_finishing_prompt(selections) - Returns None if nothing selected
- get_quality_check_prompt() - JSON scoring with issues list
- get_prompt(step, selections) - Main router

Use the exact prompts from the spec document.

**Step 2: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add -A && git commit -m "feat(pools): add AI prompts for 6-step pipeline"
```

---

## Task 4: Register Pools Tenant

**Files:**
- Modify: `api/tenants/__init__.py`

**Step 1: Add pools tenant import and registration**

Add after the BossTenantConfig import:
```python
from .pools.config import PoolsTenantConfig
```

Add after boss registration:
```python
register_tenant(PoolsTenantConfig())
```

**Step 2: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add -A && git commit -m "feat(pools): register pools tenant in registry"
```

---

## Task 5: Create Zustand Store for Pool Selections

**Files:**
- Modify: `frontend/src/store/visualizationStore.js`

**Step 1: Replace scope with comprehensive pool selections**

Update the scope/selections object:
```javascript
selections: {
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
    water_features: [],  // Array of feature IDs, max 2

    // Screen 5: Finishing Touches
    lighting: 'none',
    landscaping: 'none',
    furniture: 'none',
},
setSelection: (key, value) => set((state) => ({
    selections: { ...state.selections, [key]: value }
})),
setSelections: (updates) => set((state) => ({
    selections: { ...state.selections, ...updates }
})),
```

**Step 2: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add -A && git commit -m "feat(pools): update Zustand store with comprehensive pool selections"
```

---

## Task 6: Create Pool Config API Endpoint

**Files:**
- Modify: `api/views_config.py` (or create if missing)
- Modify: `api/urls.py`

**Step 1: Create config view**

Create or update `/home/reid/testhome/pools-visualizer/api/views_config.py`:
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from api.tenants import get_tenant_config

class TenantConfigView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        config = get_tenant_config()
        return Response(config.get_schema())
```

**Step 2: Add URL route**

In `api/urls.py`, add:
```python
from .views_config import TenantConfigView

urlpatterns = [
    # ... existing routes ...
    path('config/', TenantConfigView.as_view(), name='tenant-config'),
]
```

**Step 3: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add -A && git commit -m "feat(api): add tenant config endpoint"
```

---

## Task 7: Create Screen 1 - Pool Size & Shape

**Files:**
- Create: `frontend/src/components/UploadWizard/PoolSizeShapeStep.js`

**Step 1: Create the component**

Create the component with:
- Pool size cards showing name, dimensions, description (NOT price)
- "Popular" badge for classic size
- Pool shape grid with icons
- Selected state styling

**Step 2: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add -A && git commit -m "feat(wizard): add Screen 1 - Pool Size & Shape"
```

---

## Task 8: Create Screen 2 - Finish & Built-ins

**Files:**
- Create: `frontend/src/components/UploadWizard/FinishBuiltInsStep.js`

**Step 1: Create the component**

Create the component with:
- Interior finish cards showing name and water color
- Color swatch representing water color
- Tanning ledge toggle (default ON)
- Ledge lounger count dropdown (0, 2, 4) - only shows if tanning_ledge enabled
- Attached spa toggle

**Step 2: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add -A && git commit -m "feat(wizard): add Screen 2 - Finish & Built-ins"
```

---

## Task 9: Create Screen 3 - Deck

**Files:**
- Create: `frontend/src/components/UploadWizard/DeckStep.js`

**Step 1: Create the component**

Create the component with:
- Deck material cards (travertine, pavers, concrete, etc.)
- "Popular" badge for travertine
- Deck color chips

**Step 2: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add -A && git commit -m "feat(wizard): add Screen 3 - Deck"
```

---

## Task 10: Create Screen 4 - Water Features

**Files:**
- Create: `frontend/src/components/UploadWizard/WaterFeaturesStep.js`

**Step 1: Create the component**

Create the component with:
- Feature cards for each water feature
- Multi-select with max 2 features
- Clear indication this is optional
- Toggle selection behavior

**Step 2: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add -A && git commit -m "feat(wizard): add Screen 4 - Water Features"
```

---

## Task 11: Create Screen 5 - Finishing Touches

**Files:**
- Create: `frontend/src/components/UploadWizard/FinishingStep.js`

**Step 1: Create the component**

Create the component with:
- Lighting radio group (none, pool_lights, landscape, both)
- Landscaping radio group (none, tropical, desert, natural)
- Furniture radio group (none, basic, full)
- Clear indication all are optional

**Step 2: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add -A && git commit -m "feat(wizard): add Screen 5 - Finishing Touches"
```

---

## Task 12: Update Wizard Navigation

**Files:**
- Modify: `frontend/src/pages/UploadPage.js`
- Remove/update: Old Step1Categories.js, Step2Scope.js, etc.

**Step 1: Update UploadPage to use new 5-screen wizard**

Replace the wizard steps with:
1. PoolSizeShapeStep
2. FinishBuiltInsStep
3. DeckStep
4. WaterFeaturesStep
5. FinishingStep
6. ImageUpload (existing)
7. Review

**Step 2: Update step navigation logic**

**Step 3: Update scope payload to use selections**

```javascript
const scopePayload = {
    size: selections.size,
    shape: selections.shape,
    finish: selections.finish,
    tanning_ledge: selections.tanning_ledge,
    lounger_count: selections.lounger_count,
    attached_spa: selections.attached_spa,
    deck_material: selections.deck_material,
    deck_color: selections.deck_color,
    water_features: selections.water_features,
    lighting: selections.lighting,
    landscaping: selections.landscaping,
    furniture: selections.furniture,
};
```

**Step 4: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add -A && git commit -m "feat(wizard): integrate new 5-screen pool wizard"
```

---

## Task 13: Update Review Step

**Files:**
- Modify: `frontend/src/components/UploadWizard/Step5Review.js` → rename to `ReviewStep.js`

**Step 1: Update review to show all pool selections**

Display:
- Pool Size & Shape
- Interior Finish (with water color)
- Built-in Features (tanning ledge, loungers, spa)
- Deck Material & Color
- Water Features (if any)
- Finishing Touches (if any)
- Uploaded Image preview

**Step 2: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add -A && git commit -m "feat(wizard): update review step for pool selections"
```

---

## Task 14: Add CSS Styles for Pool Wizard

**Files:**
- Modify: `frontend/src/App.css` or create `frontend/src/components/UploadWizard/PoolWizard.css`

**Step 1: Add pool-specific styles**

- Size cards with dimensions
- Shape icons grid
- Color swatches for water colors and deck colors
- Feature toggle styles
- Popular badge
- Selected state highlights

**Step 2: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add -A && git commit -m "style(wizard): add CSS for pool wizard components"
```

---

## Task 15: Test Backend Config Endpoint

**Files:** None (verification only)

**Step 1: Start backend**

```bash
cd /home/reid/testhome/pools-visualizer
source venv/bin/activate
ACTIVE_TENANT=pools python manage.py runserver 8006
```

**Step 2: Test config endpoint**

```bash
curl http://localhost:8006/api/config/ | python -m json.tool
```

Expected: Returns pools config with all options, NO pricing data visible.

**Step 3: Verify tenant is pools**

Response should show `"name": "pools"` and `"display_name": "Swimming Pools"`.

---

## Task 16: Test Frontend Wizard Flow

**Files:** None (verification only)

**Step 1: Start frontend**

```bash
cd /home/reid/testhome/pools-visualizer/frontend
npm start
```

**Step 2: Verify wizard flow**

1. Navigate to /upload
2. Screen 1: Select pool size and shape
3. Screen 2: Select finish, toggle tanning ledge, set lounger count
4. Screen 3: Select deck material and color
5. Screen 4: Select 0-2 water features
6. Screen 5: Select finishing touches
7. Upload image
8. Review shows all selections

**Step 3: Submit and verify payload**

Open browser devtools Network tab, submit, verify payload contains all selections.

---

## Task 17: Clean Up Old Security Screen References

**Files:**
- Remove: Old wizard files if not needed
- Modify: Any remaining "screen", "security", "boss" text

**Step 1: Search for remaining references**

```bash
grep -r "security\|screen\|boss" frontend/src --include="*.js" --include="*.jsx" -l
```

**Step 2: Update any remaining text**

**Step 3: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add -A && git commit -m "chore: remove remaining security screen references"
```

---

## Task 18: Final Verification

**Files:** None

**Step 1: Run full test**

1. Backend on 8006
2. Frontend on 3006
3. Complete full wizard flow
4. Upload test backyard image
5. Verify processing starts
6. Check pipeline logs for pool-specific prompts

**Step 2: Final commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add -A && git commit -m "feat: pools visualizer complete"
```

---

## Summary

After completing all tasks:

1. **Pools tenant** fully configured with config.py and prompts.py
2. **6-step AI pipeline**: cleanup → pool_shell → deck → water_features → finishing → quality_check
3. **5-screen wizard** collecting all pool customization options
4. **Pricing-ready data model** (hidden from UI)
5. **Config API** returning pools options (no pricing)
6. **Full integration** with existing Django/React architecture

The pools visualizer will generate photorealistic pool visualizations based on user selections.
