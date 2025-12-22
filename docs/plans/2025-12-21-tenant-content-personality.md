# Tenant Content Personality Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Give each tenant (pools, windows, roofs) unique marketing-ready content across wizard, landing, and results pages.

**Architecture:** Separate content files per tenant (`frontend/src/content/{tenant}.js`) with a central loader. UploadPage displays hero, value props, testimonials. ResultDetailPage shows tenant-specific labels and CTAs. Content keyed by component names for wizard steps.

**Tech Stack:** React 19.1, ES6 modules, dynamic imports

---

## Task 1: Create Content Loader

**Files:**
- Create: `frontend/src/content/index.js`

**Step 1: Create the content directory**

```bash
mkdir -p /home/reid/testhome/pools-visualizer/frontend/src/content
```

**Step 2: Create the loader file**

Create `frontend/src/content/index.js`:

```javascript
/**
 * Tenant Content Loader
 * Provides tenant-specific marketing content for UI components
 */

import { isValidTenant } from '../config/tenants';

// Import all tenant content
import { poolsContent } from './pools';
import { windowsContent } from './windows';
import { roofsContent } from './roofs';

const TENANT_CONTENT = {
  pools: poolsContent,
  windows: windowsContent,
  roofs: roofsContent,
};

/**
 * Get content for a specific tenant
 * @param {string} tenantId - The tenant identifier (pools, windows, roofs)
 * @returns {object} The tenant's content object
 */
export const getTenantContent = (tenantId) => {
  const safeTenantId = isValidTenant(tenantId) ? tenantId : 'pools';
  return TENANT_CONTENT[safeTenantId] || TENANT_CONTENT.pools;
};
```

**Step 3: Commit**

```bash
git add frontend/src/content/index.js
git commit -m "feat: add tenant content loader"
```

---

## Task 2: Create Pools Content File

**Files:**
- Create: `frontend/src/content/pools.js`

**Step 1: Create pools content**

Create `frontend/src/content/pools.js`:

```javascript
/**
 * Pools Tenant Content
 * Marketing copy for the pool designer experience
 */

export const poolsContent = {
  // Landing/Hero Section
  hero: {
    headline: "See Your Dream Pool Before You Build",
    subheadline: "Upload a photo of your backyard and watch AI create a stunning, realistic pool visualization in under 60 seconds.",
    cta: "Design Your Pool Now",
  },

  // Value Propositions
  valueProps: [
    {
      title: "Instant AI Visualization",
      description: "See exactly how your new pool will look in your actual backyard—no guessing, no surprises.",
    },
    {
      title: "Customize Everything",
      description: "Experiment with shapes, finishes, water features, and decking until it's perfect.",
    },
    {
      title: "Free Design, No Obligation",
      description: "Get a professional visualization and quote without any commitment.",
    },
  ],

  // Testimonials
  testimonials: [
    {
      quote: "We tried 3 pool companies before finding this tool. Seeing the pool in our actual yard made the decision easy.",
      author: "Sarah M.",
      location: "Austin, TX",
    },
    {
      quote: "The visualization was so accurate, I showed it to my contractor and he built it exactly like that!",
      author: "Mike D.",
      location: "Phoenix, AZ",
    },
  ],

  // FAQ
  faq: [
    {
      question: "How accurate is the visualization?",
      answer: "Our AI creates highly realistic renderings based on your actual backyard photo. Final results may vary slightly based on construction details.",
    },
    {
      question: "Can I try different pool designs?",
      answer: "Absolutely! Run the designer as many times as you like with different options—it's completely free.",
    },
    {
      question: "How do I get a quote?",
      answer: "After your visualization is complete, download your free report and we'll connect you with certified pool builders in your area.",
    },
  ],

  // Wizard Step Content (keyed by component name)
  steps: {
    PoolSizeShapeStep: {
      title: "Choose Your Pool Size & Shape",
      description: "Start with the foundation—select dimensions that fit your yard and a shape that matches your style.",
    },
    FinishBuiltInsStep: {
      title: "Select Your Interior Finish",
      description: "The finish determines your water color. Add built-in features like tanning ledges and in-pool loungers.",
    },
    DeckStep: {
      title: "Design Your Pool Deck",
      description: "Choose materials and colors that complement your home and create the perfect poolside atmosphere.",
    },
    WaterFeaturesStep: {
      title: "Add Water Features",
      description: "Waterfalls, fountains, and jets add drama and help mask neighborhood noise.",
    },
    FinishingStep: {
      title: "Finishing Touches",
      description: "Complete your oasis with lighting, landscaping, and outdoor furniture.",
    },
    Step4Upload: {
      title: "Upload Your Backyard Photo",
      description: "Take a photo of where you want your pool. For best results, capture the full area in daylight.",
    },
    Step5Review: {
      title: "Review Your Selections",
      description: "Double-check your choices before we generate your custom pool visualization.",
    },
  },

  // Results Page Content
  results: {
    afterLabel: "With Pool",
    toggleShowResult: "Show Pool",
    toggleShowOriginal: "Show Original",
    aiDisclaimer: "AI-enhanced visualization. Lighting, landscaping, and weather conditions may vary from actual appearance.",
    reportTeaser: {
      title: (count) => count > 0
        ? `${count} Design Recommendation${count === 1 ? '' : 's'} Available`
        : 'Your Pool Design Report is Ready',
      description: "Get detailed specifications, cost estimates, and connect with certified pool builders in your area.",
      buttonText: "Download Your Free Pool Report",
    },
  },
};
```

