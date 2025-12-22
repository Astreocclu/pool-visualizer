from django.urls import path
from .views import CalculatePriceView

urlpatterns = [
    path('<str:vertical_id>/calculate/', CalculatePriceView.as_view(), name='calculate-price'),
]
