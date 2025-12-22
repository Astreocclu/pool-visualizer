from django.contrib import admin
from .models import (
    Vertical,
    PriceBookCategory,
    PriceBookItem,
    ContractorProfile,
    ContractorPriceOverride,
    PriceCalculationLog,
)


@admin.register(Vertical)
class VerticalAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_name', 'calculation_unit', 'is_active')
    list_filter = ('is_active', 'calculation_unit')
    search_fields = ('id', 'name', 'display_name')


class PriceBookItemInline(admin.TabularInline):
    model = PriceBookItem
    fields = ('item_id', 'name', 'base_price', 'price_multiplier', 'is_active', 'sort_order')
    extra = 1
    ordering = ('sort_order',)


@admin.register(PriceBookCategory)
class PriceBookCategoryAdmin(admin.ModelAdmin):
    list_display = ('vertical', 'slug', 'name', 'sort_order')
    list_filter = ('vertical',)
    search_fields = ('slug', 'name')
    inlines = [PriceBookItemInline]


@admin.register(PriceBookItem)
class PriceBookItemAdmin(admin.ModelAdmin):
    list_display = ('category', 'item_id', 'name', 'base_price', 'is_active')
    list_filter = ('category__vertical', 'is_active')
    search_fields = ('item_id', 'name')
    ordering = ('category', 'sort_order')


class ContractorPriceOverrideInline(admin.TabularInline):
    model = ContractorPriceOverride
    extra = 0
    fields = ('price_book_item', 'custom_price', 'price_adjustment_percent', 'effective_date', 'expires_date')


@admin.register(ContractorProfile)
class ContractorProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'overhead_percent', 'profit_margin_percent', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('company_name', 'user__username', 'user__email')
    inlines = [ContractorPriceOverrideInline]


@admin.register(ContractorPriceOverride)
class ContractorPriceOverrideAdmin(admin.ModelAdmin):
    list_display = ('contractor', 'price_book_item', 'custom_price', 'price_adjustment_percent')
    list_filter = ('contractor',)
    search_fields = ('contractor__company_name', 'price_book_item__name')


@admin.register(PriceCalculationLog)
class PriceCalculationLogAdmin(admin.ModelAdmin):
    list_display = ('vertical', 'contractor', 'final_price', 'calculation_type', 'created_at')
    list_filter = ('vertical', 'calculation_type')
    readonly_fields = ('vertical', 'contractor', 'input_config', 'cost_breakdown', 'final_price', 'calculation_type', 'created_at')
    search_fields = ('vertical', 'contractor__company_name')

    def has_add_permission(self, request):
        # Prevent adding new calculation logs (audit trail only)
        return False

    def has_delete_permission(self, request, obj=None):
        # Prevent deleting calculation logs (audit trail)
        return False
