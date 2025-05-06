from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from ..services.file_service import handle_file_upload, list_files
import os

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