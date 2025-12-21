# Unified Tenant Wizard Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Merge 3 separate upload pages into one dynamic wizard that routes tenants correctly through the full stack.

**Architecture:** Single `UploadPage.js` component that reads `tenantId` from URL params (`/upload/:tenantId`). Backend receives `tenant_id` in request, stores on model, passes through pipeline. All legacy "security" terminology removed.

**Tech Stack:** React 19.1, React Router 7, Django 4.0, Zustand

---

## Overview

### Current State (Broken)
- 3 separate pages: `UploadPage.js` (pools), `WindowsUploadPage.js`, `RoofsUploadPage.js`
- No `tenant_id` sent to backend
- `get_tenant_config()` always defaults to 'pools'
- Legacy "security vulnerabilities" messages in `ai_enhanced_processor.py`

### Target State (Working)
- Single `UploadPage.js` with route `/upload/:tenantId`
- Frontend config drives wizard steps per tenant
- Backend receives `tenant_id`, stores on model, uses for prompts
- All security terminology replaced with visualization terminology

---

## Task 1: Add tenant_id Field to Model

**Files:**
- Modify: `api/models.py:249-253`
- Create: `api/migrations/XXXX_add_tenant_id.py` (auto-generated)

**Step 1: Add the field to VisualizationRequest model**

In `api/models.py`, add after line 253 (after `scope` field):

```python
    tenant_id = models.CharField(
        max_length=50,
        default='pools',
        help_text="Tenant identifier (pools, windows, roofs)"
    )
```

**Step 2: Create and apply migration**

Run:
```bash
cd /home/reid/testhome/pools-visualizer && source venv/bin/activate && python3 manage.py makemigrations api --name add_tenant_id
```

Expected: `Migrations for 'api': api/migrations/XXXX_add_tenant_id.py`

**Step 3: Apply migration**

Run:
```bash
cd /home/reid/testhome/pools-visualizer && source venv/bin/activate && python3 manage.py migrate
```

Expected: `Applying api.XXXX_add_tenant_id... OK`

**Step 4: Commit**

```bash
git add api/models.py api/migrations/
git commit -m "feat: add tenant_id field to VisualizationRequest model"
```

---

## Task 2: Update Serializer to Accept tenant_id

**Files:**
- Modify: `api/serializers.py:261-270`

**Step 1: Add tenant_id to serializer fields**

In `api/serializers.py`, update `VisualizationRequestCreateSerializer`:

```python
class VisualizationRequestCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating requests."""

    class Meta:
        model = VisualizationRequest
        fields = ['id', 'original_image', 'screen_type', 'opacity', 'color',
                  'screen_categories', 'mesh_choice', 'frame_color', 'mesh_color', 'scope',
                  'window_count', 'door_count', 'door_type', 'patio_enclosure',
                  'tenant_id',  # ADD THIS
                  'status', 'progress_percentage', 'status_message', 'created_at']
        read_only_fields = ['id', 'status', 'progress_percentage', 'status_message', 'created_at']
        extra_kwargs = {
            'original_image': {'required': True},
            'screen_type': {'required': False, 'allow_null': True},
            'scope': {'required': False},
            'tenant_id': {'required': False}  # ADD THIS
        }
```

**Step 2: Verify serializer accepts tenant_id**

Run:
```bash
cd /home/reid/testhome/pools-visualizer && source venv/bin/activate && python3 -c "
from api.serializers import VisualizationRequestCreateSerializer
s = VisualizationRequestCreateSerializer()
print('tenant_id in fields:', 'tenant_id' in s.fields)
"
```

Expected: `tenant_id in fields: True`

**Step 3: Commit**

```bash
git add api/serializers.py
git commit -m "feat: add tenant_id to visualization request serializer"
```

---

## Task 3: Pass tenant_id Through Processing Pipeline

**Files:**
- Modify: `api/ai_enhanced_processor.py:69-140`
- Modify: `api/ai_services/providers/gemini_provider.py:67-121`
- Modify: `api/visualizer/services.py:33-56`

**Step 1: Update AIEnhancedImageProcessor.process_image()**

In `api/ai_enhanced_processor.py`, around line 130, update to pass tenant_id:

```python
            # Extract style preferences and scope
            style_preferences = {
                "opacity": visualization_request.opacity,
                "color": visualization_request.frame_color,
                "mesh_type": visualization_request.mesh_choice,
                "scope": {},
                "tenant_id": visualization_request.tenant_id  # ADD THIS
            }
```

