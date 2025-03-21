from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from app.models.models import Template, TemplateField, ProductBase, ProductVariant, ColorConfig
from app import db
import pandas as pd
import os
import csv
import re
from werkzeug.utils import secure_filename
from datetime import datetime

product_bp = Blueprint('product', __name__)

@product_bp.route('/listing')
def listing():
    """产品上架工具主页"""
    templates = Template.query.all()
    colors = ColorConfig.query.all()
    return render_template('product/listing.html', templates=templates, colors=colors)

@product_bp.route('/templates')
def templates():
    """模板管理页面"""
    templates = Template.query.all()
    return render_template('product/templates.html', templates=templates)

@product_bp.route('/template/upload', methods=['POST'])
def upload_template():
    """上传模板文件"""
    if 'template_file' not in request.files:
        flash('没有选择文件', 'error')
        return redirect(request.referrer)
    
    file = request.files['template_file']
    if file.filename == '':
        flash('没有选择文件', 'error')
        return redirect(request.referrer)
    
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        template_dir = os.path.join(current_app.root_path, 'static', 'templates')
        os.makedirs(template_dir, exist_ok=True)
        file_path = os.path.join(template_dir, filename)
        file.save(file_path)
        
        # 解析模板
        template = Template(name=filename, file_path=file_path)
        db.session.add(template)
        db.session.flush()  # 获取template.id
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)
                template.content = ','.join(headers)
                
                for idx, header in enumerate(headers):
                    field_name, field_type, params = parse_header(header)
                    field = TemplateField(
                        template_id=template.id,
                        field_name=field_name,
                        field_type=field_type,
                        params=params,
                        order=idx
                    )
                    db.session.add(field)
            
            db.session.commit()
            flash(f'模板 {filename} 上传成功', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'模板解析失败: {str(e)}', 'error')
    else:
        flash('只支持CSV格式的模板文件', 'error')
    
    return redirect(url_for('product.templates'))

@product_bp.route('/template/<int:template_id>')
def template_detail(template_id):
    """模板详情页面"""
    template = Template.query.get_or_404(template_id)
    fields = TemplateField.query.filter_by(template_id=template_id).order_by(TemplateField.order).all()
    return render_template('product/template_detail.html', template=template, fields=fields)

