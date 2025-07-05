import sys
import os
import time
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QLineEdit, QPushButton, QLabel, 
                             QScrollArea, QFrame, QSplitter, QListWidget, 
                             QListWidgetItem, QMenu, QToolButton)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QRect, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPainter, QPen, QBrush, QFont, QPalette

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
BASE_URL = "http://127.0.0.1:5000"

class MessageBubble(QFrame):
    """聊天气泡组件"""
    def __init__(self, text, is_user=True, avatar_path=None, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.text = text
        self.avatar_path = avatar_path
        self.thinking = False
        self.thinking_dots = ""
        self.thinking_timer = None
        
        self.initUI()
        
    def initUI(self):
        # 设置整体样式
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
                margin: 2px;
            }
        """)
        
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 创建消息区域
        message_layout = QHBoxLayout()
        message_layout.setSpacing(10)
        
        # 创建头像标签
        self.avatar_label = QLabel()
        if self.avatar_path and os.path.exists(self.avatar_path):
            original_pixmap = QPixmap(self.avatar_path)
            
            # 检查图像尺寸，如果太大则按比例缩小
            scaled_size = 40
            if original_pixmap.width() > scaled_size or original_pixmap.height() > scaled_size:
                pixmap = original_pixmap.scaled(scaled_size, scaled_size, 
                                              Qt.KeepAspectRatio, 
                                              Qt.SmoothTransformation)
            else:
                pixmap = original_pixmap
                
            # 创建圆形头像
            # rounded_pixmap = QPixmap(scaled_size, scaled_size)
            # rounded_pixmap.fill(Qt.transparent)
            
            # painter = QPainter(rounded_pixmap)
            # painter.setRenderHint(QPainter.Antialiasing)
            # painter.setBrush(QBrush(pixmap))
            # painter.setPen(Qt.NoPen)
            # painter.drawEllipse(0, 0, scaled_size, scaled_size)
            # painter.end()
            
            # 修改为方形头像
            self.avatar_label.setPixmap(original_pixmap)
        else:
            # 默认头像（圆形）
            self.avatar_label.setFixedSize(40, 40)
            color = "#FFFFFF" if self.is_user else "#5F6DF9"
            self.avatar_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    border-radius: 20px;
                    color: #333333;
                    font-weight: bold;
                    qproperty-alignment: AlignCenter;
                    padding: 10px;
                }}
            """)
            self.avatar_label.setText("你" if self.is_user else "宠")
        
        self.avatar_label.setFixedSize(40, 40)
        
        # 创建文本部件
        self.message_label = QLabel()
        self.message_label.setText(self.text)
        self.message_label.setWordWrap(True)
        self.message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        # 设置不同的样式，用户和机器人
        if self.is_user:
            self.message_label.setStyleSheet("""
                QLabel {
                    background-color: #ECF3FF;
                    border-radius: 18px;
                    padding: 10px 16px;
                    color: #333333;
                    font-size: 15px;
                    
                }
            """)
        else:
            self.message_label.setStyleSheet("""
                QLabel {
                    background-color: #FFFFFF;
                    border-radius: 18px;
                    padding: 12px 16px;
                    color: #333333;
                    font-size: 15px;
                    
                }
            """)
        
        # 设置消息标签最小宽度和最大宽度
        text_width = self.message_label.sizeHint().width()* 2  if self.message_label.sizeHint().width() * 2  < 400 else 400 # 对应调整最大宽度
        self.message_label.setMinimumWidth(text_width) # 适应较短的消息内容
        self.message_label.setMaximumWidth(text_width)  # 适应更长的消息内容
        
        # 调整标签大小以适应内容
        self.message_label.adjustSize()
        
        # 确保气泡大小适合内容
        
        text_height = self.message_label.sizeHint().height() + 10
        self.message_label.setMinimumHeight(text_height)
        
        # 根据是用户还是机器人设置布局
        if self.is_user:
            message_layout.addStretch()
            message_layout.addWidget(self.message_label)
            message_layout.addWidget(self.avatar_label)
        else:
            # 为机器人添加可选的思考状态标签
            self.thinking_label = QLabel("  ")

            self.thinking_label.setStyleSheet("""
                QLabel {
                    color: #666666;
                    font-size: 12px;
                    padding-left: 50px;
                }
            """)
            self.thinking_label.setVisible(not self.is_user)  # 只为机器人显示
            
            message_layout.addWidget(self.avatar_label)
            message_layout.addWidget(self.message_label)
            message_layout.addStretch()
            
            # 将思考标签添加到布局中
            thinking_layout = QHBoxLayout()
            thinking_layout.addWidget(self.thinking_label)
            thinking_layout.addStretch()
            
            layout.addLayout(thinking_layout)
        
        layout.addLayout(message_layout)
        self.setLayout(layout)
    
    def simulateThinking(self, duration=1):
        """模拟思考状态，显示思考中的动画和标签"""
        if not self.is_user:
            self.thinking = True
            self.thinking_label.setText(f"")
            self.thinking_label.show()


