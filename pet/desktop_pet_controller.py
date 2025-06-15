from PyQt5.QtCore import QTimer
import random
import os
import threading
import time
from schedule_manager import ScheduleManager

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
    def __init__(self, pet, ui):
        self.pet = pet
        self.ui = ui
        self.isDragging = False  # 标记是否正在拖拽
        self.update_interval = 5            # 间隔3秒检查宠物动画是否需要更新
        self.bubbleTimer = QTimer()  # 定时器用于隐藏气泡框
        self.bubbleTimer.setSingleShot(True)
        self.bubbleTimer.timeout.connect(self.ui.hideBubbleMessage)
        self._start_update_animation_folder()
        self.mood = "PoorCondition"
        self.schedule_manager = ScheduleManager()    # 第二个这种类...
        # 设置默认的悬停消息
        self.setHoverMessage(f"我的心情是：{pet.mood.getMoodType()}")
        
        # 初始化点击消息字典
        self.initClickMessages()
        
        # 创建气泡消息对象
        self.msgBubble = Msg()


    def _start_update_animation_folder(self):
        """启动自动更新线程"""
        def update_loop():
            while self.isDragging == False:
                self.update_animation_folder()
                time.sleep(self.update_interval)
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
            

    def update_animation_folder(self):
        mood = self.pet.mood.getMoodType()
        # 状态、心情变化才重新加载（否则动画刷新、导致桌宠一卡一卡
        if mood != self.mood:
            charactor_path = get_resource_path(f"/pet/static/charactor/{self.pet.id}/stand/{mood}")
            self.ui.setAnimationFolder(charactor_path)
            self.mood = mood

    def movePet(self, position):
        """控制宠物移动到指定位置"""
        self.pet.position = position
        self.ui.updatePetPosition(position)

    def movePetByOffset(self, offset):
        """根据偏移量移动宠物"""
        newX = self.pet.position[0] + offset.x()
        newY = self.pet.position[1] + offset.y()
        newPosition = (newX, newY)
        self.movePet(newPosition)

    

    

    def performAction(self, action):
        """执行特定的宠物动作"""
        self.pet.performAction(action)
        self.ui.showAction(action)

    def interactWithUser(self, message):
        """响应用户输入"""
        mood = self.pet.mood
        self.ui.showBubbleMessage(message, mood)

    def initClickMessages(self):
        """初始化不同心情下的点击消息"""
        self.clickMessages = {
            "Happy": [
                "任务通通完成啦~开心",
                "0个任务待完成！"
            ],
            "Normal": [
                "有什么我能帮你的吗？"
            ],
            "PoorCondition": [
                "任务做不完了！",
            ],
            "study": [
                "我在学习中...",
                "学习真有趣！",
                "我喜欢学习新知识！",
                "学习是快乐的！",
                "继续努力吧！"
            ],  
            "tired": [
                "好困啊...",
                "需要休息一下",
                "打个盹儿...",
                "今天工作很累吧？",
                "一起休息一会儿吧"
            ],
            "excited": [
                "太棒了！",
                "好激动啊！",
                "有大事发生了！",
                "我等不及了！",
                "这太令人兴奋了！"
            ]
        }
        
        # 默认消息，当没有匹配的心情时使用
        self.defaultClickMessages = [
            "有什么需要我帮忙的吗？",
        ]

    def getRandomClickMessage(self):
        """根据当前心情获取随机点击消息"""
        mood = self.pet.mood.getMoodType()
        msg_list = []
        if mood == "Happy":
            msg_list = self.clickMessages[mood]
        elif mood in self.clickMessages:
            msg_list = self.clickMessages[mood] + self.schedule_manager.get_upcoming_schedules_summary()
        else:
            msg_list = self.defaultClickMessages + self.schedule_manager.get_upcoming_schedules_summary()
        
        msg = random.choice(msg_list)
        return msg

    def handleMouseClick(self, event):
        """响应鼠标点击事件"""
        print("宠物被点击")
        
        # 只有在未拖拽时才显示气泡框
        if not self.isDragging:
            # 获取随机消息
            message = self.getRandomClickMessage()
            mood = self.pet.mood.getMoodType()
            
            # 显示调试信息
            print(f"点击消息: {message}, 当前心情: {mood}")
            
            # 使用Bubble.py中的Msg类在桌宠上方显示气泡框，并传递心情
            # 当event为None时，使用当前宠物位置
            pet_position = self.pet.position
            self.msgBubble.show_above_pet(message, pet_position, mood)

    def handleMouseDoubleClick(self, event):
        """响应鼠标双击事件"""
        print("宠物被双击 - 现在可以拖拽了")
        # 使用Bubble.py中的Msg类在桌宠上方显示气泡框
        self.msgBubble.show_above_pet("抓住我吧！", self.pet.position)

    def handleDragStart(self, event):
        """响应拖拽开始事件"""
        print("拖拽开始")
        self.isDragging = True
        # 切换到拖拽动画
        mood = self.pet.mood.getMoodType()
        charactor_path = get_resource_path(f"/pet/static/charactor/{self.pet.id}/drag/{mood}")
        self.ui.setAnimationFolder(charactor_path)

    def handleDragEnd(self, event):
        """响应拖拽结束事件"""
        if self.isDragging:  # 只有在拖拽状态下才执行
            print("拖拽结束")
            self.isDragging = False
            # 恢复到默认动画
            mood = self.pet.mood.getMoodType()
            charactor_path = get_resource_path(f"/pet/static/charactor/{self.pet.id}/stand/{mood}")
            self.ui.setAnimationFolder(charactor_path)

    def startChat(self):
        """开始聊天"""
        print("开始聊天交互")
        
        # 显示互动消息
        message = "你好！我是你的桌宠，有什么想和我聊的吗？"
        self.interactWithUser(message)
        
    
        

    def setHoverMessage(self, message):
        """设置鼠标悬停时显示的消息"""
        if hasattr(self.ui, 'setHoverMessage'):
            self.ui.setHoverMessage(message)
    
    def updateHoverMessageBasedOnMood(self):
        # """根据宠物心情更新悬停消息"""
        mood = self.pet.mood
        print(f"当前心情: {mood}")
        mood = mood.getMoodType()
        messages = {
            "Happy": "我现在非常开心！",
            "Nomal": "我现在心情不错！",
            "PoorCondition": "我有点低落...",
            "sad": "我有点难过...",
            "angry": "我现在很生气！",
            "tired": "我好累啊，想休息一下。",
            "excited": "好激动啊！"
        }
        
        message = messages.get(mood, f"我的心情是：{mood}")
        self.setHoverMessage(message)
        return