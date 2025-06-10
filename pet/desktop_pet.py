import os

# 获取当前脚本的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# 导入相关模块
from mood import Mood
from pet_action import PetAction

class DesktopPet:
    """桌宠类，管理宠物状态和行为"""
    
    def __init__(self, position, mood, actions=None, id=1):
        self.position = position
        self.mood = mood
        self.actions = actions or []
        self.id = id
        self.stats = {
            "interaction_count": 0,
            "task_complete_count": 0
        }

    def changeMood(self, newMood):
        """更新宠物的心情"""
        self.mood = newMood
        return self.mood

    def performAction(self, action):
        """执行宠物动作"""
        print(f"执行动作: {action}")
        return action
        
    def getPosition(self):
        """获取宠物位置"""
        return self.position
        
    def updatePosition(self, new_position):
        """更新宠物位置"""
        self.position = new_position
        
    def recordInteraction(self):
        """记录互动次数"""
        self.stats["interaction_count"] += 1
        
    def recordTaskCompletion(self):
        """记录任务完成次数"""
        self.stats["task_complete_count"] += 1
        
    def getStats(self):
        """获取宠物统计信息"""
        return self.stats