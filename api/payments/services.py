import logging
import stripe
from django.conf import settings
from django.utils import timezone
from .models import HomeownerDeposit, ContractorSubscription

logger = logging.getLogger(__name__)


class StripeService:
    """
    Wrapper for Stripe API operations.
    All Stripe interactions go through this service.
    """

    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_deposit_checkout_session(self, lead, visualization, success_url, cancel_url):
        """
        Create a Stripe Checkout session for homeowner deposit.

        Args:
            lead: Lead model instance
            visualization: VisualizationRequest model instance
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if payment cancelled

        Returns:
            tuple: (checkout_session, HomeownerDeposit instance)
        """
        if not settings.ENABLE_PAYMENTS:
            raise ValueError("Payments are not enabled")

        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': settings.STRIPE_DEPOSIT_PRICE_ID,
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=lead.email,
            metadata={
                'lead_id': str(lead.id),
                'visualization_id': str(visualization.id),
                'type': 'homeowner_deposit',
            },
        )

        # Create local deposit record
        deposit = HomeownerDeposit.objects.create(
            lead=lead,
            visualization=visualization,
            stripe_checkout_session_id=checkout_session.id,
            amount=settings.HOMEOWNER_DEPOSIT_AMOUNT,
            status='pending',
        )

        return checkout_session, deposit

    def create_subscription_checkout_session(self, contractor, success_url, cancel_url):
        """
        Create a Stripe Checkout session for contractor subscription.

        Args:
            contractor: ContractorProfile model instance
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if payment cancelled

        Returns:
            checkout_session: Stripe Checkout Session object
        """
        if not settings.ENABLE_PAYMENTS:
            raise ValueError("Payments are not enabled")

        # Get or create Stripe customer
        if hasattr(contractor, 'subscription') and contractor.subscription.stripe_customer_id:
            customer_id = contractor.subscription.stripe_customer_id
        else:
            customer = stripe.Customer.create(
                email=contractor.user.email if contractor.user else None,
                name=contractor.company_name,
                metadata={'contractor_id': str(contractor.id)},
            )
            customer_id = customer.id

        # Create Checkout Session for subscription
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': settings.STRIPE_SUBSCRIPTION_PRICE_ID,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            customer=customer_id,
            metadata={
                'contractor_id': str(contractor.id),
                'type': 'contractor_subscription',
            },
        )

        return checkout_session

    def handle_checkout_completed(self, session):
        """
        Handle checkout.session.completed webhook event.

        Args:
            session: Stripe Session object from webhook
        """
        session_type = session.metadata.get('type')

        if session_type == 'homeowner_deposit':
            self._handle_deposit_completed(session)
        elif session_type == 'contractor_subscription':
            self._handle_subscription_completed(session)

    def _handle_deposit_completed(self, session):
        """Mark deposit as paid."""
        try:
            deposit = HomeownerDeposit.objects.get(
                stripe_checkout_session_id=session.id
            )
            deposit.status = 'paid'
            deposit.paid_at = timezone.now()
            if session.payment_intent:
                deposit.stripe_payment_intent_id = session.payment_intent
            deposit.save()
        except HomeownerDeposit.DoesNotExist:
            logger.error(f"Deposit not found for session {session.id}")

    def _handle_subscription_completed(self, session):
        """Create or update contractor subscription."""
        from api.pricing.models import ContractorProfile

        contractor_id = session.metadata.get('contractor_id')
        if not contractor_id:
            return

        try:
            contractor = ContractorProfile.objects.get(id=contractor_id)

            # Get subscription details from Stripe
            subscription = stripe.Subscription.retrieve(session.subscription)

            ContractorSubscription.objects.update_or_create(
                contractor=contractor,
                defaults={
                    'stripe_customer_id': session.customer,
                    'stripe_subscription_id': subscription.id,
                    'status': 'active',
                    'current_period_end': timezone.datetime.fromtimestamp(
                        subscription.current_period_end,
                        tz=timezone.utc
                    ),
                }
            )
        except ContractorProfile.DoesNotExist:
            logger.error(f"Contractor {contractor_id} not found for subscription")

    def handle_invoice_paid(self, invoice):
        """Handle successful subscription renewal."""
        subscription_id = invoice.subscription
        if not subscription_id:
            return

        try:
            sub = ContractorSubscription.objects.get(
                stripe_subscription_id=subscription_id
            )
            stripe_sub = stripe.Subscription.retrieve(subscription_id)
            sub.status = 'active'
            sub.current_period_end = timezone.datetime.fromtimestamp(
                stripe_sub.current_period_end,
                tz=timezone.utc
            )
            sub.save()
        except ContractorSubscription.DoesNotExist:
            pass

    def handle_invoice_failed(self, invoice):
        """Handle failed subscription payment."""
        subscription_id = invoice.subscription
        if not subscription_id:
            return

        try:
            sub = ContractorSubscription.objects.get(
                stripe_subscription_id=subscription_id
            )
            sub.status = 'past_due'
            sub.save()
        except ContractorSubscription.DoesNotExist:
            pass

    def handle_subscription_deleted(self, subscription):
        """Handle subscription cancellation."""
        try:
            sub = ContractorSubscription.objects.get(
                stripe_subscription_id=subscription.id
            )
            sub.status = 'canceled'
            sub.canceled_at = timezone.now()
            sub.save()
        except ContractorSubscription.DoesNotExist:
            pass


# Singleton instance
stripe_service = StripeService()
