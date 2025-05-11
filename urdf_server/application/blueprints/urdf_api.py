from flask import Blueprint, request, jsonify
from ..services.urdf_service import start_urdf_visualization, stop_urdf_visualization

bp = Blueprint('urdf_api', __name__, url_prefix='/api/urdf')

@bp.route('/visualize', methods=['POST'])
def visualize_endpoint():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({'error': 'No filename provided'}), 400
    
    result = start_urdf_visualization(data['filename'])
    return jsonify(result), result.get('status', 200)

@bp.route('/stop', methods=['POST'])
def stop_visualization_endpoint():
    result = stop_urdf_visualization()
    return jsonify(result), result.get('status', 200) 