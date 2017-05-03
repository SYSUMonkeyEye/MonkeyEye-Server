from flask import jsonify
from app import create_app

app = create_app('development')


@app.errorhandler(405)
def MethodNotAllowed(e):
    return jsonify({'message': 'Method Not Allowed'}), 405


if __name__ == '__main__':
    app.run(host=app.config.get('HOST', '127.0.0.1'), use_reloader=False)