**Step 2: Update GeminiImageGenerationService.generate_screen_visualization()**

In `api/ai_services/providers/gemini_provider.py`, around line 115-120, pass tenant_id to pipeline:

```python
            # Run the pipeline
            tenant_id = style_preferences.get('tenant_id', 'pools')  # ADD THIS
            clean_image, result_image, quality_score, quality_reason = self.visualizer.process_pipeline(
                original_image,
                scope=scope,
                options=options,
                progress_callback=progress_callback,
                tenant_id=tenant_id  # ADD THIS
            )
```

**Step 3: Update ScreenVisualizer.process_pipeline()**

In `api/visualizer/services.py`, update the method signature and use tenant_id:

```python
    def process_pipeline(self, original_image: Image.Image, scope: dict, options: dict, progress_callback=None, tenant_id: str = None) -> Tuple[Image.Image, Image.Image, float, str]:
        """
        Executes the visualization pipeline sequentially based on tenant configuration.

        Args:
            original_image (Image): The source image.
            scope (dict): Feature selections
            options (dict): Style options
            progress_callback (callable, optional): Function to update progress.
            tenant_id (str, optional): Tenant identifier for config lookup.
        """
        try:
            tenant_config = get_tenant_config(tenant_id)  # CHANGE THIS LINE
            prompts = tenant_config.get_prompts_module()
            # ... rest of method unchanged
```

**Step 4: Verify the pipeline uses tenant_id**

Run:
```bash
cd /home/reid/testhome/pools-visualizer && source venv/bin/activate && python3 -c "
from api.visualizer.services import ScreenVisualizer
import inspect
sig = inspect.signature(ScreenVisualizer.process_pipeline)
print('tenant_id param exists:', 'tenant_id' in sig.parameters)
"
```

Expected: `tenant_id param exists: True`

**Step 5: Commit**

```bash
git add api/ai_enhanced_processor.py api/ai_services/providers/gemini_provider.py api/visualizer/services.py
git commit -m "feat: pass tenant_id through visualization pipeline"
```

---

## Task 4: Remove Legacy Security Terminology

**Files:**
- Modify: `api/ai_enhanced_processor.py:175, 190`

**Step 1: Replace "Analyzing security vulnerabilities" message**

In `api/ai_enhanced_processor.py`, around line 175, change:

```python
# OLD:
visualization_request.update_progress(92, "Analyzing security vulnerabilities...")

# NEW:
visualization_request.update_progress(92, "Analyzing image quality...")
```

**Step 2: Replace "security_report" PDF naming**

In `api/ai_enhanced_processor.py`, around line 190, change:

```python
# OLD:
pdf_filename = f"security_report_{visualization_request.id}.pdf"

# NEW:
pdf_filename = f"visualization_report_{visualization_request.id}.pdf"
```

**Step 3: Verify no security terminology remains**

Run:
```bash
grep -n "security" /home/reid/testhome/pools-visualizer/api/ai_enhanced_processor.py
```

Expected: No matches (or only in variable names that were intentionally kept)

**Step 4: Commit**

```bash
git add api/ai_enhanced_processor.py
git commit -m "fix: remove legacy security terminology from processor"
```

---

## Task 5: Create Frontend Tenant Configuration

**Files:**
- Create: `frontend/src/config/tenants.js`

**Step 1: Create tenant configuration file**

Create `frontend/src/config/tenants.js`:

