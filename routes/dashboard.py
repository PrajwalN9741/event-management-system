from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import date, timedelta
from models import Event, InventoryItem, Quotation
from extensions import db
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    today = date.today()
    next_week = today + timedelta(days=7)

    # Upcoming events (next 30 days)
    upcoming_events = (Event.query
                       .filter(Event.event_date >= today)
                       .order_by(Event.event_date.asc())
                       .limit(10)
                       .all())

    # Today's events
    todays_events = Event.query.filter(Event.event_date == today).all()

    # Total events this month
    total_this_month = Event.query.filter(
        func.strftime('%Y-%m', Event.event_date) ==
        func.strftime('%Y-%m', func.date('now'))
    ).count()

    # Low stock items
    all_items = InventoryItem.query.all()
    low_stock = [i for i in all_items if i.is_low_stock]

    # Revenue estimate (sum of all event grand totals)
    all_events = Event.query.all()
    total_revenue = sum(e.grand_total() for e in all_events)

    # Recent quotations
    recent_quotations = (Quotation.query
                         .order_by(Quotation.generated_at.desc())
                         .limit(5)
                         .all())

    return render_template(
        'dashboard.html',
        upcoming_events=upcoming_events,
        todays_events=todays_events,
        total_this_month=total_this_month,
        low_stock=low_stock,
        total_revenue=total_revenue,
        recent_quotations=recent_quotations,
        total_inventory=len(all_items),
        today=today
    )
