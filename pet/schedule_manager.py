import json
import os
import time
from typing import List, Dict, Any
import threading
import sys
import requests

from pet_login import get_session_id

BASE_URL = "https://whizhou.pythonanywhere.com/"

class ScheduleManager:
    """管理日程数据的类"""
    
    def __init__(self, update_interval: int = 3):
        # self.schedules_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        #                                  "backends", "data", "example_schedules.json")
        self.schedules = []
        self.last_update_time = 0
        self.update_interval = update_interval
    #     self._start_update_thread()
    
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
            session_id = get_session_id()
            if not session_id:
                raise ValueError("Session ID is not set. Please log in first.")
            response = requests.get(
                f"{BASE_URL}/schedule/running",
                json={'schedules': self.schedules},
                cookies={'session': session_id},
            )
            self.schedules = response.json()
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
        self.update_schedules()
        return self.schedules
    
    def get_schedule_count(self) -> int:
        """获取日程数量"""
        self.update_schedules()
        print(f"日程数量: {len(self.schedules)}")
        return len(self.schedules)
    
    def get_active_schedules(self) -> List[Dict[str, Any]]:
        """获取当前活跃的日程（未过期的日程）"""
        active_schedules = []
        self.update_schedules()
        active_schedules = self.schedules.copy()
        return active_schedules
    
    
    
    def get_active_schedule_count(self) -> int:
        """获取活跃日程数量"""
        # self.update_schedules()
        return len(self.get_active_schedules())

    def get_upcoming_schedules_summary(self) -> str:
        """获取明天和后天截止的日程信息"""
        tomorrow_schedules = []
        day_after_schedules = []
        
        try:
            session_id = get_session_id()
            if not session_id:
                raise ValueError("Session ID is not set. Please log in first.")
            response = requests.get(
                f"{BASE_URL}/schedule/titles/1",
                # json={'schedules': self.schedules},
                cookies={'session': session_id},
            )
            tomorrow_schedules = response.json()['titles']
            response = requests.get(
                f"{BASE_URL}/schedule/titles/2",
                # json={'schedules': self.schedules},
                cookies={'session': session_id},
            )
            day_after_schedules = response.json()['titles']
        except Exception as e:
            print(f"Error updating schedules: {e}")
        
        
        summary = tomorrow_schedules + day_after_schedules
        return summary
    

print(ScheduleManager().get_upcoming_schedules_summary())