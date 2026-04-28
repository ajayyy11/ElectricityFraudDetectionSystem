import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///eip.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RECORDS_PER_PAGE = 10

    # Email Settings (User: Update these in your .env or here)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  #email@gmail.com
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # app-password
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'ajayyysh85@gmail.com')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