```javascript
/**
 * Tenant Configuration
 * Defines wizard steps and display info for each tenant (pools, windows, roofs)
 */

export const TENANT_CONFIG = {
  pools: {
    id: 'pools',
    name: 'Pool Designer',
    description: 'Design your dream swimming pool',
    steps: [
      { component: 'PoolSizeShapeStep', label: 'Size & Shape' },
      { component: 'FinishBuiltInsStep', label: 'Finish' },
      { component: 'DeckStep', label: 'Deck' },
      { component: 'WaterFeaturesStep', label: 'Water Features' },
      { component: 'FinishingStep', label: 'Finishing' },
      { component: 'Step4Upload', label: 'Upload' },
      { component: 'Step5Review', label: 'Review' },
    ],
    selectionsKeys: [
      'size', 'shape', 'finish', 'tanning_ledge', 'lounger_count',
      'attached_spa', 'deck_material', 'deck_color', 'water_features',
      'lighting', 'landscaping', 'furniture'
    ],
  },
  windows: {
    id: 'windows',
    name: 'Window & Door Designer',
    description: 'Visualize new windows and doors',
    steps: [
      { component: 'ProjectTypeStep', label: 'Project Type' },
      { component: 'DoorTypeStep', label: 'Door Type' },
      { component: 'WindowTypeStep', label: 'Window Type' },
      { component: 'FrameMaterialStep', label: 'Frame' },
      { component: 'GrillePatternStep', label: 'Grilles' },
      { component: 'HardwareTrimStep', label: 'Hardware' },
      { component: 'Step4Upload', label: 'Upload' },
      { component: 'Step5Review', label: 'Review' },
    ],
    selectionsKeys: [
      'project_type', 'door_type', 'window_type', 'window_style',
      'frame_material', 'frame_color', 'grille_pattern', 'glass_option',
      'hardware_finish', 'trim_style'
    ],
  },
  roofs: {
    id: 'roofs',
    name: 'Roof & Solar Designer',
    description: 'Visualize new roofing and solar panels',
    steps: [
      { component: 'RoofMaterialStep', label: 'Material' },
      { component: 'RoofColorStep', label: 'Color' },
      { component: 'SolarOptionStep', label: 'Solar' },
      { component: 'GutterOptionStep', label: 'Gutters' },
      { component: 'Step4Upload', label: 'Upload' },
      { component: 'Step5Review', label: 'Review' },
    ],
    selectionsKeys: [
      'roof_material', 'roof_color', 'solar_option', 'gutter_option'
    ],
  },
};

export const getTenantConfig = (tenantId) => {
  return TENANT_CONFIG[tenantId] || TENANT_CONFIG.pools;
};

export const isValidTenant = (tenantId) => {
  return tenantId in TENANT_CONFIG;
};
```

**Step 2: Verify file created**

Run:
```bash
ls -la /home/reid/testhome/pools-visualizer/frontend/src/config/
```

Expected: Shows `tenants.js`

**Step 3: Commit**

```bash
git add frontend/src/config/tenants.js
git commit -m "feat: add tenant configuration for unified wizard"
```

---

## Task 6: Create Unified UploadPage Component

**Files:**
- Modify: `frontend/src/pages/UploadPage.js` (complete rewrite)

**Step 1: Rewrite UploadPage.js as dynamic wizard**

Replace entire contents of `frontend/src/pages/UploadPage.js`:

