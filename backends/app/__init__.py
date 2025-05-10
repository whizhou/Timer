from flask import Flask
from ..config.config import Config
from .extensions import db, cache  # 示例扩展

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    cache.init_app(app)

    # 注册蓝图
    from ..routes.schedule import schedule_bp
    from ..routes.ai import ai_bp
    app.register_blueprint(schedule_bp)
    app.register_blueprint(ai_bp)

    return app