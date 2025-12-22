import pytest
from decimal import Decimal
from api.pricing.calculators.base import BasePricingCalculator


class TestBasePricingCalculator:
    """Tests for the abstract base calculator."""

    def test_cannot_instantiate_directly(self):
        """Base calculator is abstract and cannot be instantiated."""
        with pytest.raises(TypeError):
            BasePricingCalculator()

    def test_subclass_must_implement_vertical_id(self):
        """Subclasses must define vertical_id property."""
        class IncompleteCalculator(BasePricingCalculator):
            def calculate_base_cost(self, config):
                return {}

            def get_line_items(self, config):
                return []

        with pytest.raises(TypeError):
            IncompleteCalculator()

    def test_apply_markup_default(self):
        """Default markup is 25%."""
        class TestCalculator(BasePricingCalculator):
            @property
            def vertical_id(self):
                return 'test'

            def calculate_base_cost(self, config):
                return {'material': Decimal('1000')}

            def get_line_items(self, config):
                return []

        calc = TestCalculator()
        result = calc.apply_markup(Decimal('1000'))
        assert result == Decimal('1250')  # 1000 * 1.25

    def test_apply_overhead_default(self):
        """Default overhead is 15%."""
        class TestCalculator(BasePricingCalculator):
            @property
            def vertical_id(self):
                return 'test'

            def calculate_base_cost(self, config):
                return {'material': Decimal('1000')}

            def get_line_items(self, config):
                return []

        calc = TestCalculator()
        result = calc.apply_overhead(Decimal('1000'))
        assert result == Decimal('1150')  # 1000 * 1.15
