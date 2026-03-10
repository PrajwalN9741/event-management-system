from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import InventoryItem
from datetime import datetime

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

CATEGORIES = ['Decoration', 'Furniture', 'Audio/Visual', 'Catering', 'Floral', 'Lighting', 'Other']
UNITS = ['pcs', 'kg', 'litre', 'meter', 'box', 'set', 'pair', 'hour']


@inventory_bp.route('/')
@login_required
def list_inventory():
    q = request.args.get('q', '').strip()
    cat = request.args.get('category', '').strip()
    query = InventoryItem.query
    if q:
        query = query.filter(InventoryItem.name.ilike(f'%{q}%'))
    if cat:
        query = query.filter(InventoryItem.category == cat)
    items = query.order_by(InventoryItem.name).all()
    return render_template('inventory/inventory.html', items=items,
                           categories=CATEGORIES, units=UNITS, q=q, cat=cat)


@inventory_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_item():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        quantity = request.form.get('quantity', '0')
        unit = request.form.get('unit', 'pcs').strip()
        price = request.form.get('price_per_unit', '0')
        threshold = request.form.get('low_stock_threshold', '10')

        if not name:
            flash('Item name is required.', 'danger')
            return redirect(url_for('inventory.list_inventory'))

        try:
            quantity = float(quantity)
            price = float(price)
            threshold = float(threshold)
        except ValueError:
            flash('Invalid numeric value.', 'danger')
            return redirect(url_for('inventory.list_inventory'))

        item = InventoryItem(
            name=name,
            category=category,
            quantity=quantity,
            unit=unit,
            price_per_unit=price,
            low_stock_threshold=threshold
        )
        db.session.add(item)
        db.session.commit()
        flash(f'Item "{name}" added to inventory.', 'success')
    return redirect(url_for('inventory.list_inventory'))


@inventory_bp.route('/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = InventoryItem.query.get_or_404(item_id)

    if request.method == 'POST':
        item.name = request.form.get('name', item.name).strip()
        item.category = request.form.get('category', item.category).strip()
        item.unit = request.form.get('unit', item.unit).strip()
        try:
            item.quantity = float(request.form.get('quantity', item.quantity))
            item.price_per_unit = float(request.form.get('price_per_unit', item.price_per_unit))
            item.low_stock_threshold = float(request.form.get('low_stock_threshold', item.low_stock_threshold))
        except ValueError:
            flash('Invalid numeric value.', 'danger')
            return render_template('inventory/edit_item.html', item=item,
                                   categories=CATEGORIES, units=UNITS)

        item.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f'Item "{item.name}" updated.', 'success')
        return redirect(url_for('inventory.list_inventory'))

    return render_template('inventory/edit_item.html', item=item,
                           categories=CATEGORIES, units=UNITS)


@inventory_bp.route('/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    if not current_user.is_admin():
        flash('Only admins can delete inventory items.', 'danger')
        return redirect(url_for('inventory.list_inventory'))
    item = InventoryItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash(f'Item "{item.name}" deleted.', 'success')
    return redirect(url_for('inventory.list_inventory'))
