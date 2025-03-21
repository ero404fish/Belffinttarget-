from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from app.models.models import WarehouseSku, Inventory, UpdateHistory
from app import db
import pandas as pd
import os
import re
from werkzeug.utils import secure_filename
from datetime import datetime
import shutil

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/')
def index():
    """库存更新工具主页"""
    history = UpdateHistory.query.order_by(UpdateHistory.created_at.desc()).limit(10).all()
    return render_template('inventory/index.html', history=history)

@inventory_bp.route('/update', methods=['GET', 'POST'])
def update():
    """更新库存"""
    if request.method == 'POST':
        # 检查是否有文件上传
        if 'fba_file' not in request.files or 'inventory_file' not in request.files:
            flash('请选择FBA库存表和库存文件', 'error')
            return redirect(request.url)
        
        fba_file = request.files['fba_file']
        inventory_file = request.files['inventory_file']
        
        if fba_file.filename == '' or inventory_file.filename == '':
            flash('请选择文件', 'error')
            return redirect(request.url)
        
        if fba_file and inventory_file:
            try:
                # 创建上传目录
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                
                # 保存上传的文件
                fba_filename = secure_filename(fba_file.filename)
                inventory_filename = secure_filename(inventory_file.filename)
                
                fba_path = os.path.join(upload_dir, fba_filename)
                inventory_path = os.path.join(upload_dir, inventory_filename)
                
                fba_file.save(fba_path)
                inventory_file.save(inventory_path)
                
                # 处理数据
                result_df = process_data(fba_path, inventory_path)
                
                # 创建输出目录
                output_dir = os.path.join(current_app.root_path, 'static', 'exports')
                os.makedirs(output_dir, exist_ok=True)
                
                # 生成输出文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"inventory_update_{timestamp}.csv"
                output_path = os.path.join(output_dir, output_filename)
                
                # 备份原文件
                backup_filename = f"{os.path.splitext(inventory_filename)[0]}_备份_{timestamp}.csv"
                backup_path = os.path.join(upload_dir, backup_filename)
                shutil.copy(inventory_path, backup_path)
                
                # 保存结果
                result_df.to_csv(output_path, index=False)
                
                # 记录历史
                history = UpdateHistory(
                    source_file=inventory_path,
                    output_file=output_path,
                    updated_count=len(result_df)
                )
                db.session.add(history)
                db.session.commit()
                
                # 更新数据库中的库存信息
                update_database_inventory(result_df)
                
                # 返回下载链接
                download_url = url_for('static', filename=f'exports/{output_filename}')
                flash('库存更新成功', 'success')
                
                return render_template('inventory/result.html', 
                                      download_url=download_url, 
                                      updated_count=len(result_df),
                                      backup_path=backup_path)
            
            except Exception as e:
                flash(f'处理失败: {str(e)}', 'error')
                return redirect(request.url)
    
    return render_template('inventory/update.html')

@inventory_bp.route('/history')
def history():
    """查看更新历史"""
    history = UpdateHistory.query.order_by(UpdateHistory.created_at.desc()).all()
    return render_template('inventory/history.html', history=history)

def generate_sku_mapping(fba_df):
    """生成多级SKU映射关系"""
    sku_map = {}
    pattern = re.compile(r"([A-Za-z0-9]+-\w+?)(\d{2,})$")
    
    for _, row in fba_df.iterrows():
        sku = row['工厂SKU']
        # 精确匹配
        sku_map[sku] = sku
        
        # 提取父级SKU
        if match := pattern.match(sku):
            base_sku = match.group(1)
            sku_map[base_sku] = base_sku
            
            # 二级父级
            parent_sku = re.sub(r'-\w+\d*$', '', base_sku)
            sku_map[parent_sku] = parent_sku
    
    return sku_map

def process_data(fba_path, inventory_path):
    """处理数据"""
    # 加载数据
    fba_df = pd.read_excel(fba_path, usecols=['工厂SKU', '可售库存'])
    inv_df = pd.read_csv(inventory_path)
    
    # 生成映射关系
    sku_map = generate_sku_mapping(fba_df)
    
    # 执行三级匹配
    inv_df['matched_sku'] = inv_df['sku'].map(sku_map).fillna(inv_df['sku'])
    
    # 合并库存数据
    merged_df = inv_df.merge(
        fba_df.groupby('工厂SKU')['可售库存'].sum().reset_index(),
        left_on='matched_sku',
        right_on='工厂SKU',
        how='left'
    )
    
    # 更新库存值
    merged_df['quantity'] = merged_df['可售库存'].combine_first(merged_df['quantity'])
    return merged_df[['sku', 'warehouse_id', 'quantity']]

def update_database_inventory(result_df):
    """更新数据库中的库存信息"""
    for _, row in result_df.iterrows():
        sku = row['sku']
        quantity = row['quantity']
        
        # 查找对应的仓库SKU
        warehouse_skus = WarehouseSku.query.join(
            Inventory, WarehouseSku.id == Inventory.warehouse_sku_id, isouter=True
        ).filter(WarehouseSku.warehouse_sku == sku).all()
        
        if warehouse_skus:
            for ws in warehouse_skus:
                if ws.inventory:
                    # 更新现有库存
                    ws.inventory.quantity = quantity
                    ws.inventory.updated_at = datetime.utcnow()
                else:
                    # 创建新库存记录
                    inventory = Inventory(warehouse_sku_id=ws.id, quantity=quantity)
                    db.session.add(inventory)
        
    db.session.commit()
