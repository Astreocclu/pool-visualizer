"""
PDF Style System for TrustHome Visualizer.
Provides consistent typography, colors, and spacing across all PDF pages.
"""
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch

# Tenant color palettes
TENANT_COLORS = {
    'pools': {
        'primary': '#0077b6',
        'secondary': '#00b4d8',
        'accent': '#f77f00',
    },
    'windows': {
        'primary': '#2E7D32',
        'secondary': '#66BB6A',
        'accent': '#FF8F00',
    },
    'roofs': {
        'primary': '#D84315',
        'secondary': '#FF7043',
        'accent': '#1565C0',
    },
    'screens': {
        'primary': '#1565C0',
        'secondary': '#42A5F5',
        'accent': '#FF6F00',
    },
}

# Spacing constants (8pt grid)
MARGIN = 0.6 * inch
SECTION_SPACE = 24
PARAGRAPH_SPACE = 12
ELEMENT_SPACE = 8


def get_tenant_colors(tenant_id: str) -> dict:
    """Get color palette for tenant."""
    palette = TENANT_COLORS.get(tenant_id, TENANT_COLORS['pools'])
    return {
        'primary': colors.HexColor(palette['primary']),
        'secondary': colors.HexColor(palette['secondary']),
        'accent': colors.HexColor(palette['accent']),
        'text_dark': colors.HexColor('#333333'),
        'text_light': colors.HexColor('#666666'),
        'bg_light': colors.HexColor('#F8F9FA'),
        'white': colors.white,
        'black': colors.black,
    }


def get_styles(tenant_id: str) -> dict:
    """Get paragraph styles for tenant."""
    c = get_tenant_colors(tenant_id)
    base = getSampleStyleSheet()

    return {
        'title': ParagraphStyle(
            'Title',
            parent=base['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=28,
            textColor=c['primary'],
            alignment=1,  # Center
            spaceAfter=SECTION_SPACE,
        ),
        'subtitle': ParagraphStyle(
            'Subtitle',
            parent=base['Heading2'],
            fontName='Helvetica',
            fontSize=16,
            textColor=c['text_light'],
            alignment=1,
            spaceAfter=PARAGRAPH_SPACE,
        ),
        'heading': ParagraphStyle(
            'Heading',
            parent=base['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=c['primary'],
            spaceBefore=SECTION_SPACE,
            spaceAfter=PARAGRAPH_SPACE,
        ),
        'subheading': ParagraphStyle(
            'Subheading',
            parent=base['Heading3'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=c['text_dark'],
            spaceBefore=PARAGRAPH_SPACE,
            spaceAfter=ELEMENT_SPACE,
        ),
        'body': ParagraphStyle(
            'Body',
            parent=base['Normal'],
            fontName='Helvetica',
            fontSize=11,
            textColor=c['text_dark'],
            leading=16,  # Line height
            spaceAfter=ELEMENT_SPACE,
        ),
        'body_center': ParagraphStyle(
            'BodyCenter',
            parent=base['Normal'],
            fontName='Helvetica',
            fontSize=11,
            textColor=c['text_dark'],
            alignment=1,
            spaceAfter=ELEMENT_SPACE,
        ),
        'caption': ParagraphStyle(
            'Caption',
            parent=base['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=9,
            textColor=c['text_light'],
            alignment=1,
        ),
        'disclaimer': ParagraphStyle(
            'Disclaimer',
            parent=base['Normal'],
            fontName='Helvetica',
            fontSize=8,
            textColor=c['text_light'],
            leading=10,
        ),
        'price_large': ParagraphStyle(
            'PriceLarge',
            parent=base['Normal'],
            fontName='Times-Bold',
            fontSize=24,
            textColor=c['primary'],
            alignment=1,
        ),
        'cta': ParagraphStyle(
            'CTA',
            parent=base['Normal'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=c['accent'],
            alignment=1,
            spaceAfter=PARAGRAPH_SPACE,
        ),
    }
