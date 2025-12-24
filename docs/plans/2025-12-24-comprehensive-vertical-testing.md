# Comprehensive Vertical Testing Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Achieve the same 95% production readiness across all 4 verticals (roofs, windows, screens) that pools currently has.

**Architecture:**
- Source vertical-specific test images via web search
- Create comprehensive test scripts per vertical (adapted from pools)
- Run automated tests + manual quality evaluation
- Document results in quality reports

**Tech Stack:** Django REST Framework, Gemini AI (google-genai), PIL, Python requests

---

## Summary

| Task | Description | Est. Time |
|------|-------------|-----------|
| Task 1 | Source & download roofs test images | 15 min |
| Task 2 | Create roofs test framework & run tests | 30 min |
| Task 3 | Source & download windows test images | 15 min |
| Task 4 | Create windows test framework & run tests | 30 min |
| Task 5 | Source & download screens test images | 15 min |
| Task 6 | Create screens test framework & run tests | 30 min |
| Task 7 | Manual quality evaluation (all verticals) | 45 min |
| Task 8 | Generate quality reports | 15 min |

**Total:** ~3.5 hours

---

## Task 1: Source & Download Roofs Test Images

**Files:**
- Create: `media/test_houses/` directory
- Create: `media/test_houses/download_images.py`

**Step 1: Create test directory structure**

```bash
mkdir -p /home/astre/command-center/testhome/testhome-visualizer/media/test_houses/comprehensive_results
```

**Step 2: Search and download house exterior images**

Search for images using these criteria:
- "house exterior roofline" - Homes showing clear roof from elevated angle
- "residential house front view" - Various architectural styles
- "home roof visible aerial" - Showing multiple roof planes
- Need 15-20 diverse images (different styles, colors, angles)

Download from: Unsplash (unsplash.com), Pexels (pexels.com), Pixabay (pixabay.com)

**Step 3: Save images**

Save as `house_01.jpg`, `house_02.jpg`, etc. in `media/test_houses/`

**Step 4: Verify images**

```bash
ls -la /home/astre/command-center/testhome/testhome-visualizer/media/test_houses/*.jpg | wc -l
# Expected: 15-20 images
```

**Success Criteria:**
- [ ] 15+ house exterior images downloaded
- [ ] Images show clear rooflines from various angles
- [ ] Diverse house styles (ranch, two-story, colonial, modern)

---

## Task 2: Create Roofs Test Framework & Run Tests

**Files:**
- Create: `media/test_houses/comprehensive_test.py`
- Create: `docs/ROOFS_QUALITY_TEST.md`

**Step 1: Create test configuration**

