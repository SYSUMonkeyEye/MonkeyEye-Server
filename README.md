# MonkeyEye-Server

猿眼电影订票系统服务端

## 安装 & 运行
1. 克隆仓库后在项目文件夹下打开终端，安装virtualenv
```
pip install virtualenv
```
2. 新建虚拟环境
```
virtualenv venv
```
3. 激活虚拟环境
```
source venv/bin/activate       # Linux 下
venv\scripts\activate          # Windows 下
```
4. 安装第三方模块
```
pip install -r requirements
```
5. 切换主程序目录
```
cd Flask-Server/
```
6. 运行项目
```
gunicorn -c gunicornConf.py server:app
或者
python server.py
```
** 注意

运行项目前，需要在Flask-Server目录下新建`instance`目录，并在`instance`目录下新建`config.py`文件，在该文件中添加项目的私密配置
```python
SECRET_KEY = 
SQLALCHEMY_DATABASE_URI = 
APPKEY = 
APPSECRET = 
ADMIN_USERNAME = 
ADMIN_PASSWORD = 
```
