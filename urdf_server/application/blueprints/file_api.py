from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from ..services.file_service import handle_file_upload

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