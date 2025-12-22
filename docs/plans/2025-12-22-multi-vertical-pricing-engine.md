# Multi-Vertical Pricing Engine Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a professional pricing engine that calculates itemized quotes for each vertical (pools, roofs, solar, windows, security screens), with platform defaults and contractor overrides.

**Architecture:**
- Database-backed price book with contractor override system
- Abstract `BasePricingCalculator` with vertical-specific implementations
- Price calculated during `/api/visualize/` and stored on `VisualizationRequest`
- Frontend displays itemized breakdown on results page

**Tech Stack:** Django 4.0, DRF, PostgreSQL/SQLite, React 19.1, Zustand

---

## Phase 1: Core Pricing Infrastructure

### Task 1: Create Pricing App Structure

**Files:**
- Create: `api/pricing/__init__.py`
- Create: `api/pricing/models.py`
- Create: `api/pricing/admin.py`
- Create: `api/pricing/apps.py`
- Modify: `pools_project/settings.py`

**Step 1: Create the pricing app directory**

```bash
mkdir -p api/pricing/calculators
touch api/pricing/__init__.py
touch api/pricing/calculators/__init__.py
```

**Step 2: Create apps.py**

```python
# api/pricing/apps.py
from django.apps import AppConfig

class PricingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.pricing'
    verbose_name = 'Pricing Engine'
```

**Step 3: Register in settings**

Modify `pools_project/settings.py`:
```python
INSTALLED_APPS = [
    # ... existing apps
    'api.pricing',  # Add this line
]
```

**Step 4: Verify app loads**

```bash
cd /home/reid/testhome/pools-visualizer
source venv/bin/activate
python3 manage.py check
```

Expected: `System check identified no issues`

**Step 5: Commit**

```bash
git add api/pricing/ pools_project/settings.py
git commit -m "feat(pricing): create pricing app structure"
```

---

### Task 2: Create Core Database Models

**Files:**
- Create: `api/pricing/models.py`
- Create: `api/pricing/migrations/0001_initial.py` (auto-generated)

**Step 1: Write the models**

```python
# api/pricing/models.py
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
```

**Step 2: Create and run migration**

```bash
python3 manage.py makemigrations pricing
python3 manage.py migrate
```

Expected: Migration created and applied successfully

**Step 3: Commit**

```bash
git add api/pricing/
git commit -m "feat(pricing): add core database models"
```

---

### Task 3: Create Admin Interface

**Files:**
- Modify: `api/pricing/admin.py`

**Step 1: Write the admin configuration**

```python
# api/pricing/admin.py
from django.contrib import admin
from .models import (
    Vertical, PriceBookCategory, PriceBookItem,
    ContractorProfile, ContractorPriceOverride, PriceCalculationLog
)


@admin.register(Vertical)
class VerticalAdmin(admin.ModelAdmin):
    list_display = ['id', 'display_name', 'calculation_unit', 'is_active']
    list_filter = ['is_active', 'calculation_unit']
    search_fields = ['name', 'display_name']


class PriceBookItemInline(admin.TabularInline):
    model = PriceBookItem
    extra = 0
    fields = ['item_id', 'name', 'base_price', 'price_multiplier', 'is_active', 'sort_order']


@admin.register(PriceBookCategory)
class PriceBookCategoryAdmin(admin.ModelAdmin):
    list_display = ['vertical', 'slug', 'name', 'sort_order']
    list_filter = ['vertical']
    search_fields = ['name', 'slug']
    inlines = [PriceBookItemInline]


@admin.register(PriceBookItem)
class PriceBookItemAdmin(admin.ModelAdmin):
    list_display = ['category', 'item_id', 'name', 'base_price', 'price_multiplier', 'is_active']
    list_filter = ['category__vertical', 'category', 'is_active', 'is_popular']
    search_fields = ['item_id', 'name']
    list_editable = ['base_price', 'is_active']


@admin.register(ContractorProfile)
class ContractorProfileAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'overhead_percent', 'profit_margin_percent', 'is_active']
    list_filter = ['is_active']
    search_fields = ['company_name']


@admin.register(ContractorPriceOverride)
class ContractorPriceOverrideAdmin(admin.ModelAdmin):
    list_display = ['contractor', 'price_book_item', 'custom_price', 'price_adjustment_percent', 'effective_date']
    list_filter = ['contractor', 'price_book_item__category__vertical']
    search_fields = ['contractor__company_name', 'price_book_item__name']


@admin.register(PriceCalculationLog)
class PriceCalculationLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'vertical', 'contractor', 'final_price', 'calculation_type', 'created_at']
    list_filter = ['vertical', 'calculation_type', 'created_at']
    readonly_fields = ['input_config', 'cost_breakdown', 'final_price', 'created_at']
    date_hierarchy = 'created_at'
```