**Step 2: Commit**

```bash
git add frontend/src/content/pools.js
git commit -m "feat: add pools tenant content"
```

---

## Task 3: Create Windows Content File

**Files:**
- Create: `frontend/src/content/windows.js`

**Step 1: Create windows content**

Create `frontend/src/content/windows.js`:

```javascript
/**
 * Windows Tenant Content
 * Marketing copy for the window & door designer experience
 */

export const windowsContent = {
  // Landing/Hero Section
  hero: {
    headline: "Visualize Your New Windows & Doors",
    subheadline: "Upload a photo of your home and see exactly how new windows and doors will transform your curb appeal.",
    cta: "Start Your Design",
  },

  // Value Propositions
  valueProps: [
    {
      title: "See Before You Buy",
      description: "No more guessing how new windows will look—see them on your actual home before you commit.",
    },
    {
      title: "Compare Styles Instantly",
      description: "Try different frame materials, colors, and grille patterns until you find the perfect match.",
    },
    {
      title: "Get Expert Recommendations",
      description: "Our AI considers your home's architecture to suggest the most complementary options.",
    },
  ],

  // Testimonials
  testimonials: [
    {
      quote: "We were torn between white and black frames. Seeing both options on our actual house made the choice obvious.",
      author: "Jennifer K.",
      location: "Dallas, TX",
    },
    {
      quote: "The visualization helped us realize we wanted to upgrade all the windows, not just the front. Worth every penny.",
      author: "Robert T.",
      location: "Houston, TX",
    },
  ],

  // FAQ
  faq: [
    {
      question: "What types of windows can I visualize?",
      answer: "We support double-hung, casement, sliding, bay windows, and more. Plus entry doors, French doors, and sliding glass doors.",
    },
    {
      question: "Will this work with my home's style?",
      answer: "Yes! Our AI adapts to any architectural style—modern, traditional, craftsman, colonial, and everything in between.",
    },
    {
      question: "How do I get pricing?",
      answer: "Download your free report to receive estimates and connect with certified installers in your area.",
    },
  ],

  // Wizard Step Content
  steps: {
    ProjectTypeStep: {
      title: "What's Your Project?",
      description: "Tell us whether you're replacing existing windows, adding new ones, or upgrading doors.",
    },
    DoorTypeStep: {
      title: "Select Door Style",
      description: "Choose from entry doors, French doors, sliding glass, or folding patio doors.",
    },
    WindowTypeStep: {
      title: "Choose Window Type",
      description: "Select the window style that best fits your home and ventilation needs.",
    },
    FrameMaterialStep: {
      title: "Pick Your Frame Material",
      description: "Vinyl, wood, fiberglass, or aluminum—each has unique benefits for Texas weather.",
    },
    GrillePatternStep: {
      title: "Add Grille Patterns",
      description: "Grilles add character and can match your home's architectural style.",
    },
    HardwareTrimStep: {
      title: "Hardware & Trim Details",
      description: "The finishing touches that complete your window and door design.",
    },
    Step4Upload: {
      title: "Upload Your Home Photo",
      description: "Take a clear photo of the area where you want new windows or doors. Daylight works best.",
    },
    Step5Review: {
      title: "Review Your Selections",
      description: "Confirm your choices before we create your home transformation visualization.",
    },
  },

  // Results Page Content
  results: {
    afterLabel: "With New Windows",
    toggleShowResult: "Show New Look",
    toggleShowOriginal: "Show Original",
    aiDisclaimer: "AI-enhanced visualization. Actual product appearance may vary slightly based on installation details.",
    reportTeaser: {
      title: (count) => count > 0
        ? `${count} Upgrade Opportunity${count === 1 ? '' : 'ies'} Identified`
        : 'Your Window & Door Report is Ready',
      description: "Get detailed specifications, energy efficiency ratings, and quotes from certified installers.",
      buttonText: "Download Your Free Report",
    },
  },
};
```

