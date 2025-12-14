# Remove Boss Branding Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove all Boss Security Screens branding and references, making this a pools-only visualizer.

**Architecture:** Replace all user-facing Boss branding with Pool Visualizer branding. Remove boss tenant entirely. Update tests and fallbacks.

**Tech Stack:** React, Django, Python

---

## Risk Assessment

**HIGH RISK Areas:**
- `api/tenants/__init__.py` - Removing boss tenant could break imports elsewhere
- `api/tests/test_tenant_registry.py` - Tests import boss tenant directly
- PDF generator has substantial boss content

**MITIGATION:**
- Run tests after each major change
- Keep api/visualizer/prompts.py as legacy fallback (don't delete)
- Verify no other files import from api/tenants/boss

---

## Pre-Flight Check

**Step 1: Verify no hidden boss imports**

```bash
cd /home/reid/testhome/pools-visualizer && grep -r "from api.tenants.boss" --include="*.py" | grep -v __pycache__ | grep -v test_tenant
```

Expected: Only test_tenant_registry.py should import boss tenant

**Step 2: Run existing tests to establish baseline**

```bash
cd /home/reid/testhome/pools-visualizer && source venv/bin/activate && python manage.py test api.tests.test_tenant_registry -v 2
```

Expected: Tests pass (they test boss tenant currently)

---

## Task 1: Fix ProcessingScreen.jsx Branding

**Files:**
- Modify: `frontend/src/components/ProcessingScreen/ProcessingScreen.jsx:209`

**Step 1: Make the change**

Line 209 currently:
```jsx
          Powered by <span className="brand-name">Boss Security Screens</span>
```

Change to:
```jsx
          Powered by <span className="brand-name">Pool Visualizer AI</span>
```

**Step 2: Verify**

```bash
grep -n "Boss" /home/reid/testhome/pools-visualizer/frontend/src/components/ProcessingScreen/ProcessingScreen.jsx
```

Expected: No output (no Boss references remain)

**Step 3: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add frontend/src/components/ProcessingScreen/ProcessingScreen.jsx && git commit -m "fix(ui): remove Boss branding from ProcessingScreen"
```

---

## Task 2: Fix ResultDetailPage.js Branding

**Files:**
- Modify: `frontend/src/pages/ResultDetailPage.js`

**Step 1: Change line 188**

From:
```jsx
            <span className="label after-label">Boss Security Screen</span>
```

To:
```jsx
            <span className="label after-label">With Pool</span>
```

**Step 2: Change line 196**

From:
```jsx
              {showOriginal ? 'Show Security Screens' : 'Show Original'}
```

To:
```jsx
              {showOriginal ? 'Show Pool Design' : 'Show Original'}
```

**Step 3: Change lines 209-239 (Security Report section)**

Replace entire security-report-teaser section (lines 209-240) with pool-appropriate content:

From:
```jsx
      {/* Simplified Security Teaser + CTA */}
      {request.status === 'complete' && (
        <div className="security-report-teaser">
          <div className="teaser-content">
            <Shield size={32} className="teaser-icon" />
            <div className="teaser-text">
              <h3>
                {vulnerabilityCount > 0
                  ? `${vulnerabilityCount} Security Vulnerabilit${vulnerabilityCount === 1 ? 'y' : 'ies'} Detected`
                  : 'Security Analysis Complete'}
              </h3>
              <p>
                Your free security assessment reveals what intruders see when they look at your home—and exactly how to stop them.
              </p>
            </div>
          </div>
          <button
            className="btn-download-report"
            onClick={() => {
              if (isSalesRep) {
                // Sales reps skip lead capture, go direct to PDF
                window.open(`/api/visualization/${id}/pdf/`, '_blank');
              } else {
                setShowLeadModal(true);
              }
            }}
          >
            <Download size={20} />
            Download Your Free Security Report
          </button>
        </div>
      )}
```

To:
```jsx
      {/* Pool Design CTA */}
      {request.status === 'complete' && (
        <div className="security-report-teaser">
          <div className="teaser-content">
            <Shield size={32} className="teaser-icon" />
            <div className="teaser-text">
              <h3>Pool Design Complete</h3>
              <p>
                Your custom pool visualization is ready. Download the full quote to share with contractors.
              </p>
            </div>
          </div>
          <button
            className="btn-download-report"
            onClick={() => {
              if (isSalesRep) {
                window.open(`/api/visualization/${id}/pdf/`, '_blank');
              } else {
                setShowLeadModal(true);
              }
            }}
          >
            <Download size={20} />
            Download Pool Quote
          </button>
        </div>
      )}
```

**Step 4: Verify**

```bash
grep -n "Boss\|Security Screen\|security screen" /home/reid/testhome/pools-visualizer/frontend/src/pages/ResultDetailPage.js
```

Expected: No output

**Step 5: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add frontend/src/pages/ResultDetailPage.js && git commit -m "fix(ui): remove Boss branding from ResultDetailPage"
```

---

## Task 3: Rewrite QuoteSuccessPage.js for Pools

**Files:**
- Modify: `frontend/src/pages/QuoteSuccessPage.js`

**Step 1: Replace entire file content**

```jsx
import { Link, useLocation } from 'react-router-dom';
import { Mail, ArrowLeft, Waves, CheckCircle } from 'lucide-react';
import './QuoteSuccessPage.css';

const QuoteSuccessPage = () => {
  const location = useLocation();
  const { afterImageUrl } = location.state || {};

  const quoteDate = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  const quoteNumber = `POOL-${Math.floor(1000 + Math.random() * 9000)}`;

  return (
    <div className="quote-page">
      {/* Digital Paper Document */}
      <div className="quote-document">
        {/* Document Header */}
        <header className="doc-header">
          <div className="doc-header-left">
            <Waves className="doc-logo-icon" size={32} />
            <div className="doc-brand">
              <span className="doc-brand-name">POOL</span>
              <span className="doc-brand-tagline">Visualizer</span>
            </div>
          </div>
          <div className="doc-header-right">
            <h1 className="doc-title">POOL DESIGN QUOTE</h1>
            <p className="doc-number">#{quoteNumber}</p>
          </div>
        </header>

        {/* Document Body */}
        <div className="doc-body">
          {/* Client & Quote Info Row */}
          <div className="doc-info-row">
            <div className="doc-info-block">
              <h3>Client Details</h3>
              <p className="client-name">Valued Customer</p>
              <p className="client-address">
                Your Address<br />
                City, State ZIP
              </p>
            </div>
            <div className="doc-info-block">
              <h3>Quote Information</h3>
              <p><strong>Date:</strong> {quoteDate}</p>
              <p><strong>Valid Until:</strong> 30 Days</p>
              <p><strong>Designer:</strong> AI Visualizer</p>
            </div>
          </div>

          {/* Visual Verification */}
          {afterImageUrl && (
            <div className="visual-verification">
              <h3>Pool Design Preview</h3>
              <div className="verification-image-wrapper">
                <img src={afterImageUrl} alt="Pool Design Preview" />
                <div className="verification-label">
                  <CheckCircle size={14} />
                  AI-Generated Preview
                </div>
              </div>
            </div>
          )}

          {/* Design Specs */}
          <div className="specs-section">
            <h3>Design Specifications</h3>
            <table className="specs-table">
              <tbody>
                <tr>
                  <td className="spec-label">Pool Type</td>
                  <td className="spec-value">Custom In-Ground Pool</td>
                </tr>
                <tr>
                  <td className="spec-label">Finish</td>
                  <td className="spec-value">Premium Pebble Tec</td>
                </tr>
                <tr>
                  <td className="spec-label">Deck</td>
                  <td className="spec-value">Travertine Stone</td>
                </tr>
                <tr>
                  <td className="spec-label">Features</td>
                  <td className="spec-value">Per visualization selections</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Footer Note */}
          <div className="doc-footer-note">
            <p>
              This AI-generated visualization is for planning purposes. Final pricing
              requires on-site consultation with a licensed pool contractor.
              Actual results may vary based on site conditions.
            </p>
          </div>
        </div>

        {/* Document Footer */}
        <footer className="doc-footer">
          <div className="footer-contact">
            <p>Pool Visualizer AI</p>
            <p>Powered by advanced AI imaging technology</p>
          </div>
        </footer>
      </div>

      {/* Action Buttons (Outside the paper) */}
      <div className="quote-actions">
        <button className="btn-email-pdf">
          <Mail size={18} />
          EMAIL QUOTE
        </button>
        <Link to="/" className="btn-return">
          <ArrowLeft size={18} />
          RETURN TO DASHBOARD
        </Link>
      </div>
    </div>
  );
};

export default QuoteSuccessPage;
```

**Step 2: Verify**

```bash
grep -n "Boss\|BOSS\|Security" /home/reid/testhome/pools-visualizer/frontend/src/pages/QuoteSuccessPage.js
```

Expected: No output

**Step 3: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add frontend/src/pages/QuoteSuccessPage.js && git commit -m "fix(ui): rewrite QuoteSuccessPage for pools branding"
```

---

## Task 4: Update useTenantConfig.js Default

**Files:**
- Modify: `frontend/src/hooks/useTenantConfig.js`

**Step 1: Change getDefaultConfig function (lines 56-85)**

From:
```javascript
function getDefaultConfig() {
    return {
        tenant_id: 'boss',
        display_name: 'Boss Security Screens',
        choices: {
            mesh: [
                ['10x10', '10x10 Standard'],
                ['12x12', '12x12 Standard'],
                ['12x12_american', '12x12 American'],
            ],
            frame_color: [
                ['Black', 'Black'],
                ['Dark Bronze', 'Dark Bronze'],
                ['Stucco', 'Stucco'],
                ['White', 'White'],
                ['Almond', 'Almond'],
            ],
            mesh_color: [
                ['Black', 'Black (Recommended)'],
                ['Stucco', 'Stucco'],
                ['Bronze', 'Bronze'],
            ],
            opacity: [
                ['80', '80%'],
                ['95', '95%'],
                ['99', '99%'],
            ],
        },
    };
}
```

To:
```javascript
function getDefaultConfig() {
    return {
        tenant_id: 'pools',
        display_name: 'Pool Visualizer',
        choices: {
            // Pools don't use mesh/frame/opacity - these are for compatibility
            mesh: [],
            frame_color: [],
            mesh_color: [],
            opacity: [],
        },
    };
}
```

**Step 2: Verify**

```bash
grep -n "boss\|Boss" /home/reid/testhome/pools-visualizer/frontend/src/hooks/useTenantConfig.js
```

Expected: No output

**Step 3: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add frontend/src/hooks/useTenantConfig.js && git commit -m "fix(config): update default tenant config to pools"
```

---

## Task 5: Update Tenant Registry

**Files:**
- Modify: `api/tenants/__init__.py`

**Step 1: Remove boss import and registration**

Change lines 14-16 from:
```python
from .base import BaseTenantConfig
from .boss.config import BossTenantConfig
from .pools.config import PoolsTenantConfig
```

To:
```python
from .base import BaseTenantConfig
from .pools.config import PoolsTenantConfig
```

**Step 2: Change default tenant (lines 57-62)**

From:
```python
    # Determine active tenant from settings
    active_id = getattr(settings, 'ACTIVE_TENANT', 'boss')

    if active_id not in _TENANT_REGISTRY:
        logger.warning(f"Configured tenant '{active_id}' not found, falling back to 'boss'")
        active_id = 'boss'
```

To:
```python
    # Determine active tenant from settings
    active_id = getattr(settings, 'ACTIVE_TENANT', 'pools')

    if active_id not in _TENANT_REGISTRY:
        logger.warning(f"Configured tenant '{active_id}' not found, falling back to 'pools'")
        active_id = 'pools'
```

**Step 3: Remove boss registration (lines 85-87)**

From:
```python
# Auto-register Boss tenant on module load
register_tenant(BossTenantConfig())
register_tenant(PoolsTenantConfig())
```

To:
```python
# Auto-register Pools tenant on module load
register_tenant(PoolsTenantConfig())
```

**Step 4: Verify**

```bash
grep -n "boss\|Boss" /home/reid/testhome/pools-visualizer/api/tenants/__init__.py
```

Expected: No output

**Step 5: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add api/tenants/__init__.py && git commit -m "fix(tenants): remove boss tenant, default to pools"
```

---

## Task 6: Update Test File

**Files:**
- Modify: `api/tests/test_tenant_registry.py`

**Step 1: Replace entire file**

```python
"""Tests for tenant registry system."""
import unittest
from django.test import TestCase, override_settings

from api.tenants import (
    get_tenant_config,
    get_tenant_prompts,
    clear_cache,
    register_tenant
)
from api.tenants.pools.config import PoolsTenantConfig


class TenantRegistryTest(TestCase):

    def setUp(self):
        clear_cache()

    def test_pools_tenant_registered(self):
        """Pools tenant should be auto-registered."""
        config = get_tenant_config('pools')
        self.assertEqual(config.tenant_id, 'pools')

    def test_default_tenant_is_pools(self):
        """Default active tenant should be Pools."""
        config = get_tenant_config()
        self.assertEqual(config.tenant_id, 'pools')

    def test_prompts_module_has_required_functions(self):
        """Prompts module should have all required functions."""
        prompts = get_tenant_prompts()
        self.assertTrue(hasattr(prompts, 'get_cleanup_prompt'))
        self.assertTrue(hasattr(prompts, 'get_prompt'))

    def test_unknown_tenant_raises_error(self):
        """Unknown tenant ID should raise ValueError."""
        with self.assertRaises(ValueError):
            get_tenant_config('nonexistent')


class PoolsPromptTest(TestCase):
    """Verify pools tenant prompts work correctly."""

    def test_cleanup_prompt_exists(self):
        """Cleanup prompt should exist and be non-empty."""
        prompts = get_tenant_prompts('pools')
        prompt = prompts.get_cleanup_prompt()
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 100)

    def test_pool_shell_prompt_exists(self):
        """Pool shell prompt should exist."""
        prompts = get_tenant_prompts('pools')
        prompt = prompts.get_pool_shell_prompt({})
        self.assertIsInstance(prompt, str)
        self.assertIn('pool', prompt.lower())
