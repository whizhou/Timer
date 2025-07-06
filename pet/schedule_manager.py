import json
import os
import time
from typing import List, Dict, Any
import threading
import sys
import requests

from pet_login import get_session_id

from config import PetConfig
BASE_URL = PetConfig.BASE_URL
SCHEDULE_REMINDER_DAYS = PetConfig.SCHEDULE_REMINDER_DAYS

def singleton(cls):
    """单例装饰器"""
    instances = {}
    
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

@singleton
class ScheduleManager:
    """管理日程数据的单例类"""
    
    def __init__(self, update_interval: int = 3):
        # 检查是否已经初始化过
        if hasattr(self, '_initialized'):
            return
            
        # self.schedules_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        #                                  "backends", "data", "example_schedules.json")
        self.schedules = []
        self.last_update_time = 0
        self.update_interval = update_interval
        self.count = 0
        self.summary = []
        # self._start_update_thread()
        
        # 标记已初始化
        self._initialized = True
    
    # def _start_update_thread(self):
    #     """启动自动更新线程"""
    #     def update_loop():
    #         while True:
    #             self.update_schedules()
    #             time.sleep(self.update_interval)
        
    #     update_thread = threading.Thread(target=update_loop, daemon=True)
    #     update_thread.start()
    
    def update_schedules(self) -> None:
        """更新日程数据"""
        try:
            # session_id = get_session_id()
            # if not session_id:
            #     raise ValueError("Session ID is not set. Please log in first.")
            # response = requests.get(
            #     f"{BASE_URL}/schedule/running",
            #     json={'schedules': self.schedules},
            #     cookies={'session': session_id},
            # )
            # self.schedules = response.json()
            self.schedules = self.get_upcoming_schedules_summary(right_now=True)
            # print("2")
            print(f"日程数量: {len(self.schedules)}")
            print(self.schedules)
        except Exception as e:
            print(f"Error updating schedules: {e}")
            self.schedules = []
        # try:
        #     if os.path.exists(self.schedules_file):
        #         with open(self.schedules_file, 'r', encoding='utf-8') as f:
        #             data = json.load(f)
        #             self.schedules = data.get('schedules', [])
        #             print(f"日程数量: {len(self.schedules)}")
        #             self.last_update_time = time.time()
        # except Exception as e:
        #     print(f"Error updating schedules: {e}")

    
    def get_schedules(self) -> List[Dict[str, Any]]:
        """获取所有日程"""
        return self.summary
    
    def get_schedule_count(self) -> int:
        """获取日程数量"""
        print(f"日程数量: {len(self.schedules)}")
        return len(self.summary)
    
    def get_active_schedules(self, right_now = False) -> List[Dict[str, Any]]:
        """获取当前活跃的日程（未过期的日程）"""
        return self.get_upcoming_schedules_summary_count()
    
    
    def get_active_schedule_count(self, right_now = False) -> int:
        """获取活跃日程数量"""
        return self.get_upcoming_schedules_summary_count(right_now=right_now)

    def get_upcoming_schedules_summary(self, right_now = False, days = SCHEDULE_REMINDER_DAYS) -> str:
        """获取未来days天截止的日程信息"""
        if right_now == False:
            return self.summary
        
        try:
            session_id = get_session_id()
            self.summary = []   # 清空summary, 避免重复添加 && 刷新，去除旧日程
            if not session_id:
                raise ValueError("Session ID is not set. Please log in first.")
            for i in range(0, days):
                response = requests.get(
                    f"{BASE_URL}/schedule/titles/{i}",
                    # json={'schedules': self.schedules},
                    cookies={'session': session_id},
                )
                schedules = response.json()['titles']
                self.summary.extend(schedules)
        except Exception as e:
            print(f"Error updating schedules: {e}")
        
        return self.summary
    
    def get_upcoming_schedules_summary_count(self, right_now = False, days = SCHEDULE_REMINDER_DAYS) -> int:
        """获取未来days天截止的日程信息数量"""
        return len(self.get_upcoming_schedules_summary(right_now=right_now, days=days))
    

# 测试
# print("1")
ScheduleManager().update_schedules()
# print("2")
# print(ScheduleManager().get_active_schedules())
# print("3")
# print(ScheduleManager().get_upcoming_schedules_summary(right_now=True))
