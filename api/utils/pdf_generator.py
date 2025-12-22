import io
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.conf import settings
from PIL import Image as PILImage

# Import pricing configs from each tenant
from api.tenants.pools.config import (
    POOL_SIZES, POOL_SHAPES, INTERIOR_FINISHES, BUILT_IN_FEATURES,
    DECK_MATERIALS, WATER_FEATURES, get_full_config_with_pricing as get_pools_pricing
)
from api.tenants.windows.config import (
    WINDOW_TYPES, FRAME_MATERIALS, GRILLE_PATTERNS, GLASS_OPTIONS,
    get_full_config_with_pricing as get_windows_pricing
)
from api.tenants.roofs.config import (
    ROOF_MATERIALS, SOLAR_OPTIONS, GUTTER_OPTIONS,
    get_full_config_with_pricing as get_roofs_pricing
)
from api.tenants.screens.config import (
    MESH_TYPES_PRICING, FRAME_COLORS_PRICING, COVERAGE_OPTIONS,
    INSTALLATION_BASE, INSTALLATION_PER_SQFT,
    get_full_config_with_pricing as get_screens_pricing
)


# ============== POOLS QUOTE CALCULATOR ==============
def calculate_pools_quote(visualization_request):
    """Calculate quote based on pool selections."""
    options = visualization_request.scope or {}
    items = []
    total = 0

    # Pool base price by size
    size_id = options.get('size', 'classic')
    size_data = next((s for s in POOL_SIZES if s['id'] == size_id), POOL_SIZES[1])  # default to classic
    pool_price = size_data.get('base_price', 65000)

    # Shape multiplier
    shape_id = options.get('shape', 'rectangle')
    shape_data = next((s for s in POOL_SHAPES if s['id'] == shape_id), POOL_SHAPES[0])
    shape_multiplier = shape_data.get('price_multiplier', 1.0)
    pool_price = int(pool_price * shape_multiplier)

    items.append({
        'name': f'Pool Construction ({size_data["name"]} - {shape_data["name"]})',
        'qty': 1,
        'unit_price': pool_price,
        'subtotal': pool_price
    })
    total += pool_price

    # Interior finish
    finish_id = options.get('interior_finish', 'white_plaster')
    finish_data = next((f for f in INTERIOR_FINISHES if f['id'] == finish_id), INTERIOR_FINISHES[0])
    finish_add = finish_data.get('price_add', 0)
    if finish_add > 0:
        items.append({
            'name': f'Interior Finish ({finish_data["name"]})',
            'qty': 1,
            'unit_price': finish_add,
            'subtotal': finish_add
        })
        total += finish_add

    # Built-in features
    if options.get('tanning_ledge', True):
        tanning_price = BUILT_IN_FEATURES['tanning_ledge']['price_add']
        items.append({
            'name': 'Tanning Ledge (Baja Shelf)',
            'qty': 1,
            'unit_price': tanning_price,
            'subtotal': tanning_price
        })
        total += tanning_price

    if options.get('attached_spa'):
        spa_price = BUILT_IN_FEATURES['attached_spa']['price_add']
        items.append({
            'name': 'Attached Spa (Spillover)',
            'qty': 1,
            'unit_price': spa_price,
            'subtotal': spa_price
        })
        total += spa_price

    # Deck (estimate 400 sq ft)
    deck_sqft = 400
    deck_material_id = options.get('deck_material', 'travertine')
    deck_data = next((d for d in DECK_MATERIALS if d['id'] == deck_material_id), DECK_MATERIALS[0])
    deck_price_per_sqft = deck_data.get('price_per_sqft', 18)
    deck_total = deck_sqft * deck_price_per_sqft
    items.append({
        'name': f'Pool Deck - {deck_data["name"]} (~{deck_sqft} sq ft)',
        'qty': deck_sqft,
        'unit_price': deck_price_per_sqft,
        'subtotal': deck_total
    })
    total += deck_total

    # Water features
    water_features_selected = options.get('water_features', [])
    for wf_id in water_features_selected:
        wf_data = next((w for w in WATER_FEATURES if w['id'] == wf_id), None)
        if wf_data:
            wf_price = wf_data.get('price_add', 0)
            items.append({
                'name': wf_data['name'],
                'qty': 1,
                'unit_price': wf_price,
                'subtotal': wf_price
            })
            total += wf_price

    return {'items': items, 'total': total}


