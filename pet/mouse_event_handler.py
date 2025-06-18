
"""
鼠标事件处理模块
负责处理所有与鼠标相关的交互事件
"""
import os
from PyQt5.QtCore import QTimer
from config import PetConfig

class MouseEventHandler:
    """鼠标事件处理器类"""
    
    def __init__(self, controller):
        """
        初始化鼠标事件处理器
        
        Args:
            controller: 桌宠控制器实例
        """
        self.controller = controller
        
        # 拖拽相关状态
        self.drag_start_pos = None
        self.is_draggable = False
        
        # 双击检测相关
        self.is_double_click_pending = False
        self.click_timer = QTimer()
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self._on_single_click_timeout)
    
    def handle_click(self, event):
        """
        处理鼠标点击事件
        
        Args:
            event: 鼠标点击事件
        """
        # 左键点击
        if event.button() == 1:  # 左键
            if not self.is_double_click_pending:
                # 第一次点击，启动定时器，准备处理单击事件
                self.is_double_click_pending = True
                self.click_timer.start(PetConfig.DOUBLE_CLICK_TIMEOUT)
            else:
                # 已经处于等待双击状态，忽略这次点击
                pass
                
        # 启动拖拽（只有允许拖拽且是左键时才启动）
        if self.is_draggable and event.button() == 1:
            self.handle_drag_start(event)
    
    def _on_single_click_timeout(self):
        """单击定时器超时处理"""
        # 定时器到时，没有发生双击，执行单击事件
        if self.is_double_click_pending:
            self.is_double_click_pending = False
            self.controller.handle_mouse_click(None)

    def handle_double_click(self, event):
        """
        处理鼠标双击事件
        
        Args:
            event: 鼠标双击事件
        """
        # 取消单击定时器，阻止单击事件的触发
        self.click_timer.stop()
        self.is_double_click_pending = False
        
        # 执行双击处理
        self.controller.handle_mouse_double_click(event)
        
        # 双击后启用拖拽功能
        self.is_draggable = True
        print("双击后启用拖拽功能")

    def handle_drag_start(self, event):
        """
        处理拖拽开始事件
        
        Args:
            event: 鼠标事件
        """
        # 只有在可拖拽状态(双击后)才允许拖拽
        if self.is_draggable and event.button() == 1:  # 左键拖拽
            self.drag_start_pos = event.globalPos()
            self.controller.handle_drag_start(event)
            print(f"开始拖拽，起始位置: {self.drag_start_pos}")

    def handle_drag_end(self, event):
        """
        处理拖拽结束事件
        
        Args:
            event: 鼠标事件
        """
        if self.drag_start_pos is not None:
            print(f"拖拽结束，最终位置: {event.globalPos()}")
            self.drag_start_pos = None
            self.controller.handle_drag_end(event)
            
            # 拖拽完成后恢复不可拖拽状态
            self.is_draggable = False
            print("拖拽完成，恢复不可拖拽状态")

    def handle_mouse_move(self, event):
        """
        处理鼠标移动事件
        
        Args:
            event: 鼠标移动事件
        """
        if self.drag_start_pos is not None:
            # 计算鼠标移动的偏移量
            current_pos = event.globalPos()
            offset = current_pos - self.drag_start_pos
            self.drag_start_pos = current_pos
            
            # 通知控制器更新宠物位置
            self.controller.move_pet_by_offset(offset)
    
    def is_in_dragging_state(self) -> bool:
        """
        检查是否处于拖拽状态
        
        Returns:
            bool: 是否正在拖拽
        """
        return self.drag_start_pos is not None
    
    def can_drag(self) -> bool:
        """
        检查是否可以拖拽
        
        Returns:
            bool: 是否可以拖拽
        """
        return self.is_draggable
    
    def reset_drag_state(self):
        """重置拖拽状态"""
        self.drag_start_pos = None
        self.is_draggable = False
        print("拖拽状态已重置")
    
    def force_enable_drag(self):
        """强制启用拖拽功能"""
        self.is_draggable = True
        print("强制启用拖拽功能")
    
    def force_disable_drag(self):
        """强制禁用拖拽功能"""
        self.is_draggable = False
        self.drag_start_pos = None
        print("强制禁用拖拽功能")
    
    def cleanup(self):
        """清理资源"""
        if self.click_timer.isActive():
            self.click_timer.stop()
        self.reset_drag_state()
        print("鼠标事件处理器已清理")