**Step 2: Commit**

```bash
git add frontend/src/content/windows.js
git commit -m "feat: add windows tenant content"
```

---

## Task 4: Create Roofs Content File

**Files:**
- Create: `frontend/src/content/roofs.js`

**Step 1: Create roofs content**

Create `frontend/src/content/roofs.js`:

```javascript
/**
 * Roofs Tenant Content
 * Marketing copy for the roof & solar designer experience
 */

export const roofsContent = {
  // Landing/Hero Section
  hero: {
    headline: "See Your New Roof Before Installation",
    subheadline: "Upload a photo of your home and visualize new roofing materials, colors, and solar panel options instantly.",
    cta: "Design Your Roof",
  },

  // Value Propositions
  valueProps: [
    {
      title: "Visualize Any Material",
      description: "See how asphalt shingles, metal roofing, tile, or slate will look on your actual home.",
    },
    {
      title: "Explore Solar Options",
      description: "Visualize solar panels integrated with your new roof design before making the investment.",
    },
    {
      title: "Texas Weather Ready",
      description: "Our recommendations consider Texas heat, hail, and hurricane requirements.",
    },
  ],

  // Testimonials
  testimonials: [
    {
      quote: "After the hail storm, we used this to pick our new roof color. The metal roof visualization sold us completely.",
      author: "Carlos R.",
      location: "San Antonio, TX",
    },
    {
      quote: "Seeing solar panels on our roof helped convince my wife. Now we're saving $200/month on electricity!",
      author: "David L.",
      location: "Fort Worth, TX",
    },
  ],

  // FAQ
  faq: [
    {
      question: "What roofing materials can I visualize?",
      answer: "We support asphalt shingles, architectural shingles, metal roofing (standing seam and corrugated), clay tile, concrete tile, and slate.",
    },
    {
      question: "Can I see solar panels on my roof?",
      answer: "Yes! We can visualize standard solar panels, integrated solar shingles, or a combination of both.",
    },
    {
      question: "How accurate are the color options?",
      answer: "We use manufacturer-accurate colors, but actual appearance may vary slightly based on lighting conditions.",
    },
  ],

  // Wizard Step Content
  steps: {
    RoofMaterialStep: {
      title: "Choose Your Roofing Material",
      description: "Select a material that fits your style, budget, and Texas weather requirements.",
    },
    RoofColorStep: {
      title: "Select Your Roof Color",
      description: "Pick a color that complements your home's exterior and neighborhood aesthetic.",
    },
    SolarOptionStep: {
      title: "Add Solar Panels",
      description: "Optional: Visualize solar panels or solar shingles integrated with your new roof.",
    },
    GutterOptionStep: {
      title: "Upgrade Your Gutters",
      description: "New gutters complete the look and protect your investment from Texas storms.",
    },
    Step4Upload: {
      title: "Upload Your Home Photo",
      description: "Capture your home's exterior showing the full roofline. Best results in daylight.",
    },
    Step5Review: {
      title: "Review Your Selections",
      description: "Confirm your roofing choices before we generate your visualization.",
    },
  },

  // Results Page Content
  results: {
    afterLabel: "With New Roof",
    toggleShowResult: "Show New Roof",
    toggleShowOriginal: "Show Original",
    aiDisclaimer: "AI-enhanced visualization. Actual roofing appearance may vary based on installation and lighting.",
    reportTeaser: {
      title: (count) => count > 0
        ? `${count} Recommendation${count === 1 ? '' : 's'} for Your Roof`
        : 'Your Roofing Report is Ready',
      description: "Get material specifications, warranty information, and quotes from certified roofing contractors.",
      buttonText: "Download Your Free Roofing Report",
    },
  },
};
```

