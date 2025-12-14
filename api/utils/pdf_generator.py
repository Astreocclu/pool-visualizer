import io
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.conf import settings
from PIL import Image as PILImage

# Pool pricing estimates
PRICING = {
    'starter': 50000,
    'classic': 65000,
    'family': 75000,
    'resort': 95000,
    'tanning_ledge': 4500,
    'attached_spa': 15000,
    'deck_per_sqft': 30,
    'led_lighting': 2500,
}

def calculate_quote(visualization_request):
    """
    Calculate quote based on pool selections.
    """
    options = visualization_request.options or {}
    items = []
    total = 0

    # Pool base price
    size = options.get('size', 'classic')
    pool_price = PRICING.get(size, PRICING['classic'])
    items.append({
        'name': f'Pool Construction ({size.title()})',
        'qty': 1,
        'unit_price': pool_price,
        'subtotal': pool_price
    })
    total += pool_price

    # Tanning ledge
    if options.get('tanning_ledge', True):
        items.append({
            'name': 'Tanning Ledge (Baja Shelf)',
            'qty': 1,
            'unit_price': PRICING['tanning_ledge'],
            'subtotal': PRICING['tanning_ledge']
        })
        total += PRICING['tanning_ledge']

    # Attached spa
    if options.get('attached_spa'):
        items.append({
            'name': 'Attached Spa',
            'qty': 1,
            'unit_price': PRICING['attached_spa'],
            'subtotal': PRICING['attached_spa']
        })
        total += PRICING['attached_spa']

    # Deck estimate (assume 400 sq ft)
    deck_total = 400 * PRICING['deck_per_sqft']
    items.append({
        'name': 'Pool Deck (~400 sq ft)',
        'qty': 1,
        'unit_price': deck_total,
        'subtotal': deck_total
    })
    total += deck_total

    # LED lighting
    if options.get('lighting') and options.get('lighting') != 'none':
        items.append({
            'name': 'LED Lighting Package',
            'qty': 1,
            'unit_price': PRICING['led_lighting'],
            'subtotal': PRICING['led_lighting']
        })
        total += PRICING['led_lighting']

    return {'items': items, 'total': total}

def generate_visualization_pdf(visualization_request):
    """
    Generate a Pool Design Proposal PDF.

    Pages:
    1. Cover - Pool Design Proposal
    2. Your Backyard - Before image
    3. Your Dream Pool - After visualization
    4. Design Specifications
    5. Investment Estimate
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    elements = []
    styles = getSampleStyleSheet()

    # Custom Styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=1,  # Center
        spaceAfter=20,
        textColor=colors.HexColor('#0066CC')  # Pool Blue
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=18,
        alignment=1,
        spaceAfter=10,
        textColor=colors.HexColor('#004488')  # Darker Blue
    )

    body_style = styles['Normal']
    body_style.fontSize = 12

    # --- Helper: Logo ---
    def get_logo():
        logo_path = os.path.join(settings.BASE_DIR, 'frontend', 'public', 'logo512.png')
        if os.path.exists(logo_path):
            return RLImage(logo_path, width=1.5*inch, height=1.5*inch)
        return Paragraph("POOL VISUALIZER AI", title_style)

    # --- Page 1: Cover ---
    elements.append(get_logo())
    elements.append(Spacer(1, 0.5*inch))

    elements.append(Paragraph("Pool Design Proposal", title_style))
    elements.append(Spacer(1, 0.2*inch))

    # Hero Image (Use cleaned image if available)
    hero_image = None
    if hasattr(visualization_request, 'clean_image') and visualization_request.clean_image:
        hero_image = visualization_request.clean_image
    elif visualization_request.original_image:
        hero_image = visualization_request.original_image

    if hero_image:
        img_path = hero_image.path
        if os.path.exists(img_path):
            img = _get_resized_image(img_path, width=6*inch, height=4*inch)
            elements.append(img)

    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Prepared by Pool Visualizer AI", subtitle_style))
    elements.append(PageBreak())

    # --- Page 2: Your Backyard ---
    elements.append(Paragraph("Your Backyard", title_style))
    elements.append(Spacer(1, 0.2*inch))

    elements.append(Paragraph(
        "Our AI analyzed your backyard to create the perfect pool placement.",
        body_style
    ))
    elements.append(Spacer(1, 0.2*inch))

    # Before image
    if visualization_request.original_image:
        img_path = visualization_request.original_image.path
        if os.path.exists(img_path):
            img = _get_resized_image(img_path, width=5*inch, height=3.5*inch)
            elements.append(img)
            elements.append(Paragraph("Original Backyard", ParagraphStyle('Caption', parent=body_style, alignment=1)))

    elements.append(PageBreak())

    # --- Page 3: Your Dream Pool ---
    elements.append(Paragraph("Your Dream Pool", title_style))

    # After Image
    generated_result = visualization_request.results.first()
    if generated_result and generated_result.generated_image:
        img_path = generated_result.generated_image.path
        if os.path.exists(img_path):
            img = _get_resized_image(img_path, width=6*inch, height=4*inch)
            elements.append(img)
            elements.append(Paragraph("AI-Generated Pool Visualization", subtitle_style))

    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(
        "This visualization shows how your new pool could look. Final design may vary based on site conditions.",
        body_style
    ))
    elements.append(PageBreak())

    # --- Page 4: Design Specifications ---
    elements.append(Paragraph("Design Specifications", title_style))

    options = visualization_request.options or {}

    specs = [
        ["Feature", "Selection"],
        ["Pool Size", options.get('size', 'Classic').title()],
        ["Pool Shape", options.get('shape', 'Rectangle').title()],
        ["Interior Finish", options.get('finish', 'Pebble Blue').replace('_', ' ').title()],
        ["Deck Material", options.get('deck_material', 'Travertine').title()],
        ["Deck Color", options.get('deck_color', 'Cream').title()],
    ]

    # Add features
    if options.get('tanning_ledge', True):
        specs.append(["Tanning Ledge", "Included"])
    if options.get('attached_spa'):
        specs.append(["Attached Spa", "Included"])
    if options.get('water_features'):
        specs.append(["Water Features", ", ".join(options.get('water_features', []))])

    t = Table(specs, colWidths=[3*inch, 3*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066CC')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(t)
    elements.append(PageBreak())

    # --- Page 5: Investment Estimate ---
    elements.append(Paragraph("Investment Estimate", title_style))

    quote = calculate_quote(visualization_request)
    table_rows = [["Item", "Quantity", "Unit Price", "Total"]]

    for item in quote['items']:
        table_rows.append([
            item['name'],
            str(item['qty']),
            f"${item['unit_price']:,}",
            f"${item['subtotal']:,}"
        ])

    table_rows.append(["", "", "ESTIMATED TOTAL", f"${quote['total']:,}"])

    t_quote = Table(table_rows, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    t_quote.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(t_quote)

    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Important Notes", subtitle_style))
    elements.append(Paragraph("""
    This is an AI-generated visualization and cost estimate for planning purposes only.
    Actual pricing will vary based on:
    • Site conditions (soil, access, slopes)
    • Local permit requirements
    • Material availability and selections
    • Contractor pricing in your area

    We recommend obtaining quotes from licensed pool contractors in your area.
    """, body_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer

def _get_resized_image(path, width, height):
    """Helper to load and resize image for ReportLab."""
    try:
        img = RLImage(path, width=width, height=height)
        img.hAlign = 'CENTER'
        return img
    except Exception:
        return Paragraph("[Image Missing]", ParagraphStyle('Error'))
