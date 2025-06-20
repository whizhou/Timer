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
        self.is_performing_idle_action = False  # 标记是否正在执行待机动作

        
        # 定时器和管理器
        self.update_interval = PetConfig.UPDATE_INTERVAL
        self.bubble_timer = QTimer()
        self.bubble_timer.setSingleShot(True)
        self.bubble_timer.timeout.connect(self.ui.hide_bubble_message)
        self.schedule_manager = ScheduleManager()
        

        # 待机动作定时器
        self.idle_action_timer = QTimer()
        self.idle_action_timer.setSingleShot(True)
        self.idle_action_timer.timeout.connect(self._trigger_idle_action)
        
        # 待机动作恢复定时器
        self.idle_recovery_timer = QTimer()
        self.idle_recovery_timer.setSingleShot(True)
        self.idle_recovery_timer.timeout.connect(self._recover_from_idle_action)

        # 消息管理
        self.msg_bubble = Msg()
        self._init_click_messages()
        
        # 设置UI控制器引用
        self.ui.set_controller(self)
        
        # 启动自动更新
        self._start_animation_update_thread()
        
        # 设置默认悬停消息
        self._update_hover_message()
        
        # 启动待机动作定时器
        self._start_idle_action_timer()

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
        

        # 停止待机动作相关定时器
        if hasattr(self, 'idle_action_timer'):
            self.idle_action_timer.stop()
        if hasattr(self, 'idle_recovery_timer'):
            self.idle_recovery_timer.stop()
        self.is_performing_idle_action = False
        
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
        

        # 重新启动待机动作定时器
        self._restart_idle_action_timer()
        
        self.ui.show_bubble_message("放开我了~", self.pet.get_mood_type())

    def start_chat(self):
        """开始聊天"""
        print("开始聊天")
        self.pet.set_chatting_state(True)
        

        # 停止待机动作相关定时器
        if hasattr(self, 'idle_action_timer'):
            self.idle_action_timer.stop()
        if hasattr(self, 'idle_recovery_timer'):
            self.idle_recovery_timer.stop()
        self.is_performing_idle_action = False

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
        
        # 重新启动待机动作定时器
        self._restart_idle_action_timer()

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
        if hasattr(self, 'idle_action_timer'):
            self.idle_action_timer.stop()
        if hasattr(self, 'idle_recovery_timer'):
            self.idle_recovery_timer.stop()
        
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
        if hasattr(self, 'idle_action_timer'):
            self.idle_action_timer.stop()
        if hasattr(self, 'idle_recovery_timer'):
            self.idle_recovery_timer.stop()
        print("控制器已关闭")

    def _start_idle_action_timer(self):
        """启动待机动作定时器"""
        interval_ms = PetConfig.get_idle_action_interval() * 1000  # 转换为毫秒
        self.idle_action_timer.start(interval_ms)
        print(f"待机动作定时器已启动，间隔: {PetConfig.get_idle_action_interval()}秒")

    def _trigger_idle_action(self):
        """触发待机动作"""
        if self.is_dragging or self.pet.is_in_chatting_state() or self.is_exiting:
            self._restart_idle_action_timer()
            return
        print("触发待机动作")
        self.is_performing_idle_action = True
        idle_actions = PetConfig.IdleActionType.get_all_idle_actions()
        available_actions = []
        for action in idle_actions:
            animation_path = PetConfig.get_animation_path(
                self.pet.get_id(),
                action,
                self.current_mood
            )
            if os.path.exists(animation_path):
                available_actions.append(action)
                print(f"可用待机动作: {action} - {animation_path}")
        if available_actions:
            selected_action = random.choice(available_actions)
            print(f"执行待机动作: {selected_action}")
            animation_path = PetConfig.get_animation_path(
                self.pet.get_id(),
                selected_action,
                self.current_mood
            )
            # 设置动画播放完回调
            def on_idle_action_finished():
                print("待机动作动画播放完毕，恢复默认动画")
                self.is_performing_idle_action = False
                self._load_default_animation(self.current_mood)
                self._restart_idle_action_timer()
            self.ui._on_animation_finished = on_idle_action_finished
            self.ui.set_animation_folder(animation_path, loop_once=True)
            idle_message = self._get_idle_action_message(selected_action)
            if idle_message:
                pet_position = self.pet.get_position()
                self.msg_bubble.show_above_pet(idle_message, pet_position, self.current_mood)
        else:
            print("没有可用的待机动作动画")
            self.is_performing_idle_action = False
            self._restart_idle_action_timer()

    def _recover_from_idle_action(self):
        """从待机动作恢复"""
        print("从待机动作恢复到默认状态")
        self.is_performing_idle_action = False
        
        # 恢复到默认站立动画
        self._load_default_animation(self.current_mood)
        
        # 重新启动待机动作定时器
        self._restart_idle_action_timer()

    def _restart_idle_action_timer(self):
        """重新启动待机动作定时器"""
        if not self.is_exiting:
            interval_ms = PetConfig.get_idle_action_interval() * 1000
            self.idle_action_timer.start(interval_ms)

    def _get_idle_action_message(self, action: str) -> str:
        """根据待机动作获取对应的消息"""
        action_messages = {
            PetConfig.IdleActionType.FINISH_WORK: [
                "终于完成了！",
                "工作结束~",
                "任务完成！"
            ],
            PetConfig.IdleActionType.THINK: [
                "让我想想...",
                "思考中...",
                "嗯...有点想法了"
            ],
            PetConfig.IdleActionType.HUNGER: [
                "有点饿了...",
                "该吃点什么呢？",
                "肚子饿了~"
            ],
            PetConfig.IdleActionType.STUDY: [
                "学习时间！",
                "努力学习中...",
                "知识就是力量！"
            ],
            PetConfig.IdleActionType.WALK: [
                "出去走走~",
                "散步时间！",
                "活动一下身体"
            ]
        }
        
        messages = action_messages.get(action, [])
        return random.choice(messages) if messages else None

    def play_study_with_me_animation(self):
        """先播放A目录一次，播放完后循环播放B目录"""
        pet_id = self.pet.get_id()
        mood = self.pet.get_mood_type()
        # 兼容多心情/多目录，直接用绝对路径
        a_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            f'static/charactor/{pet_id}/study/A'
        )
        b_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            f'static/charactor/{pet_id}/study/B'
        )
        if not os.path.exists(a_path) or not os.path.exists(b_path):
            print(f"学习动画目录不存在: {a_path} 或 {b_path}")
            return
        def play_b():
            print("A动画播放完毕，开始循环B动画")
            self.ui.set_animation_folder(b_path, loop_once=False)
        self.ui._on_animation_finished = play_b
        print("开始播放A动画（单次）")
        self.ui.set_animation_folder(a_path, loop_once=True)
