import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from api.models import Lead, VisualizationRequest
from .services import stripe_service
from .models import HomeownerDeposit


class ConfigView(APIView):
    """
    Public endpoint returning feature flags and public keys.
    GET /api/payments/config/
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'payments_enabled': settings.ENABLE_PAYMENTS,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY if settings.ENABLE_PAYMENTS else None,
            'deposit_amount': settings.HOMEOWNER_DEPOSIT_AMOUNT,
            'subscription_amount': settings.CONTRACTOR_SUBSCRIPTION_AMOUNT,
        })


class CreateDepositCheckoutView(APIView):
    """
    Create Stripe Checkout session for homeowner deposit.
    POST /api/payments/deposit/create-checkout/
    """
    permission_classes = [AllowAny]  # Homeowners don't have accounts

    def post(self, request):
        if not settings.ENABLE_PAYMENTS:
            return Response(
                {'error': 'Payments are not enabled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        lead_id = request.data.get('lead_id')
        visualization_id = request.data.get('visualization_id')

        if not lead_id or not visualization_id:
            return Response(
                {'error': 'lead_id and visualization_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lead = Lead.objects.get(id=lead_id)
            visualization = VisualizationRequest.objects.get(id=visualization_id)
        except (Lead.DoesNotExist, VisualizationRequest.DoesNotExist):
            return Response(
                {'error': 'Lead or visualization not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        if lead.visualization_id != visualization.id:
            return Response(
                {'error': 'Lead does not match visualization'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if deposit already exists and is paid
        existing_deposit = HomeownerDeposit.objects.filter(
            lead=lead, status='paid'
        ).first()
        if existing_deposit:
            return Response(
                {'error': 'Deposit already paid'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Build redirect URLs
        base_url = request.build_absolute_uri('/').rstrip('/')
        success_url = f"{base_url}/deposit/{visualization_id}/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{base_url}/results/{visualization_id}"

        try:
            checkout_session, deposit = stripe_service.create_deposit_checkout_session(
                lead=lead,
                visualization=visualization,
                success_url=success_url,
                cancel_url=cancel_url,
            )

            return Response({
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id,
                'deposit_id': deposit.id,
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DepositStatusView(APIView):
    """
    Check deposit payment status.
    GET /api/payments/deposit/<visualization_id>/status/
    """
    permission_classes = [AllowAny]

    def get(self, request, visualization_id):
        try:
            deposits = HomeownerDeposit.objects.filter(
                visualization_id=visualization_id
            ).order_by('-created_at')

            if not deposits.exists():
                return Response({'status': 'none', 'deposit': None})

            deposit = deposits.first()
            return Response({
                'status': deposit.status,
                'deposit': {
                    'id': deposit.id,
                    'amount': str(deposit.amount),
                    'status': deposit.status,
                    'paid_at': deposit.paid_at.isoformat() if deposit.paid_at else None,
                }
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreateSubscriptionCheckoutView(APIView):
    """
    Create Stripe Checkout session for contractor subscription.
    POST /api/payments/subscription/create-checkout/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not settings.ENABLE_PAYMENTS:
            return Response(
                {'error': 'Payments are not enabled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        contractor_id = request.data.get('contractor_id')

        if not contractor_id:
            return Response(
                {'error': 'contractor_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from api.pricing.models import ContractorProfile

        try:
            contractor = ContractorProfile.objects.get(id=contractor_id)
        except ContractorProfile.DoesNotExist:
            return Response(
                {'error': 'Contractor not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Build redirect URLs
        base_url = request.build_absolute_uri('/').rstrip('/')
        success_url = f"{base_url}/contractor/subscription/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{base_url}/contractor/dashboard"

        try:
            checkout_session = stripe_service.create_subscription_checkout_session(
                contractor=contractor,
                success_url=success_url,
                cancel_url=cancel_url,
            )

            return Response({
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id,
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """
    Handle Stripe webhook events.
    POST /api/payments/webhook/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)

        # Handle events
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            stripe_service.handle_checkout_completed(session)

        elif event['type'] == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            stripe_service.handle_invoice_paid(invoice)

        elif event['type'] == 'invoice.payment_failed':
            invoice = event['data']['object']
            stripe_service.handle_invoice_failed(invoice)

        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            stripe_service.handle_subscription_deleted(subscription)

        return HttpResponse(status=200)
