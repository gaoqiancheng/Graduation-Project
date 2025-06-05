import os
from pathlib import Path
from flask import current_app, request
from ..utils.file_util import is_allowed_file
from werkzeug.utils import secure_filename
import xml.etree.ElementTree as ET
from collections import deque

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

def handle_folder_upload(files):
    """
    处理文件夹上传，保持原始文件夹结构
    :param files: 上传的文件列表
    :return: 包含上传结果的字典
    """
    uploaded_files = []
    errors = []
    
    for file in files:
        if file.filename:
            try:
                # 分割路径和文件名
                path_parts = Path(file.filename).parts
                # 只对文件名进行安全处理，保留路径结构
                safe_path = Path(*path_parts[:-1], secure_filename(path_parts[-1]))
                # 构建完整的保存路径
                save_path = Path(current_app.config['UPLOAD_FOLDER']) / safe_path
                
                # 确保目标目录存在
                save_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 保存文件
                file.save(save_path)
                uploaded_files.append({
                    'filename': str(safe_path),
                    'path': str(save_path)
                })
            except Exception as e:
                errors.append({
                    'file': file.filename,
                    'error': str(e)
                })
    
    result = {
        'uploaded_files': uploaded_files,
        'status': 200 if not errors else 400
    }
    
    if errors:
        result['errors'] = errors
    
    return result

def list_files(page=1, per_page=20):
    try:
        upload_folder = Path(current_app.config['UPLOAD_FOLDER'])
        if not upload_folder.exists():
            return {'error': 'Upload folder not found', 'status': 404}

        # 获取请求的路径
        request_path = request.args.get('path', '')
        current_path = upload_folder / request_path.lstrip('/')

        # 安全检查：确保路径不会超出上传文件夹
        try:
            current_path.relative_to(upload_folder)
        except ValueError:
            return {'error': 'Invalid path', 'status': 400}

        if not current_path.exists():
            return {'error': 'Path not found', 'status': 404}

        # 获取当前目录下的所有文件和文件夹
        items = []
        for item in current_path.iterdir():
            # 计算相对于 upload_folder 的路径
            relative_path = str(item.relative_to(upload_folder)).replace('\\', '/')
            item_info = {
                'name': item.name,
                'path': relative_path,
                'isDirectory': item.is_dir(),
                'modified': item.stat().st_mtime
            }
            
            # 如果是文件，添加文件大小
            if item.is_file():
                item_info['size'] = item.stat().st_size
            else:
                item_info['size'] = 0  # 文件夹大小设为0
                
            items.append(item_info)

        # 对文件夹和文件分别排序
        folders = sorted([item for item in items if item['isDirectory']], key=lambda x: x['name'].lower())
        files = sorted([item for item in items if not item['isDirectory']], key=lambda x: x['name'].lower())
        
        # 合并排序后的列表，文件夹在前
        sorted_items = folders + files
        
        return {
            'files': sorted_items,
            'current_path': request_path,
            'status': 200
        }
    except Exception as e:
        return {'error': str(e), 'status': 500}

def find_file_in_tree(root_dir, target_path):
    """
    在目录树中递归查找目标文件
    :param root_dir: 根目录（UPLOAD_FOLDER）
    :param target_path: 要查找的目标路径（package后的完整路径，如 staubli_tx2_90_support/meshes/...）
    :return: 找到的文件完整路径，如果未找到返回None
    """
    root_dir = Path(root_dir)
    target_path = target_path.replace('\\', '/')
    target_parts = target_path.split('/')
    first_dir = target_parts[0]  # 第一级目录名
    target_file = target_parts[-1]  # 目标文件名
    
    # 递归查找第一级目录
    def find_first_dir(current_dir):
        try:
            # 检查当前目录是否为目标目录
            if current_dir.name == first_dir:
                # 尝试完整路径
                full_path = current_dir.parent / target_path
                if full_path.exists():
                    # 额外验证：检查文件名是否匹配
                    if full_path.name == target_file:
                        return full_path
            
            # 递归搜索子目录
            for item in current_dir.iterdir():
                if item.is_dir():
                    result = find_first_dir(item)
                    if result:
                        return result
        except (PermissionError, OSError):
            pass  # 忽略权限错误
        
        return None
    
    # 如果目标路径只有一级，直接在根目录下查找
    if len(target_parts) == 2:  # 只有目录和文件名
        try:
            full_path = root_dir / target_path
            if full_path.exists():
                return full_path
        except (PermissionError, OSError):
            pass
    
    return find_first_dir(root_dir)

def process_urdf_content(file_path):
    """
    处理URDF文件内容，解析并调整资源文件的路径
    :param file_path: URDF文件的完整路径
    :return: 处理后的URDF内容和相关资源文件列表
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        base_url = "/api/files/resource"
        resources = []
        upload_folder = Path(current_app.config['UPLOAD_FOLDER'])
        
        # 查找所有mesh标签
        for mesh in root.findall(".//mesh"):
            if 'filename' in mesh.attrib:
                original_path = mesh.attrib['filename']
                
                # 处理package://格式的路径
                if original_path.startswith('package://'):
                    # 去掉package://前缀
                    search_path = original_path[len('package://'):]
                    # 在目录树中查找文件
                    found_path = find_file_in_tree(upload_folder, search_path)
                    
                    if found_path:
                        # 转换为相对于upload_folder的路径
                        relative_path = os.path.relpath(found_path, upload_folder)
                        relative_path = relative_path.replace('\\', '/')
                        resources.append(relative_path)
                        new_url = f"{base_url}/{relative_path}"
                        mesh.attrib['filename'] = new_url
                else:
                    # 处理相对路径
                    urdf_dir = os.path.dirname(file_path)
                    full_path = os.path.normpath(os.path.join(urdf_dir, original_path))
                    if os.path.exists(full_path):
                        relative_path = os.path.relpath(full_path, upload_folder)
                        relative_path = relative_path.replace('\\', '/')
                        resources.append(relative_path)
                        new_url = f"{base_url}/{relative_path}"
                        mesh.attrib['filename'] = new_url
        
        modified_content = ET.tostring(root, encoding='unicode')
        
        return {
            'content': modified_content,
            'resources': resources,
            'status': 200
        }
    except Exception as e:
        return {
            'error': f"Error processing URDF file: {str(e)}",
            'status': 500
        }

def get_resource_file(resource_path):
    """
    获取资源文件（mesh等）
    :param resource_path: 资源文件的相对路径
    :return: 文件路径和状态信息
    """
    try:
        print(f"\n>>> Resource request: {resource_path}")
        
        upload_folder = Path(current_app.config['UPLOAD_FOLDER'])
        file_path = upload_folder / resource_path
        
        # 安全检查：确保文件路径不会超出上传目录
        try:
            file_path.relative_to(upload_folder)
        except ValueError:
            print(f">>> Resource request failed: Invalid path")
            return {'error': 'Invalid resource path', 'status': 400}
        
        if not file_path.exists():
            print(f">>> Resource request failed: File not found")
            return {'error': 'Resource not found', 'status': 404}
        
        # 添加文件类型信息
        file_type = 'application/octet-stream'  # 默认二进制类型
        if file_path.suffix.lower() == '.stl':
            file_type = 'application/sla'  # STL文件的MIME类型
        
        print(f">>> Resource request successful: {file_path}")
        return {
            'file_path': str(file_path),
            'content_type': file_type,
            'status': 200
        }
    except Exception as e:
        print(f">>> Resource request failed: {str(e)}")
        return {'error': str(e), 'status': 500}