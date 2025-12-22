import pytest
from decimal import Decimal
from api.pricing.calculators.pools import PoolsPricingCalculator


class TestPoolsPricingCalculator:
    """Tests for pools-specific pricing logic."""

    def test_vertical_id_is_pools(self):
        calc = PoolsPricingCalculator()
        assert calc.vertical_id == 'pools'

    def test_calculate_base_cost_classic_pool(self):
        """Classic pool with default options."""
        calc = PoolsPricingCalculator()
        config = {
            'pool_size': 'classic',
            'shape': 'rectangle',
            'interior_finish': 'white_plaster',
            'deck_material': 'travertine',
            'deck_sqft': 600,
            'water_features': [],
            'built_in_features': {},
        }

        result = calc.calculate_base_cost(config)

        # Classic base: $65,000
        # Rectangle multiplier: 1.0
        # White plaster add: $0
        # Travertine deck: $18/sqft * 600 = $10,800
        # Total material: $75,800
        assert 'material' in result
        assert result['material'] == Decimal('75800')

    def test_shape_multiplier_applies(self):
        """Freeform shape adds 15% multiplier."""
        calc = PoolsPricingCalculator()
        config_rect = {
            'pool_size': 'starter',
            'shape': 'rectangle',
            'interior_finish': 'white_plaster',
            'deck_material': 'brushed_concrete',
            'deck_sqft': 400,
            'water_features': [],
            'built_in_features': {},
        }
        config_freeform = {**config_rect, 'shape': 'freeform'}

        rect_result = calc.calculate_base_cost(config_rect)
        freeform_result = calc.calculate_base_cost(config_freeform)

        # Freeform should be ~15% more expensive (on pool cost, not deck)
        assert freeform_result['material'] > rect_result['material']

    def test_water_features_add_cost(self):
        """Water features add to total cost."""
        calc = PoolsPricingCalculator()
        base_config = {
            'pool_size': 'classic',
            'shape': 'rectangle',
            'interior_finish': 'white_plaster',
            'deck_material': 'travertine',
            'deck_sqft': 600,
            'water_features': [],
            'built_in_features': {},
        }
        with_features = {
            **base_config,
            'water_features': ['rock_waterfall', 'fire_bowls']
        }

        base_result = calc.calculate_base_cost(base_config)
        features_result = calc.calculate_base_cost(with_features)

        # Rock waterfall: $8,000 + Fire bowls: $3,500 = $11,500 more
        diff = features_result['material'] - base_result['material']
        assert diff == Decimal('11500')

    def test_get_line_items_returns_breakdown(self):
        """Line items include pool shell, deck, features."""
        calc = PoolsPricingCalculator()
        config = {
            'pool_size': 'classic',
            'shape': 'rectangle',
            'interior_finish': 'pebble_blue',
            'deck_material': 'travertine',
            'deck_sqft': 600,
            'water_features': ['bubblers'],
            'built_in_features': {'tanning_ledge': True},
        }

        items = calc.get_line_items(config)

        # Should have: pool shell, interior finish, deck, water feature, built-in
        names = [item['name'] for item in items]
        assert 'Pool Shell - Classic (15x30)' in names
        assert 'Interior Finish - Pebble Tec - Blue' in names
        assert 'Deck - Travertine' in names
        assert 'Water Feature - Bubblers / Fountain Jets' in names