**Step 2: Verify admin loads**

```bash
python3 manage.py runserver 8006
```

Navigate to http://localhost:8006/admin/ and verify Pricing section appears.

**Step 3: Commit**

```bash
git add api/pricing/admin.py
git commit -m "feat(pricing): add Django admin interface"
```

---

### Task 4: Create Base Pricing Calculator

**Files:**
- Create: `api/pricing/calculators/base.py`
- Create: `api/pricing/tests/__init__.py`
- Create: `api/pricing/tests/test_base_calculator.py`

**Step 1: Write the failing test**

```python
# api/pricing/tests/test_base_calculator.py
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
```

**Step 2: Run test to verify it fails**

```bash
mkdir -p api/pricing/tests
touch api/pricing/tests/__init__.py
python3 -m pytest api/pricing/tests/test_base_calculator.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'api.pricing.calculators.base'`

**Step 3: Write the base calculator**

```python
# api/pricing/calculators/base.py
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
```

**Step 4: Run tests to verify they pass**

```bash
python3 -m pytest api/pricing/tests/test_base_calculator.py -v
```

Expected: All tests PASS

**Step 5: Commit**

```bash
git add api/pricing/calculators/ api/pricing/tests/
git commit -m "feat(pricing): add base pricing calculator with TDD"
```

---

### Task 5: Create Pools Pricing Calculator

**Files:**
- Create: `api/pricing/calculators/pools.py`
- Create: `api/pricing/tests/test_pools_calculator.py`

**Step 1: Write the failing test**

```python
# api/pricing/tests/test_pools_calculator.py
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
```

**Step 2: Run test to verify it fails**

```bash
python3 -m pytest api/pricing/tests/test_pools_calculator.py -v
```

Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write the pools calculator**

```python
# api/pricing/calculators/pools.py
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
```

**Step 4: Run tests to verify they pass**

```bash
python3 -m pytest api/pricing/tests/test_pools_calculator.py -v
```

Expected: All tests PASS

**Step 5: Commit**

```bash
git add api/pricing/calculators/pools.py api/pricing/tests/test_pools_calculator.py
git commit -m "feat(pricing): add pools pricing calculator with TDD"
```

---

### Task 6: Create Calculator Factory

**Files:**
- Create: `api/pricing/calculators/__init__.py`
- Create: `api/pricing/tests/test_factory.py`

**Step 1: Write the failing test**

```python
# api/pricing/tests/test_factory.py
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
```

**Step 2: Run test to verify it fails**

```bash
python3 -m pytest api/pricing/tests/test_factory.py -v
```

Expected: FAIL with `ImportError`

**Step 3: Write the factory**

```python
# api/pricing/calculators/__init__.py
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
```

**Step 4: Run tests to verify they pass**

```bash
python3 -m pytest api/pricing/tests/test_factory.py -v
```

Expected: All tests PASS

**Step 5: Commit**

```bash
git add api/pricing/calculators/__init__.py api/pricing/tests/test_factory.py
git commit -m "feat(pricing): add calculator factory with registry"
```

---

## Phase 2: API Integration

### Task 7: Create Pricing API Endpoint

**Files:**
- Create: `api/pricing/views.py`
- Create: `api/pricing/serializers.py`
- Create: `api/pricing/urls.py`
- Modify: `pools_project/urls.py`

**Step 1: Create serializers**