```python
#!/usr/bin/env python3
"""
Comprehensive Roofs Visualizer Quality Testing
Tests all roofing material and solar options systematically.
"""
import os
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# Configuration
API_BASE = "http://localhost:8000/api"
TEST_IMAGES_DIR = Path(__file__).parent
RESULTS_DIR = TEST_IMAGES_DIR / "comprehensive_results"
RESULTS_DIR.mkdir(exist_ok=True)

# Test image selection (use 3 representative images)
TEST_IMAGES = [
    "house_01.jpg",
    "house_05.jpg",
    "house_10.jpg",
]

# Roof material options from config
ROOF_MATERIALS = ['asphalt_architectural', 'metal_standing_seam', 'clay_tile', 'concrete_tile', 'slate']
ROOF_COLORS = ['charcoal', 'black', 'brown', 'terracotta', 'slate_gray']
SOLAR_OPTIONS = ['none', 'partial', 'full_south']
GUTTER_OPTIONS = ['none', 'standard', 'seamless']

# Test Configurations - Priority Order
TEST_CONFIGS = {
    # Priority 1: Most Popular Combinations (5 configs)
    "P1-01": {
        "name": "Asphalt Architectural Charcoal",
        "scope": {
            "roof_material": "asphalt_architectural",
            "roof_color": "charcoal",
            "solar_option": "none",
            "gutter_option": "standard",
        }
    },
    "P1-02": {
        "name": "Metal Standing Seam Black",
        "scope": {
            "roof_material": "metal_standing_seam",
            "roof_color": "black",
            "solar_option": "none",
            "gutter_option": "seamless",
        }
    },
    "P1-03": {
        "name": "Clay Tile Terracotta",
        "scope": {
            "roof_material": "clay_tile",
            "roof_color": "terracotta",
            "solar_option": "none",
            "gutter_option": "standard",
        }
    },
    "P1-04": {
        "name": "Asphalt with Solar",
        "scope": {
            "roof_material": "asphalt_architectural",
            "roof_color": "charcoal",
            "solar_option": "partial",
            "gutter_option": "standard",
        }
    },
    "P1-05": {
        "name": "Metal with Full Solar",
        "scope": {
            "roof_material": "metal_standing_seam",
            "roof_color": "slate_gray",
            "solar_option": "full_south",
            "gutter_option": "seamless",
        }
    },

    # Priority 2: Premium Materials (4 configs)
    "P2-01": {
        "name": "Concrete Tile Brown",
        "scope": {
            "roof_material": "concrete_tile",
            "roof_color": "brown",
            "solar_option": "none",
            "gutter_option": "standard",
        }
    },
    "P2-02": {
        "name": "Natural Slate Gray",
        "scope": {
            "roof_material": "slate",
            "roof_color": "slate_gray",
            "solar_option": "none",
            "gutter_option": "copper",
        }
    },
    "P2-03": {
        "name": "Wood Shake Brown",
        "scope": {
            "roof_material": "wood_shake",
            "roof_color": "weathered_wood",
            "solar_option": "none",
            "gutter_option": "standard",
        }
    },
    "P2-04": {
        "name": "Metal Corrugated Green",
        "scope": {
            "roof_material": "metal_corrugated",
            "roof_color": "green",
            "solar_option": "none",
            "gutter_option": "standard",
        }
    },
}


def upload_image(image_path: Path) -> dict:
    """Upload an image and get the response."""
    with open(image_path, 'rb') as f:
        files = {'original_image': (image_path.name, f, 'image/jpeg')}
        response = requests.post(f"{API_BASE}/upload/", files=files)
        return response.json()


def create_visualization(upload_id: int, scope: dict) -> dict:
    """Create a visualization request."""
    data = {
        "tenant": "roofs",
        "upload_id": upload_id,
        "scope": scope,
        "options": {},
    }
    response = requests.post(f"{API_BASE}/visualizations/", json=data)
    return response.json()


def poll_visualization(viz_id: int, timeout: int = 120) -> dict:
    """Poll until visualization is complete."""
    start = time.time()
    while time.time() - start < timeout:
        response = requests.get(f"{API_BASE}/visualizations/{viz_id}/")
        data = response.json()
        if data.get('status') in ['completed', 'failed']:
            return data
        time.sleep(5)
    return {"status": "timeout", "error": "Visualization timed out"}


def run_test(config_id: str, config: dict, image_name: str) -> dict:
    """Run a single test configuration on an image."""
    image_path = TEST_IMAGES_DIR / image_name

    result = {
        "test_id": config_id,
        "config_name": config["name"],
        "image": image_name,
        "status": "pending",
    }

    start_time = time.time()

    try:
        # Upload
        upload = upload_image(image_path)
        if 'id' not in upload:
            result["status"] = "error"
            result["error"] = f"Upload failed: {upload}"
            return result

        # Create visualization
        viz = create_visualization(upload['id'], config['scope'])
        if 'id' not in viz:
            result["status"] = "error"
            result["error"] = f"Visualization creation failed: {viz}"
            return result

        # Poll for completion
        final = poll_visualization(viz['id'])

        result["duration_seconds"] = time.time() - start_time

        if final.get('status') == 'completed':
            result["status"] = "success"
            result["quality_score"] = final.get('quality_score', 0.0)
            result["result_id"] = final.get('id')
            result["result_image"] = final.get('generated_image')
        else:
            result["status"] = "error"
            result["error"] = final.get('error', 'Unknown error')

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        result["duration_seconds"] = time.time() - start_time

    return result


def run_all_tests(configs: dict = None, images: list = None):
    """Run all test configurations."""
    configs = configs or TEST_CONFIGS
    images = images or TEST_IMAGES

    results = []
    total = len(configs) * len(images)
    current = 0

    print(f"\n{'='*60}")
    print(f"ROOFS COMPREHENSIVE TEST - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    print(f"Configurations: {len(configs)}")
    print(f"Images per config: {len(images)}")
    print(f"Total tests: {total}")
    print(f"{'='*60}\n")

    for config_id, config in configs.items():
        for image in images:
            current += 1
            print(f"[{current}/{total}] Testing {config_id} ({config['name']}) on {image}...")

            result = run_test(config_id, config, image)
            results.append(result)

            status_icon = "✓" if result["status"] == "success" else "✗"
            score = result.get("quality_score", 0)
            duration = result.get("duration_seconds", 0)
            print(f"  {status_icon} {result['status']} | Score: {score:.2f} | Duration: {duration:.1f}s")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = RESULTS_DIR / f"results_{timestamp}.json"

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(results),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] != "success"),
        "results": results,
    }

    with open(results_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*60}")
    print(f"RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"Total: {summary['total_tests']}")
    print(f"Successful: {summary['successful']} ({summary['successful']/summary['total_tests']*100:.1f}%)")
    print(f"Failed: {summary['failed']}")
    print(f"Results saved to: {results_file}")
    print(f"{'='*60}\n")

    return summary


if __name__ == "__main__":
    # Parse command line args
    if len(sys.argv) > 1:
        # Run specific priority level
        priority = sys.argv[1].upper()
        configs = {k: v for k, v in TEST_CONFIGS.items() if k.startswith(priority)}
        if configs:
            run_all_tests(configs)
        else:
            print(f"No configs found for priority: {priority}")
    else:
        # Run P1 tests by default
        p1_configs = {k: v for k, v in TEST_CONFIGS.items() if k.startswith("P1")}
        run_all_tests(p1_configs)
```

