import os
from flask import Blueprint, render_template, redirect, url_for, flash, send_file, request
from flask_login import login_required
from extensions import db
from models import Event, Quotation
from utils.pdf_utils import generate_quotation_pdf
from utils.email_utils import send_quotation_email

quotation_bp = Blueprint('quotation', __name__, url_prefix='/quotation')

QUOTATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'quotations')


def _ensure_dir():
    os.makedirs(QUOTATIONS_DIR, exist_ok=True)


def _get_or_create_pdf(event):
    """
    Returns (pdf_path, quotation_record).
    If the PDF doesn't exist or the record is missing, regenerates it automatically.
    """
    _ensure_dir()
    pdf_filename = f'quotation_event_{event.id}.pdf'
    pdf_path = os.path.join(QUOTATIONS_DIR, pdf_filename)

    quotation = Quotation.query.filter_by(event_id=event.id).first()

    # Regenerate if PDF file is missing
    if not os.path.exists(pdf_path):
        generate_quotation_pdf(event, pdf_path)

    # Create or update DB record
    if quotation:
        quotation.pdf_path = pdf_path
        quotation.total_amount = event.grand_total()
    else:
        quotation = Quotation(
            event_id=event.id,
            pdf_path=pdf_path,
            total_amount=event.grand_total()
        )
        db.session.add(quotation)
    db.session.commit()

    return pdf_path, quotation


@quotation_bp.route('/<int:event_id>/generate')
@login_required
def generate(event_id):
    event = Event.query.get_or_404(event_id)
    pdf_path, quotation = _get_or_create_pdf(event)
    # Force regenerate fresh copy
    generate_quotation_pdf(event, pdf_path)
    quotation.total_amount = event.grand_total()
    db.session.commit()

    flash('Quotation generated successfully!', 'success')
    return render_template('quotation/quotation.html', event=event, quotation=quotation)


@quotation_bp.route('/<int:event_id>/download')
@login_required
def download(event_id):
    event = Event.query.get_or_404(event_id)
    pdf_path, quotation = _get_or_create_pdf(event)

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f'Quotation_{event.name.replace(" ", "_")}.pdf',
        mimetype='application/pdf'
    )


@quotation_bp.route('/<int:event_id>/email', methods=['GET', 'POST'])
@login_required
def email_quotation(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == 'GET':
        # Show a confirmation/send page so the user can confirm the recipient
        quotation = Quotation.query.filter_by(event_id=event.id).first()
        return render_template('quotation/quotation.html', event=event, quotation=quotation)

    # POST — send the email
    recipient = request.form.get('recipient_email', '').strip()
    if not recipient:
        recipient = event.client_email or ''

    if not recipient:
        flash('Please provide a recipient email address.', 'danger')
        return redirect(url_for('quotation.generate', event_id=event_id))

    # Auto-generate PDF if missing
    pdf_path, quotation = _get_or_create_pdf(event)

    # Confirm PDF file actually exists
    if not os.path.exists(pdf_path):
        flash('Could not generate the PDF. Please try again.', 'danger')
        return redirect(url_for('quotation.generate', event_id=event_id))

    ok, err = send_quotation_email(event, pdf_path, recipient)
    if ok:
        flash(f'✅ Quotation PDF emailed to {recipient} successfully!', 'success')
    else:
        flash(f'❌ Email failed: {err}', 'danger')

    return redirect(url_for('quotation.generate', event_id=event_id))


@quotation_bp.route('/<int:event_id>/view')
@login_required
def view(event_id):
    event = Event.query.get_or_404(event_id)
    quotation = Quotation.query.filter_by(event_id=event.id).first()
    return render_template('quotation/quotation.html', event=event, quotation=quotation)