```python
# api/pricing/serializers.py
from rest_framework import serializers
from decimal import Decimal


class LineItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)


class PriceCalculationRequestSerializer(serializers.Serializer):
    config = serializers.DictField()
    contractor_id = serializers.CharField(required=False, allow_null=True)


class PriceCalculationResponseSerializer(serializers.Serializer):
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2)
    overhead = serializers.DecimalField(max_digits=12, decimal_places=2)
    profit = serializers.DecimalField(max_digits=12, decimal_places=2)
    tax = serializers.DecimalField(max_digits=12, decimal_places=2)
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    line_items = LineItemSerializer(many=True)
    cost_breakdown = serializers.DictField()
    type = serializers.CharField()
    vertical_id = serializers.CharField()
```

**Step 2: Create views**

```python
# api/pricing/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .calculators import get_calculator, CalculatorNotFoundError
from .serializers import (
    PriceCalculationRequestSerializer,
    PriceCalculationResponseSerializer,
)
from .models import PriceCalculationLog


class CalculatePriceView(APIView):
    """
    Calculate price for a vertical.

    POST /api/pricing/{vertical_id}/calculate/
    """

    def post(self, request, vertical_id):
        # Validate request
        serializer = PriceCalculationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        config = serializer.validated_data['config']
        contractor_id = serializer.validated_data.get('contractor_id')

        try:
            # Get calculator and compute price
            calculator = get_calculator(vertical_id, contractor_id=contractor_id)
            result = calculator.calculate_final_price(config)

            # Log calculation
            PriceCalculationLog.objects.create(
                vertical=vertical_id,
                input_config=config,
                cost_breakdown={k: str(v) for k, v in result['cost_breakdown'].items()},
                final_price=result['total'],
                calculation_type=result['type'],
            )

            # Serialize response
            response_serializer = PriceCalculationResponseSerializer(result)
            return Response(response_serializer.data)

        except CalculatorNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Calculation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
```

**Step 3: Create URLs**

```python
# api/pricing/urls.py
from django.urls import path
from .views import CalculatePriceView

urlpatterns = [
    path('<str:vertical_id>/calculate/', CalculatePriceView.as_view(), name='calculate-price'),
]
```

**Step 4: Register in main urls.py**

Modify `pools_project/urls.py`:
```python
from django.urls import path, include

urlpatterns = [
    # ... existing patterns
    path('api/pricing/', include('api.pricing.urls')),
]
```

**Step 5: Test the endpoint**

```bash
python3 manage.py runserver 8006
```

In another terminal:
```bash
curl -X POST http://localhost:8006/api/pricing/pools/calculate/ \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "pool_size": "classic",
      "shape": "rectangle",
      "interior_finish": "pebble_blue",
      "deck_material": "travertine",
      "deck_sqft": 600,
      "water_features": ["fire_bowls"],
      "built_in_features": {"tanning_ledge": true}
    }
  }'
```

Expected: JSON response with pricing breakdown

**Step 6: Commit**

```bash
git add api/pricing/views.py api/pricing/serializers.py api/pricing/urls.py pools_project/urls.py
git commit -m "feat(pricing): add pricing calculation API endpoint"
```

---

### Task 8: Integrate Pricing into Visualization Flow

**Files:**
- Modify: `api/visualizer/models.py` - Add price_data field
- Modify: `api/visualizer/views.py` - Calculate price on create
- Modify: `api/visualizer/serializers.py` - Include price in response

**Step 1: Add price_data to VisualizationRequest model**

In `api/visualizer/models.py`, add to VisualizationRequest:
```python
# Add this field to the VisualizationRequest model
price_data = models.JSONField(null=True, blank=True, help_text="Calculated price breakdown")
```

**Step 2: Create and run migration**

```bash
python3 manage.py makemigrations visualizer
python3 manage.py migrate
```

**Step 3: Update view to calculate price**

