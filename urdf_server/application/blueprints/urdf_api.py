from flask import Blueprint, request, jsonify
from ..services.urdf_service import start_urdf_visualization

bp = Blueprint('urdf_api', __name__, url_prefix='/api/urdf')

@bp.route('/visualize', methods=['POST'])
def visualize_urdf():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({'error': 'No filename provided'}), 400
    
    filename = data['filename']
    result = start_urdf_visualization(filename)
    return jsonify(result), result.get('status', 200) 