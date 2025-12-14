"""Debug views for capturing frontend errors."""
import json
from collections import deque
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# In-memory error store (last 100 errors)
_error_store = deque(maxlen=100)


@csrf_exempt
@require_http_methods(["GET", "POST", "DELETE"])
def debug_errors(request):
    """
    GET: Return all captured errors
    POST: Add a new error
    DELETE: Clear all errors
    """
    if request.method == "GET":
        return JsonResponse({
            "count": len(_error_store),
            "errors": list(_error_store)
        })

    elif request.method == "POST":
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            data = {"raw": request.body.decode("utf-8", errors="replace")}

        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": data.get("type", "unknown"),
            "message": data.get("message", ""),
            "filename": data.get("filename", ""),
            "lineno": data.get("lineno"),
            "colno": data.get("colno"),
            "stack": data.get("stack", ""),
            "url": data.get("url", ""),
            "userAgent": data.get("userAgent", ""),
            "extra": data.get("extra", {}),
        }
        _error_store.append(error_entry)
        return JsonResponse({"status": "captured", "id": len(_error_store) - 1})

    elif request.method == "DELETE":
        _error_store.clear()
        return JsonResponse({"status": "cleared"})
