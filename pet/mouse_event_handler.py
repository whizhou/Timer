import os

# 获取当前脚本的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

from PyQt5.QtCore import QTimer

class MouseEventHandler:
    def __init__(self, controller):
        self.controller = controller
        self.dragStartPos = None
        self.isDraggable = False  # 新增标志，控制是否可以拖拽
        self.isDoubleClickPending = False  # 标记是否可能发生双击
        self.clickTimer = QTimer()  # 双击检测定时器
        self.clickTimer.setSingleShot(True)
        self.clickTimer.timeout.connect(self.onSingleClickTimeout)

    def handleClick(self, event):
        """处理点击事件"""
        # 左键点击
        if event.button() == 1:  # 左键
            if not self.isDoubleClickPending:
                # 第一次点击，启动定时器，延迟处理单击事件
                self.isDoubleClickPending = True
                self.clickTimer.start(300)  # 300毫秒内如果有第二次点击，则是双击
            else:
                # 已经处于等待双击状态，忽略这次点击
                pass
                
        # 启动拖拽（只有允许拖拽且是左键时才启动）
        if self.isDraggable and event.button() == 1:
            self.handleDragStart(event)
    
    def onSingleClickTimeout(self):
        """单击定时器超时，确认为单击事件"""
        # 定时器到时，没有发生双击，执行单击事件
        if self.isDoubleClickPending:
            self.isDoubleClickPending = False
            self.controller.handleMouseClick(None)  # 传递None作为事件

    def handleDoubleClick(self, event):
        """处理双击事件"""
        # 取消定时器，阻止单击事件的触发
        self.clickTimer.stop()
        self.isDoubleClickPending = False
        
        # 执行双击处理
        self.controller.handleMouseDoubleClick(event)
        # 双击后启用拖拽功能
        self.isDraggable = True

    def handleDragStart(self, event):
        """处理拖拽开始事件"""
        # 只有在可拖拽状态(双击后)才允许拖拽
        if self.isDraggable and event.button() == 1:  # 左键拖拽
            self.dragStartPos = event.globalPos()
            self.controller.handleDragStart(event)

    def handleDragEnd(self, event):
        """处理拖拽结束事件"""
        if self.dragStartPos is not None:
            self.dragStartPos = None
            self.controller.handleDragEnd(event)
            # 拖拽完成后恢复不可拖拽状态
            self.isDraggable = False

    def handleMouseMove(self, event):
        """处理鼠标拖动事件"""
        if self.dragStartPos is not None:
            # 计算鼠标移动的偏移量
            currentPos = event.globalPos()
            offset = currentPos - self.dragStartPos
            self.dragStartPos = currentPos
            # 通知控制器更新宠物位置
            self.controller.movePetByOffset(offset)