In `api/visualizer/views.py`, in the visualization create view, add after creating the request:
```python
# After creating VisualizationRequest, calculate price
from api.pricing.calculators import get_calculator, CalculatorNotFoundError

try:
    # Build pricing config from visualization selections
    pricing_config = {
        'pool_size': visualization_request.scope.get('pool_size', 'classic'),
        'shape': visualization_request.scope.get('shape', 'rectangle'),
        'interior_finish': visualization_request.scope.get('interior_finish', 'white_plaster'),
        'deck_material': visualization_request.scope.get('deck_material', 'travertine'),
        'deck_sqft': visualization_request.scope.get('deck_sqft', 600),
        'water_features': visualization_request.scope.get('water_features', []),
        'built_in_features': visualization_request.scope.get('built_in_features', {}),
    }

    calculator = get_calculator('pools')
    price_result = calculator.calculate_final_price(pricing_config)

    # Convert Decimals to strings for JSON storage
    visualization_request.price_data = {
        'subtotal': str(price_result['subtotal']),
        'overhead': str(price_result['overhead']),
        'profit': str(price_result['profit']),
        'tax': str(price_result['tax']),
        'total': str(price_result['total']),
        'line_items': [
            {**item, 'unit_price': str(item['unit_price']), 'total': str(item['total'])}
            for item in price_result['line_items']
        ],
        'type': price_result['type'],
    }
    visualization_request.save()
except CalculatorNotFoundError:
    pass  # Price calculation optional
```

**Step 4: Update serializer to include price**

In `api/visualizer/serializers.py`, add to VisualizationRequestSerializer:
```python
price_data = serializers.JSONField(read_only=True)
```

**Step 5: Test the full flow**

Submit a visualization request and verify price_data is populated.

**Step 6: Commit**

```bash
git add api/visualizer/
git commit -m "feat(pricing): integrate pricing into visualization flow"
```

---

## Phase 3: Frontend Integration

### Task 9: Create Pricing Display Component

**Files:**
- Create: `frontend/src/components/PricingDisplay/PricingDisplay.jsx`
- Create: `frontend/src/components/PricingDisplay/PricingDisplay.css`

**Step 1: Create the component**

```jsx
// frontend/src/components/PricingDisplay/PricingDisplay.jsx
import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Calculator, FileText } from 'lucide-react';
import './PricingDisplay.css';

const PricingDisplay = ({ priceData, onSaveQuote, onContactSales }) => {
  const [showBreakdown, setShowBreakdown] = useState(false);

  if (!priceData) {
    return null;
  }

  const formatCurrency = (value) => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(num);
  };

  return (
    <div className="pricing-card">
      {/* Header */}
      <div className="pricing-header">
        <div className="pricing-title">
          <Calculator size={20} />
          <h3>Estimated Cost</h3>
        </div>
        <span className={`pricing-badge ${priceData.type}`}>
          {priceData.type === 'estimate' ? 'Estimate' : 'Quote'}
        </span>
      </div>

      {/* Total Price */}
      <div className="pricing-total">
        <span className="total-amount">{formatCurrency(priceData.total)}</span>
        <button
          className="breakdown-toggle"
          onClick={() => setShowBreakdown(!showBreakdown)}
        >
          {showBreakdown ? 'Hide' : 'Show'} Details
          {showBreakdown ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
      </div>

      {/* Itemized Breakdown */}
      {showBreakdown && (
        <div className="pricing-breakdown">
          <div className="line-items">
            {priceData.line_items?.map((item, index) => (
              <div key={index} className="line-item">
                <div className="item-info">
                  <span className="item-name">{item.name}</span>
                  {item.description && (
                    <span className="item-description">{item.description}</span>
                  )}
                </div>
                <span className="item-total">{formatCurrency(item.total)}</span>
              </div>
            ))}
          </div>

          <div className="pricing-subtotals">
            <div className="subtotal-row">
              <span>Subtotal</span>
              <span>{formatCurrency(priceData.subtotal)}</span>
            </div>
            <div className="subtotal-row">
              <span>Overhead & Fees</span>
              <span>{formatCurrency(priceData.overhead)}</span>
            </div>
            <div className="subtotal-row">
              <span>Tax</span>
              <span>{formatCurrency(priceData.tax)}</span>
            </div>
            <div className="subtotal-row total">
              <span>Total</span>
              <span>{formatCurrency(priceData.total)}</span>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="pricing-actions">
        <button className="btn-primary" onClick={onSaveQuote}>
          <FileText size={16} />
          Save Quote
        </button>
        <button className="btn-secondary" onClick={onContactSales}>
          Contact Sales
        </button>
      </div>

      {/* Disclaimer */}
      <p className="pricing-disclaimer">
        * Estimate valid for 30 days. Final quote subject to site inspection.
      </p>
    </div>
  );
};

export default PricingDisplay;
```