# ============== WINDOWS QUOTE CALCULATOR ==============
def calculate_windows_quote(visualization_request, window_count=5):
    """Calculate quote based on window selections."""
    options = visualization_request.scope or {}
    items = []
    total = 0

    # Base window prices
    WINDOW_BASE_PRICES = {
        'single_hung': 350,
        'double_hung': 450,
        'casement': 500,
        'slider': 400,
        'picture': 300,
    }

    # Window base price
    window_type = options.get('window_type', 'double_hung')
    base_price = WINDOW_BASE_PRICES.get(window_type, 450)

    # Material multiplier
    material = options.get('frame_material', 'vinyl')
    material_data = next((m for m in FRAME_MATERIALS if m['id'] == material), FRAME_MATERIALS[0])
    multiplier = material_data.get('price_multiplier', 1.0)

    window_unit_price = int(base_price * multiplier)
    window_total = window_unit_price * window_count

    window_type_display = window_type.replace('_', ' ').title()
    items.append({
        'name': f'{window_type_display} Windows ({material_data["name"]})',
        'qty': window_count,
        'unit_price': window_unit_price,
        'subtotal': window_total
    })
    total += window_total

    # Grille pattern
    grille = options.get('grille_pattern', 'none')
    if grille != 'none':
        grille_price = 150
        grille_total = grille_price * window_count
        grille_display = grille.replace('_', ' ').title()
        items.append({
            'name': f'{grille_display} Grille Pattern',
            'qty': window_count,
            'unit_price': grille_price,
            'subtotal': grille_total
        })
        total += grille_total

    # Glass option
    glass = options.get('glass_option', 'clear')
    if glass not in ['clear', 'low_e']:
        glass_price = 100
        glass_total = glass_price * window_count
        glass_display = glass.replace('_', ' ').title()
        items.append({
            'name': f'{glass_display} Glass',
            'qty': window_count,
            'unit_price': glass_price,
            'subtotal': glass_total
        })
        total += glass_total

    # Installation
    install_price = 150
    install_total = install_price * window_count
    items.append({
        'name': 'Professional Installation',
        'qty': window_count,
        'unit_price': install_price,
        'subtotal': install_total
    })
    total += install_total

    return {'items': items, 'total': total}


# ============== ROOFS QUOTE CALCULATOR ==============
def calculate_roofs_quote(visualization_request, roof_sqft=2000):
    """Calculate quote based on roofing selections."""
    options = visualization_request.scope or {}
    items = []
    total = 0

    # Roof material
    material_id = options.get('roof_material', 'asphalt_architectural')
    material_data = next((m for m in ROOF_MATERIALS if m['id'] == material_id), ROOF_MATERIALS[1])
    price_per_sqft = material_data.get('price_per_sqft', 4.75)
    roof_total = int(roof_sqft * price_per_sqft)

    items.append({
        'name': f'{material_data["name"]} Roofing',
        'qty': roof_sqft,
        'unit_price': price_per_sqft,
        'subtotal': roof_total
    })
    total += roof_total

    # Solar option
    solar_id = options.get('solar_option', 'none')
    if solar_id != 'none':
        # Solar pricing: $3/watt, assume coverage percentages
        solar_watts = {
            'partial': 6000,       # ~6kW system
            'full_south': 10000,   # ~10kW system
            'full_all': 15000,     # ~15kW system
        }
        watts = solar_watts.get(solar_id, 6000)
        solar_price_per_watt = 3
        solar_total = watts * solar_price_per_watt
        solar_data = next((s for s in SOLAR_OPTIONS if s['id'] == solar_id), None)
        items.append({
            'name': f'Solar Panels ({solar_data["name"] if solar_data else solar_id})',
            'qty': watts,
            'unit_price': solar_price_per_watt,
            'subtotal': solar_total
        })
        total += solar_total

    # Gutters
    gutter_id = options.get('gutter_option', 'standard')
    if gutter_id != 'none':
        gutter_prices = {
            'standard': 8,    # per linear foot
            'seamless': 12,
            'copper': 35,
        }
        linear_ft = 200  # Estimate
        gutter_price = gutter_prices.get(gutter_id, 8)
        gutter_total = linear_ft * gutter_price
        gutter_data = next((g for g in GUTTER_OPTIONS if g['id'] == gutter_id), None)
        items.append({
            'name': f'{gutter_data["name"] if gutter_data else gutter_id} (~{linear_ft} LF)',
            'qty': linear_ft,
            'unit_price': gutter_price,
            'subtotal': gutter_total
        })
        total += gutter_total

    return {'items': items, 'total': total}


