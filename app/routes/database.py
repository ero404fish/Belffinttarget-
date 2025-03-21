from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from app.models.models import ProductBase, ProductVariant, WarehouseSku, Inventory
from app import db
import pandas as pd
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy import or_

database_bp = Blueprint('database', __name__)

@database_bp.route('/')
def index():
    """产品数据库主页"""
    # 获取基本统计信息
    product_count = ProductBase.query.count()
    variant_count = ProductVariant.query.count()
    warehouse_count = WarehouseSku.query.count()
    
    # 获取最近添加的产品
    recent_products = ProductBase.query.order_by(ProductBase.created_at.desc()).limit(5).all()
    
    return render_template('database/index.html', 
                          product_count=product_count,
                          variant_count=variant_count,
                          warehouse_count=warehouse_count,
                          recent_products=recent_products)

@database_bp.route('/search', methods=['GET', 'POST'])
def search():
    """搜索产品"""
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    if query:
        # 搜索产品基础表和变体表
        products = ProductBase.query.filter(
            or_(
                ProductBase.base_sku.contains(query),
                ProductBase.title.contains(query)
            )
        ).paginate(page=page, per_page=per_page)
        
        variants = ProductVariant.query.filter(
            ProductVariant.sku.contains(query)
        ).paginate(page=page, per_page=per_page)
        
        return render_template('database/search_results.html', 
                              query=query,
                              products=products,
                              variants=variants)
    
    return render_template('database/search.html')

@database_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """产品详情页"""
    product = ProductBase.query.get_or_404(product_id)
    return render_template('database/product_detail.html', product=product)

@database_bp.route('/variant/<int:variant_id>')
def variant_detail(variant_id):
    """变体详情页"""
    variant = ProductVariant.query.get_or_404(variant_id)
    return render_template('database/variant_detail.html', variant=variant)

@database_bp.route('/import', methods=['GET', 'POST'])
def import_data():
    """导入产品数据"""
    if request.method == 'POST':
        if 'product_file' not in request.files:
            flash('请选择文件', 'error')
            return redirect(request.url)
        
        file = request.files['product_file']
        if file.filename == '':
            flash('请选择文件', 'error')
            return redirect(request.url)
        
        if file and (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            try:
                # 创建上传目录
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                
                # 保存上传的文件
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                
                # 处理数据
                if file.filename.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                
                # 导入数据
                import_count = import_product_data(df)
                
                flash(f'成功导入 {import_count} 条产品数据', 'success')
                return redirect(url_for('database.index'))
            
            except Exception as e:
                flash(f'导入失败: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('只支持CSV或Excel格式的文件', 'error')
            return redirect(request.url)
    
    return render_template('database/import.html')

@database_bp.route('/export')
def export_data():
    """导出产品数据"""
    try:
        # 创建输出目录
        output_dir = os.path.join(current_app.root_path, 'static', 'exports')
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"product_export_{timestamp}.xlsx"
        output_path = os.path.join(output_dir, output_filename)
        
        # 查询数据
        products = ProductBase.query.all()
        
        # 准备数据
        data = []
        for product in products:
            for variant in product.variants:
                row = {
                    'base_sku': product.base_sku,
                    'title': product.title,
                    'item_type': product.item_type,
                    'item_type_id': product.item_type_id,
                    'depth': product.depth,
                    'height': product.height,
                    'weight': product.weight,
                    'width': product.width,
                    'price': product.price,
                    'sku': variant.sku,
                    'color_code': variant.color_code,
                    'color_name': variant.color_name
                }
                
                # 添加仓库SKU和库存信息
                for i, ws in enumerate(variant.warehouse_skus, 1):
                    row[f'warehouse_sku{i}'] = ws.warehouse_sku
                    row[f'warehouse_code{i}'] = ws.warehouse_code
                    row[f'quantity{i}'] = ws.inventory.quantity if ws.inventory else 0
                
                data.append(row)
        
        # 创建DataFrame并导出
        df = pd.DataFrame(data)
        df.to_excel(output_path, index=False)
        
        # 返回下载链接
        download_url = url_for('static', filename=f'exports/{output_filename}')
        return render_template('database/export.html', download_url=download_url)
    
    except Exception as e:
        flash(f'导出失败: {str(e)}', 'error')
        return redirect(url_for('database.index'))

def import_product_data(df):
    """导入产品数据到数据库"""
    import_count = 0
    
    try:
        # 检查必要的列
        required_cols = {'sku'}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"文件必须包含 {required_cols} 列")
        
        # 处理每一行数据
        for _, row in df.iterrows():
            sku = row['sku']
            
            # 检查是否是变体SKU
            if '-' in sku:
                base_sku = sku.split('-')[0]
                
                # 查找或创建基础产品
                product = ProductBase.query.filter_by(base_sku=base_sku).first()
                if not product:
                    product = ProductBase(base_sku=base_sku)
                    
                    # 设置产品属性
                    if 'Product Title' in row and not pd.isna(row['Product Title']):
                        product.title = row['Product Title']
                    if 'Item Type' in row and not pd.isna(row['Item Type']):
                        product.item_type = row['Item Type']
                    if 'Item Type ID' in row and not pd.isna(row['Item Type ID']):
                        product.item_type_id = row['Item Type ID']
                    if 'Product Depth' in row and not pd.isna(row['Product Depth']):
                        product.depth = float(row['Product Depth'])
                    if 'Product Height' in row and not pd.isna(row['Product Height']):
                        product.height = float(row['Product Height'])
                    if 'Product Weight' in row and not pd.isna(row['Product Weight']):
                        product.weight = float(row['Product Weight'])
                    if 'Product Width' in row and not pd.isna(row['Product Width']):
                        product.width = float(row['Product Width'])
                    
                    db.session.add(product)
                    db.session.flush()  # 获取product.id
                
                # 查找或创建变体
                variant = ProductVariant.query.filter_by(sku=sku).first()
                if not variant:
                    color_code = sku.split('-')[-1] if len(sku.split('-')) > 1 else ''
                    variant = ProductVariant(
                        base_id=product.id,
                        sku=sku,
                        color_code=color_code
                    )
                    db.session.add(variant)
                    db.session.flush()  # 获取variant.id
                
                # 处理仓库SKU
                for i in range(1, 9):  # 假设最多8个仓库
                    warehouse_sku_col = f'仓库SKU{i}'
                    quantity_col = f'数量{i}QTY{i}'
                    
                    if warehouse_sku_col in row and not pd.isna(row[warehouse_sku_col]):
                        warehouse_sku = row[warehouse_sku_col]
                        quantity = int(row[quantity_col]) if quantity_col in row and not pd.isna(row[quantity_col]) else 0
                        
                        # 查找或创建仓库SKU
                        ws = WarehouseSku.query.filter_by(
                            variant_id=variant.id,
                            warehouse_sku=warehouse_sku
                        ).first()
                        
                        if not ws:
                            ws = WarehouseSku(
                                variant_id=variant.id,
                                warehouse_code=f'WH{i}',
                                warehouse_sku=warehouse_sku
                            )
                            db.session.add(ws)
                            db.session.flush()  # 获取ws.id
                        
                        # 查找或创建库存
                        inv = Inventory.query.filter_by(warehouse_sku_id=ws.id).first()
                        if not inv:
                            inv = Inventory(
                                warehouse_sku_id=ws.id,
                                quantity=quantity
                            )
                            db.session.add(inv)
                        else:
                            inv.quantity = quantity
                
                import_count += 1
        
        db.session.commit()
        return import_count
    
    except Exception as e:
        db.session.rollback()
        raise e
