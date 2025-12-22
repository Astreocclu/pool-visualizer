"""
Roofs Vertical Configuration
Port: 8008
Pipeline: cleanup → roof_material → solar_panels → gutters_trim → quality_check
"""
from api.tenants.base import BaseTenantConfig

VERTICAL_NAME = "roofs"
VERTICAL_DISPLAY_NAME = "Roofs & Solar"

ROOF_MATERIALS = [
    {'id': 'asphalt_3tab', 'name': 'Asphalt - 3-Tab', 'price_per_sqft': 3.50, 'prompt_hint': 'traditional 3-tab asphalt shingles', 'description': 'Affordable, classic look, 15-20 year lifespan'},
    {'id': 'asphalt_architectural', 'name': 'Asphalt - Architectural', 'price_per_sqft': 4.75, 'prompt_hint': 'dimensional architectural asphalt shingles with shadow lines', 'description': 'Premium look, 30 year lifespan', 'popular': True},
    {'id': 'metal_standing_seam', 'name': 'Metal - Standing Seam', 'price_per_sqft': 9.50, 'prompt_hint': 'standing seam metal roof with vertical ribs', 'description': 'Modern, durable, 50+ year lifespan', 'popular': True},
    {'id': 'metal_corrugated', 'name': 'Metal - Corrugated', 'price_per_sqft': 6.50, 'prompt_hint': 'corrugated metal roofing panels', 'description': 'Industrial/farmhouse look, 40+ year lifespan'},
    {'id': 'clay_tile', 'name': 'Clay Tile', 'price_per_sqft': 15.00, 'prompt_hint': 'traditional barrel clay roof tiles', 'description': 'Mediterranean style, 100+ year lifespan'},
    {'id': 'concrete_tile', 'name': 'Concrete Tile', 'price_per_sqft': 10.50, 'prompt_hint': 'flat or curved concrete roof tiles', 'description': 'Durable, fire-resistant, 50+ year lifespan'},
    {'id': 'slate', 'name': 'Natural Slate', 'price_per_sqft': 22.00, 'prompt_hint': 'natural slate roofing tiles', 'description': 'Premium natural stone, 100+ year lifespan'},
    {'id': 'wood_shake', 'name': 'Wood Shake', 'price_per_sqft': 12.50, 'prompt_hint': 'cedar wood shake shingles', 'description': 'Rustic natural look, 30 year lifespan'},
    {'id': 'tpo_flat', 'name': 'TPO (Flat Roof)', 'price_per_sqft': 5.50, 'prompt_hint': 'white TPO membrane flat roof', 'description': 'For flat/low-slope roofs, 20-30 year lifespan'},
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
    {'id': 'none', 'name': 'No Solar', 'prompt_hint': '', 'description': 'Roof only, no solar panels'},
    {'id': 'partial', 'name': 'Partial Coverage', 'prompt_hint': 'solar panel array covering approximately 30% of south-facing roof', 'description': 'Solar panels on part of the roof', 'popular': True},
    {'id': 'full_south', 'name': 'Full South Roof', 'prompt_hint': 'solar panel array covering entire south-facing roof plane', 'description': 'Maximize solar on south-facing roof'},
    {'id': 'full_all', 'name': 'Maximum Coverage', 'prompt_hint': 'solar panel arrays covering all suitable roof planes', 'description': 'Solar panels on all viable roof areas'},
]

GUTTER_OPTIONS = [
    {'id': 'none', 'name': 'No Gutters', 'prompt_hint': '', 'description': 'No gutter system'},
    {'id': 'standard', 'name': 'Standard Gutters', 'prompt_hint': 'K-style aluminum gutters with downspouts', 'description': 'Standard aluminum gutter system', 'popular': True},
    {'id': 'seamless', 'name': 'Seamless Gutters', 'prompt_hint': 'seamless aluminum gutters with downspouts', 'description': 'Premium seamless gutter system'},
    {'id': 'copper', 'name': 'Copper Gutters', 'prompt_hint': 'copper half-round gutters with copper downspouts', 'description': 'Premium copper gutter system'},
]

PIPELINE_STEPS = ['cleanup', 'roof_material', 'solar_panels', 'gutters_trim', 'quality_check']
PRIMARY_COLOR = "#D84315"
SECONDARY_COLOR = "#FF7043"


class RoofsTenantConfig(BaseTenantConfig):
    tenant_id = 'roofs'
    display_name = VERTICAL_DISPLAY_NAME
    supports_reference_images = True

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
    return {
        'name': VERTICAL_NAME,
        'display_name': VERTICAL_DISPLAY_NAME,
        'roof_materials': [{k: v for k, v in mat.items() if k != 'price_per_sqft'} for mat in ROOF_MATERIALS],
        'roof_colors': ROOF_COLORS,
        'solar_options': SOLAR_OPTIONS,
        'gutter_options': GUTTER_OPTIONS,
        'pipeline_steps': PIPELINE_STEPS,
        'primary_color': PRIMARY_COLOR,
        'secondary_color': SECONDARY_COLOR,
    }


def get_full_config_with_pricing():
    return {
        'name': VERTICAL_NAME,
        'display_name': VERTICAL_DISPLAY_NAME,
        'roof_materials': ROOF_MATERIALS,
        'roof_colors': ROOF_COLORS,
        'solar_options': SOLAR_OPTIONS,
        'gutter_options': GUTTER_OPTIONS,
        'pipeline_steps': PIPELINE_STEPS,
    }
