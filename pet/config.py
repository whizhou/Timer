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
    UPDATE_INTERVAL = 5  # 动画更新检查间隔(秒)
    
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