class PetChatWindow(QWidget):
    """与桌宠的聊天窗口"""
    chat_message_signal = pyqtSignal(str)
    
    def __init__(self, pet_controller=None, id=1):
        super().__init__()
        self.pet_controller = pet_controller
        self.user_avatar = None  # 用户头像路径
        self.id = id  # 桌宠ID
        # 使用头像文件夹下的图片作为桌宠头像
        self.pet_avatar_path = os.path.join(current_dir, "static/charactor/" + str(self.id) + "/头像/image.png")
        try:
            self.pet_avatar = self.pet_avatar_path
            print(f"使用头像: {self.pet_avatar}")
        except Exception as e:
            print(f"加载头像时出错: {e}")
            self.pet_avatar = None
            
        self.chat_history = []  # 聊天历史记录
        self.thinking_bubble = None  # 用于保存"思考中"的气泡
        
        self.initUI()
        
    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle("Chat PET")
        self.setWindowIcon(QIcon(self.pet_avatar_path))  # 设置窗口图标
        self.resize(500, 700)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QWidget {
                background-color: #F2F3F5;
                font-family: "Microsoft YaHei", "SimHei", "sans-serif";
            }
        """)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建顶部标题栏
        title_bar = QFrame()
        title_bar.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E6E6E6;
            }
        """)
        title_bar.setFixedHeight(50)
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 0, 15, 0)
        
        # 添加返回按钮
        back_button = QPushButton("≡")
        back_button.setStyleSheet("""
            QPushButton {
                border: none;
                font-size: 22px;
                color: #333333;
                background: transparent;
            }
        """)
        back_button.setFixedSize(40, 40)
        
        # 添加标题
        title_label = QLabel("Chat PET")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333333;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        # 添加更多按钮
        more_button = QPushButton("+")
        more_button.setStyleSheet("""
            QPushButton {
                border: none;
                font-size: 22px;
                color: #333333;
                background: transparent;
            }
        """)
        more_button.setFixedSize(40, 40)
        
        title_layout.addWidget(back_button)
        title_layout.addWidget(title_label, 1)
        title_layout.addWidget(more_button)
        
        main_layout.addWidget(title_bar)
        
        # 创建聊天区域（滚动区域）
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #F2F3F5;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #F2F3F5;
                width: 6px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #C1C1C1;
                min-height: 30px;
                border-radius: 3px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setContentsMargins(15, 15, 15, 15)
        self.chat_layout.setSpacing(20)
        
        self.scroll_area.setWidget(self.chat_container)
        main_layout.addWidget(self.scroll_area, 1)
        
        # 创建底部输入区域
        bottom_bar = QFrame()
        bottom_bar.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-top: 1px solid #E6E6E6;
            }
        """)
        bottom_bar.setFixedHeight(90)
        
        bottom_layout = QVBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(15, 10, 15, 10)
        
        # 创建输入区域
        input_area = QFrame()
        input_area.setStyleSheet("""
            QFrame {
                background-color: #F2F3F5;
                border-radius: 20px;
                border: none;
                min-height: 45px;
            }
        """)
        
        input_layout = QHBoxLayout(input_area)
        input_layout.setContentsMargins(15, 5, 15, 5)
        

        # 设置输入框
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("  ")   # 给deepseek发消息
        self.message_input.setStyleSheet("""
            QLineEdit {
                border: none;
                background: transparent;
                padding: 0px 0px;
                font-size: 15px;
                color: #333333;
                min-height: 35px;
            }
        """)
        
        send_button = QPushButton()
        send_button.setIcon(QIcon.fromTheme("document-send"))
        send_button.setText("发送")
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #5F6DF9;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 6px 15px;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #4F5DD9;
            }
            QPushButton:pressed {
                background-color: #3F4DC9;
            }
        """)
        
        input_layout.addWidget(self.message_input, 1)
        input_layout.addWidget(send_button)
        
        # 创建底部工具栏
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 5, 0, 0)
        toolbar_layout.setSpacing(5)
        
        # 创建工具按钮
        thinking_button = QToolButton()
        thinking_button.setText("   ") # 深度思考 (R1)
        thinking_button.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                color: #555555;
                font-size: 14px;
                padding: 5px;
            }
            QToolButton:hover {
                color: #5F6DF9;
            }
        """)
        
        search_button = QToolButton()
        search_button.setText("   ") # 联网搜索 (R2)
        search_button.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                color: #555555;
                font-size: 14px;
                padding: 5px;
            }
            QToolButton:hover {
                color: #5F6DF9;
            }
        """)
        
        more_tools_button = QToolButton()
        more_tools_button.setText(" ")
        more_tools_button.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                color: #555555;
                font-size: 18px;
                padding: 5px;
            }
        """)
        
        # 添加工具按钮到工具栏
        toolbar_layout.addWidget(thinking_button)
        toolbar_layout.addWidget(search_button)
        toolbar_layout.addStretch(1)
        toolbar_layout.addWidget(more_tools_button)
        
        # 将输入区域和工具栏添加到底部布局
        bottom_layout.addWidget(input_area)
        bottom_layout.addLayout(toolbar_layout)
        
        main_layout.addWidget(bottom_bar)
        
        self.setLayout(main_layout)
        
        # 连接信号和槽
        send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)
        thinking_button.clicked.connect(self.toggle_deep_thinking)
        
        # 添加欢迎消息
        self.add_message("你好！我是你的桌宠，很高兴和你聊天！有什么想和我聊的吗？", False)
        
        # 设置是否使用深度思考模式
        self.use_deep_thinking = False
    
    def toggle_deep_thinking(self):
        """切换深度思考模式"""
        self.use_deep_thinking = not self.use_deep_thinking
        if self.use_deep_thinking:
            self.add_message("已启用深度思考模式，我将更认真地思考您的问题。", False)
        else:
            self.add_message("已关闭深度思考模式，我会更快地回答您的问题。", False)
    
    def send_message(self):
        """发送消息"""
        message = self.message_input.text().strip()
        if not message:
            return
        
        # 添加用户消息到聊天区域
        self.add_message(message, True)
        self.message_input.clear()
        
        # 添加思考中的占位气泡
        self.show_thinking()
        
        # 根据是否使用深度思考模式，决定回复延迟时间
        if self.use_deep_thinking:
            # 深度思考模式，延迟时间更长
            thinking_time = 2000
        else:
            # 普通模式，延迟时间较短
            thinking_time = 1000
        
        # 定时器，模拟延迟回复
        QTimer.singleShot(thinking_time, lambda: self.get_pet_response(message))
    
    def show_thinking(self):
        """显示思考中的气泡"""
        # 先移除之前的思考气泡（如果有的话）
        if self.thinking_bubble:
            self.chat_layout.removeWidget(self.thinking_bubble)
            self.thinking_bubble.deleteLater()
            self.thinking_bubble = None
        
        # 创建新的思考中气泡
        self.thinking_bubble = MessageBubble("正在思考中...", False, self.pet_avatar)
        self.chat_layout.addWidget(self.thinking_bubble)
        
        # 滚动到底部
        self.scroll_to_bottom()
    
    def get_pet_response(self, user_message):
        """获取桌宠的回复"""
        # 移除思考中的气泡
        if self.thinking_bubble:
            self.chat_layout.removeWidget(self.thinking_bubble)
            self.thinking_bubble.deleteLater()
            self.thinking_bubble = None
        
        # 根据是否启用深度思考模式，决定思考时间显示
        thinking_time = 2 if self.use_deep_thinking else 1
        
        # 检查特殊指令
        if self.pet_controller and ("陪我学习吧" in user_message or "陪我学习" in user_message):
            self.add_message("好呀，我来陪你一起学习！", False, True, thinking_time)
            self.pet_controller.play_study_with_me_animation()
            return
        if self.pet_controller and ("休息一下吧" in user_message or "休息一下" in user_message):
            self.add_message("好呀，休息一下~", False, True, thinking_time)
            self.pet_controller.play_rest_c_then_restore()
            return

        # 简单的关键词匹配响应作为示例
        response = ""
        lower_msg = "请模仿桌面宠物的语气回复，语气日常一点、不要太过热情，可以的话偶尔在每句话最后加个\"喵\":" + user_message.lower()
        
        response = requests.post(
            f"{BASE_URL}/chat",
            json={'message': lower_msg}
        )
        try:
            response = response.json()["response"]
        except:
            response = "正在开发中的ai回复信息，敬请期待..."

        # # 深度思考模式下，可以给出更详细的回复
        # if self.use_deep_thinking:
        #     if "你好" in lower_msg or "hello" in lower_msg or "hi" in lower_msg:
        #         response = "你好呀！很高兴见到你。今天过得怎么样？有什么我可以帮助你的吗？"
        #     elif "名字" in lower_msg or "叫什么" in lower_msg:
        #         response = "我是你的桌宠助手，由PyQt5开发。你可以给我起一个你喜欢的名字，这样我们的交流会更加亲切。"
        #     elif "天气" in lower_msg:
        #         response = "我无法直接查询实时天气数据，但我注意到最近天气变化比较大。如果你需要准确的天气信息，可以考虑使用专业的天气应用或网站。"
        #     elif "任务" in lower_msg or "代办" in lower_msg or "todo" in lower_msg:
        #         response = "任务管理是提高效率的好方法。我可以帮你记录任务，你可以告诉我任务的详细信息，比如名称、截止日期和优先级等。你想要添加什么任务呢？"
        #     elif "心情" in lower_msg or "感觉" in lower_msg:
        #         if self.pet_controller:
        #             mood = self.pet_controller.pet.mood.getMoodType()
        #             response = f"我现在的心情是：{mood}。心情会影响工作和学习的效率，保持积极的心态很重要。你今天的心情如何？发生了什么有趣的事情吗？"
        #         else:
        #             response = "我的心情很不错！保持良好的心态对提高效率和生活质量都很有帮助。你今天感觉怎么样？有什么想分享的吗？"
        #     elif "谢谢" in lower_msg or "thank" in lower_msg:
        #         response = "不客气！能够帮助到你是我的荣幸。如果还有其他需要，随时告诉我。"
        #     elif "再见" in lower_msg or "拜拜" in lower_msg or "goodbye" in lower_msg:
        #         response = "再见！希望我们的交流对你有所帮助。期待下次与你聊天！祝你有愉快的一天。"
        #     elif "学习" in lower_msg or "学校" in lower_msg:
        #         response = "学习是一个持续的过程，每个人都有自己适合的学习方法。你可以尝试番茄工作法、思维导图等方法提高学习效率。有什么特定的学习困难我可以帮助你解决吗？"
        #     else:
        #         # 默认深度思考回复
        #         responses = [
        #             "这是一个很有深度的话题。从不同角度来看，可能会有不同的理解和见解。你对这个问题有什么特别的想法吗？",
        #             "我理解你的意思了。这让我想到了知识的多样性和复杂性，每个问题都可能有多种解读方式。你想继续探讨这个话题的哪个方面？",
        #             "这个问题很有趣，值得深入思考。有时候答案并不是唯一的，而是取决于具体的情境和个人的理解。你是从什么角度考虑这个问题的？",
        #             "谢谢分享！这个话题很有启发性，让我思考了一些平时容易忽略的细节。我很好奇你是如何想到这个问题的？"
        #         ]
        #         import random
        #         response = random.choice(responses)
        # else:
        #     # 普通模式的回复，简短直接
        #     if "你好" in lower_msg or "hello" in lower_msg or "hi" in lower_msg:
        #         response = "你好呀！今天过得怎么样？"
        #     elif "名字" in lower_msg or "叫什么" in lower_msg:
        #         response = "我是你的桌宠助手，你可以给我起个名字哦！"
        #     elif "天气" in lower_msg:
        #         response = "我不能查看实时天气，但我希望今天是个好天气！"
        #     elif "任务" in lower_msg or "代办" in lower_msg or "todo" in lower_msg:
        #         response = "需要我帮你记录任务吗？你可以告诉我任务的详细信息。"
        #     elif "心情" in lower_msg or "感觉" in lower_msg:
        #         if self.pet_controller:
        #             mood = self.pet_controller.pet.mood.getMoodType()
        #             response = f"我现在的心情是：{mood}。你呢？"
        #         else:
        #             response = "我的心情很不错！你呢？"
        #     elif "谢谢" in lower_msg or "thank" in lower_msg:
        #         response = "不客气！很高兴能帮到你。"
        #     elif "再见" in lower_msg or "拜拜" in lower_msg or "goodbye" in lower_msg:
        #         response = "再见！期待下次与你聊天！"
        #     elif "学习" in lower_msg or "学校" in lower_msg:
        #         response = "学习是很重要的！我也在不断学习中。有什么学习上的困难吗？"
        #     elif "工作" in lower_msg:
        #         response = "工作辛苦了！别忘了适当休息，劳逸结合才能更有效率。"
        #     elif "帮助" in lower_msg or "help" in lower_msg:
        #         response = "我可以陪你聊天，提醒你完成任务，或者只是做个伴。有什么具体需要帮助的吗？"
        #     elif "?" in lower_msg or "？" in lower_msg:
        #         response = "这是个好问题！让我想想..."
        #     else:
        #         # 默认响应
        #         responses = [
        #             "嗯，我明白了。还有什么想聊的吗？",
        #             "真有趣！我想了解更多。",
        #             "我还在学习中，请继续告诉我更多！",
        #             "谢谢分享！我很喜欢和你聊天。",
        #             "这很有趣，能详细说说吗？"
        #         ]
        #         import random
        #         response = random.choice(responses)
        
        # 添加桌宠的回复到聊天区域
        self.add_message(response, False, True, thinking_time)  # 添加思考时间标记
        
        # 如果有控制器，可以通过它来更新桌宠的状态
        if self.pet_controller:
            self.pet_controller.interact_with_user(response)
    
    def add_message(self, text, is_user=True, show_thinking=False, thinking_time=1):
        """添加消息到聊天区域"""
        # 创建消息气泡
        bubble = MessageBubble(text, is_user, self.pet_avatar if not is_user else self.user_avatar)
        
        # 如果是机器人，并且需要显示思考时间，则设置思考标签
        if not is_user and show_thinking:
            bubble.simulateThinking(thinking_time)
        
        # 添加到布局
        self.chat_layout.addWidget(bubble)
        
        # 保存到聊天历史
        self.chat_history.append({"text": text, "is_user": is_user})
        
        # 滚动到底部
        self.scroll_to_bottom()
    
    def scroll_to_bottom(self):
        """滚动到聊天区域底部"""
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 可以在这里添加关闭前的确认或保存聊天记录等功能
        event.accept()


if __name__ == "__main__":
    # 测试代码
    app = QApplication(sys.argv)
    chat_window = PetChatWindow()
    chat_window.show()
    sys.exit(app.exec_())
