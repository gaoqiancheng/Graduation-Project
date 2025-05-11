from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from ..services.file_service import handle_file_upload, list_files
import os
from pathlib import Path
from flask import current_app

bp = Blueprint('file_api', __name__, url_prefix='/api/files')

@bp.route('/upload', methods=['POST'])
def upload_endpoint():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    result = handle_file_upload(file)
    return jsonify(result), result.get('status', 200)

@bp.route('/list', methods=['GET'])
def list_files_endpoint():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    result = list_files(page, per_page)
    return jsonify(result), result.get('status', 200)

@bp.route('/<filename>', methods=['GET'])
def get_file(filename):
    try:
        file_path = Path(current_app.config['UPLOAD_FOLDER']) / filename
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            file_path,
            mimetype='application/xml',  # URDF 文件是 XML 格式
            as_attachment=False
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<filename>/content', methods=['GET'])
def get_file_content(filename):
    try:
        file_path = Path(current_app.config['UPLOAD_FOLDER']) / filename
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'content': content,
            'filename': filename
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500