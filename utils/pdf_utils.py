import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

# ── Colour palette ─────────────────────────────────────────────────────────────
PURPLE     = colors.HexColor('#6c3ff3')
LIGHT_PURPLE = colors.HexColor('#f3f0ff')
GOLD       = colors.HexColor('#f59e0b')
DARK       = colors.HexColor('#1e1b4b')
GREY       = colors.HexColor('#6b7280')
WHITE      = colors.white
LIGHT_GREY = colors.HexColor('#f9fafb')
BORDER     = colors.HexColor('#e5e7eb')
NAVY       = colors.HexColor('#1a237e')
RED        = colors.HexColor('#c62828')

# ── Company details ─────────────────────────────────────────────────────────────
COMPANY_NAME    = "MNNMP EVENTS"
COMPANY_TAGLINE = "||Sri Seeti Byraveshwara Swamy Prasana||"
COMPANY_ADDRESS = "Amitiganahalli, Chintamani(T) Chikkabalapur(D)"
COMPANY_PROP    = "Prop:- Mithun  K"
COMPANY_MOB     = "Mob:- 9141840705"
HEADER_IMG      = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'static', 'images', 'company_header.png'
)


def _company_header(page_width):
    """
    Returns a Table containing the MNNMP Events company letterhead (Text-based).
    """
    # ── Text-based branding ────────────────────────────────────────────────────────
    tagline_s = ParagraphStyle('Tagline', fontSize=10, textColor=GREY,
                               fontName='Helvetica-Oblique', alignment=TA_CENTER, leading=12)
    name_s    = ParagraphStyle('BrandName', fontSize=28, textColor=NAVY,
                               fontName='Helvetica-Bold', alignment=TA_CENTER, leading=32, spaceAfter=2)
    addr_s    = ParagraphStyle('Addr', fontSize=12, textColor=NAVY,
                               fontName='Helvetica', alignment=TA_CENTER, leading=14, spaceAfter=4)
    prop_s    = ParagraphStyle('Prop', fontSize=10, textColor=WHITE, fontName='Helvetica-Bold', leading=12)
    mob_s     = ParagraphStyle('Mob', fontSize=10, textColor=WHITE,
                               fontName='Helvetica-Bold', alignment=TA_RIGHT, leading=12)

    # Bottom bar with Prop and Mob
    contact_table = Table([[Paragraph(COMPANY_PROP, prop_s), Paragraph(COMPANY_MOB, mob_s)]],
                         colWidths=[page_width / 2, page_width / 2])
    contact_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NAVY),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    data = [
        [Paragraph(COMPANY_TAGLINE, tagline_s)],
        [Paragraph(COMPANY_NAME, name_s)],
        [Paragraph(COMPANY_ADDRESS, addr_s)],
        [contact_table],
    ]
    
    t = Table(data, colWidths=[page_width])
    t.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    return t


