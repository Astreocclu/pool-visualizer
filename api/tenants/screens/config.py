"""Security Screens tenant configuration."""
from typing import List, Tuple, Dict, Any
from ..base import BaseTenantConfig

# Pricing data for security screens
MESH_TYPES_PRICING = [
    {'id': '10x10_standard', 'name': '10x10 Standard', 'price_per_sqft': 12},
    {'id': '12x12_standard', 'name': '12x12 Standard', 'price_per_sqft': 15},
    {'id': '12x12_american', 'name': '12x12 American', 'price_per_sqft': 18},
]

FRAME_COLORS_PRICING = [
    {'id': 'black', 'name': 'Black', 'price_add': 0},
    {'id': 'dark_bronze', 'name': 'Dark Bronze', 'price_add': 200},
    {'id': 'stucco', 'name': 'Stucco', 'price_add': 150},
    {'id': 'white', 'name': 'White', 'price_add': 0},
    {'id': 'almond', 'name': 'Almond', 'price_add': 100},
]

COVERAGE_OPTIONS = {
    'patio': {'name': 'Patio Enclosure', 'base_sqft': 200, 'description': 'Full patio screen enclosure'},
    'windows': {'name': 'Window Screens', 'base_sqft': 50, 'per_window': 10, 'description': 'Security window screens'},
    'doors': {'name': 'Entry Doors', 'base_price': 800, 'per_door': 800, 'description': 'Security screen doors'},
}

INSTALLATION_BASE = 500  # Base installation fee
INSTALLATION_PER_SQFT = 5  # Per sq ft installation


def get_full_config_with_pricing():
    """Return full config including pricing for PDF generation."""
    return {
        'mesh_types': MESH_TYPES_PRICING,
        'frame_colors': FRAME_COLORS_PRICING,
        'coverage_options': COVERAGE_OPTIONS,
        'installation_base': INSTALLATION_BASE,
        'installation_per_sqft': INSTALLATION_PER_SQFT,
    }


class ScreensTenantConfig(BaseTenantConfig):

    supports_reference_images = True

    @property
    def tenant_id(self) -> str:
        return "screens"

    @property
    def display_name(self) -> str:
        return "Security Screens"

    def get_product_schema(self) -> List[Dict[str, Any]]:
        """
        Product categories for Security Screens.

        Note: No 'opacity' category - mesh density and color determine visibility.
        """
        return [
            {
                "key": "mesh_type",
                "label": "Mesh Type",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "10x10_standard", "label": "10x10 Standard"},
                    {"value": "12x12_standard", "label": "12x12 Standard"},
                    {"value": "12x12_american", "label": "12x12 American"},
                ]
            },
            {
                "key": "frame_color",
                "label": "Frame Color",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "black", "label": "Black"},
                    {"value": "dark_bronze", "label": "Dark Bronze"},
                    {"value": "stucco", "label": "Stucco"},
                    {"value": "white", "label": "White"},
                    {"value": "almond", "label": "Almond"},
                ]
            },
            {
                "key": "mesh_color",
                "label": "Mesh Color",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "black", "label": "Black (Recommended)"},
                    {"value": "stucco", "label": "Stucco"},
                    {"value": "bronze", "label": "Bronze"},
                ]
            },
        ]

    def get_mesh_choices(self) -> List[Tuple[str, str]]:
        """Return mesh type choices as tuples for forms."""
        return [
            ('10x10_standard', '10x10 Standard'),
            ('12x12_standard', '12x12 Standard'),
            ('12x12_american', '12x12 American'),
        ]

    def get_frame_color_choices(self) -> List[Tuple[str, str]]:
        """Return frame color choices as tuples for forms."""
        return [
            ('black', 'Black'),
            ('dark_bronze', 'Dark Bronze'),
            ('stucco', 'Stucco'),
            ('white', 'White'),
            ('almond', 'Almond'),
        ]

    def get_mesh_color_choices(self) -> List[Tuple[str, str]]:
        """Return mesh color choices as tuples for forms."""
        return [
            ('black', 'Black (Recommended)'),
            ('stucco', 'Stucco'),
            ('bronze', 'Bronze'),
        ]

    def get_opacity_choices(self) -> List[Tuple[str, str]]:
        """Return opacity choices - not directly applicable to screens."""
        return []  # Mesh density determines visibility, not separate opacity

    def get_pipeline_steps(self) -> List[str]:
        # Order: doors -> windows -> patio (patio last as largest envelope)
        return ['cleanup', 'doors', 'windows', 'patio', 'quality_check']

    def get_prompts_module(self):
        from . import prompts
        return prompts

    def get_step_config(self, step_name: str) -> Dict[str, Any]:
        configs = {
            'cleanup': {
                'type': 'cleanup',
                'description': 'Cleaning',
                'progress_weight': 30
            },
            'patio': {
                'type': 'insertion',
                'feature_name': 'patio enclosure',
                'scope_key': 'patio',
                'description': 'Building Patio',
                'progress_weight': 50
            },
            'windows': {
                'type': 'insertion',
                'feature_name': 'windows',
                'scope_key': 'windows',
                'description': 'Building Windows',
                'progress_weight': 60
            },
            'doors': {
                'type': 'insertion',
                'feature_name': 'entry doors',
                'scope_key': 'doors',
                'description': 'Building Doors',
                'progress_weight': 70
            },
            'quality_check': {
                'type': 'quality_check',
                'description': 'Checking Quality',
                'progress_weight': 90
            }
        }
        return configs.get(step_name, {})
