import os
import random

# 获取当前脚本的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# 使用相对导入
from pet_action import PetAction

class PetActionController:
    def __init__(self, pet):
        self.pet = pet
        self.pet_action = PetAction()
        self.action_probabilities = {
            "stand": 0.6,  # 发呆概率
            "walk": 0.3,  # 走路概率
            "study": 0.1  # 学习概率
        }
    
    def get_random_action(self):
        """获取随机动作"""
        actions = list(self.action_probabilities.keys())
        probabilities = list(self.action_probabilities.values())
        return random.choices(actions, weights=probabilities, k=1)[0]
    
    def updateAction(self):
        """更新桌宠动作"""
        # 如果当前是受控动作(drag, chat)，不随机更新
        current_action = self.getAction()
        if current_action in ["drag", "chat"]:
            return current_action
        
        # 根据心情调整动作概率
        mood = self.pet.mood.getMoodType() if hasattr(self.pet, 'mood') else "normal"
        
        if mood == "happy":
            self.action_probabilities = {
                "stand": 0.5,
                "walk": 0.4,
                "study": 0.1
            }
        elif mood == "down":
            self.action_probabilities = {
                "stand": 0.8,
                "walk": 0.1,
                "study": 0.1
            }
        elif mood == "study":
            self.action_probabilities = {
                "stand": 0.3,
                "walk": 0.1,
                "study": 0.6
            }
        else:  # normal
            self.action_probabilities = {
                "stand": 0.6,
                "walk": 0.3,
                "study": 0.1
            }
        
        # 随机选择一个动作
        new_action = self.get_random_action()
        self.setAction(new_action)
        return new_action
    
    def setAction(self, action_type):
        """手动设置动作"""
        return self.pet_action.setActionType(action_type)
    
    def getAction(self):
        """获取当前动作"""
        return self.pet_action.getActionType()
    
    def playAction(self, action):
        """播放宠物的动作"""
        print(f"播放动作: {action}")
        if hasattr(self.ui, 'showAction'):
            self.ui.showAction(action)

    def stopAction(self, action):
        """停止宠物的动作"""
        print(f"停止动作: {action}")