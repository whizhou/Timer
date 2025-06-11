from PyQt5.QtWidgets import QLabel, QMenu, QApplication
from PyQt5.QtCore import Qt, QTimer, QPoint, QEvent
from PyQt5.QtGui import QPixmap
import os

# 获取当前脚本的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# 使用相对导入
from pet_chat import PetChatWindow

class DesktopPetUI(QLabel):
    def __init__(self, frame_folder, target_width=300, target_height=300):
        super().__init__(None, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setContextMenuPolicy(Qt.CustomContextMenu)  # Enable custom context menu
        self.customContextMenuRequested.connect(self.showContextMenu)  # Connect context menu signal

        # 启用鼠标跟踪
        self.setMouseTracking(True)

        # 初始化帧相关变量
        self.frame_folder = frame_folder
        self.frames = self.load_frames(self.frame_folder)
        self.current_frame_index = 0

        # 设置窗口大小
        self.target_width = target_width
        self.target_height = target_height
        self.setGeometry(0, 0, self.target_width, self.target_height)

        # 定时器用于循环播放帧
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(100)

        # 初始化气泡框
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
        self.bubble.setVisible(False)  # 默认隐藏气泡框
        self.bubble.setWordWrap(True)  # 允许文本自动换行
        self.bubble.setMaximumWidth(250)  # 设置气泡最大宽度
        
        # 悬停检测相关
        self.hoverTimer = QTimer(self)
        self.hoverTimer.setSingleShot(True)
        self.hoverTimer.timeout.connect(self.onHoverTimeout)
        self.isHovering = False
        self.hoverMessage = "你好，我是桌面宠物！"
        
        # 淡出效果相关
        self.fadeOutTimer = QTimer(self)
        self.fadeOutTimer.timeout.connect(self.fadeOutBubble)
        self.fadeOutOpacity = 1.0
        
        # 安装事件过滤器以捕获Enter和Leave事件
        self.installEventFilter(self)

        self.show()

    def load_frames(self, folder_path):
        """加载文件夹中的所有图片帧"""
        try:
            frames = [os.path.join(folder_path, f) for f in sorted(os.listdir(folder_path)) if f.endswith(('.png', '.jpg', '.jpeg'))]
            return frames
        except Exception as e:
            print(f"加载帧失败: {e}")
            return []

    def update_frame(self):
        """更新当前帧"""
        if self.frames:
            frame_path = self.frames[self.current_frame_index]
            pixmap = QPixmap(frame_path).scaled(self.target_width, self.target_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(pixmap)
            self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)

    def setAnimationFolder(self, folder_path):
        """切换动画帧文件夹"""
        self.frame_folder = folder_path
        self.frames = self.load_frames(self.frame_folder)
        self.current_frame_index = 0

    def updatePetPosition(self, position):
        """更新宠物位置"""
        self.move(QPoint(position[0], position[1]))

    def showBubbleMessage(self, message, mood_type=None):
        """显示气泡消息
        
        Args:
            message: 要显示的消息
            mood_type: 心情类型，影响气泡的颜色
        """
        print(f"显示气泡消息: {message}")  # 添加调试信息
        self.bubble.setText(message)
        
        # 限制气泡宽度并允许文本自动换行
        self.bubble.setMaximumWidth(200)
        self.bubble.setWordWrap(True)
        self.bubble.adjustSize()
        
        # 默认样式
        self.bubble.setStyleSheet("""
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
            """)
        
        # 计算气泡的大小
        bubble_width = self.bubble.width()
        bubble_height = self.bubble.height()
        
        # 计算气泡的位置
        # 位于宠物图像上方，水平居中
        bubble_x = max(0, (self.width() - bubble_width) // 2)
        
        # 宠物窗口顶部上方的位置 (负值表示在窗口之上)
        bubble_y = -bubble_height - 10
        
        self.bubble.move(bubble_x, bubble_y)
        self.bubble.setVisible(True)
        self.bubble.raise_()  # 确保气泡显示在最前面
        
        # 重置淡出透明度
        self.fadeOutOpacity = 1.0

    # def setBubbleStyleByMood(self, mood_type):
    #     """根据心情设置气泡样式"""
    #     styles = {
    #         "happy": """
    #             QLabel {
    #                 background-color: #E6FFE6;
    #                 border: 2px solid #4CAF50;
    #                 border-radius: 10px;
    #                 padding: 5px;
    #                 font-family: "Courier New", monospace;
    #                 font-size: 14px;
    #                 color: #2E7D32;
    #                 opacity: 1.0;
    #             }
    #         """,
    #         "sad": """
    #             QLabel {
    #                 background-color: #E3F2FD;
    #                 border: 2px solid #2196F3;
    #                 border-radius: 10px;
    #                 padding: 5px;
    #                 font-family: "Courier New", monospace;
    #                 font-size: 14px;
    #                 color: #0D47A1;
    #                 opacity: 1.0;
    #             }
    #         """,
    #         "angry": """
    #             QLabel {
    #                 background-color: #FFEBEE;
    #                 border: 2px solid #F44336;
    #                 border-radius: 10px;
    #                 padding: 5px;
    #                 font-family: "Courier New", monospace;
    #                 font-size: 14px;
    #                 color: #B71C1C;
    #                 opacity: 1.0;
    #             }
    #         """,
    #         "tired": """
    #             QLabel {
    #                 background-color: #FFF8E1;
    #                 border: 2px solid #FFC107;
    #                 border-radius: 10px;
    #                 padding: 5px;
    #                 font-family: "Courier New", monospace;
    #                 font-size: 14px;
    #                 color: #FF6F00;
    #                 opacity: 1.0;
    #             }
    #         """,
    #         "excited": """
    #             QLabel {
    #                 background-color: #F3E5F5;
    #                 border: 2px solid #9C27B0;
    #                 border-radius: 10px;
    #                 padding: 5px;
    #                 font-family: "Courier New", monospace;
    #                 font-size: 14px;
    #                 color: #4A148C;
    #                 opacity: 1.0;
    #             }
    #         """
    #     }
        
    #     self.bubble.setStyleSheet(styles.get(mood_type, styles.get("happy")))
        
    def hideBubbleMessage(self):
        """隐藏气泡消息"""
        self.startFadeOut()  # 使用渐变淡出效果

    def showMood(self, mood):
        """显示宠物的心情"""
        print(f"当前心情: {mood}")

    def showAction(self, action):
        """显示宠物的动作"""
        print(f"当前动作: {action}")

    def showContextMenu(self, position):
        """显示右键菜单"""
        menu = QMenu(self)
        
        # 添加菜单项
        chatAction = menu.addAction("聊天")
        menu.addSeparator()  # 添加分隔线
        exitAction = menu.addAction("退出")
        
        # 显示菜单并获取选择的动作
        action = menu.exec_(self.mapToGlobal(position))
        
        # 处理菜单动作
        if action == chatAction:
            # 打开聊天窗口
            if hasattr(self, 'chat_window') and self.chat_window.isVisible():
                # 如果聊天窗口已经存在且可见，则将其激活
                self.chat_window.activateWindow()
            else:
                # 创建新的聊天窗口
                self.chat_window = PetChatWindow(pet_controller=self.controller)
                # 设置窗口模态
                self.chat_window.setWindowModality(Qt.NonModal)
                # 显示窗口
                self.chat_window.show()
            
            # 同时也调用控制器的聊天方法（切换桌宠动画状态）
            if hasattr(self, 'controller'):
                self.controller.startChat()
        elif action == exitAction:
            QApplication.quit()

    def eventFilter(self, obj, event):
        if obj is self:
            if event.type() == QEvent.Enter:
                # 鼠标进入宠物区域
                self.isHovering = True
                self.hoverTimer.start(2000)  # 2秒后触发
                return True
            elif event.type() == QEvent.Leave:
                # 鼠标离开宠物区域
                self.isHovering = False
                self.hoverTimer.stop()
                if self.bubble.isVisible():
                    self.startFadeOut()
                return True
        return super().eventFilter(obj, event)
        
    def onHoverTimeout(self):
        """鼠标悬停超过指定时间后触发"""
        if self.isHovering:
            if hasattr(self, 'controller') and hasattr(self.controller.pet, 'mood'):
                self.showBubbleMessage(self.hoverMessage, self.controller.pet.mood.getMoodType())
            else:
                self.showBubbleMessage(self.hoverMessage)
            self.fadeOutOpacity = 1.0  # 重置透明度
    
    def startFadeOut(self):
        """开始气泡淡出效果"""
        self.fadeOutOpacity = 1.0
        self.fadeOutTimer.start(50)  # 每50毫秒更新一次透明度
    
    def fadeOutBubble(self):
        """逐渐淡出气泡框"""
        self.fadeOutOpacity -= 0.05
        if self.fadeOutOpacity <= 0:
            self.fadeOutTimer.stop()
            self.bubble.setVisible(False)
            return
            
        # 在现有样式表中添加不透明度
        current_style = self.bubble.styleSheet()
        if "opacity:" in current_style:
            # 替换现有的不透明度值
            updated_style = current_style.replace(
                f"opacity: {self.fadeOutOpacity + 0.05};", 
                f"opacity: {self.fadeOutOpacity};"
            )
        else:
            # 如果没有不透明度，则在现有样式中添加
            updated_style = current_style.replace(
                "QLabel {", 
                f"QLabel {{ opacity: {self.fadeOutOpacity};"
            )
        
        self.bubble.setStyleSheet(updated_style)
        
    def setHoverMessage(self, message):
        """设置悬停时显示的消息"""
        self.hoverMessage = message