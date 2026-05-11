import os
from flask import Flask
from flask_login import LoginManager
from models import db, User
from config import Config
from routes.auth import auth_bp
from routes.blog import blog_bp
from routes.user import user_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(blog_bp)
    app.register_blueprint(user_bp)

    @app.route('/api/preview', methods=['POST'])
    def markdown_preview():
        from flask import request, jsonify
        from utils import render_markdown
        data = request.get_json(silent=True) or {}
        content = data.get('content', '')
        return jsonify({'html': render_markdown(content)})

    with app.app_context():
        db.create_all()
        _seed_default_avatar(app)

    return app


def _seed_default_avatar(app):
    dest = os.path.join(app.config['UPLOAD_FOLDER'], 'profiles', 'default.png')
    if not os.path.exists(dest):
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        # Create a simple 128x128 grey placeholder
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (128, 128), color='#8CB0D1')
            draw = ImageDraw.Draw(img)
            draw.ellipse([24, 24, 104, 104], fill='#DCE2E9')
            img.save(dest)
        except Exception:
            pass


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