@product_bp.route('/template/delete/<int:template_id>', methods=['POST'])
def delete_template(template_id):
    """删除模板"""
    template = Template.query.get_or_404(template_id)
    try:
        # 删除文件
        if template.file_path and os.path.exists(template.file_path):
            os.remove(template.file_path)
        
        db.session.delete(template)
        db.session.commit()
        flash(f'模板 {template.name} 删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'error')
    
    return redirect(url_for('product.templates'))

@product_bp.route('/colors')
def colors():
    """颜色配置管理页面"""
    colors = ColorConfig.query.all()
    return render_template('product/colors.html', colors=colors)

@product_bp.route('/color/upload', methods=['POST'])
def upload_color_config():
    """上传颜色配置文件"""
    if 'color_file' not in request.files:
        flash('没有选择文件', 'error')
        return redirect(request.referrer)
    
    file = request.files['color_file']
    if file.filename == '':
        flash('没有选择文件', 'error')
        return redirect(request.referrer)
    
    if file and (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            required_cols = {'color_code', 'display_name'}
            if not required_cols.issubset(df.columns):
                flash(f'颜色文件必须包含 {required_cols} 列', 'error')
                return redirect(request.referrer)
            
            # 清除现有颜色配置
            ColorConfig.query.delete()
            
            # 添加新的颜色配置
            for _, row in df.iterrows():
                color = ColorConfig(
                    color_code=row['color_code'],
                    display_name=row['display_name']
                )
                db.session.add(color)
            
            db.session.commit()
            flash(f'已加载 {len(df)} 种颜色配置', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'加载失败: {str(e)}', 'error')
    else:
        flash('只支持CSV或Excel格式的颜色配置文件', 'error')
    
    return redirect(url_for('product.colors'))

@product_bp.route('/color/add', methods=['POST'])
def add_color():
    """添加颜色配置"""
    color_code = request.form.get('color_code')
    display_name = request.form.get('display_name')
    
    if not color_code or not display_name:
        flash('颜色代码和显示名称不能为空', 'error')
        return redirect(request.referrer)
    
    try:
        color = ColorConfig(color_code=color_code, display_name=display_name)
        db.session.add(color)
        db.session.commit()
        flash('颜色配置添加成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'添加失败: {str(e)}', 'error')
    
    return redirect(url_for('product.colors'))

@product_bp.route('/color/delete/<int:color_id>', methods=['POST'])
def delete_color(color_id):
    """删除颜色配置"""
    color = ColorConfig.query.get_or_404(color_id)
    try:
        db.session.delete(color)
        db.session.commit()
        flash(f'颜色 {color.display_name} 删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'error')
    
    return redirect(url_for('product.colors'))

@product_bp.route('/generate_variants', methods=['POST'])
def generate_variants():
    """生成变体预览"""
    base_sku = request.form.get('base_sku', '').strip()
    base_name = request.form.get('base_name', '').strip()
    
    if not base_sku:
        return jsonify({'error': '基础SKU不能为空'})
    
    if not re.match(r"^[a-zA-Z0-9_\-]+$", base_sku):
        return jsonify({'error': 'SKU包含非法字符（只允许字母、数字、下划线和连字符）'})
    
    colors = ColorConfig.query.all()
    if not colors:
        return jsonify({'error': '请先添加颜色配置'})
    
    variants = []
    for color in colors:
        sku = f"{base_sku}-{color.color_code}"
        name = f"{base_name}, {color.display_name}" if base_name else color.display_name
        variants.append({'sku': sku, 'name': name})
    
    return jsonify({'variants': variants})

@product_bp.route('/export_csv', methods=['POST'])
def export_csv():
    """导出CSV文件"""
    template_id = request.form.get('template_id')
    base_sku = request.form.get('base_sku', '').strip()
    base_name = request.form.get('base_name', '').strip()
    field_values = request.form.to_dict()
    
    if not template_id:
        flash('请选择模板', 'error')
        return redirect(request.referrer)
    
    if not base_sku:
        flash('基础SKU不能为空', 'error')
        return redirect(request.referrer)
    
    template = Template.query.get_or_404(template_id)
    fields = TemplateField.query.filter_by(template_id=template_id).order_by(TemplateField.order).all()
    
    # 生成变体
    colors = ColorConfig.query.all()
    if not colors:
        flash('请先添加颜色配置', 'error')
        return redirect(request.referrer)
    
    try:
        # 创建输出目录
        output_dir = os.path.join(current_app.root_path, 'static', 'exports')
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"{base_sku}_{timestamp}.csv")
        
        # 准备CSV头
        headers = [field.field_name for field in fields]
        
        # 准备数据行
        rows = []
        for color in colors:
            sku = f"{base_sku}-{color.color_code}"
            name = f"{base_name}, {color.display_name}" if base_name else color.display_name
            
            row = {}
            for field in fields:
                if field.field_name == 'sku':
                    row[field.field_name] = sku
                elif field.field_name == 'title' or field.field_name == 'Product Title':
                    row[field.field_name] = name
                elif field.field_type == 'lock' and field.params:
                    row[field.field_name] = field.params
                else:
                    # 获取表单中的值
                    form_key = f"field_{field.id}"
                    if form_key in field_values:
                        row[field.field_name] = field_values[form_key]
                    else:
                        row[field.field_name] = ""
            
            rows.append(row)
        
        # 写入CSV文件
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        
        # 保存到数据库
        product = ProductBase(
            base_sku=base_sku,
            title=base_name
        )
        db.session.add(product)
        db.session.flush()  # 获取product.id
        
        for color in colors:
            sku = f"{base_sku}-{color.color_code}"
            name = f"{base_name}, {color.display_name}" if base_name else color.display_name
            
            variant = ProductVariant(
                base_id=product.id,
                sku=sku,
                color_code=color.color_code,
                color_name=color.display_name
            )
            db.session.add(variant)
        
        db.session.commit()
        
        # 返回下载链接
        download_url = url_for('static', filename=f'exports/{os.path.basename(output_file)}')
        flash('CSV文件生成成功', 'success')
        return jsonify({'success': True, 'download_url': download_url})
    
    except Exception as e:
        db.session.rollback()
        flash(f'生成失败: {str(e)}', 'error')
        return jsonify({'error': str(e)})

def parse_header(header):
    """解析字段头"""
    if match := re.match(r"^([^\[]+?)\[([^\]]+)\]$", header):
        field_name = match.group(1).strip()
        type_part = match.group(2)
        if ":" in type_part:
            field_type, params = type_part.split(":", 1)
        else:
            field_type, params = type_part, ""
        return field_name, field_type, params.strip()
    return header.strip(), "normal", ""
