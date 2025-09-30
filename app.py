# from flask import Flask
# from config import Config
# from extensions import init_extensions
# from routes.weather import bp as weather_bp

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)

#     # Initialize extensions
#     init_extensions(app)

#     # Register blueprints
#     app.register_blueprint(weather_bp)

#     # DB tables will not be automatically created here

#     return app

# if __name__ == "__main__":
#     app = create_app()
#     app.run(debug=app.config.get("DEBUG", True), host="127.0.0.1", port=5000)
from flask import Flask
from config import Config
from extensions import init_extensions
from routes.weather import bp as weather_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    init_extensions(app)

    # Register routes
    app.register_blueprint(weather_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config.get("DEBUG", True), host="127.0.0.1", port=5000)
