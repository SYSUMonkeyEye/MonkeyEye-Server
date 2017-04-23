from app import create_app

app = create_app('development')

if __name__ == '__main__':
    app.run(host=app.config.get('HOST', '127.0.0.1'), use_reloader=False)
