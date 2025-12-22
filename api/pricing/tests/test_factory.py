import pytest
from api.pricing.calculators import get_calculator, CalculatorNotFoundError


class TestCalculatorFactory:
    """Tests for the calculator factory."""

    def test_get_pools_calculator(self):
        calc = get_calculator('pools')
        assert calc.vertical_id == 'pools'

    def test_unknown_vertical_raises(self):
        with pytest.raises(CalculatorNotFoundError):
            get_calculator('unknown_vertical')

    def test_get_calculator_with_contractor(self):
        calc = get_calculator('pools', contractor_id='test-123')
        assert calc.contractor_id == 'test-123'
