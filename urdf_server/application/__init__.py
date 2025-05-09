from flask import Flask
from .extensions import cors

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    cors.init_app(app)
    
    # 确保上传目录存在
    app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)
    
    # 注册蓝图
    from .blueprints import file_api
    from .blueprints import urdf_api
    app.register_blueprint(file_api.bp)
    app.register_blueprint(urdf_api.bp)
    return app