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


# ============== FINANCING CALCULATOR ==============
def calculate_monthly_payment(principal: float, annual_rate: float = 0.0799, months: int = 60) -> float:
    """
    Calculate monthly payment using standard amortization formula.

    Args:
        principal: Total loan amount
        annual_rate: Annual interest rate (default 7.99%)
        months: Loan term in months (default 60)

    Returns:
        Monthly payment amount
    """
    if principal <= 0:
        return 0
    monthly_rate = annual_rate / 12
    if monthly_rate == 0:
        return principal / months
    payment = (principal * monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
    return round(payment, 2)


def get_financing_options(total: float) -> list:
    """Get financing options for different terms."""
    return [
        {'months': 36, 'payment': calculate_monthly_payment(total, months=36), 'label': '36 months'},
        {'months': 60, 'payment': calculate_monthly_payment(total, months=60), 'label': '60 months'},
        {'months': 120, 'payment': calculate_monthly_payment(total, months=120), 'label': '120 months'},
    ]


# ============== UPGRADE COMPARISON ==============
def get_available_upgrades(visualization_request) -> list:
    """
    Get upgrades the customer didn't select.
    Returns list of {category, selected, upgrades: [{name, price_add, benefit}]}
    """
    tenant_id = getattr(visualization_request, 'tenant_id', 'pools')
    options = visualization_request.scope or {}
    upgrades = []

    if tenant_id == 'pools':
        # Pool size upgrades
        from api.tenants.pools.config import POOL_SIZES, INTERIOR_FINISHES, WATER_FEATURES

        selected_size = options.get('size', 'classic')
        size_upgrades = []
        found_selected = False
        # Get default from config (classic is index 1)
        default_size = next((s for s in POOL_SIZES if s['id'] == 'classic'), POOL_SIZES[1])
        selected_name = default_size['name']
        selected_price = default_size.get('base_price', 0)
        for size in POOL_SIZES:
            if size['id'] == selected_size:
                found_selected = True
                selected_name = size['name']
                selected_price = size.get('base_price', 0)
            elif found_selected:
                size_upgrades.append({
                    'name': size['name'],
                    'price_add': size.get('base_price', 0) - selected_price,
                    'benefit': size.get('description', ''),
                })
        if size_upgrades:
            upgrades.append({
                'category': 'Pool Size',
                'selected': selected_name,
                'upgrades': size_upgrades,
            })

        # Water features not selected
        selected_features = options.get('water_features', [])
        feature_upgrades = []
        for feat in WATER_FEATURES:
            if feat['id'] not in selected_features:
                feature_upgrades.append({
                    'name': feat['name'],
                    'price_add': feat.get('price_add', 0),
                    'benefit': feat.get('description', feat.get('prompt_hint', '')),
                })
        if feature_upgrades:
            upgrades.append({
                'category': 'Water Features',
                'selected': f"{len(selected_features)} selected" if selected_features else 'None',
                'upgrades': feature_upgrades,
            })

    elif tenant_id == 'windows':
        from api.tenants.windows.config import FRAME_MATERIALS

        # Use base prices from quote calculator
        WINDOW_BASE_PRICES = {
            'single_hung': 350,
            'double_hung': 450,
            'casement': 500,
            'slider': 400,
            'picture': 300,
        }

        selected_material = options.get('frame_material', 'vinyl')
        window_type = options.get('window_type', 'double_hung')
        base_price = WINDOW_BASE_PRICES.get(window_type, 450)

        material_upgrades = []
        selected_name = 'Vinyl'
        selected_multiplier = 1.0

        for mat in FRAME_MATERIALS:
            if mat['id'] == selected_material:
                selected_name = mat['name']
                selected_multiplier = mat.get('price_multiplier', 1.0)
                break

        for mat in FRAME_MATERIALS:
            if mat['id'] != selected_material and mat.get('price_multiplier', 1.0) > selected_multiplier:
                price_diff = mat.get('price_multiplier', 1.0) - selected_multiplier
                material_upgrades.append({
                    'name': mat['name'],
                    'price_add': int(base_price * price_diff),
                    'benefit': mat.get('description', ''),
                })
        if material_upgrades:
            upgrades.append({
                'category': 'Frame Material',
                'selected': selected_name,
                'upgrades': material_upgrades,
            })

    elif tenant_id == 'roofs':
        from api.tenants.roofs.config import SOLAR_OPTIONS

        # Solar pricing from quote calculator: $3/watt
        solar_watts = {
            'partial': 6000,       # ~6kW system
            'full_south': 10000,   # ~10kW system
            'full_all': 15000,     # ~15kW system
        }
        solar_price_per_watt = 3

        selected_solar = options.get('solar_option', 'none')
        if selected_solar == 'none':
            solar_upgrades = []
            for opt in SOLAR_OPTIONS:
                if opt['id'] != 'none':
                    watts = solar_watts.get(opt['id'], 6000)
                    solar_upgrades.append({
                        'name': opt['name'],
                        'price_add': watts * solar_price_per_watt,
                        'benefit': opt.get('description', 'Add solar power'),
                    })
            if solar_upgrades:
                upgrades.append({
                    'category': 'Solar Panels',
                    'selected': 'None',
                    'upgrades': solar_upgrades,
                })

    elif tenant_id == 'screens':
        from api.tenants.screens.config import MESH_TYPES_PRICING

        # Calculate total square footage from scope (same as quote calculator)
        patio_sqft = 200 if options.get('patio', True) else 0
        window_count = options.get('window_count', 4)
        window_sqft = window_count * 10
        total_sqft = patio_sqft + window_sqft

        selected_mesh = options.get('mesh_type', '12x12_standard')
        mesh_upgrades = []
        # Get default from config
        default_mesh = next((m for m in MESH_TYPES_PRICING if m['id'] == '12x12_standard'), MESH_TYPES_PRICING[1])
        selected_name = default_mesh['name']
        selected_price = default_mesh.get('price_per_sqft', 0)

        for mesh in MESH_TYPES_PRICING:
            if mesh['id'] == selected_mesh:
                selected_name = mesh['name']
                selected_price = mesh.get('price_per_sqft', selected_price)
                break

        for mesh in MESH_TYPES_PRICING:
            if mesh['id'] != selected_mesh and mesh.get('price_per_sqft', 0) > selected_price:
                price_per_sqft_diff = mesh.get('price_per_sqft', 0) - selected_price
                mesh_upgrades.append({
                    'name': mesh['name'],
                    'price_add': price_per_sqft_diff * total_sqft,
                    'benefit': mesh.get('description', 'Premium mesh quality and durability'),
                })
        if mesh_upgrades:
            upgrades.append({
                'category': 'Mesh Type',
                'selected': selected_name,
                'upgrades': mesh_upgrades,
            })

    return upgrades


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


def build_cover_page(elements, visualization_request, styles, tenant_colors):
    """Build Page 1: The Vision - Cover page with hero image.

    Args:
        elements: List to append PDF elements to
        visualization_request: VisualizationRequest model instance
        styles: Dictionary of ParagraphStyle objects with keys:
                'title', 'subtitle', 'body_center', 'caption'
        tenant_colors: Dictionary mapping tenant_id to color hex codes (not used directly)
    """
    from reportlab.platypus import Spacer, Image as RLImage, Paragraph
    from reportlab.lib.units import inch
    import os
    from django.conf import settings
    from datetime import datetime

    tenant_id = getattr(visualization_request, 'tenant_id', 'pools')
    tenant_name = get_tenant_display_name(tenant_id)

    # Logo
    logo_path = os.path.join(settings.BASE_DIR, 'frontend', 'public', 'logo512.png')
    if os.path.exists(logo_path):
        logo = RLImage(logo_path, width=1.2*inch, height=1.2*inch)
        logo.hAlign = 'CENTER'
        elements.append(logo)

    elements.append(Spacer(1, 0.3*inch))

    # Title
    elements.append(Paragraph(
        f"Your {tenant_name} Vision",
        styles['title']
    ))

    # Subtitle
    elements.append(Paragraph(
        "A Personalized Design Proposal",
        styles['subtitle']
    ))

    elements.append(Spacer(1, 0.3*inch))

    # Hero image - the AI-generated result
    generated_result = visualization_request.results.first()
    if generated_result and generated_result.generated_image:
        img_path = generated_result.generated_image.path
        if os.path.exists(img_path):
            hero = _get_resized_image(img_path, width=6.5*inch, height=4.5*inch)
            elements.append(hero)

    elements.append(Spacer(1, 0.3*inch))

    # Personalized intro
    elements.append(Paragraph(
        "This proposal was prepared exclusively for you, showcasing how your "
        f"new {tenant_name.lower()} could transform your home.",
        styles['body_center']
    ))

    elements.append(Spacer(1, 0.2*inch))

    # Date
    date_str = datetime.now().strftime("%B %d, %Y")
    elements.append(Paragraph(
        f"Prepared on {date_str}",
        styles['caption']
    ))


def build_investment_page(elements, visualization_request, styles, tenant_colors):
    """Build Page 2: Your Investment - selections, pricing, financing, testimonials space."""
    from reportlab.platypus import Spacer, Paragraph, Table, TableStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors

    elements.append(Paragraph("Your Investment", styles['title']))

    # Get quote
    quote = calculate_quote_for_tenant(visualization_request)

    # Selections table
    elements.append(Paragraph("What You Selected", styles['heading']))

    table_data = [["Item", "Price"]]
    for item in quote['items']:
        table_data.append([
            item['name'],
            f"${item['subtotal']:,}"
        ])
    table_data.append(["", ""])  # Spacer row
    table_data.append(["Total Project Investment", f"${quote['total']:,}"])

    t = Table(table_data, colWidths=[4.5*inch, 2*inch])
    t.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), tenant_colors['primary']),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('PADDING', (0, 0), (-1, 0), 10),
        # Body
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 10),
        ('PADDING', (0, 1), (-1, -2), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, tenant_colors['bg_light']]),
        # Total row
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('BACKGROUND', (0, -1), (-1, -1), tenant_colors['bg_light']),
        ('LINEABOVE', (0, -1), (-1, -1), 1, tenant_colors['primary']),
        # Alignment
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(t)

    elements.append(Spacer(1, 0.3*inch))

    # Financing options
    elements.append(Paragraph("Flexible Financing Options", styles['subheading']))

    financing = get_financing_options(quote['total'])
    finance_data = [["Term", "Monthly Payment"]]
    for opt in financing:
        finance_data.append([opt['label'], f"${opt['payment']:,.2f}/mo"])

    ft = Table(finance_data, colWidths=[2*inch, 2*inch])
    ft.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), tenant_colors['secondary']),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, tenant_colors['text_light']),
    ]))
    elements.append(ft)

    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(
        "*Estimated monthly payment assumes 7.99% APR. Actual terms depend on credit approval.",
        styles['disclaimer']
    ))

    elements.append(Spacer(1, 0.4*inch))

    # Testimonials placeholder
    elements.append(Paragraph("What Our Customers Say", styles['subheading']))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(
        "<i>Customer testimonials coming soon from our beta program.</i>",
        styles['body_center']
    ))
    elements.append(Spacer(1, 0.5*inch))


