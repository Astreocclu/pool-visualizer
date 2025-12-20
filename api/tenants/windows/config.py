"""
Windows Vertical Configuration
Port: 8003
Pipeline: cleanup → window_frame → grilles_glass → trim → quality_check
"""
from api.tenants.base import BaseTenantConfig

VERTICAL_NAME = "windows"
VERTICAL_DISPLAY_NAME = "Window Replacement"

WINDOW_TYPES = [
    {
        'id': 'single_hung',
        'name': 'Single Hung',
        'prompt_hint': 'single hung window with bottom sash that opens',
        'description': 'Classic style with bottom sash that opens vertically',
    },
    {
        'id': 'double_hung',
        'name': 'Double Hung',
        'prompt_hint': 'double hung window with both sashes that open',
        'description': 'Both top and bottom sashes open for ventilation',
        'popular': True,
    },
    {
        'id': 'casement',
        'name': 'Casement',
        'prompt_hint': 'casement window that opens outward on hinges',
        'description': 'Hinged window that opens outward with crank handle',
    },
    {
        'id': 'slider',
        'name': 'Slider',
        'prompt_hint': 'horizontal sliding window',
        'description': 'Slides horizontally, ideal for wide openings',
    },
    {
        'id': 'picture',
        'name': 'Picture',
        'prompt_hint': 'large fixed picture window',
        'description': 'Large fixed window for maximum light and views',
    },
]

WINDOW_STYLES = [
    {'id': 'modern', 'name': 'Modern', 'prompt_hint': 'modern contemporary style'},
    {'id': 'traditional', 'name': 'Traditional', 'prompt_hint': 'traditional classic style'},
    {'id': 'colonial', 'name': 'Colonial', 'prompt_hint': 'colonial style with divided lites'},
    {'id': 'craftsman', 'name': 'Craftsman', 'prompt_hint': 'craftsman style with clean lines'},
]

FRAME_MATERIALS = [
    {
        'id': 'vinyl',
        'name': 'Vinyl',
        'price_multiplier': 1.0,
        'prompt_hint': 'vinyl frame material',
        'description': 'Low-maintenance, energy-efficient, affordable',
        'popular': True,
    },
    {
        'id': 'wood',
        'name': 'Wood',
        'price_multiplier': 1.5,
        'prompt_hint': 'natural wood frame material',
        'description': 'Classic beauty, excellent insulation, requires maintenance',
    },
    {
        'id': 'fiberglass',
        'name': 'Fiberglass',
        'price_multiplier': 1.3,
        'prompt_hint': 'fiberglass frame material',
        'description': 'Extremely durable, low-maintenance, premium option',
    },
    {
        'id': 'aluminum',
        'name': 'Aluminum',
        'price_multiplier': 1.2,
        'prompt_hint': 'aluminum frame material',
        'description': 'Sleek modern look, strong and durable',
    },
]

FRAME_COLORS = [
    {'id': 'white', 'name': 'White', 'prompt_hint': 'white frame'},
    {'id': 'tan', 'name': 'Tan', 'prompt_hint': 'tan/beige frame'},
    {'id': 'brown', 'name': 'Brown', 'prompt_hint': 'brown frame'},
    {'id': 'black', 'name': 'Black', 'prompt_hint': 'black frame'},
    {'id': 'bronze', 'name': 'Bronze', 'prompt_hint': 'bronze frame'},
]

GRILLE_PATTERNS = [
    {
        'id': 'none',
        'name': 'No Grilles',
        'prompt_hint': 'no grilles, clean glass',
        'description': 'Clean, unobstructed view',
    },
    {
        'id': 'colonial',
        'name': 'Colonial',
        'prompt_hint': 'colonial grille pattern with divided lites',
        'description': 'Classic grid pattern, traditional look',
        'popular': True,
    },
    {
        'id': 'prairie',
        'name': 'Prairie',
        'prompt_hint': 'prairie style grilles with perimeter pattern',
        'description': 'Perimeter pattern with clean center',
    },
    {
        'id': 'craftsman',
        'name': 'Craftsman',
        'prompt_hint': 'craftsman style grilles',
        'description': 'Top section divided, bottom open',
    },
    {
        'id': 'diamond',
        'name': 'Diamond',
        'prompt_hint': 'diamond pattern grilles',
        'description': 'Elegant diamond pattern',
    },
]

GLASS_OPTIONS = [
    {
        'id': 'clear',
        'name': 'Clear',
        'prompt_hint': 'clear glass',
        'description': 'Standard clear glass for maximum visibility',
        'popular': True,
    },
    {
        'id': 'low_e',
        'name': 'Low-E',
        'prompt_hint': 'low-E energy efficient glass',
        'description': 'Energy-efficient coating for temperature control',
    },
    {
        'id': 'frosted',
        'name': 'Frosted',
        'prompt_hint': 'frosted privacy glass',
        'description': 'Privacy glass with light transmission',
    },
    {
        'id': 'obscure',
        'name': 'Obscure',
        'prompt_hint': 'obscure textured glass',
        'description': 'Textured glass for privacy',
    },
    {
        'id': 'rain',
        'name': 'Rain Glass',
        'prompt_hint': 'rain glass texture',
        'description': 'Water-like texture for privacy and style',
    },
]

