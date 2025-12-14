# Session Notes

---

## Session: 2025-12-13 - Pools Visualizer Full Implementation

### Context
- User wanted to create a standalone pools visualizer forked from the boss-security-visualizer
- Previous session had forked the repo to `/home/reid/testhome/pools-visualizer/`
- This session implemented the full 5-screen wizard and 6-step AI pipeline

### Work Completed
- **Backend - Pools Tenant (Tasks 1-4)**
  - Created `api/tenants/pools/__init__.py`
  - Created `api/tenants/pools/config.py` - comprehensive config with pricing-ready data model (prices hidden from API)
  - Created `api/tenants/pools/prompts.py` - 6-step AI pipeline prompts
  - Registered PoolsTenantConfig in `api/tenants/__init__.py`
  - Added missing abstract methods (`get_mesh_color_choices`, `get_opacity_choices`)

- **Frontend - 5-Screen Wizard (Tasks 5-14)**
  - Updated Zustand store with pool selections in `frontend/src/store/visualizationStore.js`
  - Created config API endpoint in `api/views_config.py`
  - Created 5 new wizard screens:
    - `PoolSizeShapeStep.js` - Size (Starter/Classic/Family/Resort/Custom) + Shape (7 options)
    - `FinishBuiltInsStep.js` - Interior finish, tanning ledge, loungers, spa
    - `DeckStep.js` - Deck material + color with navigation buttons
    - `WaterFeaturesStep.js` - Multi-select water features (max 2)
    - `FinishingStep.js` - Lighting, landscaping, furniture radio groups
  - Updated `Step5Review.js` with pool-specific review display
  - Integrated wizard in `frontend/src/pages/UploadPage.js`
  - Added comprehensive CSS for all wizard components in `UploadPage.css`

- **Cleanup & Fixes (Tasks 15-18)**
  - Updated `Navigation.js` - Changed title from "Homescreen Visualizer" to "Pool Visualizer"
  - Updated `ProcessingScreen.jsx` - Pool-relevant messages and "Pool Visualizer AI" branding
  - Fixed DeckStep missing navigation buttons
  - Fixed API port from 8000 to 8006 in `frontend/src/services/api.js`

### Current State
- **Backend:** Running on port 8006 with `ACTIVE_TENANT=pools`
- **Frontend:** Running on port 3006
- **Config API:** Working at `http://localhost:8006/api/config/` - returns pools config with no pricing data
- **Wizard:** All 5 screens functional with navigation
- **Issue:** User reported "Network Error" on submit - fixed API port, needs verification

### Next Steps
1. **Verify submit works** - User needs to refresh and test the full wizard flow
2. **Test AI pipeline** - Submit an image and verify the 6-step pipeline runs correctly
3. **Prompts refinement** - The prompts.py has the full pipeline but may need tuning after testing
4. **Style polish** - Some wizard screens may need visual tweaks for uniformity

### Notes
- **Port Configuration:** Backend runs on 8006, frontend on 3006. API port was hardcoded to 8000 - fixed to 8006.
- **Pricing Hidden:** Config API excludes all pricing data (base_price, price_multiplier, price_add, price_per_sqft)
- **Pipeline Steps:** cleanup → pool_shell → deck → water_features → finishing → quality_check
- **State Management:** Components use Zustand store directly, UploadPage passes props but they're not always used
- **User Instruction:** "NEVER TOUCH PROMPTS UNLESS THE USER SPECIFICALLY SAYS ITS OK" - prompts should not be modified without explicit approval

### Key Files
- `api/tenants/pools/config.py` - All pool configuration options
- `api/tenants/pools/prompts.py` - 6-step AI pipeline prompts (DO NOT MODIFY without approval)
- `frontend/src/pages/UploadPage.js` - Main wizard container
- `frontend/src/pages/UploadPage.css` - All wizard styling
- `frontend/src/components/UploadWizard/*.js` - Individual wizard step components
- `frontend/src/services/api.js` - API configuration (port 8006)

### Git Commits This Session
```
109b8a2 fix(api): change default API port to 8006
4d3f280 fix(wizard): add navigation buttons to DeckStep and unify CSS across all wizard steps
3ce4469 feat: pools visualizer complete
4b99d3e chore: remove remaining security screen references
96b06f4 fix(wizard): correct store import and remove missing CSS import in DeckStep
aa92d76 fix(pools): add missing abstract methods to PoolsTenantConfig
9decff9 style(wizard): add CSS for pool wizard components
6c08770 feat(wizard): update review step for pool selections
0d4ce85 feat(wizard): integrate new 5-screen pool wizard
... (and earlier tasks)
```

---

## Session: 2025-12-01 - Boss Visualizer Diagnostics