# ============== SCREENS QUOTE CALCULATOR ==============
def calculate_screens_quote(visualization_request):
    """Calculate quote based on security screen selections."""
    options = visualization_request.scope or {}
    items = []
    total = 0

    # Mesh type
    mesh_id = options.get('mesh_type', '12x12_standard')
    mesh_data = next((m for m in MESH_TYPES_PRICING if m['id'] == mesh_id), MESH_TYPES_PRICING[1])
    price_per_sqft = mesh_data.get('price_per_sqft', 15)

    # Calculate total sq ft from scope
    patio_sqft = 200 if options.get('patio', True) else 0
    window_count = options.get('window_count', 4)
    window_sqft = window_count * 10
    door_count = options.get('door_count', 1)

    # Patio enclosure
    if patio_sqft > 0:
        patio_total = patio_sqft * price_per_sqft
        items.append({
            'name': f'Patio Enclosure - {mesh_data["name"]} (~{patio_sqft} sq ft)',
            'qty': patio_sqft,
            'unit_price': price_per_sqft,
            'subtotal': patio_total
        })
        total += patio_total

    # Window screens
    if window_sqft > 0:
        window_total = window_sqft * price_per_sqft
        items.append({
            'name': f'Window Screens - {mesh_data["name"]} ({window_count} windows)',
            'qty': window_sqft,
            'unit_price': price_per_sqft,
            'subtotal': window_total
        })
        total += window_total

    # Door screens
    if door_count > 0:
        door_price = 800
        door_total = door_count * door_price
        items.append({
            'name': 'Security Screen Doors',
            'qty': door_count,
            'unit_price': door_price,
            'subtotal': door_total
        })
        total += door_total

    # Frame color upgrade
    frame_color = options.get('frame_color', 'black')
    frame_data = next((f for f in FRAME_COLORS_PRICING if f['id'] == frame_color), None)
    if frame_data and frame_data.get('price_add', 0) > 0:
        items.append({
            'name': f'Frame Color Upgrade ({frame_data["name"]})',
            'qty': 1,
            'unit_price': frame_data['price_add'],
            'subtotal': frame_data['price_add']
        })
        total += frame_data['price_add']

    # Installation
    total_sqft = patio_sqft + window_sqft
    install_total = INSTALLATION_BASE + (total_sqft * INSTALLATION_PER_SQFT)
    items.append({
        'name': 'Professional Installation',
        'qty': 1,
        'unit_price': install_total,
        'subtotal': install_total
    })
    total += install_total

    return {'items': items, 'total': total}


