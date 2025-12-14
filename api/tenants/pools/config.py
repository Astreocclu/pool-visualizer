"""
Pools Vertical Configuration
Port: 8006
Pipeline: cleanup → pool_shell → deck → water_features → finishing → quality_check
"""
from api.tenants.base import BaseTenantConfig

VERTICAL_NAME = "pools"
VERTICAL_DISPLAY_NAME = "Swimming Pools"

POOL_SIZES = [
    {
        'id': 'starter',
        'name': 'Starter',
        'dimensions': '12x24',
        'length_ft': 24,
        'width_ft': 12,
        'sq_ft': 288,
        'gallons': 10800,
        'base_price': 50000,
        'prompt_hint': 'compact pool approximately 12 by 24 feet',
        'description': 'Best for: Small yards, couples, plunge pools',
    },
    {
        'id': 'classic',
        'name': 'Classic',
        'dimensions': '15x30',
        'length_ft': 30,
        'width_ft': 15,
        'sq_ft': 450,
        'gallons': 16875,
        'base_price': 65000,
        'prompt_hint': 'medium-sized pool approximately 15 by 30 feet',
        'description': 'Best for: Average yards, families',
        'popular': True,
    },
    {
        'id': 'family',
        'name': 'Family',
        'dimensions': '16x36',
        'length_ft': 36,
        'width_ft': 16,
        'sq_ft': 576,
        'gallons': 21600,
        'base_price': 75000,
        'prompt_hint': 'large family pool approximately 16 by 36 feet',
        'description': 'Best for: Larger yards, kids, entertaining',
    },
    {
        'id': 'resort',
        'name': 'Resort',
        'dimensions': '18x40',
        'length_ft': 40,
        'width_ft': 18,
        'sq_ft': 720,
        'gallons': 27000,
        'base_price': 95000,
        'prompt_hint': 'large resort-style pool approximately 18 by 40 feet',
        'description': 'Best for: Large properties, serious swimmers',
    },
]

POOL_SHAPES = [
    {'id': 'rectangle', 'name': 'Rectangle', 'price_multiplier': 1.0, 'prompt_hint': 'rectangular'},
    {'id': 'roman', 'name': 'Roman', 'price_multiplier': 1.05, 'prompt_hint': 'roman-style with rounded ends'},
    {'id': 'grecian', 'name': 'Grecian', 'price_multiplier': 1.05, 'prompt_hint': 'grecian-style with cut corners'},
    {'id': 'kidney', 'name': 'Kidney', 'price_multiplier': 1.10, 'prompt_hint': 'kidney-shaped with organic curves'},
    {'id': 'freeform', 'name': 'Freeform', 'price_multiplier': 1.15, 'prompt_hint': 'freeform natural lagoon shape'},
    {'id': 'lazy_l', 'name': 'Lazy L', 'price_multiplier': 1.10, 'prompt_hint': 'L-shaped with extended shallow area'},
    {'id': 'oval', 'name': 'Oval', 'price_multiplier': 1.05, 'prompt_hint': 'oval-shaped'},
]

INTERIOR_FINISHES = [
    {'id': 'white_plaster', 'name': 'White Plaster', 'water_color': 'light turquoise/aqua', 'price_add': 0, 'prompt_hint': 'smooth white plaster finish creating light turquoise water'},
    {'id': 'pebble_blue', 'name': 'Pebble Tec - Blue', 'water_color': 'deep ocean blue', 'price_add': 8000, 'prompt_hint': 'textured pebble finish with deep ocean blue water', 'popular': True},
    {'id': 'pebble_midnight', 'name': 'Pebble Tec - Midnight', 'water_color': 'dark navy/black', 'price_add': 9000, 'prompt_hint': 'dark pebble finish with deep midnight blue water'},
    {'id': 'quartz_blue', 'name': 'Quartz - Ocean Blue', 'water_color': 'vibrant blue', 'price_add': 6000, 'prompt_hint': 'sparkling quartz aggregate with vibrant blue water'},
    {'id': 'quartz_aqua', 'name': 'Quartz - Caribbean', 'water_color': 'bright Caribbean aqua', 'price_add': 6000, 'prompt_hint': 'sparkling quartz aggregate with bright Caribbean aqua water'},
    {'id': 'glass_tile', 'name': 'Glass Tile', 'water_color': 'crystal clear with shimmer', 'price_add': 15000, 'prompt_hint': 'shimmering glass tile with crystal clear sparkling water'},
]

