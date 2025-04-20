import os
from pathlib import Path

from flask import current_app
from ..utils.file_util import is_allowed_file
from werkzeug.utils import secure_filename

def handle_file_upload(file):
    if not is_allowed_file(file.filename):
        return {'error': 'File type not allowed', 'status': 400}
    
    filename = secure_filename(file.filename)
    save_path = Path(current_app.config['UPLOAD_FOLDER']) / filename
    
    try:
        file.save(save_path)
        return {
            'message': 'File uploaded successfully',
            'filename': filename,
            'path': str(save_path),
            'status': 200
        }
    except Exception as e:
        return {'error': str(e), 'status': 500}