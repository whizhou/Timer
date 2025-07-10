"""
桌宠配置管理模块
集中管理所有配置信息、资源路径和常量
"""
import os

class PetConfig:
    """桌宠全局配置类"""
    
    # 获取当前脚本的绝对路径
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
    
    # 动画相关配置
    ANIMATION_FRAME_INTERVAL = 100  # 动画帧间隔(毫秒)
    UPDATE_INTERVAL = 70  # 动画更新检查间隔(秒)
    
    # 待机动作相关配置
    IDLE_ACTION_INTERVAL = 30  # 待机动作触发间隔(秒)
    IDLE_ACTION_DURATION = 3000  # 待机动作持续时间(毫秒)
    IDLE_ACTION_MIN_INTERVAL = 15  # 最小待机动作间隔(秒)
    IDLE_ACTION_MAX_INTERVAL = 60  # 最大待机动作间隔(秒)

    
    # UI相关配置
    DEFAULT_PET_WIDTH = 300
    DEFAULT_PET_HEIGHT = 300
    BUBBLE_MAX_WIDTH = 250
    HOVER_DELAY = 2000  # 悬停延迟(毫秒)
    BUBBLE_FADE_INTERVAL = 50  # 气泡淡出间隔(毫秒)
    
    # 交互相关配置
    DOUBLE_CLICK_TIMEOUT = 300  # 双击检测超时(毫秒)
    
    # 动画文件夹路径模板
    STATIC_PATH = os.path.join(CURRENT_DIR, "static")
    CHARACTER_PATH_TEMPLATE = "charactor/{pet_id}/{animation_type}/{mood}"
    
    # 动画类型
    class AnimationType:
        STAND = "stand"
        DRAG = "drag"
        CHAT = "chat"
        STUDY = "study"
        WALK = "walk"
        SWITCH_UP = "switch_up"
        SWITCH_DOWN = "switch_down"
        FINISH_WORK = "finish_work"
        SHUTDOWN = "shutdown"  # 退出动画，与finish_work相同
        HUNGER = "hunger"
        THINK = "think"  # 思考动作
    
    # 待机动作类型列表
    class IdleActionType:
        """待机动作类型"""
        FINISH_WORK = "finish_work"  # 完成工作
        THINK = "think"  # 思考
        HUNGER = "hunger"  # 饥饿
        STUDY = "study"  # 学习
        WALK = "walk"  # 散步
        
        @classmethod
        def get_all_idle_actions(cls):
            """获取所有待机动作类型"""
            return [
                cls.FINISH_WORK,
                cls.THINK,
                cls.HUNGER,
                cls.STUDY,
                cls.WALK
            ]

    
    # 心情类型
    class MoodType:
        HAPPY = "Happy"
        NORMAL = "Normal"
        POOR_CONDITION = "PoorCondition"
    
    # 退出动画播放时长(毫秒)
    EXIT_ANIMATION_DURATION = 3000
    
    @classmethod
    def get_animation_path(cls, pet_id, animation_type, mood=None):
        """获取动画资源路径"""
        if mood is None:
            path_template = f"charactor/{pet_id}/{animation_type}"
        else:
            path_template = cls.CHARACTER_PATH_TEMPLATE.format(
                pet_id=pet_id, 
                animation_type=animation_type, 
                mood=mood
            )
        return os.path.join(cls.STATIC_PATH, path_template)
    
    @classmethod
    def get_resource_path(cls, relative_path):
        """获取资源的正确路径"""

        return os.path.join(cls.PROJECT_ROOT, relative_path.lstrip('/'))
    
    @classmethod 
    def get_idle_action_interval(cls):
        """获取待机动作间隔时间(秒)"""
        return cls.IDLE_ACTION_INTERVAL
    
    @classmethod
    def set_idle_action_interval(cls, interval):
        """设置待机动作间隔时间(秒)"""
        cls.IDLE_ACTION_INTERVAL = max(cls.IDLE_ACTION_MIN_INTERVAL, min(interval, cls.IDLE_ACTION_MAX_INTERVAL))
    
    @classmethod
    def get_idle_action_duration(cls):
        """获取待机动作持续时间(毫秒)"""
        return cls.IDLE_ACTION_DURATION
    
    @classmethod
    def set_idle_action_duration(cls, duration):
        """设置待机动作持续时间(毫秒)"""
        cls.IDLE_ACTION_DURATION = max(1000, min(duration, 10000))  # 限制在1-10秒之间 

