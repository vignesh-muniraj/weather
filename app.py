
from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import init_extensions, db
from routes.weather import bp as weather_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_extensions(app)

    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

    app.register_blueprint(weather_bp)



    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config.get("DEBUG", True), host="127.0.0.1", port=5000)