```

**Step 2: Run tests**

```bash
cd /home/reid/testhome/pools-visualizer && source venv/bin/activate && python manage.py test api.tests.test_tenant_registry -v 2
```

Expected: All tests pass

**Step 3: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add api/tests/test_tenant_registry.py && git commit -m "test: update tenant registry tests for pools-only"
```

---

## Task 7: Update PDF Generator for Pools

**Files:**
- Modify: `api/utils/pdf_generator.py`

**Step 1: Update get_logo function (lines 129-133)**

From:
```python
    def get_logo():
        logo_path = os.path.join(settings.BASE_DIR, 'frontend', 'public', 'logo512.png')
        if os.path.exists(logo_path):
            return RLImage(logo_path, width=1.5*inch, height=1.5*inch)
        return Paragraph("BOSS SECURITY SCREENS", title_style)
```

To:
```python
    def get_logo():
        logo_path = os.path.join(settings.BASE_DIR, 'frontend', 'public', 'logo512.png')
        if os.path.exists(logo_path):
            return RLImage(logo_path, width=1.5*inch, height=1.5*inch)
        return Paragraph("POOL VISUALIZER", title_style)
```

**Step 2: Update page 1 subtitle (line 157)**

From:
```python
    elements.append(Paragraph("Prepared by Boss Security Screens", subtitle_style))
```

