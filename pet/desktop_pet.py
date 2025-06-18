"""
桌宠数据模型
管理桌宠的核心数据和状态
"""
import os
from typing import Dict, Any, List, Tuple
from config import PetConfig
from mood import Mood
from pet_action import PetAction

class DesktopPet:
    """桌宠核心数据模型类"""
    
    def __init__(self, position: Tuple[int, int] = (0, 0), mood: Mood = None, 
                 actions: List[str] = None, pet_id: int = 1):
        """
        初始化桌宠
        
        Args:
            position: 桌宠位置坐标
            mood: 桌宠心情对象
            actions: 可执行的动作列表
            pet_id: 桌宠ID
        """
        self.id = pet_id
        self.position = position
        self.mood = mood or Mood()
        self.actions = actions or ["idle", "jump", "study", "down"]
        
        # 桌宠状态
        self.current_action = "idle"
        self.is_dragging = False
        self.is_chatting = False
        self.is_exiting = False
        
        # 统计数据
        self.stats = {
            "interaction_count": 0,
            "task_complete_count": 0,
            "chat_count": 0,
            "drag_count": 0,
            "total_online_time": 0,
            "creation_time": None
        }
        
        # 初始化创建时间
        import time
        self.stats["creation_time"] = time.time()

    def get_id(self) -> int:
        """获取桌宠ID"""
        return self.id
    
    def set_id(self, pet_id: int):
        """设置桌宠ID"""
        self.id = pet_id

    def get_position(self) -> Tuple[int, int]:
        """获取桌宠位置"""
        return self.position
        
    def update_position(self, new_position: Tuple[int, int]):
        """更新桌宠位置"""
        self.position = new_position
        
    def get_mood(self) -> Mood:
        """获取桌宠心情对象"""
        return self.mood
    
    def get_mood_type(self) -> str:
        """获取当前心情类型"""
        return self.mood.getMoodType()
        
    def change_mood(self, new_mood: Mood):
        """更新桌宠的心情"""
        self.mood = new_mood
        return self.mood

    def perform_action(self, action: str) -> str:
        """执行宠物动作"""
        if action in self.actions:
            self.current_action = action
            print(f"桌宠 {self.id} 执行动作: {action}")
            return action
        else:
            print(f"动作 {action} 不在可执行列表中")
            return self.current_action
    
    def get_current_action(self) -> str:
        """获取当前动作"""
        return self.current_action
    
    def set_dragging_state(self, is_dragging: bool):
        """设置拖拽状态"""
        self.is_dragging = is_dragging
        if is_dragging:
            self.stats["drag_count"] += 1
    
    def set_chatting_state(self, is_chatting: bool):
        """设置聊天状态"""
        self.is_chatting = is_chatting
        if is_chatting:
            self.stats["chat_count"] += 1
    
    def set_exiting_state(self, is_exiting: bool):
        """设置退出状态"""
        if self.is_exiting and is_exiting:
            # 已经在退出状态，避免重复设置
            print("桌宠已处于退出状态")
            return
        self.is_exiting = is_exiting
        if is_exiting:
            print(f"桌宠 {self.id} 开始退出流程")
    
    def is_in_dragging_state(self) -> bool:
        """是否处于拖拽状态"""
        return self.is_dragging
    
    def is_in_chatting_state(self) -> bool:
        """是否处于聊天状态"""
        return self.is_chatting
    
    def is_in_exiting_state(self) -> bool:
        """是否处于退出状态"""
        return self.is_exiting
        
    def record_interaction(self):
        """记录互动次数"""
        self.stats["interaction_count"] += 1
        
    def record_task_completion(self):
        """记录任务完成次数"""
        self.stats["task_complete_count"] += 1
        
    def get_stats(self) -> Dict[str, Any]:
        """获取桌宠统计信息"""
        # 更新在线时间
        import time
        if self.stats["creation_time"]:
            self.stats["total_online_time"] = time.time() - self.stats["creation_time"]
        return self.stats
    
    def get_current_animation_path(self, animation_type: str = None) -> str:
        """
        获取当前状态对应的动画路径
        
        Args:
            animation_type: 指定动画类型，如果为None则根据当前状态自动判断
        """
        if animation_type is None:
            if self.is_exiting:
                animation_type = PetConfig.AnimationType.FINISH_WORK
            elif self.is_dragging:
                animation_type = PetConfig.AnimationType.DRAG
            elif self.is_chatting:
                animation_type = PetConfig.AnimationType.CHAT
            else:
                animation_type = PetConfig.AnimationType.STAND
        
        mood_type = self.get_mood_type()
        return PetConfig.get_animation_path(self.id, animation_type, mood_type)
    
    def get_available_actions(self) -> List[str]:
        """获取可用动作列表"""
        return self.actions.copy()
    
    def add_action(self, action: str):
        """添加新动作"""
        if action not in self.actions:
            self.actions.append(action)
    
    def remove_action(self, action: str):
        """移除动作"""
        if action in self.actions:
            self.actions.remove(action)
    
    def to_dict(self) -> Dict[str, Any]:
        """将桌宠数据转换为字典格式"""
        return {
            "id": self.id,
            "position": self.position,
            "mood_type": self.get_mood_type(),
            "actions": self.actions,
            "current_action": self.current_action,
            "is_dragging": self.is_dragging,
            "is_chatting": self.is_chatting,
            "is_exiting": self.is_exiting,
            "stats": self.stats
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"DesktopPet(id={self.id}, mood={self.get_mood_type()}, position={self.position})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()