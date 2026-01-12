from decimal import Decimal
from django.db import models
from django.conf import settings


class HomeownerDeposit(models.Model):
    """
    Tracks $500 deposits from homeowners after visualization.
    Deposit is credited toward contractor invoice when project starts.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
        ('credited', 'Credited to Invoice'),
    ]

    lead = models.OneToOneField(
        'api.Lead',
        on_delete=models.PROTECT,
        related_name='deposit',
        help_text="Lead who made this deposit"
    )
    visualization = models.ForeignKey(
        'api.VisualizationRequest',
        on_delete=models.PROTECT,
        related_name='deposits',
        help_text="Visualization this deposit is for"
    )

    # Stripe identifiers
    stripe_checkout_session_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="Stripe Checkout Session ID"
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Stripe Payment Intent ID (set after payment)"
    )

    # Amount and status
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('500.00'),
        help_text="Deposit amount in dollars"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Credit tracking
    credited_to_contractor = models.ForeignKey(
        'pricing.ContractorProfile',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Contractor this deposit was credited to"
    )
    credited_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Homeowner Deposit"
        verbose_name_plural = "Homeowner Deposits"
        ordering = ['-created_at']

    def __str__(self):
        return f"Deposit ${self.amount} - {self.lead.name} ({self.status})"


class ContractorSubscription(models.Model):
    """
    Tracks $100/month subscriptions for contractors to access visualizer.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('incomplete', 'Incomplete'),
    ]

    contractor = models.OneToOneField(
        'pricing.ContractorProfile',
        on_delete=models.CASCADE,
        related_name='subscription',
        help_text="Contractor with this subscription"
    )

    # Stripe identifiers
    stripe_customer_id = models.CharField(
        max_length=255,
        help_text="Stripe Customer ID"
    )
    stripe_subscription_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="Stripe Subscription ID"
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='incomplete'
    )
    current_period_end = models.DateTimeField(
        help_text="When current billing period ends"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    canceled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Contractor Subscription"
        verbose_name_plural = "Contractor Subscriptions"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.contractor.company_name} - {self.status}"

    @property
    def is_active(self):
        return self.status == 'active'
