from datetime import datetime
from app import db

class ProductBase(db.Model):
    """产品基础表"""
    __tablename__ = 'product_base'
    
    id = db.Column(db.Integer, primary_key=True)
    base_sku = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    item_type = db.Column(db.String(50))
    item_type_id = db.Column(db.String(50))
    depth = db.Column(db.Float)
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    width = db.Column(db.Float)
    price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    variants = db.relationship('ProductVariant', backref='base_product', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<ProductBase {self.base_sku}>'


class ProductVariant(db.Model):
    """产品变体表"""
    __tablename__ = 'product_variant'
    
    id = db.Column(db.Integer, primary_key=True)
    base_id = db.Column(db.Integer, db.ForeignKey('product_base.id'), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    color_code = db.Column(db.String(20))
    color_name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    warehouse_skus = db.relationship('WarehouseSku', backref='variant', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<ProductVariant {self.sku}>'


class WarehouseSku(db.Model):
    """仓库SKU表"""
    __tablename__ = 'warehouse_sku'
    
    id = db.Column(db.Integer, primary_key=True)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variant.id'), nullable=False)
    warehouse_code = db.Column(db.String(20), nullable=False)
    warehouse_sku = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    inventory = db.relationship('Inventory', backref='warehouse_sku', lazy=True, uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<WarehouseSku {self.warehouse_sku}>'


class Inventory(db.Model):
    """库存信息表"""
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    warehouse_sku_id = db.Column(db.Integer, db.ForeignKey('warehouse_sku.id'), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Inventory {self.id}>'


class UpdateHistory(db.Model):
    """更新历史表"""
    __tablename__ = 'update_history'
    
    id = db.Column(db.Integer, primary_key=True)
    source_file = db.Column(db.String(200))
    output_file = db.Column(db.String(200))
    updated_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UpdateHistory {self.id}>'


class Template(db.Model):
    """模板信息表"""
    __tablename__ = 'template'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(200))
    content = db.Column(db.Text)  # 存储模板内容
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    fields = db.relationship('TemplateField', backref='template', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Template {self.name}>'


class TemplateField(db.Model):
    """模板字段表"""
    __tablename__ = 'template_field'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'), nullable=False)
    field_name = db.Column(db.String(100), nullable=False)
    field_type = db.Column(db.String(20))  # 普通字段、锁定字段、选项字段、必填字段、依赖字段
    params = db.Column(db.Text)  # 字段参数，如选项值、锁定值等
    order = db.Column(db.Integer, default=0)  # 字段顺序
    
    def __repr__(self):
        return f'<TemplateField {self.field_name}>'


class ColorConfig(db.Model):
    """颜色配置表"""
    __tablename__ = 'color_config'
    
    id = db.Column(db.Integer, primary_key=True)
    color_code = db.Column(db.String(20), unique=True, nullable=False)
    display_name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ColorConfig {self.color_code}>'
