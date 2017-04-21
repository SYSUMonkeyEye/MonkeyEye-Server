from app import create_app

if __name__ == '__main__':
    app = create_app('development')
    app.run(host=app.config.get('HOST', '127.0.0.1'), use_reloader=False)