BUILT_IN_FEATURES = {
    'tanning_ledge': {
        'name': 'Tanning Ledge (Baja Shelf)',
        'description': 'Shallow 4-6 inch area for lounging in the water',
        'price_add': 4500,
        'prompt_hint': 'a tanning ledge (Baja shelf) with 4-6 inches of water',
        'default': True,
    },
    'ledge_loungers': {
        'name': 'Ledge Loungers',
        'description': 'In-water lounge chairs for the tanning ledge',
        'price_per_unit': 800,
        'options': [0, 2, 4],
        'default': 2,
        'requires': 'tanning_ledge',
        'prompt_hint': '{count} ledge lounger chairs on the tanning ledge',
    },
    'attached_spa': {
        'name': 'Attached Spa (Spillover)',
        'description': 'Hot tub with water spilling into main pool',
        'price_add': 18000,
        'prompt_hint': 'an attached raised spa with water spilling over into the main pool',
        'default': False,
    },
}

DECK_MATERIALS = [
    {'id': 'travertine', 'name': 'Travertine', 'price_per_sqft': 18, 'prompt_hint': 'natural travertine stone', 'popular': True},
    {'id': 'pavers', 'name': 'Pavers', 'price_per_sqft': 14, 'prompt_hint': 'interlocking concrete pavers'},
    {'id': 'brushed_concrete', 'name': 'Brushed Concrete', 'price_per_sqft': 8, 'prompt_hint': 'brushed concrete'},
    {'id': 'stamped_concrete', 'name': 'Stamped Concrete', 'price_per_sqft': 12, 'prompt_hint': 'stamped decorative concrete'},
    {'id': 'flagstone', 'name': 'Flagstone', 'price_per_sqft': 22, 'prompt_hint': 'natural flagstone'},
    {'id': 'wood', 'name': 'Wood Deck', 'price_per_sqft': 25, 'prompt_hint': 'wooden pool deck'},
]

DECK_COLORS = [
    {'id': 'cream', 'name': 'Cream', 'prompt_hint': 'cream-colored'},
    {'id': 'tan', 'name': 'Tan', 'prompt_hint': 'tan/sand-colored'},
    {'id': 'gray', 'name': 'Gray', 'prompt_hint': 'cool gray'},
    {'id': 'terracotta', 'name': 'Terracotta', 'prompt_hint': 'warm terracotta'},
    {'id': 'brown', 'name': 'Brown', 'prompt_hint': 'natural brown'},
    {'id': 'natural', 'name': 'Natural Stone', 'prompt_hint': 'natural stone colors with variation'},
]

WATER_FEATURES = [
    {'id': 'rock_waterfall', 'name': 'Rock Waterfall', 'price_add': 8000, 'prompt_hint': 'a natural stacked stone waterfall cascading into the pool'},
    {'id': 'bubblers', 'name': 'Bubblers / Fountain Jets', 'price_add': 2500, 'prompt_hint': 'bubbler fountain jets creating vertical water streams from the tanning ledge'},
    {'id': 'scuppers', 'name': 'Scuppers', 'price_add': 4500, 'prompt_hint': 'modern rectangular scuppers mounted on a raised wall with sheet water flow'},
    {'id': 'fire_bowls', 'name': 'Fire Bowls', 'price_add': 3500, 'prompt_hint': 'decorative fire bowls on pedestals at the pool edge with flickering flames'},
    {'id': 'deck_jets', 'name': 'Deck Jets', 'price_add': 3000, 'prompt_hint': 'laminar deck jets creating arcing streams of water into the pool'},
]

FINISHING_OPTIONS = {
    'lighting': [
        {'id': 'none', 'name': 'No Additional Lighting', 'prompt_hint': ''},
        {'id': 'pool_lights', 'name': 'LED Pool Lights', 'prompt_hint': 'underwater LED pool lights visible'},
        {'id': 'landscape', 'name': 'Landscape Lighting', 'prompt_hint': 'landscape lighting around the pool area'},
        {'id': 'both', 'name': 'Pool + Landscape Lights', 'prompt_hint': 'underwater LED pool lights and landscape lighting'},
    ],
    'landscaping': [
        {'id': 'none', 'name': 'Existing Only', 'prompt_hint': ''},
        {'id': 'tropical', 'name': 'Tropical Plants', 'prompt_hint': 'tropical landscaping with palms and flowering plants around the pool'},
        {'id': 'desert', 'name': 'Desert/Modern', 'prompt_hint': 'modern desert landscaping with ornamental grasses and succulents'},
        {'id': 'natural', 'name': 'Natural/Native', 'prompt_hint': 'natural native Texas landscaping around the pool'},
    ],
    'furniture': [
        {'id': 'none', 'name': 'No Furniture', 'prompt_hint': ''},
        {'id': 'basic', 'name': 'Lounge Chairs', 'prompt_hint': 'stylish lounge chairs on the pool deck'},
        {'id': 'full', 'name': 'Full Outdoor Set', 'prompt_hint': 'lounge chairs, side tables, and an umbrella on the pool deck'},
    ],
}

