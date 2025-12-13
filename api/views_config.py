from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from api.tenants import get_tenant_config


class TenantConfigView(APIView):
    """Return tenant configuration for frontend."""
    permission_classes = [AllowAny]

    def get(self, request):
        config = get_tenant_config()
        return Response(config.get_schema())