**Step 2: Create test documentation**

Create `docs/ROOFS_QUALITY_TEST.md` with test matrix documentation.

**Step 3: Run P1 tests**

```bash
cd /home/astre/command-center/testhome/testhome-visualizer
source venv/bin/activate
python media/test_houses/comprehensive_test.py P1
```

**Step 4: Verify results**

```bash
cat media/test_houses/comprehensive_results/results_*.json | head -50
```

**Success Criteria:**
- [ ] Test script runs without errors
- [ ] P1 tests complete (5 configs x 3 images = 15 tests)
- [ ] Success rate >= 90%
- [ ] Results saved to JSON file

---

## Task 3: Source & Download Windows Test Images

**Files:**
- Create: `media/test_windows/` directory

**Step 1: Create test directory structure**

```bash
mkdir -p /home/astre/command-center/testhome/testhome-visualizer/media/test_windows/comprehensive_results
```

**Step 2: Search and download house front images**

Search for images using these criteria:
- "house front view windows" - Homes showing clear window layout
- "residential home exterior" - Various architectural styles with visible windows
- "home facade" - Good for replacement visualization
- Need 15-20 diverse images

**Step 3: Save images**

Save as `window_house_01.jpg`, `window_house_02.jpg`, etc.

**Success Criteria:**
- [ ] 15+ house front images downloaded
- [ ] Images show clear window arrangements
- [ ] Diverse house styles

---

## Task 4: Create Windows Test Framework & Run Tests

**Files:**
- Create: `media/test_windows/comprehensive_test.py`
- Create: `docs/WINDOWS_QUALITY_TEST.md`

**Step 1: Create test configuration**

Similar to roofs, but with windows-specific TEST_CONFIGS:

