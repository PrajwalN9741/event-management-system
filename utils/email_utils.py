from flask import current_app
from flask_mail import Message
from extensions import mail


def _business_email():
    """Returns the configured business/sender email address."""
    return current_app.config.get('MAIL_USERNAME', '')


def _send(subject, recipient, html_body, attachments=None, cc=None, bcc=None):
    """
    Send an email. Returns (True, None) on success or (False, error_message) on failure.
    Never raises — the app stays running even if SMTP is misconfigured.
    """
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient] if isinstance(recipient, str) else recipient,
            html=html_body,
            cc=cc or [],
            bcc=bcc or []
        )
        if attachments:
            for filename, data, content_type in attachments:
                msg.attach(filename, content_type, data)
        mail.send(msg)
        current_app.logger.info(f'Email sent to {recipient}: {subject}')
        return True, None
    except Exception as e:
        err = str(e)
        current_app.logger.error(f'Mail send failed → {err}')
        return False, err


def _event_detail_html(event):
    time_str = event.event_time.strftime('%I:%M %p') if event.event_time else 'TBD'
    return f"""
    <table style="border-collapse:collapse;width:100%;font-family:Arial,sans-serif;font-size:14px;">
      <tr><td style="padding:6px 12px;font-weight:bold;background:#f5f5f5;width:160px;">Event Name</td>
          <td style="padding:6px 12px;">{event.name}</td></tr>
      <tr><td style="padding:6px 12px;font-weight:bold;background:#f5f5f5;">Type</td>
          <td style="padding:6px 12px;">{event.event_type}</td></tr>
      <tr><td style="padding:6px 12px;font-weight:bold;background:#f5f5f5;">Date</td>
          <td style="padding:6px 12px;">{event.event_date.strftime('%d %B %Y')}</td></tr>
      <tr><td style="padding:6px 12px;font-weight:bold;background:#f5f5f5;">Time</td>
          <td style="padding:6px 12px;">{time_str}</td></tr>
      <tr><td style="padding:6px 12px;font-weight:bold;background:#f5f5f5;">Venue</td>
          <td style="padding:6px 12px;">{event.venue}</td></tr>
      <tr><td style="padding:6px 12px;font-weight:bold;background:#f5f5f5;">Status</td>
          <td style="padding:6px 12px;text-transform:capitalize;">{event.status}</td></tr>
    </table>
    """


def _load_quotation_pdf(event):
    """
    Returns (pdf_filename, pdf_bytes, mimetype) if a quotation PDF exists
    for this event, else None. Used to auto-attach to confirmation emails.
    """
    try:
        from models import Quotation
        import os
        q = Quotation.query.filter_by(event_id=event.id).first()
        if q and q.pdf_path and os.path.exists(q.pdf_path):
            with open(q.pdf_path, 'rb') as f:
                return (
                    f'Quotation_{event.name.replace(" ", "_")}.pdf',
                    f.read(),
                    'application/pdf'
                )
    except Exception as ex:
        current_app.logger.warning(f'Could not load quotation PDF for attachment: {ex}')
    return None


# ── Public helpers ─────────────────────────────────────────────────────────────

