import os
from flask import Flask
from dotenv import load_dotenv
from extensions import db, login_manager, mail

load_dotenv()


def create_app():
    app = Flask(__name__)

    # ── Configuration ──────────────────────────────────────────────────────────
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-me')
    
    # Ensure instance folder exists for persistent SQLite on Render
    # Using Flask's native instance_path
    if not os.path.exists(app.instance_path):
        try:
            os.makedirs(app.instance_path)
        except Exception as e:
            app.logger.error(f"Failed to create instance directory: {e}")
    
    # Use absolute path for the database to avoid any ambiguity
    db_path = os.path.join(app.instance_path, 'database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Mail (Gmail SMTP via App Password)
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    try:
        app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    except (ValueError, TypeError):
        app.config['MAIL_PORT'] = 587
        
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
    # Strip spaces from Gmail App Password (spaces are display-only, not part of the password)
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '').replace(' ', '')
    app.config['MAIL_DEFAULT_SENDER'] = (
        'EMS Events', os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME', ''))
    )

    app.logger.info(f"Mail configured for: {app.config['MAIL_USERNAME']}")


    # ── Extensions ─────────────────────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # ── Blueprints ─────────────────────────────────────────────────────────────
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.events import events_bp
    from routes.inventory import inventory_bp
    from routes.quotation import quotation_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(quotation_bp)

    # ── Database init ──────────────────────────────────────────────────────────
    with app.app_context():
        app.logger.info(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        try:
            db.create_all()
            _seed_admin()
        except Exception as e:
            app.logger.error(f"Database initialization error: {e}")

    @app.errorhandler(500)
    def handle_500(e):
        import traceback
        app.logger.error(f"Internal Server Error: {e}\n{traceback.format_exc()}")
        return "Internal Server Error (Detailed logs sent to console)", 500

    return app


def _seed_admin():
    """Create a default admin account if no users exist."""
    from models import User
    from werkzeug.security import generate_password_hash
    try:
        if not User.query.first():
            admin = User(
                username='admin',
                email='admin@ems.local',
                password_hash=generate_password_hash('Admin@123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
    except Exception:
        db.session.rollback()


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