To:
```python
    elements.append(Paragraph("Prepared by Pool Visualizer AI", subtitle_style))
```

**Step 3: Update page 3 title (line 212)**

From:
```python
    elements.append(Paragraph("The Boss Solution", title_style))
```

To:
```python
    elements.append(Paragraph("Your Dream Pool", title_style))
```

**Step 4: Update page 3 subtitle (line 221)**

From:
```python
            elements.append(Paragraph("Protected with Boss Security Screens", subtitle_style))
```

To:
```python
            elements.append(Paragraph("Custom Pool Visualization", subtitle_style))
```

**Step 5: Update default item (line 263)**

From:
```python
        table_rows.append(["Security Screen Package", "1", "TBD", "TBD"])
```

To:
```python
        table_rows.append(["Pool Design Package", "1", "TBD", "TBD"])
```

**Step 6: Update page 5 guarantee section (line 289)**

From:
```python
    elements.append(Paragraph("The Boss 'No Break-In' Guarantee", subtitle_style))
```

To:
```python
    elements.append(Paragraph("Quality Guarantee", subtitle_style))
```

**Step 7: Update guarantee text (lines 290-293)**

From:
```python
    elements.append(Paragraph("""
    We are so confident in our product that if a burglar manages to break through our screen,
    we will replace the screen and pay your insurance deductible up to $3,000.
    """, body_style))
```