def generate_quotation_pdf(event, output_path, signature_name=None):
    """Generate a styled A4 PDF quotation with MNNMP Events header and signature block."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=0.8 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm
    )

    page_width = A4[0] - 3 * cm  # usable width
    styles = getSampleStyleSheet()
    story = []

    # ── Company Header ─────────────────────────────────────────────────────────
    story.append(_company_header(page_width))
    story.append(Spacer(1, 0.8 * cm))
    story.append(HRFlowable(width='100%', thickness=2, color=PURPLE, spaceAfter=8))

    # ── Quotation title & metadata ──────────────────────────────────────────────
    title_style = ParagraphStyle('Title', fontSize=18, textColor=DARK,
                                 fontName='Helvetica-Bold', spaceAfter=2)
    meta_style  = ParagraphStyle('Meta', fontSize=10, textColor=GREY, fontName='Helvetica')

    quot_no  = f"QT-{event.id:04d}-{datetime.now().year}"
    gen_date = datetime.now().strftime('%d %B %Y')

    meta_data = [
        [Paragraph("QUOTATION", title_style),
         Paragraph(f"<b>Quotation No:</b> {quot_no}<br/>"
                   f"<b>Generated:</b> {gen_date}<br/>"
                   f"<b>Status:</b> {event.status.upper()}", meta_style)]
    ]
    meta_table = Table(meta_data, colWidths=[10 * cm, 7 * cm])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(meta_table)
    story.append(HRFlowable(width='100%', thickness=2, color=PURPLE, spaceAfter=10))

    # ── Event & Client Info ─────────────────────────────────────────────────────
    label_style = ParagraphStyle('Label', fontSize=9, textColor=GREY, fontName='Helvetica-Bold')
    value_style = ParagraphStyle('Value', fontSize=10, textColor=DARK, fontName='Helvetica')

    def info_row(label, value):
        return [Paragraph(label, label_style), Paragraph(str(value) if value else '—', value_style)]

    time_str   = event.event_time.strftime('%I:%M %p') if event.event_time else 'TBD'
    event_info = [
        info_row('EVENT NAME', event.name),
        info_row('TYPE', event.event_type),
        info_row('DATE', event.event_date.strftime('%A, %d %B %Y')),
        info_row('TIME', time_str),
        info_row('VENUE', event.venue),
    ]
    client_info = [
        info_row('CLIENT NAME', event.client_name),
        info_row('EMAIL', event.client_email or '—'),
        info_row('PHONE', event.client_phone or '—'),
    ]

    combined = []
    for i in range(max(len(event_info), len(client_info))):
        e_row = event_info[i] if i < len(event_info) else ['', '']
        c_row = client_info[i] if i < len(client_info) else ['', '']
        combined.append(e_row + [''] + c_row)

    info_table = Table(combined, colWidths=[3.5 * cm, 5 * cm, 0.5 * cm, 3.5 * cm, 4.5 * cm])
    info_table.setStyle(TableStyle([
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [WHITE, LIGHT_GREY]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (1, -1), 0.5, BORDER),
        ('GRID', (3, 0), (4, -1), 0.5, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Section heading helper ──────────────────────────────────────────────────
    section_style = ParagraphStyle('Section', fontSize=12, textColor=WHITE,
                                   fontName='Helvetica-Bold', leftIndent=8)

    def section_heading(text):
        t = Table([[Paragraph(text, section_style)]], colWidths=[page_width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), PURPLE),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        return t

    th_style = ParagraphStyle('TH', fontSize=9, textColor=WHITE,
                              fontName='Helvetica-Bold', alignment=TA_CENTER)
    td_style = ParagraphStyle('TD', fontSize=10, textColor=DARK, fontName='Helvetica')
    td_r     = ParagraphStyle('TDR', fontSize=10, textColor=DARK,
                              fontName='Helvetica', alignment=TA_RIGHT)

    # ── Flower Items ────────────────────────────────────────────────────────────
    flower_items = event.flower_items
    if flower_items:
        story.append(section_heading("Flower Arrangements"))
        story.append(Spacer(1, 0.2 * cm))
        flower_data = [[
            Paragraph('#', th_style), Paragraph('Flower Type', th_style),
            Paragraph('Quantity', th_style), Paragraph('Unit Price (Rs.)', th_style),
            Paragraph('Total (Rs.)', th_style),
        ]]
        for i, f in enumerate(flower_items, 1):
            total = f.get('qty', 0) * f.get('price', 0)
            flower_data.append([
                Paragraph(str(i), td_style),
                Paragraph(f.get('type', ''), td_style),
                Paragraph(str(f.get('qty', 0)), td_r),
                Paragraph(f"Rs.{float(f.get('price', 0)):.2f}", td_r),
                Paragraph(f"Rs.{float(total):.2f}", td_r),
            ])
        flower_table = Table(flower_data, colWidths=[1*cm, 6*cm, 3*cm, 3.5*cm, 3.5*cm])
        flower_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PURPLE),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(flower_table)
        story.append(Spacer(1, 0.4 * cm))

    # ── Inventory Items ─────────────────────────────────────────────────────────
    inv_usages = event.inventory_usages
    if inv_usages:
        story.append(section_heading("Inventory & Equipment"))
        story.append(Spacer(1, 0.2 * cm))
        inv_data = [[
            Paragraph('#', th_style), Paragraph('Item', th_style),
            Paragraph('Category', th_style), Paragraph('Qty Used', th_style),
            Paragraph('Unit Price (Rs.)', th_style), Paragraph('Total (Rs.)', th_style),
        ]]
        for i, usage in enumerate(inv_usages, 1):
            item = usage.item
            if item:
                total = usage.quantity_used * item.price_per_unit
                inv_data.append([
                    Paragraph(str(i), td_style),
                    Paragraph(item.name, td_style),
                    Paragraph(item.category or '—', td_style),
                    Paragraph(f"{usage.quantity_used} {item.unit}", td_r),
                    Paragraph(f"Rs.{item.price_per_unit:.2f}", td_r),
                    Paragraph(f"Rs.{total:.2f}", td_r),
                ])
        inv_table = Table(inv_data, colWidths=[1*cm, 4*cm, 2.5*cm, 2.5*cm, 3*cm, 4*cm])
        inv_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PURPLE),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(inv_table)
        story.append(Spacer(1, 0.4 * cm))

    # ── Totals ──────────────────────────────────────────────────────────────────
    flower_total = event.flower_total()
    inv_total    = event.inventory_total()
    grand_total  = event.grand_total()

    total_label = ParagraphStyle('TL', fontSize=10, fontName='Helvetica-Bold', alignment=TA_RIGHT)
    total_value = ParagraphStyle('TV', fontSize=10, fontName='Helvetica', alignment=TA_RIGHT)
    grand_label = ParagraphStyle('GL', fontSize=13, fontName='Helvetica-Bold',
                                 textColor=WHITE, alignment=TA_RIGHT)
    grand_value = ParagraphStyle('GV', fontSize=13, fontName='Helvetica-Bold',
                                 textColor=WHITE, alignment=TA_RIGHT)

    totals_data = [
        [Paragraph('Flower Total:', total_label),    Paragraph(f'Rs.{flower_total:.2f}', total_value)],
        [Paragraph('Inventory Total:', total_label), Paragraph(f'Rs.{inv_total:.2f}', total_value)],
        [Paragraph('GRAND TOTAL:', grand_label),     Paragraph(f'Rs.{grand_total:.2f}', grand_value)],
    ]
    totals_table = Table(totals_data, colWidths=[page_width - 4 * cm, 4 * cm])
    totals_table.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('LINEBELOW', (0, 1), (-1, 1), 1, BORDER),
        ('BACKGROUND', (0, 2), (-1, 2), PURPLE),
    ]))
    story.append(totals_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Notes ───────────────────────────────────────────────────────────────────
    if event.notes:
        story.append(section_heading("Notes"))
        story.append(Spacer(1, 0.2 * cm))
        notes_style = ParagraphStyle('Notes', fontSize=10, textColor=DARK,
                                     fontName='Helvetica', leftIndent=8, rightIndent=8)
        story.append(Paragraph(event.notes, notes_style))
        story.append(Spacer(1, 0.4 * cm))

    # ── Terms ───────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=1, color=BORDER, spaceAfter=6))
    terms_style = ParagraphStyle('Terms', fontSize=8, textColor=GREY,
                                 fontName='Helvetica', alignment=TA_CENTER)
    story.append(Paragraph(
        "Terms & Conditions: 50% advance payment required to confirm booking. "
        "Cancellation within 7 days of event is non-refundable. "
        "This quotation is valid for 30 days from the date of issue.",
        terms_style
    ))
    story.append(Spacer(1, 0.6 * cm))

    # ── Signature Section ───────────────────────────────────────────────────────
    sig_label  = ParagraphStyle('SigLabel', fontSize=9, textColor=GREY,
                                fontName='Helvetica-Bold', alignment=TA_CENTER)
    sig_name   = ParagraphStyle('SigName', fontSize=10, textColor=DARK,
                                fontName='Helvetica-Bold', alignment=TA_CENTER)
    sig_line   = ParagraphStyle('SigLine', fontSize=10, textColor=DARK,
                                fontName='Helvetica', alignment=TA_CENTER)

    # Client signature block (left) | Authorised signatory block (right)
    client_sig = [
        [Paragraph("", sig_line)],           # blank space for physical signature
        [HRFlowable(width=5*cm, thickness=1, color=DARK)],
        [Paragraph("Client Signature", sig_label)],
        [Paragraph(event.client_name, sig_name)],
        [Paragraph(f"Date: _______________", sig_label)],
    ]
    auth_sig  = []
    signer    = signature_name or COMPANY_PROP.replace("Prop:- ", "")
    auth_sig  = [
        [Paragraph("", sig_line)],
        [HRFlowable(width=5*cm, thickness=1, color=DARK)],
        [Paragraph("Authorised Signatory", sig_label)],
        [Paragraph(signer, sig_name)],
        [Paragraph(COMPANY_NAME, sig_label)],
    ]

    def sig_block(rows):
        t = Table(rows, colWidths=[6 * cm])
        t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        return t

    sig_spacer = Paragraph("", sig_line)
    sig_table  = Table(
        [[sig_block(client_sig), sig_spacer, sig_block(auth_sig)]],
        colWidths=[6 * cm, page_width - 12 * cm, 6 * cm]
    )
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 0.3 * cm))

    # ── Footer ──────────────────────────────────────────────────────────────────
    footer_style = ParagraphStyle('Footer', fontSize=8, textColor=GREY,
                                  fontName='Helvetica-Oblique', alignment=TA_CENTER)
    story.append(Paragraph(
        f"Generated by MNNMP Events • {datetime.now().strftime('%d %B %Y %I:%M %p')} • "
        f"Contact: {COMPANY_MOB}",
        footer_style
    ))

    doc.build(story)
    return output_path
