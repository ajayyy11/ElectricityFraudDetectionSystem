import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template
from flask_login import LoginManager
from flask_mail import Mail
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.config import config
from app.models import db, User

login_manager = LoginManager()
mail = Mail()
talisman = Talisman()
limiter = Limiter(key_func=get_remote_address)

def configure_logging(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/efd_system.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('EFD System Startup')

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # Security: Talisman (only force https if not in dev)
    talisman.init_app(app, content_security_policy=None, force_https=(config_name == 'production'))
    
    # Rate Limiting: 100 per day per IP globally, 5 per minute for auth
    limiter.init_app(app)
    app.config['RATELIMIT_DEFAULT'] = "100 per day"
    
    configure_logging(app)
    
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register Blueprints
    from app.routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from app.routes.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)
    
    from app.routes.dashboard import dashboard as dashboard_blueprint
    app.register_blueprint(dashboard_blueprint)
    
    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    return app