def build_upgrades_page(elements, visualization_request, styles, tenant_colors):
    """Build Page 3: Upgrade Options - what they could add."""
    from reportlab.platypus import Spacer, Paragraph, Table, TableStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors

    elements.append(Paragraph("Explore Available Upgrades", styles['title']))

    elements.append(Paragraph(
        "Here are some options you might consider to enhance your project. "
        "Discuss these with your contractor during your consultation.",
        styles['body']
    ))

    elements.append(Spacer(1, 0.2*inch))

    upgrades = get_available_upgrades(visualization_request)

    if not upgrades:
        elements.append(Paragraph(
            "You've selected our premium options! No additional upgrades to show.",
            styles['body_center']
        ))
    else:
        for upgrade_group in upgrades:
            # Category heading
            elements.append(Paragraph(upgrade_group['category'], styles['subheading']))
            elements.append(Paragraph(
                f"<b>Your selection:</b> {upgrade_group['selected']}",
                styles['body']
            ))

            # Upgrades table
            if upgrade_group['upgrades']:
                table_data = [["Upgrade Option", "Added Cost", "Benefit"]]
                for up in upgrade_group['upgrades']:
                    benefit_text = up.get('benefit', '')
                    if len(benefit_text) > 50:
                        benefit_text = benefit_text[:50] + '...'
                    table_data.append([
                        up['name'],
                        f"+${up['price_add']:,}",
                        benefit_text
                    ])

                t = Table(table_data, colWidths=[2*inch, 1.2*inch, 3*inch])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), tenant_colors['bg_light']),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('PADDING', (0, 0), (-1, -1), 6),
                    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 0.5, tenant_colors['text_light']),
                ]))
                elements.append(t)

            elements.append(Spacer(1, 0.2*inch))


