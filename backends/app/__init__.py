from flask import Flask
from datetime import timedelta
from flask_session import Session
from flask_cors import CORS
from config.config import Config, DevelopmentConfig
# from .extensions import db, cache  # 示例扩展
from core.core import scheduler

def create_app(cfg=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(cfg)

    CORS(app, supports_credentials=True)  # 启用跨域资源共享

    Session(app)  # 初始化会话扩展

    # 初始化扩展
    # db.init_app(app)
    # cache.init_app(app)
    scheduler.init_app(app)

    @app.route('/')
    def index():
        return "Hello, World!"

    # 注册蓝图
    from routes import chat_routes, schedule_routes
    app.register_blueprint(schedule_routes.bp)
    app.register_blueprint(chat_routes.bp)

    return app