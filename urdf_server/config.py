import os
from pathlib import Path

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-fallback-key')
    UPLOAD_FOLDER = Path('C:/uploads').absolute()
    ALLOWED_EXTENSIONS = {'urdf', 'txt', 'pdf'}
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB