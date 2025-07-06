
"""
测试右键菜单功能
"""
import sys
import os

# 添加父目录到Python路径，以便导入pet模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from desktop_pet_ui import DesktopPetUI
from config import PetConfig

def test_context_menu():
    """测试右键菜单功能"""
    app = QApplication(sys.argv)
    
    # 创建一个简单的UI实例用于测试
    test_frame_folder = PetConfig.get_animation_path(1, PetConfig.AnimationType.STAND, PetConfig.MoodType.NORMAL)
    ui = DesktopPetUI(frame_folder=test_frame_folder)
    
    print("右键菜单测试：")
    print("1. 右键点击桌宠")
    print("2. 选择'关联日程管理账号'")
    print("3. 应该打开登录窗口")
    
    ui.show()
    return app.exec_()

if __name__ == '__main__':
    test_context_menu() 