# ============== TENANT ROUTER ==============
def calculate_quote_for_tenant(visualization_request):
    """Route to the correct quote calculator based on tenant."""
    tenant_id = getattr(visualization_request, 'tenant_id', 'pools')

    if tenant_id == 'pools':
        return calculate_pools_quote(visualization_request)
    elif tenant_id == 'windows':
        return calculate_windows_quote(visualization_request)
    elif tenant_id == 'roofs':
        return calculate_roofs_quote(visualization_request)
    elif tenant_id == 'screens':
        return calculate_screens_quote(visualization_request)
    else:
        # Fallback to pools
        return calculate_pools_quote(visualization_request)


def get_specs_for_tenant(visualization_request):
    """Get design specifications table based on tenant."""
    tenant_id = getattr(visualization_request, 'tenant_id', 'pools')
    options = visualization_request.scope or {}

    if tenant_id == 'pools':
        return [
            ["Feature", "Selection"],
            ["Pool Size", options.get('size', 'Classic').replace('_', ' ').title()],
            ["Pool Shape", options.get('shape', 'Rectangle').replace('_', ' ').title()],
            ["Interior Finish", options.get('interior_finish', 'Pebble Blue').replace('_', ' ').title()],
            ["Deck Material", options.get('deck_material', 'Travertine').replace('_', ' ').title()],
            ["Deck Color", options.get('deck_color', 'Cream').replace('_', ' ').title()],
            ["Tanning Ledge", "Included" if options.get('tanning_ledge', True) else "Not Included"],
            ["Attached Spa", "Included" if options.get('attached_spa') else "Not Included"],
        ]
    elif tenant_id == 'windows':
        return [
            ["Feature", "Selection"],
            ["Window Type", options.get('window_type', 'Double Hung').replace('_', ' ').title()],
            ["Frame Material", options.get('frame_material', 'Vinyl').replace('_', ' ').title()],
            ["Frame Color", options.get('frame_color', 'White').replace('_', ' ').title()],
            ["Grille Pattern", options.get('grille_pattern', 'None').replace('_', ' ').title()],
            ["Glass Option", options.get('glass_option', 'Clear').replace('_', ' ').title()],
        ]
    elif tenant_id == 'roofs':
        return [
            ["Feature", "Selection"],
            ["Roof Material", options.get('roof_material', 'Asphalt Architectural').replace('_', ' ').title()],
            ["Roof Color", options.get('roof_color', 'Charcoal').replace('_', ' ').title()],
            ["Solar Option", options.get('solar_option', 'None').replace('_', ' ').title()],
            ["Gutter System", options.get('gutter_option', 'Standard').replace('_', ' ').title()],
        ]
    elif tenant_id == 'screens':
        return [
            ["Feature", "Selection"],
            ["Mesh Type", options.get('mesh_type', '12x12 Standard').replace('_', ' ').title()],
            ["Frame Color", options.get('frame_color', 'Black').replace('_', ' ').title()],
            ["Mesh Color", options.get('mesh_color', 'Black').replace('_', ' ').title()],
            ["Patio Enclosure", "Included" if options.get('patio', True) else "Not Included"],
            ["Window Count", str(options.get('window_count', 4))],
            ["Door Count", str(options.get('door_count', 1))],
        ]
    else:
        return [["Feature", "Selection"], ["Configuration", "Custom"]]


def get_tenant_display_name(tenant_id):
    """Get display name for tenant."""
    names = {
        'pools': 'Swimming Pool',
        'windows': 'Windows & Doors',
        'roofs': 'Roofing & Solar',
        'screens': 'Security Screens',
    }
    return names.get(tenant_id, 'Home Improvement')


def get_tenant_color(tenant_id):
    """Get brand color for tenant."""
    colors_map = {
        'pools': '#0077b6',      # Pool blue
        'windows': '#2E7D32',    # Forest green
        'roofs': '#D84315',      # Terra cotta
        'screens': '#1565C0',    # Security blue
    }
    return colors_map.get(tenant_id, '#0066CC')