```python
TEST_CONFIGS = {
    # Priority 1: Most Popular (5 configs)
    "P1-01": {
        "name": "Double Hung Vinyl White",
        "scope": {
            "project_type": "replace_existing",
            "window_type": "double_hung",
            "window_style": "modern",
            "frame_material": "vinyl",
            "frame_color": "white",
            "grille_pattern": "none",
            "glass_option": "clear",
            "door_type": "none",
            "trim_style": "standard",
            "enclosure_type": "none",
        }
    },
    "P1-02": {
        "name": "Casement Vinyl + Colonial Grilles",
        "scope": {
            "project_type": "replace_existing",
            "window_type": "casement",
            "window_style": "traditional",
            "frame_material": "vinyl",
            "frame_color": "white",
            "grille_pattern": "colonial",
            "glass_option": "low_e",
            "door_type": "none",
            "trim_style": "colonial",
            "enclosure_type": "none",
        }
    },
    "P1-03": {
        "name": "Double Hung + Sliding Door",
        "scope": {
            "project_type": "replace_existing",
            "window_type": "double_hung",
            "window_style": "modern",
            "frame_material": "vinyl",
            "frame_color": "white",
            "grille_pattern": "none",
            "glass_option": "clear",
            "door_type": "sliding_glass",
            "trim_style": "standard",
            "enclosure_type": "none",
        }
    },
    "P1-04": {
        "name": "Picture Window + French Door",
        "scope": {
            "project_type": "replace_existing",
            "window_type": "picture",
            "window_style": "traditional",
            "frame_material": "wood",
            "frame_color": "brown",
            "grille_pattern": "none",
            "glass_option": "clear",
            "door_type": "french",
            "trim_style": "craftsman",
            "enclosure_type": "none",
        }
    },
    "P1-05": {
        "name": "Three-Season Sunroom",
        "scope": {
            "project_type": "enclose_patio",
            "window_type": "double_hung",
            "window_style": "modern",
            "frame_material": "vinyl",
            "frame_color": "white",
            "grille_pattern": "none",
            "glass_option": "clear",
            "door_type": "sliding_glass",
            "trim_style": "standard",
            "enclosure_type": "three_season",
            "enclosure_glass_type": "single_pane",
        }
    },

    # Priority 2: Premium Options (4 configs)
    "P2-01": {
        "name": "Accordion Door System",
        "scope": {
            "project_type": "enclose_patio",
            "window_type": "double_hung",
            "window_style": "modern",
            "frame_material": "aluminum",
            "frame_color": "black",
            "grille_pattern": "none",
            "glass_option": "clear",
            "door_type": "accordion",
            "trim_style": "modern",
            "enclosure_type": "none",
        }
    },
    "P2-02": {
        "name": "Bi-Fold Door + Modern",
        "scope": {
            "project_type": "replace_existing",
            "window_type": "slider",
            "window_style": "modern",
            "frame_material": "aluminum",
            "frame_color": "black",
            "grille_pattern": "none",
            "glass_option": "clear",
            "door_type": "bifold",
            "trim_style": "modern",
            "enclosure_type": "none",
        }
    },
    "P2-03": {
        "name": "Four-Season Sunroom",
        "scope": {
            "project_type": "enclose_patio",
            "window_type": "casement",
            "window_style": "modern",
            "frame_material": "fiberglass",
            "frame_color": "white",
            "grille_pattern": "none",
            "glass_option": "low_e",
            "door_type": "sliding_glass",
            "trim_style": "standard",
            "enclosure_type": "four_season",
            "enclosure_glass_type": "low_e_double",
        }
    },
    "P2-04": {
        "name": "Retractable Glass Walls",
        "scope": {
            "project_type": "enclose_patio",
            "window_type": "picture",
            "window_style": "modern",
            "frame_material": "aluminum",
            "frame_color": "black",
            "grille_pattern": "none",
            "glass_option": "clear",
            "door_type": "none",
            "trim_style": "modern",
            "enclosure_type": "glass_walls",
            "enclosure_glass_type": "double_pane",
        }
    },
}
```

**Step 2: Run P1 tests**

```bash
python media/test_windows/comprehensive_test.py P1
```

**Success Criteria:**
- [ ] Test script runs without errors
- [ ] P1 tests complete
- [ ] Success rate >= 90%

---

## Task 5: Source & Download Screens Test Images

**Files:**
- Create: `media/test_patios/` directory

**Step 1: Create test directory structure**

```bash
mkdir -p /home/astre/command-center/testhome/testhome-visualizer/media/test_patios/comprehensive_results
```

**Step 2: Search and download patio/porch images**

Search for images:
- "open patio porch" - Patios ready for enclosure
- "covered patio no screens" - Good for screen visualization
- "home porch exterior" - Various styles
- Need 10-15 images (screens has fewer options)

**Step 3: Save images**

Save as `patio_01.jpg`, `patio_02.jpg`, etc.

**Success Criteria:**
- [ ] 10+ patio images downloaded
- [ ] Images show open patios/porches suitable for enclosure
- [ ] Diverse styles

---

## Task 6: Create Screens Test Framework & Run Tests

**Files:**
- Create: `media/test_patios/comprehensive_test.py`
- Create: `docs/SCREENS_QUALITY_TEST.md`

