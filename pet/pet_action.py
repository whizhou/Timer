import os

# 获取当前脚本的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

class PetAction:
    """桌宠动作类"""
    
    def __init__(self, actionType="idle"):
        self.actionType = actionType
        self.action_types = ["idle", "walk", "study", "chat", "drag", "stand"]

    def perform(self):
        """执行该动作"""
        print(f"执行动作: {self.actionType}")
        
    def getActionType(self):
        """获取动作类型"""
        return self.actionType
        
    def setActionType(self, actionType):
        """设置动作类型"""
        if actionType in self.action_types:
            self.actionType = actionType
            return True
        return False