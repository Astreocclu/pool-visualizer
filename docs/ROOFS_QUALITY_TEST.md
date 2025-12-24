# Roofs Quality Test Matrix

## Overview

This document describes the comprehensive quality testing framework for the roofs vertical in the testhome-visualizer application.

**Test Script:** `/media/test_houses/comprehensive_test.py`

**Test Images:** 3 representative house exterior images from `/media/test_houses/`
- `house_01.jpg` - Representative house style 1
- `house_07.jpg` - Representative house style 2
- `house_15.jpg` - Representative house style 3

**Total P1 Tests:** 5 configurations × 3 images = 15 tests

---

## Test Configuration Matrix

### Priority 1: Most Popular Combinations (5 configs)

These represent the most common roofing projects we expect to visualize.

| Test ID | Configuration Name | Roof Material | Roof Color | Solar | Gutters | Use Case |
|---------|-------------------|---------------|------------|-------|---------|----------|
| P1-01 | Asphalt Architectural Charcoal | asphalt_architectural | charcoal | none | standard | Most common residential roof |
| P1-02 | Metal Standing Seam Black | metal_standing_seam | black | none | seamless | Modern/premium metal roof |
| P1-03 | Clay Tile Terracotta | clay_tile | terracotta | none | standard | Mediterranean/Spanish style |
| P1-04 | Asphalt with Solar | asphalt_architectural | charcoal | partial | standard | Solar integration test |
| P1-05 | Metal with Full Solar | metal_standing_seam | slate_gray | full_south | seamless | Maximum solar coverage |

### Priority 2: Premium Materials (4 configs)

These test premium roofing options for high-end projects.

| Test ID | Configuration Name | Roof Material | Roof Color | Solar | Gutters | Use Case |
|---------|-------------------|---------------|------------|-------|---------|----------|
| P2-01 | Concrete Tile Brown | concrete_tile | brown | none | standard | Durable tile option |
| P2-02 | Natural Slate Gray | slate | slate_gray | none | copper | Premium natural slate |
| P2-03 | Wood Shake Brown | wood_shake | weathered_wood | none | standard | Traditional wood shake |
| P2-04 | Metal Corrugated Green | metal_corrugated | green | none | standard | Agricultural/barn style |

---

## API Scope Fields

The roofs tenant uses these scope fields:

```python
{
    "roof_material": str,    # Material type
    "roof_color": str,       # Color option
    "solar_option": str,     # Solar panel coverage
    "gutter_option": str,    # Gutter type
}
```

### Valid Options

**Roof Materials:**
- `asphalt_architectural` - Standard architectural shingles
- `metal_standing_seam` - Vertical seam metal roofing
- `clay_tile` - Traditional clay tiles
- `concrete_tile` - Concrete tile alternative
- `slate` - Natural slate
- `wood_shake` - Wood shake shingles
- `metal_corrugated` - Corrugated metal panels

**Roof Colors:**
- `charcoal` - Dark gray/black
- `black` - True black
- `brown` - Earthy brown
- `terracotta` - Orange/red clay color
- `slate_gray` - Medium gray
- `weathered_wood` - Natural wood tone
- `green` - Forest/barn green

**Solar Options:**
- `none` - No solar panels
- `partial` - Partial coverage (south-facing section)
- `full_south` - Full south-facing roof coverage

**Gutter Options:**
- `none` - No gutters
- `standard` - Standard aluminum gutters
- `seamless` - Seamless gutters
- `copper` - Premium copper gutters

---

## Running Tests

### Run P1 Tests Only (Default)
```bash
cd /home/astre/command-center/testhome/testhome-visualizer
source venv/bin/activate
python media/test_houses/comprehensive_test.py
# or explicitly:
python media/test_houses/comprehensive_test.py P1
```

### Run P2 Tests Only
```bash
python media/test_houses/comprehensive_test.py P2
```

### Run All Tests
```bash
# Run P1 then P2 separately or modify script to run both
python media/test_houses/comprehensive_test.py P1
python media/test_houses/comprehensive_test.py P2
```

---

## Test Results

Results are saved to: `/media/test_houses/comprehensive_results/results_YYYYMMDD_HHMMSS.json`

### Result Format

```json
{
  "timestamp": "2025-12-24T19:30:00",
  "total_tests": 15,
  "successful": 14,
  "failed": 1,
  "results": [
    {
      "test_id": "P1-01",
      "config_name": "Asphalt Architectural Charcoal",
      "image": "house_01.jpg",
      "status": "success",
      "quality_score": 8.5,
      "duration_seconds": 45.2,
      "result_id": 123,
      "result_image": "/media/generated/roofs/123_generated.jpg"
    }
  ]
}
```

---

## Success Criteria

### Automated Criteria
- **Success Rate:** >= 90% (14+ out of 15 P1 tests)
- **Average Quality Score:** >= 8.0
- **Processing Time:** < 60 seconds per image

### Manual Evaluation Criteria

For each generated image, evaluate on 1-10 scale:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Material Realism | 25% | Does the roof material look authentic and photorealistic? |
| Color Accuracy | 20% | Is the color correctly applied and consistent? |
| Placement | 20% | Are roof elements (shingles, tiles, panels) correctly positioned? |
| Integration | 20% | Does the new roof look naturally installed vs. digitally pasted? |
| Preservation | 15% | Is the rest of the house (walls, windows, landscaping) unchanged? |

**Overall Target:** Average manual score >= 8.5/10

---

## Common Issues & Troubleshooting

### Test Image Issues
- **Missing Images:** Ensure Task 1 (downloading test images) is completed
- **Wrong Format:** Images must be JPEG format
- **File Size:** Keep images under 10MB for best performance

### API Issues
- **Django Server Not Running:** Start with `python manage.py runserver 8000`
- **Authentication Failed:** Check that test user registration is working
- **Timeout Errors:** Increase `max_wait` in script if needed

### Quality Issues
- **Low Quality Scores:** Review AI prompts in `/api/tenants/roofs/prompts.py`
- **Incorrect Material:** Check material reference images in `/media/reference_images/roofs/`
- **Poor Integration:** May need to adjust blending parameters

---

## Next Steps After Testing

1. **Review Results:** Analyze JSON output for patterns
2. **Manual Review:** Visually inspect all generated images
3. **Document Issues:** Note any systematic failures
4. **Iterate Prompts:** Adjust AI prompts based on findings
5. **Re-test:** Run tests again after improvements
6. **Production Readiness:** Document final readiness assessment

---

## Related Documentation

- [Comprehensive Vertical Testing Plan](./plans/2025-12-24-comprehensive-vertical-testing.md)
- [Pools Quality Test](../media/test_backyards/comprehensive_test.py) - Working reference implementation
- [Roofs Tenant Config](/api/tenants/roofs/config.py)
- [Roofs AI Prompts](/api/tenants/roofs/prompts.py)