def send_event_confirmation(event, recipient_email):
    """
    Send event confirmation to the client.
    - Attaches quotation PDF if one has already been generated for this event.
    - BCCs the business email so a copy is kept internally.
    """
    subject = f"✅ Event Confirmation – {event.name}"

    quotation_note = ""
    attachments = []

    pdf_attachment = _load_quotation_pdf(event)
    if pdf_attachment:
        attachments.append(pdf_attachment)
        quotation_note = (
            "<p style='background:#f0fff4;border-left:4px solid #10b981;"
            "padding:10px 14px;border-radius:4px;margin-top:16px;'>"
            "📎 <strong>Your quotation is attached</strong> to this email for reference.</p>"
        )

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;border:1px solid #e0e0e0;border-radius:8px;overflow:hidden;">
      <div style="background:linear-gradient(135deg,#6c3ff3,#a855f7);padding:24px;color:white;text-align:center;">
        <h1 style="margin:0;font-size:24px;">Event Confirmed 🎉</h1>
      </div>
      <div style="padding:24px;">
        <p style="font-size:16px;">Dear <strong>{event.client_name}</strong>,</p>
        <p>Your event has been successfully booked. Here are the details:</p>
        {_event_detail_html(event)}
        {quotation_note}
        <p style="margin-top:20px;">Our team will be in touch closer to the date.
        If you have any questions, please don't hesitate to contact us.</p>
        <p style="color:#888;font-size:12px;margin-top:32px;">
          This is an automated message from the Event Management System.
        </p>
      </div>
    </div>
    """
    biz = _business_email()
    bcc = [biz] if biz and biz != recipient_email else []
    return _send(subject, recipient_email, html,
                 attachments=attachments or None, bcc=bcc)


def send_event_update(event, recipient_email, changes):
    """
    Send event update notification to the client.
    BCCs the business email for internal record.
    """
    subject = f"📝 Event Update – {event.name}"
    changes_html = ''.join(f'<li>{c}</li>' for c in changes)
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;border:1px solid #e0e0e0;border-radius:8px;overflow:hidden;">
      <div style="background:linear-gradient(135deg,#f59e0b,#f97316);padding:24px;color:white;text-align:center;">
        <h1 style="margin:0;font-size:24px;">Event Updated ✏️</h1>
      </div>
      <div style="padding:24px;">
        <p style="font-size:16px;">Dear <strong>{event.client_name}</strong>,</p>
        <p>Your event <strong>{event.name}</strong> has been updated. Changes made:</p>
        <ul style="background:#fff8f0;border-left:4px solid #f59e0b;padding:12px 12px 12px 28px;border-radius:4px;">
          {changes_html}
        </ul>
        <p>Updated event details:</p>
        {_event_detail_html(event)}
        <p style="color:#888;font-size:12px;margin-top:32px;">
          This is an automated message from the Event Management System.
        </p>
      </div>
    </div>
    """
    biz = _business_email()
    bcc = [biz] if biz and biz != recipient_email else []
    return _send(subject, recipient_email, html, bcc=bcc)


def send_quotation_email(event, pdf_path, recipient_email):
    """
    Send quotation PDF to the client.
    Also CCs the business email (mnnmpevents@gmail.com) so a copy is always kept.
    """
    subject = f"📄 Quotation for {event.name}"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;border:1px solid #e0e0e0;border-radius:8px;overflow:hidden;">
      <div style="background:linear-gradient(135deg,#10b981,#059669);padding:24px;color:white;text-align:center;">
        <h1 style="margin:0;font-size:24px;">Your Quotation is Ready 📋</h1>
      </div>
      <div style="padding:24px;">
        <p style="font-size:16px;">Dear <strong>{event.client_name}</strong>,</p>
        <p>Please find attached the quotation for your upcoming event <strong>{event.name}</strong>.</p>
        {_event_detail_html(event)}
        <p style="background:#f0fff4;border-left:4px solid #10b981;padding:10px 14px;border-radius:4px;margin-top:16px;">
          📎 <strong>Quotation PDF</strong> is attached to this email.
        </p>
        <p style="margin-top:20px;">Please review the attached PDF and let us know if you have any questions.</p>
        <p style="color:#888;font-size:12px;margin-top:32px;">
          This is an automated message from the Event Management System.
        </p>
      </div>
    </div>
    """
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()

    pdf_name = f'Quotation_{event.name.replace(" ", "_")}.pdf'
    attachments = [(pdf_name, pdf_data, 'application/pdf')]

    biz = _business_email()
    # CC the business email so it always receives a copy
    cc = [biz] if biz and biz != recipient_email else []

    return _send(subject, recipient_email, html, attachments=attachments, cc=cc)
