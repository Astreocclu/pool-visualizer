from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('config/', views.ConfigView.as_view(), name='config'),
    path('deposit/create-checkout/', views.CreateDepositCheckoutView.as_view(), name='deposit-checkout'),
    path('deposit/<int:visualization_id>/status/', views.DepositStatusView.as_view(), name='deposit-status'),
    path('subscription/create-checkout/', views.CreateSubscriptionCheckoutView.as_view(), name='subscription-checkout'),
    path('webhook/', views.StripeWebhookView.as_view(), name='webhook'),
]