**Step 2: Commit**

```bash
git add frontend/src/content/roofs.js
git commit -m "feat: add roofs tenant content"
```

---

## Task 5: Update UploadPage with Hero Section

**Files:**
- Modify: `frontend/src/pages/UploadPage.js`
- Modify: `frontend/src/pages/UploadPage.css`

**Step 1: Add content import to UploadPage.js**

At line 6, after the tenants import, add:

```javascript
import { getTenantContent } from '../content';
```

**Step 2: Add content loading in component**

After line 66 (`const tenantConfig = ...`), add:

```javascript
  const content = useMemo(() => getTenantContent(tenantId), [tenantId]);
```

**Step 3: Replace tenant header with hero section**

Replace lines 151-155 (the tenant-header div) with:

```javascript
      {/* Hero Section */}
      <div className="hero-section">
        <h1>{content.hero.headline}</h1>
        <p className="hero-subheadline">{content.hero.subheadline}</p>
      </div>

      {/* Value Propositions */}
      <div className="value-props">
        {content.valueProps.map((prop, idx) => (
          <div key={idx} className="value-prop">
            <h3>{prop.title}</h3>
            <p>{prop.description}</p>
          </div>
        ))}
      </div>
```

**Step 4: Add hero and value prop CSS**

Add to end of `frontend/src/pages/UploadPage.css`:

```css
/* Hero Section */
.hero-section {
  text-align: center;
  padding: 2rem 1rem;
  max-width: 800px;
  margin: 0 auto 2rem;
}

.hero-section h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--white);
  margin: 0 0 1rem 0;
  line-height: 1.2;
}

.hero-subheadline {
  font-size: 1.25rem;
  color: var(--light-gray);
  margin: 0;
  line-height: 1.5;
}

/* Value Propositions */
.value-props {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  max-width: 1000px;
  margin: 0 auto 2rem;
  padding: 0 1rem;
}

.value-prop {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}

.value-prop h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--white);
  margin: 0 0 0.5rem 0;
}

.value-prop p {
  font-size: 0.95rem;
  color: var(--light-gray);
  margin: 0;
  line-height: 1.4;
}
```

**Step 5: Commit**

```bash
git add frontend/src/pages/UploadPage.js frontend/src/pages/UploadPage.css
git commit -m "feat: add hero section and value props to UploadPage"
```

---

## Task 6: Update ResultDetailPage with Tenant Content

**Files:**
- Modify: `frontend/src/pages/ResultDetailPage.js`

