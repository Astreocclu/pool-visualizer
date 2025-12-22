from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class Vertical(models.Model):
    """Supported verticals (pools, roofing, solar, windows, security_screens)."""
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    calculation_unit = models.CharField(
        max_length=20,
        choices=[
            ('project', 'Project-Based'),
            ('square', 'Per Square (100 sqft)'),
            ('watt', 'Per Watt'),
            ('opening', 'Per Opening'),
            ('unit', 'Per Unit'),
        ],
        default='project'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Verticals'

    def __str__(self):
        return self.display_name


class PriceBookCategory(models.Model):
    """Categories within a vertical (e.g., 'pool_sizes', 'finishes', 'water_features')."""
    vertical = models.ForeignKey(Vertical, on_delete=models.CASCADE, related_name='categories')
    slug = models.SlugField(max_length=50)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Price Book Categories'
        unique_together = ['vertical', 'slug']
        ordering = ['vertical', 'sort_order']

    def __str__(self):
        return f"{self.vertical_id} / {self.name}"


class PriceBookItem(models.Model):
    """Individual priced item in the price book."""
    category = models.ForeignKey(PriceBookCategory, on_delete=models.CASCADE, related_name='items')
    item_id = models.CharField(max_length=50)  # e.g., 'pebble_tec_blue'
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Pricing fields
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    price_multiplier = models.DecimalField(max_digits=5, decimal_places=3, default=Decimal('1.000'))
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit_type = models.CharField(max_length=20, blank=True)  # 'sqft', 'each', etc.

    # Metadata
    prompt_hint = models.CharField(max_length=200, blank=True)  # For AI prompts
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['category', 'item_id']
        ordering = ['category', 'sort_order']

    def __str__(self):
        return f"{self.category.slug}/{self.item_id}: ${self.base_price}"


class ContractorProfile(models.Model):
    """Contractor-specific pricing settings."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pricing_profile', null=True, blank=True)
    company_name = models.CharField(max_length=200)

    # Markup settings
    overhead_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('15.00'))
    profit_margin_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('25.00'))

    # Regional settings
    default_labor_rate = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('75.00'))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=3, default=Decimal('8.250'))

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name


class ContractorPriceOverride(models.Model):
    """Contractor-specific price overrides."""
    contractor = models.ForeignKey(ContractorProfile, on_delete=models.CASCADE, related_name='overrides')
    price_book_item = models.ForeignKey(PriceBookItem, on_delete=models.CASCADE)

    # Override type: either custom price OR percentage adjustment
    custom_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_adjustment_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    effective_date = models.DateField(auto_now_add=True)
    expires_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['contractor', 'price_book_item']

    def get_effective_price(self) -> Decimal:
        """Calculate effective price with override applied."""
        base = self.price_book_item.base_price
        if self.custom_price is not None:
            return self.custom_price
        if self.price_adjustment_percent is not None:
            return base * (Decimal('1') + self.price_adjustment_percent / Decimal('100'))
        return base


class PriceCalculationLog(models.Model):
    """Audit log for price calculations."""
    vertical = models.CharField(max_length=50)
    contractor = models.ForeignKey(ContractorProfile, on_delete=models.SET_NULL, null=True, blank=True)

    # Input/output
    input_config = models.JSONField(default=dict)
    cost_breakdown = models.JSONField(default=dict)
    final_price = models.DecimalField(max_digits=12, decimal_places=2)

    # Metadata
    calculation_type = models.CharField(max_length=20, default='estimate')  # 'estimate' or 'quote'
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