def build_trust_page(elements, visualization_request, styles, tenant_colors):
    """Build Page 4: Why TrustHome - trust signals and credibility."""
    from reportlab.platypus import Spacer, Paragraph
    from reportlab.lib.units import inch

    elements.append(Paragraph("Why TrustHome", styles['title']))

    elements.append(Paragraph(
        "Your peace of mind is built into every project.",
        styles['subtitle']
    ))

    elements.append(Spacer(1, 0.3*inch))

    # Trust signals
    trust_signals = [
        {
            'title': 'Vetted Contractors',
            'desc': 'Every contractor in our network is licensed, insured, and background-checked.',
        },
        {
            'title': 'Price Certainty',
            'desc': 'No hidden fees or surprise charges. Your quoted price is the price you pay.',
        },
        {
            'title': 'Warranty Protection',
            'desc': 'Industry-leading warranties on both materials and workmanship.',
        },
        {
            'title': 'Streamlined Process',
            'desc': 'From visualization to installation, we manage the details so you can relax.',
        },
    ]

    for signal in trust_signals:
        elements.append(Paragraph(signal['title'], styles['subheading']))
        elements.append(Paragraph(signal['desc'], styles['body']))
        elements.append(Spacer(1, 0.15*inch))

    elements.append(Spacer(1, 0.3*inch))

    # Important notes
    elements.append(Paragraph("Important Notes", styles['subheading']))
    elements.append(Paragraph(
        "This proposal is an AI-generated visualization and cost estimate for planning purposes. "
        "Actual pricing may vary based on site conditions, permit requirements, material availability, "
        "and contractor pricing in your area. We recommend discussing your project with a licensed "
        "contractor for a final quote.",
        styles['body']
    ))


