import json
from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from extensions import db
from models import Event, InventoryItem, EventInventory
from utils.email_utils import send_event_confirmation, send_event_update

events_bp = Blueprint('events', __name__, url_prefix='/events')

EVENT_TYPES = ['Wedding', 'Corporate', 'Birthday', 'Anniversary', 'Engagement', 'Other']


def _parse_flower_items(form):
    """Extract flower items list from form POST."""
    flowers = []
    types = request.form.getlist('flower_type[]')
    qtys = request.form.getlist('flower_qty[]')
    prices = request.form.getlist('flower_price[]')
    for t, q, p in zip(types, qtys, prices):
        if t.strip():
            flowers.append({
                'type': t.strip(),
                'qty': int(q) if q else 0,
                'price': float(p) if p else 0.0
            })
    return flowers


def _parse_inventory_items(form):
    """Return list of (item_id, quantity_used) from form."""
    item_ids = request.form.getlist('inv_item_id[]')
    quantities = request.form.getlist('inv_quantity[]')
    result = []
    for iid, qty in zip(item_ids, quantities):
        try:
            result.append((int(iid), float(qty)))
        except (ValueError, TypeError):
            pass
    return result


def _restore_inventory(event):
    """Return used inventory quantities back to stock before updating/deleting."""
    for usage in event.inventory_usages:
        item = InventoryItem.query.get(usage.item_id)
        if item:
            item.quantity += usage.quantity_used
    db.session.flush()


def _apply_inventory(event, inv_items):
    """Deduct inventory from stock and create EventInventory records."""
    for item_id, qty in inv_items:
        item = InventoryItem.query.get(item_id)
        if item and qty > 0:
            item.quantity -= qty
            usage = EventInventory(event_id=event.id, item_id=item_id, quantity_used=qty)
            db.session.add(usage)