To:
```python
    elements.append(Paragraph("""
    This AI-generated visualization is for planning purposes only. Final designs and pricing
    require consultation with a licensed pool contractor. Results may vary based on site conditions.
    """, body_style))
```

**Step 8: Verify**

```bash
grep -n -i "boss\|security screen" /home/reid/testhome/pools-visualizer/api/utils/pdf_generator.py
```

Expected: No output (only "Security" in context of door names which is fine)

**Step 9: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add api/utils/pdf_generator.py && git commit -m "fix(pdf): update PDF generator for pools branding"
```

---

## Task 8: Delete Boss Tenant Directory

**Files:**
- Delete: `api/tenants/boss/` (entire directory)

**Step 1: Verify no imports will break**

```bash
cd /home/reid/testhome/pools-visualizer && grep -r "from api.tenants.boss" --include="*.py" | grep -v __pycache__
```

Expected: No output (we removed the import in Task 5)

**Step 2: Delete directory**

```bash
rm -rf /home/reid/testhome/pools-visualizer/api/tenants/boss/
```

**Step 3: Verify deletion**

```bash
ls /home/reid/testhome/pools-visualizer/api/tenants/
```

Expected: Should show `base.py`, `pools/`, `__init__.py`, `__pycache__/` - NO `boss/`

**Step 4: Commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add -A && git commit -m "chore: remove boss tenant directory"
```