def build_cta_page(elements, visualization_request, styles, tenant_colors):
    """Build Page 5: Next Steps - clear call to action."""
    from reportlab.platypus import Spacer, Paragraph, Table, TableStyle
    from reportlab.lib.units import inch

    elements.append(Paragraph("Let's Make This a Reality", styles['title']))

    elements.append(Paragraph(
        "You've envisioned your perfect home. Now, bring it to life with a trusted expert.",
        styles['body_center']
    ))

    elements.append(Spacer(1, 0.4*inch))

    # Steps
    elements.append(Paragraph("Here's What Happens Next", styles['heading']))

    steps = [
        ("1. Contact TrustHome", "Reach out to us to get connected with a vetted contractor in your area."),
        ("2. Meet Your Contractor", "Schedule a consultation to discuss your project and finalize details."),
        ("3. Finalize Your Plan", "Review materials, timeline, and pricing with your contractor."),
        ("4. Transform Your Home", "Sit back and watch your vision become reality."),
    ]

    for step_title, step_desc in steps:
        elements.append(Paragraph(f"<b>{step_title}</b>", styles['body']))
        elements.append(Paragraph(step_desc, styles['body']))
        elements.append(Spacer(1, 0.1*inch))

    elements.append(Spacer(1, 0.4*inch))

    # CTA Box
    elements.append(Paragraph(
        "Ready to Get Started?",
        styles['cta']
    ))

    cta_data = [
        ["Contact TrustHome to connect with a vetted contractor"],
        [""],
        ["Phone: (888) 555-HOME"],
        ["Email: projects@trusthome.com"],
        ["Web: trusthome.com/connect"],
    ]

    cta_table = Table(cta_data, colWidths=[5*inch])
    cta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), tenant_colors['bg_light']),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 2), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 2), (-1, -1), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 2, tenant_colors['accent']),
    ]))
    cta_table.hAlign = 'CENTER'
    elements.append(cta_table)

    elements.append(Spacer(1, 0.3*inch))

    # Validity note
    elements.append(Paragraph(
        "This proposal is valid for 30 days. We look forward to helping you transform your home.",
        styles['caption']
    ))


def generate_visualization_pdf(visualization_request):
    """
    Generate a premium 5-page Design Proposal PDF.

    Pages:
    1. The Vision (Cover)
    2. Your Investment (Selections, Pricing, Financing, Testimonials)
    3. Upgrade Options
    4. Why TrustHome (Trust Signals)
    5. Next Steps (CTA)
    """
    from reportlab.platypus import SimpleDocTemplate, PageBreak
    from api.utils.pdf_styles import get_styles, get_tenant_colors, MARGIN

    tenant_id = getattr(visualization_request, 'tenant_id', 'pools')
    styles = get_styles(tenant_id)
    tenant_colors = get_tenant_colors(tenant_id)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=MARGIN,
        leftMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
    )

    elements = []

    # Page 1: Cover
    build_cover_page(elements, visualization_request, styles, tenant_colors)
    elements.append(PageBreak())

    # Page 2: Investment
    build_investment_page(elements, visualization_request, styles, tenant_colors)
    elements.append(PageBreak())

    # Page 3: Upgrades
    build_upgrades_page(elements, visualization_request, styles, tenant_colors)
    elements.append(PageBreak())

    # Page 4: Trust
    build_trust_page(elements, visualization_request, styles, tenant_colors)
    elements.append(PageBreak())

    # Page 5: CTA
    build_cta_page(elements, visualization_request, styles, tenant_colors)

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
