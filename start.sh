#!/bin/bash

# 安装依赖
pip3 install flask flask-sqlalchemy flask-wtf pandas openpyxl

# 创建必要的目录
mkdir -p app/static/uploads
mkdir -p app/static/exports

# 初始化数据库
python3 -c "from app import create_app; app = create_app()"

# 运行应用
python3 run.py
