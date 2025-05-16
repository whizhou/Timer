import os
import yaml
from pathlib import Path
from datetime import timedelta
from cachelib.file import FileSystemCache

class Config:
    cur_dir = Path(__file__).resolve().parent
    root_dir = cur_dir.parent

    # private key settings
    _DEEPSEEK_API_KEY = cur_dir.joinpath('deepseek_api_key.txt').read_text().strip()
    _SCHEDULE_JSON_PATH = cur_dir / '../data/example_schedules.json'

    # session settings
    SESSION_TYPE = 'filesystem'  # 使用文件系统存储会话
    SESSION_CACHELIB = FileSystemCache(
        cache_dir=str(root_dir / 'data' / 'chat_session'),
        threshold=1000,  # 最大缓存数量
    )
    SESSION_PERMANENT = True  # 启用持久化
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # 过期时间

    # Scheduler settings
    SCHEDULER_SETTINGS = {}

    @property
    def DEEPSEEK_API_KEY(self):
        return self._DEEPSEEK_API_KEY
    
    @property
    def SCHEDULE_JSON_PATH(self):
        return self._SCHEDULE_JSON_PATH

class DevelopmentConfig(Config):
    # DEBUG = True
    SECRET_KEY = 'dev'
    pass

class ProductionConfig(Config):
    # DEBUG = False
    pass

class TestingConfig(Config):
    pass