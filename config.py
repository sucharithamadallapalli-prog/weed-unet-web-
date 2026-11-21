
import os
from dotenv import load_dotenv

load_dotenv()

BASE = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    if not SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY environment variable is required"
        )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///weed_unet.db"
    )

    MODEL_PATH = os.path.join(
        BASE, "models", "smart_weed_unet.keras"
    )

    UPLOAD_DIR = os.path.join(BASE, "uploads")
    EXPORT_DIR = os.path.join(BASE, "exports")

    IMG_SIZE = 256
    THRESHOLD = 0.5
    MAX_CONTENT_LENGTH = 64 * 1024 * 1024
    ALLOWED_EXT = {"png", "jpg", "jpeg", "tif", "tiff"}


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False
