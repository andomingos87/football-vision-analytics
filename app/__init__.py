from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'football-vision-analytics-secret-key'
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
    app.config['RESULTS_FOLDER'] = 'app/static/results'
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload size
    app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'mov'}
    
    from .routes import main
    app.register_blueprint(main)
    
    return app
