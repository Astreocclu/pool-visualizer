from django.contrib import admin
from .models import HomeownerDeposit, ContractorSubscription


@admin.register(HomeownerDeposit)
class HomeownerDepositAdmin(admin.ModelAdmin):
    list_display = ['id', 'lead', 'amount', 'status', 'created_at', 'paid_at']
    list_filter = ['status', 'created_at']
    search_fields = ['lead__name', 'lead__email', 'stripe_checkout_session_id']
    readonly_fields = ['stripe_checkout_session_id', 'stripe_payment_intent_id', 'created_at']
    date_hierarchy = 'created_at'


@admin.register(ContractorSubscription)
class ContractorSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'contractor', 'status', 'current_period_end', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['contractor__company_name', 'stripe_subscription_id']
    readonly_fields = ['stripe_customer_id', 'stripe_subscription_id', 'created_at']
    date_hierarchy = 'created_at'
