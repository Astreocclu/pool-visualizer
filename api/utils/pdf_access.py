import hashlib
import hmac

from django.conf import settings


def build_pdf_signature(lead_id, visualization_id):
    """Build an HMAC signature for PDF access links."""
    payload = f"{lead_id}:{visualization_id}".encode("utf-8")
    secret = settings.SECRET_KEY.encode("utf-8")
    return hmac.new(secret, payload, hashlib.sha256).hexdigest()


def verify_pdf_signature(lead_id, visualization_id, signature):
    """Verify PDF access link signature."""
    if not signature:
        return False
    expected = build_pdf_signature(lead_id, visualization_id)
    return hmac.compare_digest(expected, signature)
