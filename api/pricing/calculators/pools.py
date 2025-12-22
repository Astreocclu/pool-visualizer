from decimal import Decimal
from typing import Dict, List, Any
from .base import BasePricingCalculator


# Pool pricing data (migrated from config.py - will move to DB later)
POOL_SIZES = {
    'starter': {'name': 'Starter', 'dimensions': '12x24', 'base_price': Decimal('50000')},
    'classic': {'name': 'Classic', 'dimensions': '15x30', 'base_price': Decimal('65000')},
    'family': {'name': 'Family', 'dimensions': '16x36', 'base_price': Decimal('75000')},
    'resort': {'name': 'Resort', 'dimensions': '18x40', 'base_price': Decimal('95000')},
}

POOL_SHAPES = {
    'rectangle': {'name': 'Rectangle', 'multiplier': Decimal('1.00')},
    'roman': {'name': 'Roman', 'multiplier': Decimal('1.05')},
    'grecian': {'name': 'Grecian', 'multiplier': Decimal('1.05')},
    'kidney': {'name': 'Kidney', 'multiplier': Decimal('1.10')},
    'freeform': {'name': 'Freeform', 'multiplier': Decimal('1.15')},
    'lazy_l': {'name': 'Lazy L', 'multiplier': Decimal('1.10')},
    'oval': {'name': 'Oval', 'multiplier': Decimal('1.05')},
}

INTERIOR_FINISHES = {
    'white_plaster': {'name': 'White Plaster', 'price_add': Decimal('0')},
    'pebble_blue': {'name': 'Pebble Tec - Blue', 'price_add': Decimal('8000')},
    'pebble_midnight': {'name': 'Pebble Tec - Midnight', 'price_add': Decimal('9000')},
    'quartz_blue': {'name': 'Quartz - Ocean Blue', 'price_add': Decimal('6000')},
    'quartz_aqua': {'name': 'Quartz - Caribbean', 'price_add': Decimal('6000')},
    'glass_tile': {'name': 'Glass Tile', 'price_add': Decimal('15000')},
}

DECK_MATERIALS = {
    'travertine': {'name': 'Travertine', 'price_per_sqft': Decimal('18')},
    'pavers': {'name': 'Pavers', 'price_per_sqft': Decimal('14')},
    'brushed_concrete': {'name': 'Brushed Concrete', 'price_per_sqft': Decimal('8')},
    'stamped_concrete': {'name': 'Stamped Concrete', 'price_per_sqft': Decimal('12')},
    'flagstone': {'name': 'Flagstone', 'price_per_sqft': Decimal('22')},
    'wood': {'name': 'Wood Deck', 'price_per_sqft': Decimal('25')},
}

WATER_FEATURES = {
    'rock_waterfall': {'name': 'Rock Waterfall', 'price_add': Decimal('8000')},
    'bubblers': {'name': 'Bubblers / Fountain Jets', 'price_add': Decimal('2500')},
    'scuppers': {'name': 'Scuppers', 'price_add': Decimal('4500')},
    'fire_bowls': {'name': 'Fire Bowls', 'price_add': Decimal('3500')},
    'deck_jets': {'name': 'Deck Jets', 'price_add': Decimal('3000')},
}

BUILT_IN_FEATURES = {
    'tanning_ledge': {'name': 'Tanning Ledge (Baja Shelf)', 'price_add': Decimal('4500')},
    'attached_spa': {'name': 'Attached Spa (Spillover)', 'price_add': Decimal('18000')},
}


