
"""
桌宠UI界面模块
负责桌宠的界面显示、动画播放和用户交互
"""

from PyQt5.QtWidgets import QLabel, QMenu, QApplication
from PyQt5.QtCore import Qt, QTimer, QPoint, QEvent
from PyQt5.QtGui import QPixmap
import os

from typing import Optional, Callable
from config import PetConfig


# 获取当前脚本的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# 使用相对导入
from pet_chat import PetChatWindow

class DesktopPetUI(QLabel):
    """桌宠UI界面类"""
    
    def __init__(self, frame_folder: str, 
                 target_width: int = PetConfig.DEFAULT_PET_WIDTH, 
                 target_height: int = PetConfig.DEFAULT_PET_HEIGHT):
        """
        初始化桌宠UI
        
        Args:
            frame_folder: 动画帧文件夹路径
            target_width: 目标宽度
            target_height: 目标高度
        """
        super().__init__(None, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # 基本设置
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.setMouseTracking(True)
        
        # 控制器引用
        self.controller: Optional[object] = None
        self.exit_callback: Optional[Callable] = None
        
        # 动画相关
        self.frame_folder = frame_folder
        self.frames = self._load_frames(self.frame_folder)
        self.current_frame_index = 0
        self.is_exit_animation = False
        
        # 窗口设置
        self.target_width = target_width
        self.target_height = target_height
        self.setGeometry(0, 0, self.target_width, self.target_height)
        
        # 动画定时器
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._update_frame)
        self.animation_timer.start(PetConfig.ANIMATION_FRAME_INTERVAL)
        
        # 退出动画定时器
        self.exit_timer = QTimer(self)
        self.exit_timer.setSingleShot(True)
        self.exit_timer.timeout.connect(self._finish_exit_animation)
        
        # 初始化气泡相关
        self._init_bubble()
        
        # 初始化悬停相关
        self._init_hover_detection()
        
        # 安装事件过滤器
        self.installEventFilter(self)
        
        self.show()
    
    def _init_bubble(self):
        """初始化气泡相关组件"""
        self.bubble = QLabel(self)
        self.bubble.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 2px solid black;
                border-radius: 10px;
                padding: 5px;
                font-family: "Courier New", monospace;
                font-size: 14px;
                color: black;
            }
        """)
        self.bubble.setAlignment(Qt.AlignCenter)
        self.bubble.setVisible(False)
        self.bubble.setWordWrap(True)
        self.bubble.setMaximumWidth(PetConfig.BUBBLE_MAX_WIDTH)
        
        # 淡出效果相关
        self.fade_out_timer = QTimer(self)
        self.fade_out_timer.timeout.connect(self._fade_out_bubble)
        self.fade_out_opacity = 1.0
    
    def _init_hover_detection(self):
        """初始化悬停检测相关组件"""
        self.hover_timer = QTimer(self)
        self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(self._on_hover_timeout)
        self.is_hovering = False
        self.hover_message = "你好，我是桌面宠物！"
        
    def _load_frames(self, folder_path: str) -> list:
        """
        加载文件夹中的所有图片帧
        
        Args:
            folder_path: 文件夹路径
            
        Returns:
            图片帧路径列表
        """
        try:
            if not os.path.exists(folder_path):
                print(f"动画文件夹不存在: {folder_path}")
                return []
                
            frames = []
            for f in sorted(os.listdir(folder_path)):
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    frames.append(os.path.join(folder_path, f))
            
            if not frames:
                print(f"文件夹中没有找到图片文件: {folder_path}")
            else:
                print(f"加载了 {len(frames)} 个动画帧从: {folder_path}")
                
            return frames
        except Exception as e:
            print(f"加载动画帧失败: {e}")
            return []

    def _update_frame(self):
        """更新当前动画帧"""
        if not self.frames:
            return
            
        # 如果已经完成退出动画，停止更新
        if self.is_exit_animation and hasattr(self, '_exit_animation_finished') and self._exit_animation_finished:
            return
            
        frame_path = self.frames[self.current_frame_index]
        try:
            pixmap = QPixmap(frame_path)
            if pixmap.isNull():
                print(f"无法加载图片: {frame_path}")
                return
                
            scaled_pixmap = pixmap.scaled(
                self.target_width, self.target_height, 
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
            
            # 如果是退出动画，特殊处理
            if self.is_exit_animation:
                # 检查是否播放到最后一帧
                if self.current_frame_index >= len(self.frames) - 1:
                    print(f"退出动画播放完成，共播放{len(self.frames)}帧")
                    # 停止动画定时器，防止继续播放
                    if hasattr(self, 'animation_timer'):
                        self.animation_timer.stop()
                    self._exit_animation_finished = True
                    self._finish_exit_animation()
                    return
                else:
                    # 继续播放下一帧
                    self.current_frame_index += 1
            else:
                # 普通动画循环播放
                self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
                
        except Exception as e:
            print(f"更新动画帧失败: {e}")

    def set_animation_folder(self, folder_path: str):
        """
        切换动画帧文件夹
        
        Args:
            folder_path: 新的动画文件夹路径
        """
        print(f"切换动画文件夹到: {folder_path}")
        self.frame_folder = folder_path
        self.frames = self._load_frames(self.frame_folder)
        self.current_frame_index = 0
        self.is_exit_animation = False
        self._exit_animation_finished = False

    def _set_exit_animation_folder(self, folder_path: str):
        """
        专门用于设置退出动画文件夹
        
        Args:
            folder_path: 退出动画文件夹路径
        """
        print(f"设置退出动画文件夹: {folder_path}")
        self.frame_folder = folder_path
        self.frames = self._load_frames(self.frame_folder)
        self.current_frame_index = 0
        # 不重置退出动画标志，保持退出状态

    def update_pet_position(self, position: tuple):
        """
        更新宠物位置
        
        Args:
            position: 新位置坐标 (x, y)
        """
        self.move(QPoint(position[0], position[1]))

    def show_bubble_message(self, message: str, mood_type: str = None):
        """
        显示气泡消息
        
        Args:
            message: 要显示的消息
            mood_type: 心情类型，影响气泡的颜色
        """
        print(f"显示气泡消息: {message}")
        self.bubble.setText(message)
        
        # 设置气泡样式
        self._set_bubble_style_by_mood(mood_type)
        
        # 调整气泡大小
        self.bubble.setMaximumWidth(200)
        self.bubble.setWordWrap(True)
        self.bubble.adjustSize()
        

        # 强制更新窗口几何信息，确保位置计算准确
        self.update()
        self.repaint()
        
        # 计算并设置气泡位置
        self._position_bubble()
        
        # 显示气泡
        self.bubble.setVisible(True)
        self.bubble.raise_()
        
        # 重置淡出透明度
        self.fade_out_opacity = 1.0

    def _set_bubble_style_by_mood(self, mood_type: str):
        """
        根据心情设置气泡样式
        
        Args:
            mood_type: 心情类型
        """
        styles = {
            PetConfig.MoodType.HAPPY: """
                QLabel {
                    background-color: #E6FFE6;
                    border: 2px solid #4CAF50;
                    border-radius: 10px;
                    padding: 5px;
                    font-family: "Courier New", monospace;
                    font-size: 14px;
                    color: #2E7D32;
                    opacity: 1.0;
                }
            """,
            PetConfig.MoodType.NORMAL: """
                QLabel {
                    background-color: #E3F2FD;
                    border: 2px solid #2196F3;
                    border-radius: 10px;
                    padding: 5px;
                    font-family: "Courier New", monospace;
                    font-size: 14px;
                    color: #0D47A1;
                    opacity: 1.0;
                }
            """,
            PetConfig.MoodType.POOR_CONDITION: """
                QLabel {
                    background-color: #FFEBEE;
                    border: 2px solid #F44336;
                    border-radius: 10px;
                    padding: 5px;
                    font-family: "Courier New", monospace;
                    font-size: 14px;
                    color: #B71C1C;
                    opacity: 1.0;
                }
            """
        }
        
        # 使用对应心情的样式，默认为开心样式
        style = styles.get(mood_type, styles[PetConfig.MoodType.HAPPY])
        self.bubble.setStyleSheet(style)

    def _position_bubble(self):
        """计算并设置气泡位置"""
        bubble_width = self.bubble.width()
        bubble_height = self.bubble.height()
        
        # 水平居中相对于桌宠窗口
        bubble_x = max(0, (self.width() - bubble_width) // 2)
        
        # 位于宠物上方，确保有足够的间距
        bubble_y = -bubble_height - 15
        
        # 设置气泡位置
        self.bubble.move(bubble_x, bubble_y)
        
        # 确保气泡在父窗口中正确显示
        self.bubble.raise_()

    def hide_bubble_message(self):
        """隐藏气泡消息"""
        self._start_fade_out()

    def _start_fade_out(self):
        """开始气泡淡出效果"""
        self.fade_out_opacity = 1.0
        self.fade_out_timer.start(PetConfig.BUBBLE_FADE_INTERVAL)
    
    def _fade_out_bubble(self):
        """逐渐淡出气泡框"""
        self.fade_out_opacity -= 0.05
        if self.fade_out_opacity <= 0:
            self.fade_out_timer.stop()
            self.bubble.setVisible(False)
            return
            
        # 更新样式表中的不透明度
        current_style = self.bubble.styleSheet()
        if "opacity:" in current_style:
            import re
            updated_style = re.sub(r'opacity:\s*[0-9.]+;', 
                                 f'opacity: {self.fade_out_opacity};', 
                                 current_style)
        else:
            updated_style = current_style.replace(
                "QLabel {", 
                f"QLabel {{ opacity: {self.fade_out_opacity};"
            )
        
        self.bubble.setStyleSheet(updated_style)

    def show_context_menu(self, position: QPoint):
        """
        显示右键菜单
        
        Args:
            position: 菜单显示位置
        """
        menu = QMenu(self)
        
        # 添加菜单项
        chat_action = menu.addAction("聊天")
        menu.addSeparator()
        exit_action = menu.addAction("退出")
        
        # 显示菜单并获取选择的动作
        action = menu.exec_(self.mapToGlobal(position))
        
        # 处理菜单动作
        if action == chat_action:
            self._handle_chat_action()
        elif action == exit_action:
            self._handle_exit_action()

    def _handle_chat_action(self):
        """处理聊天动作"""
        # 打开聊天窗口
        if hasattr(self, 'chat_window') and self.chat_window.isVisible():
            self.chat_window.activateWindow()
        else:
            self.chat_window = PetChatWindow(pet_controller=self.controller)
            self.chat_window.setWindowModality(Qt.NonModal)
            self.chat_window.show()
        
        # 通知控制器开始聊天
        if self.controller:
            self.controller.start_chat()

    def _handle_exit_action(self):
        """处理退出动作"""
        if self.controller:
            # 通知控制器开始退出流程
            self.controller.start_exit()
        else:
            # 如果没有控制器，直接退出
            QApplication.quit()

    def start_exit_animation(self, exit_callback: Callable = None):
        """
        开始播放退出动画
        
        Args:
            exit_callback: 退出动画完成后的回调函数
        """
        # 防止重复播放退出动画
        if self.is_exit_animation:
            print("退出动画已在播放中，忽略重复调用")
            return
            
        print("开始播放退出动画")
        self.exit_callback = exit_callback
        self.is_exit_animation = True
        self._exit_animation_finished = False  # 初始化退出动画完成标志
        
        # 停止所有其他定时器
        if hasattr(self, 'hover_timer'):
            self.hover_timer.stop()
        if hasattr(self, 'fade_out_timer'):
            self.fade_out_timer.stop()
        
        # 隐藏气泡
        if self.bubble.isVisible():
            self.bubble.setVisible(False)
        
        # 获取退出动画路径
        if self.controller and hasattr(self.controller, 'pet'):
            pet = self.controller.pet
            mood_type = pet.get_mood_type()
            exit_animation_path = PetConfig.get_animation_path(
                pet.get_id(), 
                PetConfig.AnimationType.SHUTDOWN, 
                mood_type
            )
            
            print(f"播放退出动画: {exit_animation_path}")
            # 特殊处理退出动画文件夹切换
            self._set_exit_animation_folder(exit_animation_path)
            
            # 设置退出动画定时器（备用机制）
            self.exit_timer.start(PetConfig.EXIT_ANIMATION_DURATION)
        else:
            # 如果没有控制器，直接退出
            self._finish_exit_animation()

    def _finish_exit_animation(self):
        """完成退出动画"""
        # 防止重复调用
        if not self.is_exit_animation or (hasattr(self, '_exit_animation_finished') and self._exit_animation_finished):
            return
            
        print("退出动画播放完成")
        
        
        # 标记动画完成（防止重复调用）
        self._exit_animation_finished = True
        
        # 停止所有定时器
        if hasattr(self, 'animation_timer'):
            self.animation_timer.stop()
        if hasattr(self, 'exit_timer'):
            self.exit_timer.stop()
        if hasattr(self, 'hover_timer'):
            self.hover_timer.stop()
        if hasattr(self, 'fade_out_timer'):
            self.fade_out_timer.stop()
        
        # 标记为已完成
        self.is_exit_animation = False
        
        
        # 延迟执行回调，确保动画播放完毕
        def delayed_exit():
            if self.exit_callback:
                callback = self.exit_callback
                self.exit_callback = None  # 清除回调引用
                callback()
            else:
                QApplication.quit()
        
        # 延迟500毫秒后执行退出
        QTimer.singleShot(500, delayed_exit)
        

    def set_hover_message(self, message: str):
        """
        设置悬停时显示的消息
        
        Args:
            message: 悬停消息
        """
        self.hover_message = message

    def eventFilter(self, obj, event):
        """事件过滤器"""
        if obj is self:
            if event.type() == QEvent.Enter:
                # 鼠标进入
                self.is_hovering = True
                self.hover_timer.start(PetConfig.HOVER_DELAY)
                return True
            elif event.type() == QEvent.Leave:
                # 鼠标离开
                self.is_hovering = False
                self.hover_timer.stop()
                if self.bubble.isVisible():
                    self._start_fade_out()
                return True
        return super().eventFilter(obj, event)
        
    def _on_hover_timeout(self):
        """鼠标悬停超时处理"""
        if self.is_hovering:
            mood_type = None
            if (self.controller and hasattr(self.controller, 'pet') 
                and hasattr(self.controller.pet, 'mood')):
                mood_type = self.controller.pet.get_mood_type()
            
            self.show_bubble_message(self.hover_message, mood_type)
            self.fade_out_opacity = 1.0

    def show_mood(self, mood: str):
        """
        显示宠物的心情
        
        Args:
            mood: 心情类型
        """
        print(f"当前心情: {mood}")

    def show_action(self, action: str):
        """
        显示宠物的动作
        
        Args:
            action: 动作类型
        """
        print(f"当前动作: {action}")
    
    def set_controller(self, controller):
        """
        设置控制器引用
        
        Args:
            controller: 控制器对象
        """
        self.controller = controller