### What We Did
- Created comprehensive TENANT-ARCHITECTURE.md documentation (~700 lines)
  - Documented tenant configuration system (BaseTenantConfig, BossTenantConfig)
  - Documented scope system flow: frontend → backend → AI pipeline
  - Documented AI prompts system (cleanup, insertion, quality check)
  - Added live database example output
  - Mapped pipeline steps to scope keys
  - Listed all related files
- Updated CLAUDE.md with "During Session" logging requirements
- Investigated scope mismatch concern:
  - Created safety branch `fix/scope-mismatch-20251201-0956`
  - Ran diagnostic on all 104 VisualizationRequests
  - **Finding: NOT A BUG** - Empty `scope: {}` is historical data (IDs 1-35)
  - Scope system working correctly since ID 36+
  - Created DIAGNOSTIC-SCOPE-MISMATCH.md with full report
- Deep dive investigation (5 questions):
  - Q1: `screen_categories` vs `scope` - scope is source of truth, categories is dead code
  - Q2: Legacy fallback exists in gemini_provider.py:101-113 (could mask bugs)
  - Q3: Cleanup runs UNCONDITIONALLY - weather issues are prompt bugs, not scope
  - Q4: No `hasPatio` format in DB - all lowercase, transform happens in UploadPage.js
  - Q5: Step2Scope.js → Zustand → UploadPage.js (transforms) → Backend
- Discovered hidden issues:
  - `doorType` is collected but NOT sent to backend (missing from scopePayload)
  - `screen_categories` is dead code cluttering the model
- Weather change investigation (DIAGNOSTIC-WEATHER-CHANGE.md):
  - Analyzed 14 pipeline debug images across multiple sequences
  - **Finding: PATIO step causes weather change, not cleanup**
  - Brick house: overcast → blue sky at patio step
  - Modern house: weather preserved throughout (image-dependent)
  - Windows-only: weather always preserved
  - Root cause: Patio prompt lacks sky preservation instruction
  - Quality check doesn't validate weather preservation
- **Comprehensive visual analysis (ANALYSIS-WEATHER-VISUAL.md):**
  - Reviewed ~25 sequences from 307 total pipeline images
  - **Finding: Weather change is STOCHASTIC, not deterministic**
  - Same image can produce different weather across runs (~50% change rate)
  - Brick house: ~60% of runs change weather
  - Modern house: 0% of runs change weather
  - **RECOMMENDATION: GO WITH DISCLAIMER** instead of fixing
- **Implemented AI disclaimer in UI:**
  - Added to `ResultDetailPage.js` below image comparison
  - Text: "AI-enhanced visualization. Lighting and weather conditions may vary from actual appearance."
  - Styled with `.ai-disclaimer` class (italic, centered, subtle gray)
- **Pipeline reorder + prompt updates:**
  - Changed pipeline order: cleanup → doors → windows → patio → quality_check
  - Reason: Patio is largest envelope, must see doors/windows already installed
  - Updated cleanup prompt to explicitly make weather sunny
  - Reverted insertion prompts to original (complex) version
  - Synced both `api/tenants/boss/prompts.py` and `api/visualizer/prompts.py`
- **RESTORED THINKING MODE (likely root cause of all issues!):**
  - Found that commit `4ccfea9` (Nov 28) removed thinking mode
  - Original: `ThinkingConfig(include_thoughts=True)` + `response_modalities: ["TEXT", "IMAGE"]`
  - After revert: `pass` (no thinking at all)
  - **This explains weather changes, inconsistent results, ignored instructions**
  - Restored original config with `include_thoughts=True`
  - Added thinking log output to `media/thinking_logs/` for debugging
  - Each step logs: timestamp, prompt, and Gemini's reasoning

### What's Working
- Tenant registry system auto-registers Boss tenant
- Scope flows from frontend wizard through to AI pipeline
- Quality check prompts adapt based on scope flags
- **Scope IS being saved correctly** on all recent requests (ID 36+)

### What's Broken / Blocked
- `screen-visualizer` branch referenced in TODO.md doesn't exist
- 3 requests stuck in `processing` status (IDs 3, 52, 59)
- `screen_categories` field is deprecated but still in model
- **`doorType` not being sent to backend** - UI collects but UploadPage.js doesn't include it
- Legacy fallback in gemini_provider.py could mask scope bugs
- ~~PATIO prompt changes weather~~ → **ACCEPTABLE** (use disclaimer instead)

### Next Session Should
- ~~Add disclaimer to results UI~~ ✓ DONE
- ~~Pipeline reorder + sunny prompts~~ ✓ DONE
- **Organize reference images** - Move from `_raw/` to feature folders
- **Implement reference image loading** - Add to services.py
- **Fix `doorType` transmission** - Add to scopePayload in UploadPage.js
- Remove `screen_categories` from model/serializers (migration)
- Add logging to fallback in gemini_provider.py to detect when it activates
- Investigate stuck `processing` requests (3, 52, 59)

---

## Previous Sessions

### 2025-11-30
- Cleaned up git branches
- Deleted dev repo
- Created feature branches from master