**Step 1: Add content imports**

After line 8, add:

```javascript
import { getTenantContent } from '../content';
```

**Step 2: Add content state and loading**

After line 25 (`const [showLeadModal, setShowLeadModal] = useState(false);`), add:

```javascript
  const [content, setContent] = useState(null);
```

**Step 3: Load content when request is fetched**

Inside `fetchRequestDetails`, after line 33 (`setRequest(data);`), add:

```javascript
      // Load tenant-specific content
      if (data.tenant_id) {
        setContent(getTenantContent(data.tenant_id));
      }
```

**Step 4: Replace hardcoded "With Pool" label**

At line 188, replace:

```javascript
            <span className="label after-label">With Pool</span>
```

With:

```javascript
            <span className="label after-label">{content?.results?.afterLabel || 'After'}</span>
```

**Step 5: Replace toggle button text**

At lines 196-197, replace:

```javascript
              {showOriginal ? 'Show Pool' : 'Show Original'}
```

With:

```javascript
              {showOriginal ? (content?.results?.toggleShowResult || 'Show Result') : (content?.results?.toggleShowOriginal || 'Show Original')}
```

**Step 6: Replace AI disclaimer**

At lines 204-206, replace the hardcoded disclaimer with:

```javascript
        <p className="ai-disclaimer">
          {content?.results?.aiDisclaimer || 'AI-enhanced visualization. Actual appearance may vary.'}
        </p>
```

**Step 7: Replace security teaser content**

Replace lines 215-222 (the teaser-text div content) with:

```javascript
            <div className="teaser-text">
              <h3>
                {content?.results?.reportTeaser?.title
                  ? content.results.reportTeaser.title(vulnerabilityCount)
                  : (vulnerabilityCount > 0
                      ? `${vulnerabilityCount} Item${vulnerabilityCount === 1 ? '' : 's'} to Review`
                      : 'Your Report is Ready')}
              </h3>
              <p>
                {content?.results?.reportTeaser?.description || 'Download your detailed report and recommendations.'}
              </p>
            </div>
```

**Step 8: Replace download button text**

At line 237, replace:

```javascript
            Download Your Free Security Report
```

With:

```javascript
            {content?.results?.reportTeaser?.buttonText || 'Download Your Free Report'}
```

**Step 9: Commit**

```bash
git add frontend/src/pages/ResultDetailPage.js
git commit -m "feat: add tenant-specific content to ResultDetailPage"
```

---

## Task 7: Verify Build and Test

**Step 1: Run frontend build**

```bash
cd /home/reid/testhome/pools-visualizer/frontend && npm run build
```

Expected: Build succeeds with no errors

**Step 2: Start frontend and test each tenant**

```bash
cd /home/reid/testhome/pools-visualizer/frontend && PORT=3006 npm start
```

Test URLs:
- http://localhost:3006/upload/pools - Should show pool hero and value props
- http://localhost:3006/upload/windows - Should show windows hero and value props
- http://localhost:3006/upload/roofs - Should show roofs hero and value props

**Step 3: Commit final state**

```bash
git add -A
git commit -m "feat: tenant-specific content personality complete

- Added content loader with getTenantContent()
- Created marketing content for pools, windows, roofs
- UploadPage shows hero section and value props
- ResultDetailPage uses tenant-specific labels and CTAs"
```

---

## Verification Checklist

After completing all tasks, verify:

- [ ] `/upload/pools` shows "See Your Dream Pool Before You Build" headline
- [ ] `/upload/windows` shows "Visualize Your New Windows & Doors" headline
- [ ] `/upload/roofs` shows "See Your New Roof Before Installation" headline
- [ ] Each tenant shows 3 unique value propositions
- [ ] Results page shows tenant-specific "after" label (With Pool, With New Windows, With New Roof)
- [ ] Results page shows tenant-specific report download button text
- [ ] Frontend builds without errors
