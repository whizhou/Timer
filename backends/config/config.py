import os
import yaml
from pathlib import Path

class Config:
    DEEPSEEK_API_KEY = Path("deepseek_api_key.txt").read_text().strip()
    SCHEDULE_JSON_PATH = "./data/schedules.json"

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False