---

## Task 9: Final Verification

**Step 1: Search for any remaining boss references**

```bash
cd /home/reid/testhome/pools-visualizer && grep -r -i "boss" --include="*.py" --include="*.js" --include="*.jsx" | grep -v node_modules | grep -v venv | grep -v __pycache__ | grep -v ".pyc"
```

Expected: Only documentation files (*.md) should have references, no code files

**Step 2: Run all tests**

```bash
cd /home/reid/testhome/pools-visualizer && source venv/bin/activate && python manage.py test api -v 2
```

Expected: All tests pass

**Step 3: Start server and verify**

```bash
cd /home/reid/testhome/pools-visualizer && source venv/bin/activate && python manage.py runserver 8006
```

Then check: http://127.0.0.1:8006/api/config/

Expected: Returns pools tenant config

**Step 4: Final commit**

```bash
cd /home/reid/testhome/pools-visualizer && git add -A && git commit -m "chore: complete boss branding removal" --allow-empty
```

---

## Rollback Plan

If something breaks:

```bash
cd /home/reid/testhome/pools-visualizer && git log --oneline -10
# Find the commit before changes started
git reset --hard <commit-hash>
```

---

## Files Summary

| File | Action | Risk |
|------|--------|------|
| `frontend/src/components/ProcessingScreen/ProcessingScreen.jsx` | Edit line 209 | Low |
| `frontend/src/pages/ResultDetailPage.js` | Edit multiple lines | Low |
| `frontend/src/pages/QuoteSuccessPage.js` | Replace entire file | Medium |
| `frontend/src/hooks/useTenantConfig.js` | Edit default config | Low |
| `api/tenants/__init__.py` | Remove boss, change default | High |
| `api/tests/test_tenant_registry.py` | Replace entire file | Medium |
| `api/utils/pdf_generator.py` | Edit multiple lines | Medium |
| `api/tenants/boss/` | Delete directory | High |