**Step 2: Create the styles**

```css
/* frontend/src/components/PricingDisplay/PricingDisplay.css */
.pricing-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
  margin-top: 24px;
}

.pricing-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.pricing-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pricing-title h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.pricing-badge {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.pricing-badge.estimate {
  background: #fff3cd;
  color: #856404;
}

.pricing-badge.quote {
  background: #d4edda;
  color: #155724;
}

.pricing-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #e5e5e5;
}

.total-amount {
  font-size: 36px;
  font-weight: 700;
  color: #0077b6;
}

.breakdown-toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  font-size: 14px;
}

.breakdown-toggle:hover {
  color: #0077b6;
}

.pricing-breakdown {
  padding: 16px 0;
  border-bottom: 1px solid #e5e5e5;
}

.line-items {
  margin-bottom: 16px;
}

.line-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px dashed #e5e5e5;
}

.line-item:last-child {
  border-bottom: none;
}

.item-info {
  display: flex;
  flex-direction: column;
}

.item-name {
  font-weight: 500;
  color: #1a1a1a;
}

.item-description {
  font-size: 12px;
  color: #666;
}

.item-total {
  font-weight: 500;
  color: #1a1a1a;
}

.pricing-subtotals {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
}

.subtotal-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  font-size: 14px;
  color: #666;
}

.subtotal-row.total {
  font-weight: 600;
  font-size: 16px;
  color: #1a1a1a;
  border-top: 1px solid #dee2e6;
  margin-top: 8px;
  padding-top: 8px;
}

.pricing-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.pricing-actions button {
  flex: 1;
  padding: 12px 16px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary {
  background: #0077b6;
  color: white;
  border: none;
}

.btn-primary:hover {
  background: #005f8a;
}

.btn-secondary {
  background: white;
  color: #0077b6;
  border: 2px solid #0077b6;
}

.btn-secondary:hover {
  background: #f0f7fa;
}

.pricing-disclaimer {
  margin-top: 16px;
  font-size: 12px;
  color: #999;
  text-align: center;
  font-style: italic;
}
```

**Step 3: Commit**

```bash
git add frontend/src/components/PricingDisplay/
git commit -m "feat(frontend): add PricingDisplay component"
```

---

### Task 10: Integrate Pricing into ResultDetailPage

**Files:**
- Modify: `frontend/src/pages/ResultDetailPage.js`

**Step 1: Import and use PricingDisplay**

Add to ResultDetailPage.js:
```jsx
import PricingDisplay from '../components/PricingDisplay/PricingDisplay';

// In the component, after the image comparison section:
{result?.price_data && (
  <PricingDisplay
    priceData={result.price_data}
    onSaveQuote={() => console.log('Save quote')}
    onContactSales={() => console.log('Contact sales')}
  />
)}
```

**Step 2: Test the integration**

```bash
cd frontend
npm run dev
```

Navigate to a result page and verify pricing displays.

**Step 3: Commit**

```bash
git add frontend/src/pages/ResultDetailPage.js
git commit -m "feat(frontend): integrate pricing display in results page"
```

---

## Phase 4: Database Seeding

### Task 11: Create Price Book Migration Script

**Files:**
- Create: `api/pricing/management/__init__.py`
- Create: `api/pricing/management/commands/__init__.py`
- Create: `api/pricing/management/commands/seed_pricebook.py`

**Step 1: Create the management command**

