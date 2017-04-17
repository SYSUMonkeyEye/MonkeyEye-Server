from app import create_app
from app.controller.user import user

if __name__ == '__main__':
    app = create_app("development")
    app.register_blueprint(user)
    app.run()