```javascript
import React, { useState, useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Check } from 'lucide-react';
import { createVisualizationRequest } from '../services/api';
import useVisualizationStore from '../store/visualizationStore';
import { getTenantConfig, isValidTenant } from '../config/tenants';

// Pool steps
import PoolSizeShapeStep from '../components/UploadWizard/PoolSizeShapeStep';
import FinishBuiltInsStep from '../components/UploadWizard/FinishBuiltInsStep';
import DeckStep from '../components/UploadWizard/DeckStep';
import WaterFeaturesStep from '../components/UploadWizard/WaterFeaturesStep';
import FinishingStep from '../components/UploadWizard/FinishingStep';

// Windows steps
import ProjectTypeStep from '../components/UploadWizard/ProjectTypeStep';
import DoorTypeStep from '../components/UploadWizard/DoorTypeStep';
import WindowTypeStep from '../components/UploadWizard/WindowTypeStep';
import FrameMaterialStep from '../components/UploadWizard/FrameMaterialStep';
import GrillePatternStep from '../components/UploadWizard/GrillePatternStep';
import HardwareTrimStep from '../components/UploadWizard/HardwareTrimStep';

// Roofs steps
import RoofMaterialStep from '../components/UploadWizard/RoofMaterialStep';
import RoofColorStep from '../components/UploadWizard/RoofColorStep';
import SolarOptionStep from '../components/UploadWizard/SolarOptionStep';
import GutterOptionStep from '../components/UploadWizard/GutterOptionStep';

// Shared steps
import Step4Upload from '../components/UploadWizard/Step4Upload';
import Step5Review from '../components/UploadWizard/Step5Review';

import './UploadPage.css';

// Component registry - maps component names to actual components
const STEP_COMPONENTS = {
  PoolSizeShapeStep,
  FinishBuiltInsStep,
  DeckStep,
  WaterFeaturesStep,
  FinishingStep,
  ProjectTypeStep,
  DoorTypeStep,
  WindowTypeStep,
  FrameMaterialStep,
  GrillePatternStep,
  HardwareTrimStep,
  RoofMaterialStep,
  RoofColorStep,
  SolarOptionStep,
  GutterOptionStep,
  Step4Upload,
  Step5Review,
};

const UploadPage = () => {
  const { tenantId = 'pools' } = useParams();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({ image: null });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { selections } = useVisualizationStore();

  // Get tenant configuration
  const tenantConfig = useMemo(() => getTenantConfig(tenantId), [tenantId]);
  const steps = tenantConfig.steps;
  const totalSteps = steps.length;

  // Redirect if invalid tenant
  if (!isValidTenant(tenantId)) {
    navigate('/upload/pools');
    return null;
  }

  const nextStep = () => setStep(prev => Math.min(prev + 1, totalSteps));
  const prevStep = () => setStep(prev => Math.max(prev - 1, 1));

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      const data = new FormData();

      // Build selections payload from tenant-specific keys
      const selectionsPayload = {};
      tenantConfig.selectionsKeys.forEach(key => {
        if (selections[key] !== undefined) {
          selectionsPayload[key] = selections[key];
        }
      });

      data.append('scope', JSON.stringify(selectionsPayload));
      data.append('tenant_id', tenantId);  // CRITICAL: Send tenant_id
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

  // Render current step component
  const renderStep = () => {
    const stepConfig = steps[step - 1];
    const StepComponent = STEP_COMPONENTS[stepConfig.component];

    if (!StepComponent) {
      return <div>Unknown step: {stepConfig.component}</div>;
    }

    // Shared props for all steps
    const stepProps = {
      nextStep,
      prevStep,
    };

    // Special props for specific steps
    if (stepConfig.component === 'Step4Upload') {
      return (
        <StepComponent
          {...stepProps}
          formData={formData}
          setFormData={setFormData}
        />
      );
    }

    if (stepConfig.component === 'Step5Review') {
      return (
        <StepComponent
          {...stepProps}
          formData={formData}
          selections={selections}
          handleSubmit={handleSubmit}
          isSubmitting={isSubmitting}
          error={error}
        />
      );
    }

    return <StepComponent {...stepProps} />;
  };

  return (
    <div className="upload-page">
      {/* Tenant header */}
      <div className="tenant-header">
        <h1>{tenantConfig.name}</h1>
        <p>{tenantConfig.description}</p>
      </div>

      {/* Progress bar */}
      <div className="wizard-progress-bar">
        <div className="progress-track">
          <div
            className="progress-fill"
            style={{ width: `${((step - 1) / (totalSteps - 1)) * 100}%` }}
          />
        </div>
        <div className="steps-indicator">
          {steps.map((s, idx) => (
            <div
              key={idx}
              className={`step-dot ${idx + 1 <= step ? 'active' : ''} ${idx + 1 === step ? 'current' : ''}`}
              title={s.label}
            >
              {idx + 1 < step ? <Check size={12} /> : idx + 1}
            </div>
          ))}
        </div>
      </div>

      {/* Current step */}
      {renderStep()}
    </div>
  );
};

export default UploadPage;
```

**Step 2: Verify file syntax**

Run:
```bash
cd /home/reid/testhome/pools-visualizer/frontend && node -e "require('./src/pages/UploadPage.js')" 2>&1 | head -5 || echo "Note: ES module, will verify with npm build"
```

**Step 3: Commit**

```bash
git add frontend/src/pages/UploadPage.js
git commit -m "feat: create unified dynamic wizard UploadPage"
```

---

## Task 7: Update App.js Routes

**Files:**
- Modify: `frontend/src/App.js:7-9, 118-134`

**Step 1: Remove separate page imports**

In `frontend/src/App.js`, remove lines 8-9:

```javascript
// REMOVE these lines:
import WindowsUploadPage from './pages/WindowsUploadPage';
import RoofsUploadPage from './pages/RoofsUploadPage';
```

**Step 2: Update routes to use dynamic parameter**

Replace the upload routes (lines 118-134) with:

```javascript
          {/* Single dynamic upload route for all tenants */}
          <Route path="/upload/:tenantId" element={
            <ProtectedRoute>
              <UploadPage />
            </ProtectedRoute>
          } />

          {/* Redirect /upload to /upload/pools for backwards compatibility */}
          <Route path="/upload" element={<Navigate to="/upload/pools" replace />} />
```

**Step 3: Verify routes updated**

Run:
```bash
grep -n "upload" /home/reid/testhome/pools-visualizer/frontend/src/App.js
```

Expected: Shows `/upload/:tenantId` route and redirect

**Step 4: Commit**

```bash
git add frontend/src/App.js
git commit -m "feat: update routes for unified tenant wizard"
```

