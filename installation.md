# Belffin Target运营工具 - 安装指引

本文档提供了Belffin Target运营工具的详细安装指引，帮助您快速上手使用该工具。

## 1. 系统要求

在安装Belffin Target运营工具之前，请确保您的系统满足以下要求：

- **操作系统**：Windows 7/10/11、macOS 10.14+、Ubuntu 18.04+或其他Linux发行版
- **Python**：Python 3.6或更高版本
- **磁盘空间**：至少100MB可用空间
- **内存**：至少2GB RAM
- **浏览器**：Chrome、Firefox、Edge或Safari的最新版本

## 2. 下载安装包

1. 从提供的链接下载`belffin_target_tool.zip`压缩包
2. 将压缩包保存到您计算机上的一个容易找到的位置

## 3. 安装步骤

### 3.1 Windows系统

1. 右键点击下载的`belffin_target_tool.zip`文件，选择"提取全部"
2. 选择一个目标文件夹，例如`C:\belffin_target_tool`
3. 打开命令提示符（按Win+R，输入cmd，然后按Enter）
4. 导航到解压后的文件夹：
   ```
   cd C:\belffin_target_tool
   ```
5. 运行安装脚本：
   ```
   start.bat
   ```
6. 等待安装完成，系统将自动打开浏览器访问应用

### 3.2 macOS系统

1. 双击下载的`belffin_target_tool.zip`文件解压
2. 打开终端（在应用程序/实用工具中找到）
3. 导航到解压后的文件夹：
   ```
   cd /path/to/belffin_target_tool
   ```
4. 给启动脚本添加执行权限：
   ```
   chmod +x start.sh
   ```
5. 运行安装脚本：
   ```
   ./start.sh
   ```
6. 等待安装完成，然后在浏览器中访问`http://localhost:5000`

### 3.3 Linux系统

1. 打开终端
2. 导航到下载文件夹，解压文件：
   ```
   unzip belffin_target_tool.zip -d /home/user/belffin_target_tool
   ```
3. 导航到解压后的文件夹：
   ```
   cd /home/user/belffin_target_tool
   ```
4. 给启动脚本添加执行权限：
   ```
   chmod +x start.sh
   ```
5. 运行安装脚本：
   ```
   ./start.sh
   ```
6. 等待安装完成，然后在浏览器中访问`http://localhost:5000`

## 4. 验证安装

安装完成后，您应该能够在浏览器中看到Belffin Target运营工具的主页面。如果一切正常，您将看到以下功能模块：

- 产品上架工具
- 库存更新工具
- 产品数据库

## 5. 安装常见问题

### 5.1 Python未安装或版本过低

如果您收到"Python未找到"或"Python版本过低"的错误，请从[Python官网](https://www.python.org/downloads/)下载并安装最新版本的Python。

安装时，请确保勾选"Add Python to PATH"选项。

### 5.2 依赖安装失败

如果依赖安装失败，可能是由于网络问题或权限问题。尝试以下解决方案：

- 检查您的网络连接
- 使用管理员/超级用户权限运行安装脚本
- 手动安装依赖：
  ```
  pip3 install flask flask-sqlalchemy flask-wtf pandas openpyxl
  ```

### 5.3 端口冲突

如果5000端口已被其他应用占用，您可以修改`run.py`文件中的端口号：

```python
app.run(host='0.0.0.0', port=5001, debug=True)  # 将5000改为其他端口
```

### 5.4 数据库初始化问题

如果数据库初始化失败，尝试删除现有的数据库文件并重新初始化：

```bash
# 删除数据库文件
rm -f instance/belffin_target.db

# 重新初始化
python3 -c "from app import create_app; app = create_app()"
```

## 6. 下一步

安装完成后，请参阅[使用说明](./user_guide.md)文档，了解如何使用Belffin Target运营工具的各项功能。