```python
# api/pricing/management/commands/seed_pricebook.py
from django.core.management.base import BaseCommand
from api.pricing.models import Vertical, PriceBookCategory, PriceBookItem
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed the price book with default values from config'

    def handle(self, *args, **options):
        self.stdout.write('Seeding price book...')

        # Create Pools vertical
        pools, _ = Vertical.objects.update_or_create(
            id='pools',
            defaults={
                'name': 'pools',
                'display_name': 'Swimming Pools',
                'calculation_unit': 'project',
            }
        )

        # Pool Sizes category
        sizes_cat, _ = PriceBookCategory.objects.update_or_create(
            vertical=pools,
            slug='pool_sizes',
            defaults={'name': 'Pool Sizes', 'sort_order': 1}
        )

        pool_sizes = [
            ('starter', 'Starter (12x24)', Decimal('50000')),
            ('classic', 'Classic (15x30)', Decimal('65000')),
            ('family', 'Family (16x36)', Decimal('75000')),
            ('resort', 'Resort (18x40)', Decimal('95000')),
        ]

        for item_id, name, price in pool_sizes:
            PriceBookItem.objects.update_or_create(
                category=sizes_cat,
                item_id=item_id,
                defaults={'name': name, 'base_price': price}
            )

        # Interior Finishes category
        finishes_cat, _ = PriceBookCategory.objects.update_or_create(
            vertical=pools,
            slug='interior_finishes',
            defaults={'name': 'Interior Finishes', 'sort_order': 2}
        )

        finishes = [
            ('white_plaster', 'White Plaster', Decimal('0')),
            ('pebble_blue', 'Pebble Tec - Blue', Decimal('8000')),
            ('pebble_midnight', 'Pebble Tec - Midnight', Decimal('9000')),
            ('quartz_blue', 'Quartz - Ocean Blue', Decimal('6000')),
            ('glass_tile', 'Glass Tile', Decimal('15000')),
        ]

        for item_id, name, price in finishes:
            PriceBookItem.objects.update_or_create(
                category=finishes_cat,
                item_id=item_id,
                defaults={'name': name, 'base_price': price}
            )

        # Water Features category
        water_cat, _ = PriceBookCategory.objects.update_or_create(
            vertical=pools,
            slug='water_features',
            defaults={'name': 'Water Features', 'sort_order': 3}
        )

        water_features = [
            ('rock_waterfall', 'Rock Waterfall', Decimal('8000')),
            ('bubblers', 'Bubblers / Fountain Jets', Decimal('2500')),
            ('scuppers', 'Scuppers', Decimal('4500')),
            ('fire_bowls', 'Fire Bowls', Decimal('3500')),
            ('deck_jets', 'Deck Jets', Decimal('3000')),
        ]

        for item_id, name, price in water_features:
            PriceBookItem.objects.update_or_create(
                category=water_cat,
                item_id=item_id,
                defaults={'name': name, 'base_price': price}
            )

        self.stdout.write(self.style.SUCCESS('Price book seeded successfully!'))
```

**Step 2: Create directory structure and run**

```bash
mkdir -p api/pricing/management/commands
touch api/pricing/management/__init__.py
touch api/pricing/management/commands/__init__.py
python3 manage.py seed_pricebook
```

**Step 3: Verify in admin**

Navigate to http://localhost:8006/admin/pricing/ and verify data.

**Step 4: Commit**

```bash
git add api/pricing/management/
git commit -m "feat(pricing): add price book seeding command"
```

---

## Summary

**Total Tasks:** 11 tasks across 4 phases

**Phase 1 (Core Infrastructure):** Tasks 1-6
- Pricing app structure, models, admin, base calculator, pools calculator, factory

**Phase 2 (API Integration):** Tasks 7-8
- Pricing API endpoint, visualization flow integration

**Phase 3 (Frontend):** Tasks 9-10
- PricingDisplay component, ResultDetailPage integration

**Phase 4 (Data):** Task 11
- Price book seeding from config.py

**Future Phases (not in this plan):**
- Phase 5: Other vertical calculators (roofing, solar, windows, security)
- Phase 6: Contractor override admin UI
- Phase 7: Regional pricing adjustments
- Phase 8: TCO calculations and value-based selling