class PoolsPricingCalculator(BasePricingCalculator):
    """Pools-specific pricing calculator."""

    @property
    def vertical_id(self) -> str:
        return 'pools'

    def calculate_base_cost(self, config: Dict[str, Any]) -> Dict[str, Decimal]:
        """Calculate pool installation base costs."""
        # Get selections with defaults
        pool_size_id = config.get('pool_size', 'classic')
        shape_id = config.get('shape', 'rectangle')
        interior_id = config.get('interior_finish', 'white_plaster')
        deck_material_id = config.get('deck_material', 'travertine')
        deck_sqft = Decimal(str(config.get('deck_sqft', 600)))
        water_features = config.get('water_features', [])
        built_in_features = config.get('built_in_features', {})

        # Pool shell base price
        pool_size = POOL_SIZES.get(pool_size_id, POOL_SIZES['classic'])
        pool_base = pool_size['base_price']

        # Apply shape multiplier to pool shell only
        shape = POOL_SHAPES.get(shape_id, POOL_SHAPES['rectangle'])
        pool_cost = pool_base * shape['multiplier']

        # Interior finish add-on
        interior = INTERIOR_FINISHES.get(interior_id, INTERIOR_FINISHES['white_plaster'])
        interior_cost = interior['price_add']

        # Deck cost
        deck = DECK_MATERIALS.get(deck_material_id, DECK_MATERIALS['travertine'])
        deck_cost = deck_sqft * deck['price_per_sqft']

        # Water features
        water_features_cost = Decimal('0')
        for wf_id in water_features:
            wf = WATER_FEATURES.get(wf_id)
            if wf:
                water_features_cost += wf['price_add']

        # Built-in features
        built_in_cost = Decimal('0')
        for feature_id, enabled in built_in_features.items():
            if enabled:
                feature = BUILT_IN_FEATURES.get(feature_id)
                if feature:
                    built_in_cost += feature['price_add']

        # Total material cost
        total_material = pool_cost + interior_cost + deck_cost + water_features_cost + built_in_cost

        # Labor estimate (simplified: 35% of material for pools)
        labor_cost = total_material * Decimal('0.35')

        # Equipment (excavation, pumps, etc) - 10%
        equipment_cost = total_material * Decimal('0.10')

        return {
            'material': total_material,
            'labor': labor_cost,
            'equipment': equipment_cost,
        }

    def get_line_items(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return itemized line items for display."""
        items = []

        # Pool shell
        pool_size_id = config.get('pool_size', 'classic')
        pool_size = POOL_SIZES.get(pool_size_id, POOL_SIZES['classic'])
        shape_id = config.get('shape', 'rectangle')
        shape = POOL_SHAPES.get(shape_id, POOL_SHAPES['rectangle'])
        pool_cost = pool_size['base_price'] * shape['multiplier']

        items.append({
            'name': f"Pool Shell - {pool_size['name']} ({pool_size['dimensions']})",
            'description': f"{shape['name']} shape",
            'quantity': 1,
            'unit_price': pool_cost,
            'total': pool_cost,
        })

        # Interior finish
        interior_id = config.get('interior_finish', 'white_plaster')
        interior = INTERIOR_FINISHES.get(interior_id, INTERIOR_FINISHES['white_plaster'])
        if interior['price_add'] > 0:
            items.append({
                'name': f"Interior Finish - {interior['name']}",
                'description': 'Pool surface finish upgrade',
                'quantity': 1,
                'unit_price': interior['price_add'],
                'total': interior['price_add'],
            })

        # Deck
        deck_material_id = config.get('deck_material', 'travertine')
        deck = DECK_MATERIALS.get(deck_material_id, DECK_MATERIALS['travertine'])
        deck_sqft = Decimal(str(config.get('deck_sqft', 600)))
        deck_total = deck_sqft * deck['price_per_sqft']

        items.append({
            'name': f"Deck - {deck['name']}",
            'description': f'{deck_sqft} sq ft @ ${deck["price_per_sqft"]}/sqft',
            'quantity': int(deck_sqft),
            'unit_price': deck['price_per_sqft'],
            'total': deck_total,
        })

        # Water features
        for wf_id in config.get('water_features', []):
            wf = WATER_FEATURES.get(wf_id)
            if wf:
                items.append({
                    'name': f"Water Feature - {wf['name']}",
                    'description': '',
                    'quantity': 1,
                    'unit_price': wf['price_add'],
                    'total': wf['price_add'],
                })

        # Built-in features
        for feature_id, enabled in config.get('built_in_features', {}).items():
            if enabled:
                feature = BUILT_IN_FEATURES.get(feature_id)
                if feature:
                    items.append({
                        'name': f"Built-In - {feature['name']}",
                        'description': '',
                        'quantity': 1,
                        'unit_price': feature['price_add'],
                        'total': feature['price_add'],
                    })

        return items