HARDWARE_STYLES = [
    {'id': 'standard', 'name': 'Standard', 'prompt_hint': 'standard hardware'},
    {'id': 'modern', 'name': 'Modern', 'prompt_hint': 'modern contemporary hardware'},
    {'id': 'classic', 'name': 'Classic', 'prompt_hint': 'classic traditional hardware'},
]

HARDWARE_FINISHES = [
    {'id': 'white', 'name': 'White', 'prompt_hint': 'white finish'},
    {'id': 'brushed_nickel', 'name': 'Brushed Nickel', 'prompt_hint': 'brushed nickel finish'},
    {'id': 'oil_rubbed_bronze', 'name': 'Oil Rubbed Bronze', 'prompt_hint': 'oil rubbed bronze finish'},
    {'id': 'brass', 'name': 'Brass', 'prompt_hint': 'brass finish'},
]

TRIM_STYLES = [
    {'id': 'standard', 'name': 'Standard', 'prompt_hint': 'standard trim'},
    {'id': 'craftsman', 'name': 'Craftsman', 'prompt_hint': 'craftsman style trim'},
    {'id': 'colonial', 'name': 'Colonial', 'prompt_hint': 'colonial style trim'},
    {'id': 'modern', 'name': 'Modern', 'prompt_hint': 'modern minimal trim'},
]

PIPELINE_STEPS = ['cleanup', 'window_frame', 'grilles_glass', 'trim', 'quality_check']

PRIMARY_COLOR = "#2E7D32"  # Forest Green
SECONDARY_COLOR = "#66BB6A"


class WindowsTenantConfig(BaseTenantConfig):
    """Windows vertical tenant configuration."""

    tenant_id = 'windows'
    display_name = VERTICAL_DISPLAY_NAME

    def get_pipeline_steps(self):
        return PIPELINE_STEPS

    def get_step_config(self, step_name):
        configs = {
            'cleanup': {'type': 'cleanup', 'progress_weight': 20, 'description': 'Preparing image'},
            'window_frame': {'type': 'insertion', 'scope_key': None, 'feature_name': 'window', 'progress_weight': 40, 'description': 'Installing window frame'},
            'grilles_glass': {'type': 'insertion', 'scope_key': 'grilles_glass', 'feature_name': 'grilles_glass', 'progress_weight': 20, 'description': 'Adding grilles and glass'},
            'trim': {'type': 'insertion', 'scope_key': 'trim', 'feature_name': 'trim', 'progress_weight': 15, 'description': 'Installing trim'},
            'quality_check': {'type': 'quality_check', 'progress_weight': 5, 'description': 'Quality check'},
        }
        return configs.get(step_name, {})

    def get_prompts_module(self):
        from api.tenants.windows import prompts
        return prompts

    def get_schema(self):
        return get_config()

    def get_mesh_choices(self):
        return []  # Not applicable to windows

    def get_frame_color_choices(self):
        return [(color['id'], color['name']) for color in FRAME_COLORS]

    def get_mesh_color_choices(self):
        return []  # Not applicable to windows

    def get_opacity_choices(self):
        return []  # Not applicable to windows


def get_config():
    """Return config dict for API responses. Excludes pricing data."""
    return {
        'name': VERTICAL_NAME,
        'display_name': VERTICAL_DISPLAY_NAME,
        'window_types': WINDOW_TYPES,
        'window_styles': WINDOW_STYLES,
        'frame_materials': [
            {k: v for k, v in mat.items() if k != 'price_multiplier'}
            for mat in FRAME_MATERIALS
        ],
        'frame_colors': FRAME_COLORS,
        'grille_patterns': GRILLE_PATTERNS,
        'glass_options': GLASS_OPTIONS,
        'hardware_styles': HARDWARE_STYLES,
        'hardware_finishes': HARDWARE_FINISHES,
        'trim_styles': TRIM_STYLES,
        'pipeline_steps': PIPELINE_STEPS,
        'primary_color': PRIMARY_COLOR,
        'secondary_color': SECONDARY_COLOR,
    }


def get_full_config_with_pricing():
    """Return full config including pricing. For internal/admin use only."""
    return {
        'name': VERTICAL_NAME,
        'display_name': VERTICAL_DISPLAY_NAME,
        'window_types': WINDOW_TYPES,
        'window_styles': WINDOW_STYLES,
        'frame_materials': FRAME_MATERIALS,
        'frame_colors': FRAME_COLORS,
        'grille_patterns': GRILLE_PATTERNS,
        'glass_options': GLASS_OPTIONS,
        'hardware_styles': HARDWARE_STYLES,
        'hardware_finishes': HARDWARE_FINISHES,
        'trim_styles': TRIM_STYLES,
        'pipeline_steps': PIPELINE_STEPS,
    }
