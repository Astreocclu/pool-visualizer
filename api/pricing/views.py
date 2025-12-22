from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

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
    permission_classes = [permissions.AllowAny]  # Dev mode - no auth required

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
