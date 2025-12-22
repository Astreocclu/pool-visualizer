"""
Reference Image Service - Fetches reference images for product options.
"""
import logging
from typing import Dict, Optional
from PIL import Image

from api.models import ReferenceImage

logger = logging.getLogger(__name__)


def get_reference_image(
    tenant_id: str,
    category: str,
    option_value: str
) -> Optional[Image.Image]:
    """
    Fetch a reference image for a specific tenant/category/option.

    Args:
        tenant_id: Tenant identifier (e.g., 'screens', 'pools')
        category: Product category key (e.g., 'mesh_type', 'frame_color')
        option_value: Option value (e.g., 'black', 'bronze')

    Returns:
        PIL Image if found, None otherwise
    """
    ref = ReferenceImage.objects.filter(
        tenant_id=tenant_id,
        category=category,
        option_value=option_value
    ).first()

    if not ref:
        logger.debug(f"No reference image for {tenant_id}/{category}/{option_value}")
        return None

    try:
        return Image.open(ref.image.path)
    except Exception as e:
        logger.error(f"Failed to load reference image: {e}")
        return None


def get_reference_images_for_options(
    tenant_id: str,
    options: Dict[str, str]
) -> Dict[str, Image.Image]:
    """
    Fetch all reference images for a set of product options.

    Args:
        tenant_id: Tenant identifier
        options: Dict mapping category to option_value

    Returns:
        Dict mapping category to PIL Image (only includes found images)
    """
    result = {}
    for category, option_value in options.items():
        img = get_reference_image(tenant_id, category, option_value)
        if img:
            result[category] = img
    return result
