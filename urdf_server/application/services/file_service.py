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

def list_files(page=1, per_page=20):
    try:
        upload_folder = Path(current_app.config['UPLOAD_FOLDER'])
        if not upload_folder.exists():
            return {'error': 'Upload folder not found', 'status': 404}

        # Get all files
        all_files = [f for f in upload_folder.iterdir() if f.is_file()]
        total_files = len(all_files)
        
        # Calculate pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        files_page = all_files[start_idx:end_idx]
        
        # Format file information
        files_info = [{
            'name': f.name,
            'size': f.stat().st_size,
            'modified': f.stat().st_mtime
        } for f in files_page]
        
        return {
            'files': files_info,
            'total': total_files,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_files + per_page - 1) // per_page,
            'status': 200
        }
    except Exception as e:
        return {'error': str(e), 'status': 500}