
"""
桌宠控制器模块
负责桌宠的核心逻辑控制、动画管理和用户交互处理
"""
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

import random
import os
import threading
import time

from typing import Optional
from config import PetConfig
from schedule_manager import ScheduleManager
from Bubble import Msg


# 获取当前脚本的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

print(f"当前项目根目录: {project_root}")

# 使用相对导入
from Bubble import Msg  # 导入Bubble.py中的Msg类

# 定义一个函数来获取正确的资源路径
def get_resource_path(relative_path):
    """获取资源的正确路径，优先查找本地目录，然后是上级目录"""
    local_path = os.path.join(project_root + relative_path)    
    return local_path

class DesktopPetController:

    """桌宠核心控制器类"""
    
    def __init__(self, pet, ui):
        """
        初始化控制器
        
        Args:
            pet: 桌宠数据模型
            ui: 桌宠UI界面
        """
        self.pet = pet
        self.ui = ui
        
        # 状态管理
        self.is_dragging = False
        self.current_mood = pet.get_mood_type()
        self.is_exiting = False
        
        # 定时器和管理器
        self.update_interval = PetConfig.UPDATE_INTERVAL
        self.bubble_timer = QTimer()
        self.bubble_timer.setSingleShot(True)
        self.bubble_timer.timeout.connect(self.ui.hide_bubble_message)
        self.schedule_manager = ScheduleManager()
        
        # 消息管理
        self.msg_bubble = Msg()
        self._init_click_messages()
        
        # 设置UI控制器引用
        self.ui.set_controller(self)
        
        # 启动自动更新
        self._start_animation_update_thread()
        
        # 设置默认悬停消息
        self._update_hover_message()

    def _init_click_messages(self):
        """初始化不同心情下的点击消息"""
        self.click_messages = {
            PetConfig.MoodType.HAPPY: [
                "任务通通完成啦~开心",
                "0个任务待完成！",
                "今天状态很好呢！"
            ],
            PetConfig.MoodType.NORMAL: [
                "有什么我能帮你的吗？",
                "今天过得还不错",
                "一起加油吧！"
            ],
            PetConfig.MoodType.POOR_CONDITION: [
                "任务做不完了！",
                "好忙啊...",
                "需要帮忙吗？"
            ]
        }
        
        # 默认消息
        self.default_click_messages = [
            "有什么需要我帮忙的吗？",
            "我在这里呢！",
            "点击我试试看！"
        ]

    def _start_animation_update_thread(self):
        """启动动画更新线程"""
        def update_loop():
            while not self.is_exiting:
                if not self.is_dragging:
                    self._update_animation_folder()
                time.sleep(self.update_interval)
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()

    def _update_animation_folder(self):
        """更新动画文件夹"""
        try:
            current_mood = self.pet.get_mood_type()
            
            # 检查心情是否发生变化
            if current_mood != self.current_mood:
                self._handle_mood_change(current_mood)
            
            # 更新默认动画
            self._load_default_animation(current_mood)
            
        except Exception as e:
            print(f"更新动画文件夹时出错: {e}")

    def _handle_mood_change(self, new_mood: str):
        """
        处理心情变化
        
        Args:
            new_mood: 新的心情类型
        """
        old_mood = self.current_mood
        print(f"心情变化: {old_mood} -> {new_mood}")
        
        # 播放心情转换动画
        if self._is_mood_improving(old_mood, new_mood):
            # 心情变好
            switch_animation_path = PetConfig.get_animation_path(
                self.pet.get_id(), 
                PetConfig.AnimationType.SWITCH_UP, 
                old_mood
            )
        elif self._is_mood_declining(old_mood, new_mood):
            # 心情变差
            switch_animation_path = PetConfig.get_animation_path(
                self.pet.get_id(), 
                PetConfig.AnimationType.SWITCH_DOWN, 
                old_mood
            )
        else:
            switch_animation_path = None
        
        if switch_animation_path and os.path.exists(switch_animation_path):
            print(f"播放心情转换动画: {switch_animation_path}")
            self.ui.set_animation_folder(switch_animation_path)
            
            # 延迟后切换到默认动画
            QTimer.singleShot(2000, lambda: self._load_default_animation(new_mood))
        
        self.current_mood = new_mood
        self._update_hover_message()

    def _is_mood_improving(self, old_mood: str, new_mood: str) -> bool:
        """判断心情是否在改善"""
        mood_levels = {
            PetConfig.MoodType.POOR_CONDITION: 0,
            PetConfig.MoodType.NORMAL: 1,
            PetConfig.MoodType.HAPPY: 2
        }
        return mood_levels.get(new_mood, 0) > mood_levels.get(old_mood, 0)

    def _is_mood_declining(self, old_mood: str, new_mood: str) -> bool:
        """判断心情是否在下降"""
        mood_levels = {
            PetConfig.MoodType.POOR_CONDITION: 0,
            PetConfig.MoodType.NORMAL: 1,
            PetConfig.MoodType.HAPPY: 2
        }
        return mood_levels.get(new_mood, 0) < mood_levels.get(old_mood, 0)

    def _load_default_animation(self, mood: str):
        """
        加载默认待机动画
        
        Args:
            mood: 心情类型
        """
        animation_path = PetConfig.get_animation_path(
            self.pet.get_id(),
            PetConfig.AnimationType.STAND,
            mood
        )
        
        if os.path.exists(animation_path):
            self.ui.set_animation_folder(animation_path)
        else:
            print(f"默认动画路径不存在: {animation_path}")

    def move_pet(self, position: tuple):
        """
        控制宠物移动到指定位置
        
        Args:
            position: 目标位置 (x, y)
        """
        self.pet.update_position(position)
        self.ui.update_pet_position(position)

    def move_pet_by_offset(self, offset):
        """
        根据偏移量移动宠物
        
        Args:
            offset: QPoint偏移量
        """
        current_pos = self.pet.get_position()
        new_x = current_pos[0] + offset.x()
        new_y = current_pos[1] + offset.y()
        new_position = (new_x, new_y)
        self.move_pet(new_position)

    def perform_action(self, action: str):
        """
        执行特定的宠物动作
        
        Args:
            action: 动作名称
        """
        result = self.pet.perform_action(action)
        self.ui.show_action(result)
        return result

    def interact_with_user(self, message: str):
        """
        响应用户输入
        
        Args:
            message: 用户消息
        """
        mood_type = self.pet.get_mood_type()
        self.ui.show_bubble_message(message, mood_type)

    def get_random_click_message(self) -> str:
        """获取随机点击消息"""
        mood = self.pet.get_mood_type()
        msg_list = []
        
        # 根据心情获取消息列表
        if mood in self.click_messages:
            msg_list = self.click_messages[mood].copy()
        else:
            msg_list = self.default_click_messages.copy()
        
        # 添加日程相关消息
        schedule_messages = self.schedule_manager.get_upcoming_schedules_summary()
        if schedule_messages:
            msg_list.extend(schedule_messages)
        
        return random.choice(msg_list) if msg_list else "你好！"

    def handle_mouse_click(self, event):
        """
        处理鼠标点击事件
        
        Args:
            event: 鼠标事件
        """
        print("桌宠被点击")
        
        # 记录交互
        self.pet.record_interaction()
        
        # 只有在未拖拽时才显示气泡框
        if not self.is_dragging:
            message = self.get_random_click_message()
            mood = self.pet.get_mood_type()
            pet_position = self.pet.get_position()
            
            print(f"点击消息: {message}, 当前心情: {mood}")
            
            # 使用Bubble显示消息
            self.msg_bubble.show_above_pet(message, pet_position, mood)

    def handle_mouse_double_click(self, event):
        """
        处理鼠标双击事件
        
        Args:
            event: 鼠标事件
        """
        print("桌宠被双击 - 现在可以拖拽了")
        pet_position = self.pet.get_position()
        self.msg_bubble.show_above_pet("抓住我吧！", pet_position)

    def handle_drag_start(self, event):
        """
        处理拖拽开始事件
        
        Args:
            event: 鼠标事件
        """
        print("拖拽开始")
        self.is_dragging = True
        self.pet.set_dragging_state(True)
        
        # 切换到拖拽动画
        drag_animation_path = PetConfig.get_animation_path(
            self.pet.get_id(),
            PetConfig.AnimationType.DRAG,
            self.pet.get_mood_type()
        )
        
        if os.path.exists(drag_animation_path):
            self.ui.set_animation_folder(drag_animation_path)
        
        self.ui.show_bubble_message("被抓住了！", self.pet.get_mood_type())

    def handle_drag_end(self, event):
        """
        处理拖拽结束事件
        
        Args:
            event: 鼠标事件
        """
        print("拖拽结束")
        self.is_dragging = False
        self.pet.set_dragging_state(False)
        
        # 恢复默认动画
        self._load_default_animation(self.pet.get_mood_type())
        
        self.ui.show_bubble_message("放开我了~", self.pet.get_mood_type())

    def start_chat(self):
        """开始聊天"""
        print("开始聊天")
        self.pet.set_chatting_state(True)
        
        # 切换到聊天动画
        chat_animation_path = PetConfig.get_animation_path(
            self.pet.get_id(),
            PetConfig.AnimationType.CHAT,
            self.pet.get_mood_type()
        )
        
        if os.path.exists(chat_animation_path):
            self.ui.set_animation_folder(chat_animation_path)

    def end_chat(self):
        """结束聊天"""
        print("结束聊天")
        self.pet.set_chatting_state(False)
        
        # 恢复默认动画
        self._load_default_animation(self.pet.get_mood_type())

    def start_exit(self):
        """开始退出流程"""
        # 防止重复调用退出流程
        if self.is_exiting:
            print("退出流程已在进行中，忽略重复调用")
            return
            
        print("开始退出流程")
        self.is_exiting = True
        self.pet.set_exiting_state(True)
        
        # 停止更新线程和定时器
        if hasattr(self, 'bubble_timer'):
            self.bubble_timer.stop()
        
        # 显示退出消息
        self.ui.show_bubble_message("再见了，我们下次再见吧！", self.pet.get_mood_type())
        
        # 延迟开始退出动画，让用户看到消息
        QTimer.singleShot(2, self._start_exit_animation)
        QTimer.singleShot(2000, QApplication.quit)

    def _start_exit_animation(self):
        """开始播放退出动画"""
        # 再次检查是否已经在退出过程中
        if not self.is_exiting:
            print("退出流程已被取消")
            return
        
        print("控制器开始播放退出动画")
        
        def exit_callback():
            print("退出回调被调用")
            # 清理资源
            self.shutdown()
            QApplication.quit()
        
        # 确保UI停止所有非退出相关的动画更新
        try:
            self.ui.start_exit_animation(exit_callback)
        except Exception as e:
            print(f"播放退出动画时出错: {e}")
            # 如果出错，直接退出
            exit_callback()

    def _update_hover_message(self):
        """更新悬停消息"""
        mood = self.pet.get_mood_type()
        active_count = self.schedule_manager.get_active_schedule_count()
        
        hover_messages = {
            PetConfig.MoodType.HAPPY: f"我很开心！当前有{active_count}个任务",
            PetConfig.MoodType.NORMAL: f"心情还不错，有{active_count}个任务要做",
            PetConfig.MoodType.POOR_CONDITION: f"有点累了，还有{active_count}个任务..."
        }
        
        message = hover_messages.get(mood, f"我的心情是：{mood}")
        self.ui.set_hover_message(message)
        

    def set_hover_message(self, message: str):
        """
        设置悬停消息
        
        Args:
            message: 悬停消息内容
        """
        self.ui.set_hover_message(message)

    def get_pet_stats(self) -> dict:
        """获取宠物统计信息"""
        return self.pet.get_stats()

    def update_pet_mood(self):
        """手动更新宠物心情"""
        self.pet.mood.getMoodType()  # 这会触发心情更新
        self._update_hover_message()

    def shutdown(self):
        """关闭控制器"""
        self.is_exiting = True
        if hasattr(self, 'bubble_timer'):
            self.bubble_timer.stop()
        print("控制器已关闭")
