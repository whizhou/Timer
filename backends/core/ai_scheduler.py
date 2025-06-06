# AIScheduler class for managing AI-related tasks and schedules.
# This class is inherited from the Scheduler class and is responsible for managing AI-related tasks and schedules.

import json
import os
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

from .deepseekv2 import parse_schedule
from .scheduler import Scheduler
from .database.schedule_manager import ScheduleManager

class AIScheduler(Scheduler):
    def __init__(self, app=None):
        super().__init__()
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the AIScheduler with the given app."""
        super().init_app(app)  # type: ignore
        self.settings = app.config.get('AI_SCHEDULER_SETTINGS', {})

    # Add AI-specific methods here
    def create_json(self, context, existing_schedules=None):
        """
        调用parse_schedule生成AI日程，并创建到数据库
        Args:
            context: 用户输入的任务内容
            existing_schedules: 已有日程（可选）
        Returns:
            List[int]: 新建日程的ID列表
        """
        target_json = parse_schedule(context, existing_schedules=existing_schedules)
        # create_schedule 期望参数为 List[Dict]
        return self.create_schedule([target_json])
