import os
from pathlib import Path
from flask import current_app
import logging
from datetime import datetime

def save_urdf_file(content, filename):
    """
    保存URDF文件到指定目录
    
    Args:
        content (str): URDF文件内容
        filename (str): 文件名
        
    Returns:
        dict: 包含操作结果的字典
    """
    try:
        # 确保文件名以.urdf结尾
        if not filename.endswith('.urdf'):
            filename += '.urdf'
        
        # 获取上传目录路径
        file_path = Path(current_app.config['UPLOAD_FOLDER']) / filename
        
        # 如果文件已存在，添加时间戳
        if file_path.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name, ext = file_path.stem, file_path.suffix
            filename = f"{name}_{timestamp}{ext}"
            file_path = Path(current_app.config['UPLOAD_FOLDER']) / filename
        
        # 写入文件内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            'message': 'File saved successfully',
            'filename': filename,
            'status': 200
        }
    except Exception as e:
        logging.error(f"Error saving URDF file: {str(e)}")
        return {'error': str(e), 'status': 500} 