import json
import os
import time
from typing import List, Dict, Any
import threading
import sys
import requests

from pet_login import get_session_id

BASE_URL = "http://127.0.0.1:5000"

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
        self.update_schedules()
        current_time = time.time()
        active_schedules = []
        
        print(self.schedules)
        for schedule in self.schedules:
            print("?",schedule)
            content = schedule.get('content', {})
            if 'end_time' in content:
                end_time_str = ' '.join(content['end_time'])
                try:
                    end_timestamp = time.mktime(time.strptime(end_time_str, '%Y-%m-%d %H:%M'))
                    if end_timestamp > current_time:
                        active_schedules.append(schedule)
                except ValueError:
                    continue
        
        return active_schedules
    
    
    
    def get_active_schedule_count(self) -> int:
        """获取活跃日程数量"""
        self.update_schedules()
        return len(self.get_active_schedules())

    def get_upcoming_schedules_summary(self) -> str:
        """获取明天和后天截止的日程信息总结"""
        active_schedules = self.get_active_schedules()
        current_time = time.localtime()
        tomorrow = time.localtime(time.time() + 24 * 3600)
        day_after_tomorrow = time.localtime(time.time() + 48 * 3600)
        
        tomorrow_schedules = []
        day_after_schedules = []
        
        for schedule in active_schedules:
            content = schedule.get('content', {})
            if 'end_time' in content:
                end_time_str = ' '.join(content['end_time'])
                try:
                    end_time = time.strptime(end_time_str, '%Y-%m-%d %H:%M')
                    # 检查是否是明天截止
                    if (end_time.tm_year == tomorrow.tm_year and 
                        end_time.tm_mon == tomorrow.tm_mon and 
                        end_time.tm_mday == tomorrow.tm_mday):
                        tomorrow_schedules.append(content.get('title', '未命名日程'))
                    # 检查是否是后天截止
                    elif (end_time.tm_year == day_after_tomorrow.tm_year and 
                          end_time.tm_mon == day_after_tomorrow.tm_mon and 
                          end_time.tm_mday == day_after_tomorrow.tm_mday):
                        day_after_schedules.append(content.get('title', '未命名日程'))
                except ValueError:
                    continue
        
        summary = []
        if tomorrow_schedules:
            for task in tomorrow_schedules:
                summary.append(f"明天要完成{task}！")
        if day_after_schedules:
            for task in day_after_schedules:
                summary.append(f"后天要完成{task}！")
                
        return summary
    

print(ScheduleManager().get_upcoming_schedules_summary())