PIPELINE_STEPS = ['cleanup', 'pool_shell', 'deck', 'water_features', 'finishing', 'quality_check']

PRIMARY_COLOR = "#0077b6"
SECONDARY_COLOR = "#00b4d8"


class PoolsTenantConfig(BaseTenantConfig):
    """Pools vertical tenant configuration."""

    tenant_id = 'pools'
    display_name = VERTICAL_DISPLAY_NAME

    def get_pipeline_steps(self):
        return PIPELINE_STEPS

    def get_step_config(self, step_name):
        configs = {
            'cleanup': {'type': 'cleanup', 'progress_weight': 20, 'description': 'Preparing image'},
            'pool_shell': {'type': 'insertion', 'scope_key': None, 'feature_name': 'pool', 'progress_weight': 30, 'description': 'Adding pool'},
            'deck': {'type': 'insertion', 'scope_key': None, 'feature_name': 'deck', 'progress_weight': 20, 'description': 'Adding deck'},
            'water_features': {'type': 'insertion', 'scope_key': 'water_features', 'feature_name': 'water_features', 'progress_weight': 15, 'description': 'Adding water features'},
            'finishing': {'type': 'insertion', 'scope_key': 'finishing', 'feature_name': 'finishing', 'progress_weight': 10, 'description': 'Adding finishing touches'},
            'quality_check': {'type': 'quality_check', 'progress_weight': 5, 'description': 'Quality check'},
        }
        return configs.get(step_name, {})

    def get_prompts_module(self):
        from api.tenants.pools import prompts
        return prompts

    def get_schema(self):
        return get_config()

    def get_mesh_choices(self):
        return []  # Not applicable to pools

    def get_frame_color_choices(self):
        return []  # Not applicable to pools

    def get_mesh_color_choices(self):
        return []  # Not applicable to pools

    def get_opacity_choices(self):
        return []  # Not applicable to pools


def get_config():
    """Return config dict for API responses. Excludes pricing data."""
    return {
        'name': VERTICAL_NAME,
        'display_name': VERTICAL_DISPLAY_NAME,
        'pool_sizes': [
            {k: v for k, v in size.items() if k not in ['base_price', 'gallons']}
            for size in POOL_SIZES
        ],
        'pool_shapes': [
            {k: v for k, v in shape.items() if k != 'price_multiplier'}
            for shape in POOL_SHAPES
        ],
        'interior_finishes': [
            {k: v for k, v in finish.items() if k != 'price_add'}
            for finish in INTERIOR_FINISHES
        ],
        'built_in_features': {
            k: {kk: vv for kk, vv in v.items() if 'price' not in kk}
            for k, v in BUILT_IN_FEATURES.items()
        },
        'deck_materials': [
            {k: v for k, v in mat.items() if k != 'price_per_sqft'}
            for mat in DECK_MATERIALS
        ],
        'deck_colors': DECK_COLORS,
        'water_features': [
            {k: v for k, v in feat.items() if k != 'price_add'}
            for feat in WATER_FEATURES
        ],
        'finishing_options': FINISHING_OPTIONS,
        'pipeline_steps': PIPELINE_STEPS,
        'primary_color': PRIMARY_COLOR,
        'secondary_color': SECONDARY_COLOR,
    }


def get_full_config_with_pricing():
    """Return full config including pricing. For internal/admin use only."""
    return {
        'name': VERTICAL_NAME,
        'display_name': VERTICAL_DISPLAY_NAME,
        'pool_sizes': POOL_SIZES,
        'pool_shapes': POOL_SHAPES,
        'interior_finishes': INTERIOR_FINISHES,
        'built_in_features': BUILT_IN_FEATURES,
        'deck_materials': DECK_MATERIALS,
        'deck_colors': DECK_COLORS,
        'water_features': WATER_FEATURES,
        'finishing_options': FINISHING_OPTIONS,
        'pipeline_steps': PIPELINE_STEPS,
    }
