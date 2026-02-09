import os

# Load environment variables dari .env file (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Jika dotenv tidak terinstall, skip
    pass

# Path ke folder aplikasi (tempat file config.py berada)
APP_DIR = os.path.abspath(os.path.dirname(__file__))

# Path ke root project (satu level di atas app/)
ROOT_DIR = os.path.abspath(os.path.dirname(APP_DIR))


class Config:
    """Base configuration"""
    # Secret key untuk session encryption
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Upload folder - berada di root project, bukan di app/
    UPLOAD_FOLDER = os.path.join(ROOT_DIR, "uploads")
    
    # Logs folder
    LOG_FOLDER = os.path.join(ROOT_DIR, "logs")
    
    # File extensions yang diizinkan
    ALLOWED_EXTENSIONS = {"pdf"}
    
    # Ukuran file maksimal (50 MB)
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))
    
    # Flask settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    UPLOAD_FOLDER = os.path.join(ROOT_DIR, "tests", "uploads")


# Pilih konfigurasi berdasarkan environment
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}

def get_config(env=None):
    """Get config object based on environment"""
    if env is None:
        env = os.getenv("FLASK_ENV", "development")
    return config.get(env, config["default"])
