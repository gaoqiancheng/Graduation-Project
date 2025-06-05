from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from ..services.file_service import (
    handle_file_upload, 
    list_files, 
    handle_folder_upload,
    process_urdf_content,
    get_resource_file
)
from ..services.urdf_service import save_urdf_file
import os
from pathlib import Path
from flask import current_app
from datetime import datetime

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

@bp.route('/upload-folder', methods=['POST'])
def upload_folder_endpoint():
    if 'files' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files selected'}), 400
    
    result = handle_folder_upload(files)
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
            return jsonify({'error': 'File not found', 'status': 404}), 404
        
        return send_file(
            file_path,
            mimetype='application/xml',  # URDF 文件是 XML 格式
            as_attachment=False
        )
    except Exception as e:
        return jsonify({'error': str(e), 'status': 500}), 500

@bp.route('/<path:file_path>/content', methods=['GET'])
def get_file_content(file_path):
    """获取文件内容"""
    try:
        upload_folder = Path(current_app.config['UPLOAD_FOLDER'])
        file_path = upload_folder / file_path
        
        # 安全检查：确保路径不会超出上传文件夹
        try:
            file_path.relative_to(upload_folder)
        except ValueError:
            return jsonify({'error': 'Invalid file path'}), 400
        
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'content': content,
            'filename': os.path.basename(file_path)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/save', methods=['POST'])
def save_urdf():
    try:
        data = request.get_json()
        if not data or 'content' not in data or 'filename' not in data:
            return jsonify({'error': 'Missing content or filename'}), 400
        
        filename = secure_filename(data['filename'])
        result = save_urdf_file(data['content'], filename)
        
        return jsonify(result), result.get('status', 200)
    except Exception as e:
        return jsonify({'error': str(e), 'status': 500}), 500

@bp.route('/<path:file_path>/urdf', methods=['GET'])
def get_processed_urdf(file_path):
    """获取处理后的URDF文件内容"""
    try:
        upload_folder = Path(current_app.config['UPLOAD_FOLDER'])
        file_path = upload_folder / file_path
        
        # 安全检查
        try:
            file_path.relative_to(upload_folder)
        except ValueError:
            return jsonify({'error': 'Invalid file path'}), 400
            
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
            
        if not file_path.name.lower().endswith('.urdf'):
            return jsonify({'error': 'Not a URDF file'}), 400
        
        # 处理URDF文件
        result = process_urdf_content(file_path)
        return jsonify(result), result.get('status', 200)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/resource/<path:resource_path>', methods=['GET'])
def get_resource(resource_path):
    """获取资源文件（mesh等）"""
    result = get_resource_file(resource_path)
    
    if result.get('status') != 200:
        return jsonify({'error': result.get('error')}), result.get('status')
    
    try:
        response = send_file(
            result['file_path'],
            mimetype=result['content_type'],
            as_attachment=False
        )
        print(f">>> Resource sent successfully: {resource_path}")
        return response
    except Exception as e:
        print(f">>> Failed to send resource: {str(e)}")
        return jsonify({'error': str(e)}), 500