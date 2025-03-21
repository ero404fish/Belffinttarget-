# Belffin Target运营工具 - 部署步骤

本文档提供了Belffin Target运营工具的详细部署步骤，包括环境准备、安装依赖、配置和启动应用。

## 1. 环境要求

- Python 3.6+
- pip3 (Python包管理器)
- 操作系统：Windows、macOS或Linux

## 2. 安装步骤

### 2.1 下载并解压程序包

1. 下载`belffin_target_tool.zip`压缩包
2. 将压缩包解压到您选择的目录，例如：
   - Windows: `C:\belffin_target_tool`
   - macOS/Linux: `/home/user/belffin_target_tool`

### 2.2 安装依赖

打开命令行终端（Windows的命令提示符或PowerShell，macOS/Linux的终端），进入解压后的目录：

```bash
# Windows
cd C:\belffin_target_tool

# macOS/Linux
cd /home/user/belffin_target_tool
```

安装所需的Python依赖：

```bash
pip3 install -r requirements.txt
```

这将安装以下依赖：
- Flask：Web框架
- Flask-SQLAlchemy：数据库ORM
- Flask-WTF：表单处理
- pandas：数据处理
- openpyxl：Excel文件处理

### 2.3 初始化数据库

在应用目录中运行以下命令初始化数据库：

```bash
# Windows
python -c "from app import create_app; app = create_app()"

# macOS/Linux
python3 -c "from app import create_app; app = create_app()"
```

这将创建SQLite数据库文件和所有必要的表。

## 3. 启动应用

### 3.1 使用启动脚本（推荐）

我们提供了一个启动脚本，可以自动完成依赖安装、数据库初始化和应用启动：

```bash
# Windows
start.bat

# macOS/Linux
./start.sh
```

注意：在macOS/Linux上，您可能需要先赋予脚本执行权限：

```bash
chmod +x start.sh
```

### 3.2 手动启动

如果您不想使用启动脚本，也可以手动启动应用：

```bash
# Windows
python run.py

# macOS/Linux
python3 run.py
```

## 4. 访问应用

应用启动后，打开Web浏览器，访问以下地址：

```
http://localhost:5000
```

您应该能看到Belffin Target运营工具的主页面。

## 5. 配置（可选）

### 5.1 修改端口

如果您需要更改默认端口（5000），可以编辑`run.py`文件，修改以下行：

```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

将`port=5000`更改为您想要的端口号。

### 5.2 生产环境部署

对于生产环境，建议：

1. 将`debug=True`改为`debug=False`
2. 使用Gunicorn或uWSGI作为WSGI服务器
3. 使用Nginx或Apache作为反向代理

生产环境部署示例（使用Gunicorn）：

```bash
# 安装Gunicorn
pip3 install gunicorn

# 启动应用
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

## 6. 故障排除

### 6.1 依赖安装问题

如果安装依赖时遇到权限问题，尝试：

```bash
# Windows (以管理员身份运行命令提示符)
pip3 install -r requirements.txt

# macOS/Linux
sudo pip3 install -r requirements.txt
```

### 6.2 数据库初始化问题

如果数据库初始化失败，尝试删除现有的数据库文件并重新初始化：

```bash
# 删除数据库文件
rm -f instance/belffin_target.db

# 重新初始化
python3 -c "from app import create_app; app = create_app()"
```

### 6.3 端口占用问题

如果5000端口已被占用，您会看到类似以下错误：

```
OSError: [Errno 98] Address already in use
```

请修改`run.py`中的端口号，或终止占用该端口的进程。

## 7. 联系支持

如果您在部署过程中遇到任何问题，请联系Belffin技术支持团队获取帮助。
