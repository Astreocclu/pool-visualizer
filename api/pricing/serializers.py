from rest_framework import serializers


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
