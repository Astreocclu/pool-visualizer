# PDF Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform the PDF from a generic template into a premium, trustworthy 5-page sales document.

**Architecture:** Complete rewrite of `pdf_generator.py` with new page structure, visual styling, financing calculations, and upgrade comparison. Tenant-aware throughout.

**Tech Stack:** ReportLab (Platypus for layout, built-in Helvetica/Times fonts), existing tenant configs for pricing data.

---

## Task 1: Create PDF Style System

**Files:**
- Create: `api/utils/pdf_styles.py`

**Step 1: Create the styles module**

```python
# api/utils/pdf_styles.py
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
```

**Step 2: Verify import works**

Run: `cd /home/reid/command-center/testhome/testhome-visualizer && source venv/bin/activate && python3 -c "from api.utils.pdf_styles import get_styles, get_tenant_colors; print('OK')"`

Expected: `OK`

**Step 3: Commit**

```bash
git add api/utils/pdf_styles.py
git commit -m "feat(pdf): add style system for PDF redesign"
```

---

## Task 2: Add Financing Calculator

**Files:**
- Modify: `api/utils/pdf_generator.py`

**Step 1: Add financing calculation function**

Add after the imports in `pdf_generator.py`:

```python
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
```

**Step 2: Verify calculation**

Run: `cd /home/reid/command-center/testhome/testhome-visualizer && source venv/bin/activate && python3 -c "from api.utils.pdf_generator import calculate_monthly_payment; print(calculate_monthly_payment(50000))"`

Expected: ~`1014.27` (approximately)

**Step 3: Commit**

```bash
git add api/utils/pdf_generator.py
git commit -m "feat(pdf): add financing calculator"
```

---

## Task 3: Add Upgrade Comparison Logic

**Files:**
- Modify: `api/utils/pdf_generator.py`

**Step 1: Add function to get available upgrades**

```python
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
                'upgrades': size_upgrades[:2],  # Max 2
            })

        # Water features not selected
        selected_features = options.get('water_features', [])
        feature_upgrades = []
        for feat in WATER_FEATURES:
            if feat['id'] not in selected_features:
                feature_upgrades.append({
                    'name': feat['name'],
                    'price_add': feat.get('price_add', 0),
                    'benefit': 'Enhance your pool experience',
                })
        if feature_upgrades:
            upgrades.append({
                'category': 'Water Features',
                'selected': f"{len(selected_features)} selected" if selected_features else 'None',
                'upgrades': feature_upgrades[:3],  # Max 3
            })

    elif tenant_id == 'windows':
        from api.tenants.windows.config import FRAME_MATERIALS, GRILLE_PATTERNS

        selected_material = options.get('frame_material', 'vinyl')
        material_upgrades = []
        selected_name = 'Vinyl'
        for mat in FRAME_MATERIALS:
            if mat['id'] == selected_material:
                selected_name = mat['name']
            elif mat.get('price_multiplier', 1.0) > 1.0:
                material_upgrades.append({
                    'name': mat['name'],
                    'price_add': int(450 * (mat.get('price_multiplier', 1.0) - 1.0)),
                    'benefit': mat.get('description', ''),
                })
        if material_upgrades:
            upgrades.append({
                'category': 'Frame Material',
                'selected': selected_name,
                'upgrades': material_upgrades[:2],
            })

    elif tenant_id == 'roofs':
        from api.tenants.roofs.config import ROOF_MATERIALS, SOLAR_OPTIONS

        selected_solar = options.get('solar_option', 'none')
        if selected_solar == 'none':
            solar_upgrades = []
            for opt in SOLAR_OPTIONS:
                if opt['id'] != 'none':
                    solar_upgrades.append({
                        'name': opt['name'],
                        'price_add': 18000 if 'partial' in opt['id'] else 30000,
                        'benefit': opt.get('description', 'Add solar power'),
                    })
            if solar_upgrades:
                upgrades.append({
                    'category': 'Solar Panels',
                    'selected': 'None',
                    'upgrades': solar_upgrades[:2],
                })

    elif tenant_id == 'screens':
        from api.tenants.screens.config import MESH_TYPES_PRICING

        selected_mesh = options.get('mesh_type', '12x12_standard')
        mesh_upgrades = []
        selected_name = '12x12 Standard'
        selected_price = 15
        for mesh in MESH_TYPES_PRICING:
            if mesh['id'] == selected_mesh:
                selected_name = mesh['name']
                selected_price = mesh.get('price_per_sqft', 15)
            elif mesh.get('price_per_sqft', 0) > selected_price:
                mesh_upgrades.append({
                    'name': mesh['name'],
                    'price_add': (mesh.get('price_per_sqft', 0) - selected_price) * 200,
                    'benefit': 'Premium mesh durability',
                })
        if mesh_upgrades:
            upgrades.append({
                'category': 'Mesh Type',
                'selected': selected_name,
                'upgrades': mesh_upgrades,
            })

    return upgrades
```

**Step 2: Verify function**

Run: `cd /home/reid/command-center/testhome/testhome-visualizer && source venv/bin/activate && python3 -c "from api.utils.pdf_generator import get_available_upgrades; print('OK')"`

Expected: `OK`

**Step 3: Commit**

```bash
git add api/utils/pdf_generator.py
git commit -m "feat(pdf): add upgrade comparison logic"
```

---

