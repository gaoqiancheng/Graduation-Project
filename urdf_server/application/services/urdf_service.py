import subprocess
from pathlib import Path
from flask import current_app
import logging
import os
import time
from datetime import datetime

# 存储当前运行的进程
current_process = None

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

def start_urdf_visualization(filename):
    global current_process
    try:
        # 先尝试停止之前的进程
        if current_process and current_process.poll() is None:
            print("Stopping previous visualization process...")
            current_process.terminate()
            current_process.wait(timeout=5)
            current_process = None
        
        upload_folder = Path(current_app.config['UPLOAD_FOLDER'])
        file_path = upload_folder / filename
        
        # 打印文件信息
        print(f"\n=== URDF Visualization Request ===")
        print(f"Selected file: {filename}")
        print(f"Full path: {file_path}")
        print(f"File exists: {file_path.exists()}")
        if file_path.exists():
            print(f"File size: {file_path.stat().st_size} bytes")
            print(f"Last modified: {file_path.stat().st_mtime}")
        print("================================\n")
        
        if not file_path.exists():
            return {'error': 'File not found', 'status': 404}
        
        if not file_path.suffix.lower() == '.urdf':
            return {'error': 'File is not a URDF file', 'status': 400}
        
        # 启动 URDF 可视化进程
        try:
            print(f"Starting urdf-viz for file: {file_path}")
            # 设置环境变量以使用UTF-8编码
            my_env = os.environ.copy()
            my_env["PYTHONIOENCODING"] = "utf-8"
            
            current_process = subprocess.Popen(
                ['urdf-viz', str(file_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace',
                env=my_env
            )
            
            # 等待一段时间以确保进程正常启动
            time.sleep(2)
            
            # 检查进程是否成功启动
            if current_process.poll() is None:
                print(f"URDF visualization process started successfully for file: {filename}")
                return {
                    'message': 'URDF visualization started successfully',
                    'status': 200
                }
            else:
                stdout, stderr = current_process.communicate()
                print(f"Failed to start visualization for file: {filename}")
                print(f"Error: {stderr}")
                return {
                    'error': f'Failed to start visualization: {stderr}',
                    'status': 500
                }
                
        except FileNotFoundError:
            print(f"urdf-viz command not found when trying to visualize: {filename}")
            return {'error': 'urdf-viz command not found. Please ensure it is installed and in your system PATH.', 'status': 500}
        except Exception as e:
            print(f"Error starting visualization for file: {filename}")
            print(f"Exception: {str(e)}")
            return {'error': f'Error starting visualization: {str(e)}', 'status': 500}
            
    except Exception as e:
        print(f"General error processing file: {filename}")
        print(f"Exception: {str(e)}")
        return {'error': str(e), 'status': 500}

def stop_urdf_visualization():
    global current_process
    try:
        if current_process and current_process.poll() is None:
            current_process.terminate()
            current_process.wait(timeout=5)  # 等待进程结束，最多等待5秒
            current_process = None
            return {'message': 'URDF visualization stopped successfully', 'status': 200}
        else:
            return {'message': 'No visualization process running', 'status': 200}
    except Exception as e:
        print(f"Error stopping visualization: {str(e)}")
        return {'error': f'Error stopping visualization: {str(e)}', 'status': 500} 