@events_bp.route('/')
@login_required
def list_events():
    query = Event.query

    # Filters
    q = request.args.get('q', '').strip()
    etype = request.args.get('type', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()

    if q:
        query = query.filter(
            (Event.name.ilike(f'%{q}%')) |
            (Event.client_name.ilike(f'%{q}%')) |
            (Event.venue.ilike(f'%{q}%'))
        )
    if etype:
        query = query.filter(Event.event_type == etype)
    if date_from:
        try:
            query = query.filter(Event.event_date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        except ValueError:
            pass
    if date_to:
        try:
            query = query.filter(Event.event_date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        except ValueError:
            pass

    events = query.order_by(Event.event_date.desc()).all()
    return render_template('events/view_events.html', events=events,
                           event_types=EVENT_TYPES, q=q, etype=etype,
                           date_from=date_from, date_to=date_to)


@events_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_event():
    inventory_items = InventoryItem.query.order_by(InventoryItem.name).all()

    if request.method == 'POST':
        # Basic fields
        name = request.form.get('name', '').strip()
        event_type = request.form.get('event_type', '').strip()
        event_date_str = request.form.get('event_date', '')
        event_time_str = request.form.get('event_time', '')
        venue = request.form.get('venue', '').strip()
        client_name = request.form.get('client_name', '').strip()
        client_email = request.form.get('client_email', '').strip()
        client_phone = request.form.get('client_phone', '').strip()
        notes = request.form.get('notes', '').strip()
        status = request.form.get('status', 'confirmed')

        if not all([name, event_type, event_date_str, venue, client_name]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('events/add_event.html', event_types=EVENT_TYPES,
                                   inventory_items=inventory_items)

        try:
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('events/add_event.html', event_types=EVENT_TYPES,
                                   inventory_items=inventory_items)

        event_time = None
        if event_time_str:
            try:
                event_time = datetime.strptime(event_time_str, '%H:%M').time()
            except ValueError:
                pass

        # Duplicate check (same name + date + venue)
        duplicate = Event.query.filter_by(name=name, event_date=event_date, venue=venue).first()
        if duplicate:
            flash('An event with the same name, date, and venue already exists.', 'warning')
            return render_template('events/add_event.html', event_types=EVENT_TYPES,
                                   inventory_items=inventory_items)

        flower_items = _parse_flower_items(request.form)
        inv_items = _parse_inventory_items(request.form)

        event = Event(
            name=name,
            event_type=event_type,
            event_date=event_date,
            event_time=event_time,
            venue=venue,
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            notes=notes,
            status=status,
            created_by=current_user.id
        )
        event.flower_items = flower_items
        db.session.add(event)
        db.session.flush()  # get event.id

        _apply_inventory(event, inv_items)
        db.session.commit()

        # Send confirmation email
        if client_email:
            ok, err = send_event_confirmation(event, client_email)
            if ok:
                flash(f'Confirmation email sent to {client_email}.', 'info')
            else:
                flash(f'Event created, but confirmation email failed: {err}', 'warning')

        flash(f'Event "{name}" created successfully!', 'success')
        return redirect(url_for('events.list_events'))

    return render_template('events/add_event.html', event_types=EVENT_TYPES,
                           inventory_items=inventory_items)


@events_bp.route('/<int:event_id>/view')
@login_required
def view_event(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('events/view_event.html', event=event)


@events_bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    inventory_items = InventoryItem.query.order_by(InventoryItem.name).all()

    if request.method == 'POST':
        old_date = event.event_date
        old_venue = event.venue

        name = request.form.get('name', '').strip()
        event_type = request.form.get('event_type', '').strip()
        event_date_str = request.form.get('event_date', '')
        event_time_str = request.form.get('event_time', '')
        venue = request.form.get('venue', '').strip()
        client_name = request.form.get('client_name', '').strip()
        client_email = request.form.get('client_email', '').strip()
        client_phone = request.form.get('client_phone', '').strip()
        notes = request.form.get('notes', '').strip()
        status = request.form.get('status', 'confirmed')

        if not all([name, event_type, event_date_str, venue, client_name]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('events/add_event.html', event=event,
                                   event_types=EVENT_TYPES, inventory_items=inventory_items)

        try:
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('events/add_event.html', event=event,
                                   event_types=EVENT_TYPES, inventory_items=inventory_items)

        event_time = None
        if event_time_str:
            try:
                event_time = datetime.strptime(event_time_str, '%H:%M').time()
            except ValueError:
                pass

        # Restore old inventory, apply new
        _restore_inventory(event)
        EventInventory.query.filter_by(event_id=event.id).delete()

        flower_items = _parse_flower_items(request.form)
        inv_items = _parse_inventory_items(request.form)

        changes = []
        if event.event_date != event_date:
            changes.append(f'Date changed from {event.event_date} to {event_date}')
        if event.venue != venue:
            changes.append(f'Venue changed from "{event.venue}" to "{venue}"')
        if event.status != status:
            changes.append(f'Status changed to {status}')

        event.name = name
        event.event_type = event_type
        event.event_date = event_date
        event.event_time = event_time
        event.venue = venue
        event.client_name = client_name
        event.client_email = client_email
        event.client_phone = client_phone
        event.notes = notes
        event.status = status
        event.flower_items = flower_items
        event.updated_at = datetime.utcnow()

        db.session.flush()
        _apply_inventory(event, inv_items)
        db.session.commit()

        # Send update email
        if client_email and changes:
            ok, err = send_event_update(event, client_email, changes)
            if not ok:
                flash(f'Update email failed: {err}', 'warning')

        flash(f'Event "{name}" updated successfully!', 'success')
        return redirect(url_for('events.list_events'))

    return render_template('events/add_event.html', event=event, event_types=EVENT_TYPES,
                           inventory_items=inventory_items)


@events_bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if not current_user.is_admin():
        flash('Only admins can delete events.', 'danger')
        return redirect(url_for('events.list_events'))

    _restore_inventory(event)
    db.session.delete(event)
    db.session.commit()
    flash(f'Event "{event.name}" deleted.', 'success')
    return redirect(url_for('events.list_events'))