---

## Task 8: Add CSS for Tenant Header

**Files:**
- Modify: `frontend/src/pages/UploadPage.css`

**Step 1: Add tenant header styles**

Add to end of `frontend/src/pages/UploadPage.css`:

```css
/* Tenant Header */
.tenant-header {
  text-align: center;
  margin-bottom: 2rem;
  padding: 1rem;
}

.tenant-header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: var(--white);
  margin: 0 0 0.5rem 0;
}

.tenant-header p {
  font-size: 1rem;
  color: var(--light-gray);
  margin: 0;
}
```

**Step 2: Commit**

```bash
git add frontend/src/pages/UploadPage.css
git commit -m "style: add tenant header styles"
```

---

## Task 9: Delete Old Upload Pages

**Files:**
- Delete: `frontend/src/pages/WindowsUploadPage.js`
- Delete: `frontend/src/pages/RoofsUploadPage.js`

**Step 1: Remove deprecated files**

Run:
```bash
rm /home/reid/testhome/pools-visualizer/frontend/src/pages/WindowsUploadPage.js
rm /home/reid/testhome/pools-visualizer/frontend/src/pages/RoofsUploadPage.js
```

**Step 2: Verify files removed**

Run:
```bash
ls /home/reid/testhome/pools-visualizer/frontend/src/pages/*Upload*.js
```

Expected: Only shows `UploadPage.js`

**Step 3: Commit**

```bash
git add -A
git commit -m "chore: remove deprecated tenant-specific upload pages"
```

---

## Task 10: Update Dashboard Links

**Files:**
- Modify: `frontend/src/pages/DashboardPage.js`

**Step 1: Find and update links to upload pages**

Search for links in DashboardPage.js:
```bash
grep -n "upload" /home/reid/testhome/pools-visualizer/frontend/src/pages/DashboardPage.js
```

Update any hardcoded links like `/upload/windows` to use the new route format (they should already work since we're keeping the same URL structure).

**Step 2: Verify links work**

The existing links `/upload/windows` and `/upload/roofs` should work with the new dynamic route.

**Step 3: Commit (if changes needed)**

```bash
git add frontend/src/pages/DashboardPage.js
git commit -m "fix: update dashboard upload links for unified wizard"
```

---

## Task 11: Integration Test - Full Flow

**Step 1: Start backend**

Run:
```bash
cd /home/reid/testhome/pools-visualizer && source venv/bin/activate && python3 manage.py runserver 8006
```

**Step 2: Start frontend (separate terminal)**

Run:
```bash
cd /home/reid/testhome/pools-visualizer/frontend && npm start
```

**Step 3: Test each tenant route**

1. Navigate to `http://localhost:3006/upload/pools` - Should show pool wizard
2. Navigate to `http://localhost:3006/upload/windows` - Should show windows wizard
3. Navigate to `http://localhost:3006/upload/roofs` - Should show roofs wizard

**Step 4: Test submission**

1. Complete a windows wizard flow
2. Submit with an image
3. Verify in Django admin or logs that `tenant_id='windows'` is saved

**Step 5: Verify tenant routing**

Check the thinking logs to confirm windows prompts are used (not pools):
```bash
ls -lt /home/reid/testhome/pools-visualizer/media/thinking_logs/ | head -5
```

---

## Task 12: Final Commit and Cleanup

**Step 1: Check git status**

Run:
```bash
cd /home/reid/testhome/pools-visualizer && git status
```

**Step 2: Final commit if needed**

```bash
git add -A
git commit -m "feat: unified tenant wizard with proper routing

- Merged 3 upload pages into single dynamic component
- Added tenant_id field to VisualizationRequest model
- Pass tenant_id through full pipeline to get_tenant_config()
- Removed legacy security terminology
- Added tenant configuration file for wizard steps
- Updated routes to /upload/:tenantId pattern"
```

---

## Verification Checklist

After completing all tasks, verify:

- [ ] `/upload/pools` shows pool wizard with 7 steps
- [ ] `/upload/windows` shows windows wizard with 8 steps
- [ ] `/upload/roofs` shows roofs wizard with 6 steps
- [ ] Submitting from windows wizard creates request with `tenant_id='windows'`
- [ ] AI generation uses correct prompts (check thinking logs)
- [ ] No "security vulnerabilities" message appears during processing
- [ ] PDF is named `visualization_report_*.pdf` not `security_report_*.pdf`
- [ ] Old upload pages are deleted
- [ ] All routes work correctly
