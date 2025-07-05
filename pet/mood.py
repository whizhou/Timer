import os
import random
import time
from schedule_manager import ScheduleManager

# 获取当前脚本的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # \Timer

class Mood:
    """桌宠心情类"""
    
    def __init__(self, moodType = "normal"):
        self.moodType = moodType
        self.mood_timestamp = time.time()
        self.schedule_manager = ScheduleManager()
        self.active_count = 0
        self.count = 0

    def getMoodType(self):
        """根据当前任务信息，获取当前心情类型"""
        if self.count != 0:
            self.count = (self.count + 1) % 50  # 每50次调用获取一次活跃日程数量
            return self.moodType
        
        self.count = (self.count + 1) % 50  # 每50次调用获取一次活跃日程数量
        self.active_count = self.schedule_manager.get_active_schedule_count()
        print(f"活跃日程数量: {self.active_count}")
        # 根据活跃日程数量设置心情
        if self.active_count == 0:
            self.moodType = "Happy"  # 没有日程，心情好
        elif self.active_count <= 3:
            self.moodType = "Normal"  # 1-3个日程，心情正常
        else:
            self.moodType = "PoorCondition"  # 超过3个日程，心情不好
            
        return self.moodType
    
    def setMoodType(self, moodType):
        """设置心情类型"""
        self.moodType = moodType
        self.mood_timestamp = time.time()
        
    def get_schedules(self):
        """获取所有日程"""
        return self.schedule_manager.get_schedules()
        
    def get_active_schedules(self):
        """获取活跃日程"""
        return self.schedule_manager.get_active_schedules()
        
    def get_schedule_count(self):
        """获取日程总数"""
        return self.schedule_manager.get_schedule_count()
        
    def get_active_schedule_count(self):
        """获取活跃日程数量"""
        return self.schedule_manager.get_active_schedule_count()