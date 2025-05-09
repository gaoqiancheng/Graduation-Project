import subprocess
from pathlib import Path
from flask import current_app
import logging

def start_urdf_visualization(filename):
    try:
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
            # 使用完整路径启动 urdf-viz 进程
            urdf_viz_path = Path("C:/Program Files/Tools/urdf-viz")
            if not urdf_viz_path.exists():
                print(f"urdf-viz not found at: {urdf_viz_path}")
                return {'error': 'urdf-viz executable not found at expected location', 'status': 500}

            print(f"Starting urdf-viz from: {urdf_viz_path}")
            process = subprocess.Popen(
                [str(urdf_viz_path), str(file_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 检查进程是否成功启动
            if process.poll() is None:
                print(f"URDF visualization process started successfully for file: {filename}")
                return {
                    'message': 'URDF visualization started successfully',
                    'status': 200
                }
            else:
                stdout, stderr = process.communicate()
                print(f"Failed to start visualization for file: {filename}")
                print(f"Error: {stderr.decode()}")
                return {
                    'error': f'Failed to start visualization: {stderr.decode()}',
                    'status': 500
                }
                
        except FileNotFoundError:
            print(f"urdf-viz command not found when trying to visualize: {filename}")
            return {'error': 'urdf-viz command not found. Please ensure it is installed.', 'status': 500}
        except Exception as e:
            print(f"Error starting visualization for file: {filename}")
            print(f"Exception: {str(e)}")
            return {'error': f'Error starting visualization: {str(e)}', 'status': 500}
            
    except Exception as e:
        print(f"General error processing file: {filename}")
        print(f"Exception: {str(e)}")
        return {'error': str(e), 'status': 500} 