## Task 4: Rewrite Page 1 - The Vision (Cover)

**Files:**
- Modify: `api/utils/pdf_generator.py`

**Step 1: Create cover page builder**

```python
def build_cover_page(elements, visualization_request, styles, tenant_colors):
    """Build Page 1: The Vision - Cover page with hero image."""
    from reportlab.platypus import Spacer, Image as RLImage, Paragraph
    from reportlab.lib.units import inch
    import os
    from django.conf import settings

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
    from datetime import datetime
    date_str = datetime.now().strftime("%B %d, %Y")
    elements.append(Paragraph(
        f"Prepared on {date_str}",
        styles['caption']
    ))
```

**Step 2: Commit**

```bash
git add api/utils/pdf_generator.py
git commit -m "feat(pdf): add cover page builder"
```

---

## Task 5: Rewrite Page 2 - Your Investment

**Files:**
- Modify: `api/utils/pdf_generator.py`

**Step 1: Create investment page builder**

```python
def build_investment_page(elements, visualization_request, styles, tenant_colors):
    """Build Page 2: Your Investment - selections, pricing, financing, testimonials space."""
    from reportlab.platypus import Spacer, Paragraph, Table, TableStyle, PageBreak
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
```

**Step 2: Commit**

```bash
git add api/utils/pdf_generator.py
git commit -m "feat(pdf): add investment page with financing and testimonials"
```

---

## Task 6: Rewrite Page 3 - Upgrade Options

**Files:**
- Modify: `api/utils/pdf_generator.py`

**Step 1: Create upgrades page builder**

```python
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
                    table_data.append([
                        up['name'],
                        f"+${up['price_add']:,}",
                        up['benefit'][:50] + '...' if len(up.get('benefit', '')) > 50 else up.get('benefit', '')
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
```

**Step 2: Commit**

```bash
git add api/utils/pdf_generator.py
git commit -m "feat(pdf): add upgrades page"
```

---

## Task 7: Rewrite Page 4 - Why TrustHome

**Files:**
- Modify: `api/utils/pdf_generator.py`

**Step 1: Create trust signals page builder**

```python
def build_trust_page(elements, visualization_request, styles, tenant_colors):
    """Build Page 4: Why TrustHome - trust signals and credibility."""
    from reportlab.platypus import Spacer, Paragraph, Table, TableStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors

    elements.append(Paragraph("Why TrustHome", styles['title']))

    elements.append(Paragraph(
        "Your peace of mind is built into every project.",
        styles['subtitle']
    ))

    elements.append(Spacer(1, 0.3*inch))

    # Trust signals as a grid
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
```

**Step 2: Commit**

```bash
git add api/utils/pdf_generator.py
git commit -m "feat(pdf): add trust signals page"
```

---

## Task 8: Rewrite Page 5 - Next Steps (CTA)

**Files:**
- Modify: `api/utils/pdf_generator.py`

**Step 1: Create CTA page builder**

```python
def build_cta_page(elements, visualization_request, styles, tenant_colors):
    """Build Page 5: Next Steps - clear call to action."""
    from reportlab.platypus import Spacer, Paragraph, Table, TableStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors

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
```

**Step 2: Commit**

```bash
git add api/utils/pdf_generator.py
git commit -m "feat(pdf): add CTA page"
```

---

## Task 9: Rewrite Main PDF Generator Function

**Files:**
- Modify: `api/utils/pdf_generator.py`

**Step 1: Replace generate_visualization_pdf function**

```python
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
```

**Step 2: Run syntax check**

Run: `cd /home/reid/command-center/testhome/testhome-visualizer && source venv/bin/activate && python3 -m py_compile api/utils/pdf_generator.py && echo "Syntax OK"`

Expected: `Syntax OK`

**Step 3: Commit**

```bash
git add api/utils/pdf_generator.py
git commit -m "feat(pdf): rewrite main generator with 5-page premium structure"
```

---

## Task 10: Test End-to-End

**Files:**
- None (testing only)

**Step 1: Start Django server**

```bash
cd /home/reid/command-center/testhome/testhome-visualizer
source venv/bin/activate
python3 manage.py runserver 8000
```

**Step 2: Test PDF generation**

In browser or via curl, access an existing visualization's PDF endpoint.

**Step 3: Verify PDF has 5 pages**

Open the downloaded PDF and verify:
- Page 1: Cover with hero image
- Page 2: Investment table with financing
- Page 3: Upgrade options
- Page 4: Trust signals
- Page 5: CTA with contact info

**Step 4: Commit final touches if needed**

```bash
git add -A
git commit -m "feat(pdf): complete PDF redesign - 5 page premium proposal"
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Create PDF style system | `api/utils/pdf_styles.py` (new) |
| 2 | Add financing calculator | `pdf_generator.py` |
| 3 | Add upgrade comparison logic | `pdf_generator.py` |
| 4 | Rewrite Page 1 - Cover | `pdf_generator.py` |
| 5 | Rewrite Page 2 - Investment | `pdf_generator.py` |
| 6 | Rewrite Page 3 - Upgrades | `pdf_generator.py` |
| 7 | Rewrite Page 4 - Trust | `pdf_generator.py` |
| 8 | Rewrite Page 5 - CTA | `pdf_generator.py` |
| 9 | Rewrite main generator | `pdf_generator.py` |
| 10 | Test end-to-end | None |
