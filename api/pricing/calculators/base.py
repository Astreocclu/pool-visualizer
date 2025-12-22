from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, List, Any, Optional


class BasePricingCalculator(ABC):
    """
    Abstract base class for all vertical pricing calculators.

    Each vertical implements:
    - vertical_id: Identifier for the vertical
    - calculate_base_cost: Compute raw costs from config
    - get_line_items: Return itemized breakdown for display
    """

    def __init__(self, contractor_id: Optional[str] = None):
        self.contractor_id = contractor_id
        self.contractor_profile = None
        self._load_contractor_profile()

    def _load_contractor_profile(self):
        """Load contractor-specific settings if contractor_id provided."""
        if self.contractor_id:
            from api.pricing.models import ContractorProfile
            try:
                self.contractor_profile = ContractorProfile.objects.get(
                    user_id=self.contractor_id,
                    is_active=True
                )
            except ContractorProfile.DoesNotExist:
                pass

    @property
    @abstractmethod
    def vertical_id(self) -> str:
        """Return the vertical identifier (e.g., 'pools', 'roofing')."""
        pass

    @abstractmethod
    def calculate_base_cost(self, config: Dict[str, Any]) -> Dict[str, Decimal]:
        """
        Calculate base costs from user selections.

        Returns dict with cost components:
        {'material': Decimal, 'labor': Decimal, 'equipment': Decimal, ...}
        """
        pass

    @abstractmethod
    def get_line_items(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Return itemized line items for display.

        Each item: {'name': str, 'description': str, 'quantity': int,
                    'unit_price': Decimal, 'total': Decimal}
        """
        pass

    def apply_overhead(self, total_cost: Decimal) -> Decimal:
        """Apply overhead percentage to total cost."""
        overhead_percent = Decimal('15.00')  # Default 15%
        if self.contractor_profile:
            overhead_percent = self.contractor_profile.overhead_percent

        multiplier = Decimal('1') + (overhead_percent / Decimal('100'))
        return total_cost * multiplier

    def apply_markup(self, total_cost: Decimal) -> Decimal:
        """Apply profit margin markup to total cost."""
        markup_percent = Decimal('25.00')  # Default 25%
        if self.contractor_profile:
            markup_percent = self.contractor_profile.profit_margin_percent

        multiplier = Decimal('1') + (markup_percent / Decimal('100'))
        return total_cost * multiplier

    def apply_tax(self, total: Decimal) -> Decimal:
        """Apply sales tax to final price."""
        tax_rate = Decimal('8.250')  # Default 8.25%
        if self.contractor_profile:
            tax_rate = self.contractor_profile.tax_rate

        return total * (tax_rate / Decimal('100'))

    def calculate_final_price(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point - calculate complete price with breakdown.

        Returns:
        {
            'subtotal': Decimal,
            'overhead': Decimal,
            'profit': Decimal,
            'tax': Decimal,
            'total': Decimal,
            'line_items': List[Dict],
            'cost_breakdown': Dict[str, Decimal],
            'type': 'estimate'
        }
        """
        # Calculate base costs
        cost_breakdown = self.calculate_base_cost(config)
        subtotal = sum(cost_breakdown.values())

        # Apply overhead
        with_overhead = self.apply_overhead(subtotal)
        overhead_amount = with_overhead - subtotal

        # Apply markup
        with_markup = self.apply_markup(with_overhead)
        profit_amount = with_markup - with_overhead

        # Apply tax
        tax_amount = self.apply_tax(with_markup)
        total = with_markup + tax_amount

        # Get line items
        line_items = self.get_line_items(config)

        return {
            'subtotal': subtotal,
            'overhead': overhead_amount,
            'profit': profit_amount,
            'tax': tax_amount,
            'total': total,
            'line_items': line_items,
            'cost_breakdown': cost_breakdown,
            'type': 'estimate',
            'vertical_id': self.vertical_id,
        }
