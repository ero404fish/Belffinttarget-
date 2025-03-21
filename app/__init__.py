from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# 初始化数据库
db = SQLAlchemy()

def create_app():
    """创建并配置Flask应用"""
    app = Flask(__name__)
    
    # 配置数据库
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///belffin_target.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'belffin_target_secret_key'
    
    # 创建上传和导出目录
    os.makedirs(os.path.join(app.root_path, 'static', 'uploads'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'static', 'exports'), exist_ok=True)
    
    # 初始化数据库
    db.init_app(app)
    
    with app.app_context():
        # 导入模型
        from app.models.models import ProductBase, ProductVariant, WarehouseSku, Inventory, Template, TemplateField, ColorConfig, UpdateHistory
        
        # 创建数据库表
        db.create_all()
        
        # 注册蓝图
        from app.routes.main import main_bp
        from app.routes.product import product_bp
        from app.routes.inventory import inventory_bp
        from app.routes.database import database_bp
        
        app.register_blueprint(main_bp, url_prefix='/')
        app.register_blueprint(product_bp, url_prefix='/product')
        app.register_blueprint(inventory_bp, url_prefix='/inventory')
        app.register_blueprint(database_bp, url_prefix='/database')
        
    return app