def generate_visualization_pdf(visualization_request):
    """
    Generate a Design Proposal PDF - tenant-aware.

    Pages:
    1. Cover - Design Proposal
    2. Your Property - Before image
    3. Your New [Product] - After visualization
    4. Design Specifications
    5. Investment Estimate
    """
    tenant_id = getattr(visualization_request, 'tenant_id', 'pools')
    tenant_name = get_tenant_display_name(tenant_id)
    tenant_color = get_tenant_color(tenant_id)

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
        textColor=colors.HexColor(tenant_color)
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=18,
        alignment=1,
        spaceAfter=10,
        textColor=colors.HexColor(tenant_color)
    )

    body_style = styles['Normal']
    body_style.fontSize = 12

    # --- Helper: Logo ---
    def get_logo():
        logo_path = os.path.join(settings.BASE_DIR, 'frontend', 'public', 'logo512.png')
        if os.path.exists(logo_path):
            return RLImage(logo_path, width=1.5*inch, height=1.5*inch)
        return Paragraph("TESTHOME VISUALIZER", title_style)

    # --- Page 1: Cover ---
    elements.append(get_logo())
    elements.append(Spacer(1, 0.5*inch))

    elements.append(Paragraph(f"{tenant_name} Design Proposal", title_style))
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
    elements.append(Paragraph("Prepared by TrustHome Visualizer AI", subtitle_style))
    elements.append(PageBreak())

    # --- Page 2: Your Property ---
    elements.append(Paragraph("Your Property", title_style))
    elements.append(Spacer(1, 0.2*inch))

    elements.append(Paragraph(
        f"Our AI analyzed your property to create the perfect {tenant_name.lower()} visualization.",
        body_style
    ))
    elements.append(Spacer(1, 0.2*inch))

    # Before image
    if visualization_request.original_image:
        img_path = visualization_request.original_image.path
        if os.path.exists(img_path):
            img = _get_resized_image(img_path, width=5*inch, height=3.5*inch)
            elements.append(img)
            elements.append(Paragraph("Original Photo", ParagraphStyle('Caption', parent=body_style, alignment=1)))

    elements.append(PageBreak())

    # --- Page 3: Your New [Product] ---
    elements.append(Paragraph(f"Your New {tenant_name}", title_style))

    # After Image
    generated_result = visualization_request.results.first()
    if generated_result and generated_result.generated_image:
        img_path = generated_result.generated_image.path
        if os.path.exists(img_path):
            img = _get_resized_image(img_path, width=6*inch, height=4*inch)
            elements.append(img)
            elements.append(Paragraph("AI-Generated Visualization", subtitle_style))

    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(
        "This visualization shows how your project could look. Final design may vary based on site conditions.",
        body_style
    ))
    elements.append(PageBreak())

    # --- Page 4: Design Specifications ---
    elements.append(Paragraph("Design Specifications", title_style))

    specs = get_specs_for_tenant(visualization_request)

    t = Table(specs, colWidths=[3*inch, 3*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(tenant_color)),
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

    quote = calculate_quote_for_tenant(visualization_request)
    table_rows = [["Item", "Quantity", "Unit Price", "Total"]]

    for item in quote['items']:
        table_rows.append([
            item['name'],
            str(item['qty']),
            f"${item['unit_price']:,}" if item['unit_price'] >= 1 else f"${item['unit_price']:.2f}",
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
    elements.append(Paragraph(f"""
    This is an AI-generated visualization and cost estimate for planning purposes only.
    Actual pricing will vary based on:
    • Site conditions and measurements
    • Local permit requirements
    • Material availability and selections
    • Contractor pricing in your area

    We recommend obtaining quotes from licensed contractors in your area.
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


# Keep legacy functions for backwards compatibility
def calculate_quote(visualization_request):
    """Legacy function - routes to pools calculator."""
    return calculate_pools_quote(visualization_request)


def calculate_windows_quote_legacy(visualization_request, window_count=5):
    """Legacy function - routes to windows calculator."""
    return calculate_windows_quote(visualization_request, window_count)
