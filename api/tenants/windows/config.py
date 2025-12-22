"""
Windows Vertical Configuration
Port: 8003
Pipeline: cleanup → window_frame → grilles_glass → trim → doors → patio_enclosure → quality_check
"""
from api.tenants.base import BaseTenantConfig

VERTICAL_NAME = "windows"
VERTICAL_DISPLAY_NAME = "Glass Doors & Windows"

PROJECT_TYPES = [
    {
        'id': 'replace_existing',
        'name': 'Replace Existing',
        'prompt_hint': 'replacing existing windows and doors',
        'description': 'Replace current windows and/or doors with new ones',
    },
    {
        'id': 'new_opening',
        'name': 'Create New Opening',
        'prompt_hint': 'creating new window or door openings in walls',
        'description': 'Add new windows or doors where none exist',
    },
    {
        'id': 'enclose_patio',
        'name': 'Enclose Patio',
        'prompt_hint': 'enclosing patio or porch with glass doors and windows',
        'description': 'Convert open patio/porch to enclosed sunroom',
        'popular': True,
    },
]

DOOR_TYPES = [
    {
        'id': 'none',
        'name': 'Windows Only',
        'prompt_hint': '',
        'description': 'No doors, windows only',
    },
    {
        'id': 'sliding_glass',
        'name': 'Sliding Glass Door',
        'prompt_hint': 'sliding glass patio door with large glass panels',
        'description': 'Standard sliding glass door for patio access',
        'popular': True,
        'width_options': ['6ft', '8ft', '12ft'],
    },
    {
        'id': 'french',
        'name': 'French Door',
        'prompt_hint': 'french doors with glass panels and traditional styling',
        'description': 'Classic hinged double doors with glass',
        'width_options': ['5ft', '6ft'],
    },
    {
        'id': 'accordion',
        'name': 'Accordion Door',
        'prompt_hint': 'accordion folding glass door system with multiple panels',
        'description': 'Multi-panel folding door that opens completely',
        'popular': True,
        'width_options': ['8ft', '12ft', '16ft', '20ft'],
    },
    {
        'id': 'bifold',
        'name': 'Bi-Fold Door',
        'prompt_hint': 'bi-fold glass door with panels that fold in pairs',
        'description': 'Panels fold in pairs for wide opening',
        'width_options': ['8ft', '12ft', '16ft'],
    },
]

PATIO_ENCLOSURE_TYPES = [
    {
        'id': 'none',
        'name': 'No Enclosure',
        'prompt_hint': '',
        'description': 'No patio enclosure',
    },
    {
        'id': 'three_season',
        'name': 'Three-Season Sunroom',
        'prompt_hint': 'three-season sunroom with glass windows and screens',
        'description': 'Screen and glass combination, spring through fall use',
        'popular': True,
    },
    {
        'id': 'four_season',
        'name': 'Four-Season Sunroom',
        'prompt_hint': 'four-season sunroom with insulated glass and climate control',
        'description': 'Fully insulated, year-round comfort with HVAC',
        'popular': True,
    },
    {
        'id': 'screen_room',
        'name': 'Screen Room',
        'prompt_hint': 'screened patio enclosure with aluminum frame',
        'description': 'Aluminum frame with screen panels, bug protection',
    },
    {
        'id': 'glass_walls',
        'name': 'Retractable Glass Walls',
        'prompt_hint': 'retractable glass wall system that opens completely',
        'description': 'Modern sliding/folding glass panels, opens fully',
    },
]

ENCLOSURE_GLASS_TYPES = [
    {
        'id': 'single_pane',
        'name': 'Single Pane',
        'prompt_hint': 'single pane glass',
        'description': 'Basic single pane for three-season use',
    },
    {
        'id': 'double_pane',
        'name': 'Double Pane Insulated',
        'prompt_hint': 'double pane insulated glass',
        'description': 'Energy efficient, for four-season comfort',
        'popular': True,
    },
    {
        'id': 'low_e_double',
        'name': 'Low-E Double Pane',
        'prompt_hint': 'low-E double pane glass with energy coating',
        'description': 'Premium insulation with UV protection',
    },
    {
        'id': 'tinted',
        'name': 'Tinted Glass',
        'prompt_hint': 'tinted glass for sun control',
        'description': 'Reduces glare and heat gain',
    },
]

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

PIPELINE_STEPS = ['cleanup', 'window_frame', 'grilles_glass', 'trim', 'doors', 'patio_enclosure', 'quality_check']

PRIMARY_COLOR = "#2E7D32"  # Forest Green
SECONDARY_COLOR = "#66BB6A"


class WindowsTenantConfig(BaseTenantConfig):
    """Windows vertical tenant configuration."""

    tenant_id = 'windows'
    display_name = VERTICAL_DISPLAY_NAME
    supports_reference_images = True

    def get_pipeline_steps(self):
        return PIPELINE_STEPS

    def get_step_config(self, step_name):
        configs = {
            'cleanup': {'type': 'cleanup', 'progress_weight': 15, 'description': 'Preparing image'},
            'window_frame': {'type': 'insertion', 'scope_key': None, 'feature_name': 'window', 'progress_weight': 30, 'description': 'Installing window frame'},
            'grilles_glass': {'type': 'insertion', 'scope_key': 'grilles_glass', 'feature_name': 'grilles_glass', 'progress_weight': 15, 'description': 'Adding grilles and glass'},
            'trim': {'type': 'insertion', 'scope_key': 'trim', 'feature_name': 'trim', 'progress_weight': 10, 'description': 'Installing trim'},
            'doors': {'type': 'insertion', 'scope_key': 'doors', 'feature_name': 'door', 'progress_weight': 15, 'description': 'Installing doors'},
            'patio_enclosure': {'type': 'insertion', 'scope_key': 'patio_enclosure', 'feature_name': 'patio_enclosure', 'progress_weight': 10, 'description': 'Adding patio enclosure'},
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
        'project_types': PROJECT_TYPES,
        'door_types': DOOR_TYPES,
        'patio_enclosure_types': PATIO_ENCLOSURE_TYPES,
        'enclosure_glass_types': ENCLOSURE_GLASS_TYPES,
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
