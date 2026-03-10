import json
from datetime import datetime
from extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ── User ───────────────────────────────────────────────────────────────────────

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='staff')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    events = db.relationship('Event', backref='creator', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'


# ── Event ──────────────────────────────────────────────────────────────────────

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.Time, nullable=True)
    venue = db.Column(db.String(300), nullable=False)
    client_name = db.Column(db.String(150), nullable=False)
    client_email = db.Column(db.String(120), nullable=True)
    client_phone = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='confirmed')
    flower_items_json = db.Column(db.Text, default='[]')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    inventory_usages = db.relationship('EventInventory', backref='event', lazy=True, cascade='all, delete-orphan')
    quotations = db.relationship('Quotation', backref='event', lazy=True, cascade='all, delete-orphan')

    @property
    def flower_items(self):
        try:
            return json.loads(self.flower_items_json or '[]')
        except Exception:
            return []

    @flower_items.setter
    def flower_items(self, value):
        self.flower_items_json = json.dumps(value)

    def flower_total(self):
        return sum(float(f.get('price', 0)) * int(f.get('qty', 0)) for f in self.flower_items)

    def inventory_total(self):
        return sum(ui.quantity_used * ui.item.price_per_unit for ui in self.inventory_usages if ui.item)

    def grand_total(self):
        return self.flower_total() + self.inventory_total()

    def __repr__(self):
        return f'<Event {self.name}>'


# ── Inventory Item ─────────────────────────────────────────────────────────────

class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(80), nullable=True)
    quantity = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(30), default='pcs')
    price_per_unit = db.Column(db.Float, default=0.0)
    low_stock_threshold = db.Column(db.Float, default=10.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    usages = db.relationship('EventInventory', backref='item', lazy=True)

    @property
    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold

    @property
    def allocated_quantity(self):
        return sum(u.quantity_used for u in self.usages)

    @property
    def total_quantity(self):
        return self.quantity + self.allocated_quantity

    def __repr__(self):
        return f'<InventoryItem {self.name}>'


# ── Event–Inventory Junction ───────────────────────────────────────────────────

class EventInventory(db.Model):
    __tablename__ = 'event_inventory'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    quantity_used = db.Column(db.Float, nullable=False, default=0.0)


# ── Quotation ──────────────────────────────────────────────────────────────────

class Quotation(db.Model):
    __tablename__ = 'quotations'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    pdf_path = db.Column(db.String(300), nullable=True)
    total_amount = db.Column(db.Float, default=0.0)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Quotation event_id={self.event_id}>'