**Step 1: Create test configuration**

```python
TEST_CONFIGS = {
    # Priority 1: Core Use Cases (3 configs)
    "P1-01": {
        "name": "Patio Enclosure Black",
        "scope": {
            "patio": True,
            "windows": False,
            "doors": False,
            "mesh_type": "12x12_standard",
            "frame_color": "black",
            "mesh_color": "black",
        }
    },
    "P1-02": {
        "name": "Patio + Entry Door",
        "scope": {
            "patio": True,
            "windows": False,
            "doors": True,
            "mesh_type": "12x12_standard",
            "frame_color": "black",
            "mesh_color": "black",
        }
    },
    "P1-03": {
        "name": "Full Coverage - All Features",
        "scope": {
            "patio": True,
            "windows": True,
            "doors": True,
            "mesh_type": "12x12_american",
            "frame_color": "dark_bronze",
            "mesh_color": "bronze",
        }
    },

    # Priority 2: Variations (3 configs)
    "P2-01": {
        "name": "Window Screens Only",
        "scope": {
            "patio": False,
            "windows": True,
            "doors": False,
            "mesh_type": "10x10_standard",
            "frame_color": "white",
            "mesh_color": "black",
        }
    },
    "P2-02": {
        "name": "Stucco Frame",
        "scope": {
            "patio": True,
            "windows": False,
            "doors": True,
            "mesh_type": "12x12_standard",
            "frame_color": "stucco",
            "mesh_color": "stucco",
        }
    },
    "P2-03": {
        "name": "Almond Frames",
        "scope": {
            "patio": True,
            "windows": True,
            "doors": True,
            "mesh_type": "12x12_standard",
            "frame_color": "almond",
            "mesh_color": "black",
        }
    },
}
```

**Step 2: Run P1 tests**

```bash
python media/test_patios/comprehensive_test.py P1
```

**Success Criteria:**
- [ ] Test script runs without errors
- [ ] P1 tests complete
- [ ] Success rate >= 90%

---

## Task 7: Manual Quality Evaluation (All Verticals)

**Files:**
- Review: Generated images in `media/generated/` per tenant

**Step 1: Collect all generated images**

For each vertical, identify all generated images from test results.

**Step 2: Manual evaluation criteria**

For each image, evaluate on 1-10 scale:

| Criterion | Description |
|-----------|-------------|
| Material Realism | Does material look authentic? |
| Placement | Is feature in correct position? |
| Integration | Does it look installed vs. pasted? |
| Preservation | Is rest of image unchanged? |
| Overall Quality | Sales-ready visualization? |

**Step 3: Document findings**

Note any patterns:
- Which configurations produce best results?
- Which image types work best?
- Any common failure modes?

**Success Criteria:**
- [ ] All P1 generated images reviewed
- [ ] At least 12 images manually scored per vertical
- [ ] Average score >= 8.5/10 per vertical

---

## Task 8: Generate Quality Reports

**Files:**
- Create: `docs/ROOFS_QUALITY_EVALUATION_REPORT.md`
- Create: `docs/WINDOWS_QUALITY_EVALUATION_REPORT.md`
- Create: `docs/SCREENS_QUALITY_EVALUATION_REPORT.md`

**Step 1: Create report template**

For each vertical, document:
- Test summary (total tests, success rate)
- Manual evaluation results (average scores)
- Best configurations (highest quality)
- Issues identified
- Recommendations

**Step 2: Final summary**

Create overall production readiness assessment across all verticals.

**Success Criteria:**
- [ ] Quality report created for each vertical
- [ ] Production readiness % documented
- [ ] Recommendations for any issues

---

## Completion Checklist

- [ ] Task 1: Roofs test images sourced (15+ images)
- [ ] Task 2: Roofs tests completed (90%+ success)
- [ ] Task 3: Windows test images sourced (15+ images)
- [ ] Task 4: Windows tests completed (90%+ success)
- [ ] Task 5: Screens test images sourced (10+ images)
- [ ] Task 6: Screens tests completed (90%+ success)
- [ ] Task 7: Manual evaluation complete (8.5+ average)
- [ ] Task 8: Quality reports generated

**Overall Goal:** All 4 verticals at 95% production readiness
