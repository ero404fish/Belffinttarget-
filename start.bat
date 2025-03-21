@echo off
REM 安装依赖
pip install -r requirements.txt

REM 创建必要的目录
mkdir app\static\uploads
mkdir app\static\exports

REM 初始化数据库
python -c "from app import create_app; app = create_app()"

REM 运行应用
python run.py
