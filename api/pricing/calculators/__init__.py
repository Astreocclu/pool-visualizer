from typing import Optional
from .base import BasePricingCalculator
from .pools import PoolsPricingCalculator


class CalculatorNotFoundError(Exception):
    """Raised when no calculator exists for a vertical."""
    pass


# Registry of calculators by vertical ID
CALCULATOR_REGISTRY = {
    'pools': PoolsPricingCalculator,
    # 'roofing': RoofingPricingCalculator,  # TODO: Phase 2
    # 'solar': SolarPricingCalculator,       # TODO: Phase 2
    # 'windows': WindowsPricingCalculator,   # TODO: Phase 2
    # 'security_screens': SecurityScreensPricingCalculator,  # TODO: Phase 2
}


def get_calculator(vertical_id: str, contractor_id: Optional[str] = None) -> BasePricingCalculator:
    """
    Factory function to get a calculator for a vertical.

    Args:
        vertical_id: The vertical identifier (e.g., 'pools')
        contractor_id: Optional contractor ID for custom pricing

    Returns:
        Configured pricing calculator instance

    Raises:
        CalculatorNotFoundError: If no calculator exists for the vertical
    """
    calculator_class = CALCULATOR_REGISTRY.get(vertical_id)
    if not calculator_class:
        raise CalculatorNotFoundError(f"No calculator found for vertical: {vertical_id}")

    return calculator_class(contractor_id=contractor_id)


__all__ = [
    'BasePricingCalculator',
    'PoolsPricingCalculator',
    'get_calculator',
    'CalculatorNotFoundError',
]
