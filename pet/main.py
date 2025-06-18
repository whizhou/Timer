
"""
桌宠应用程序主入口
负责初始化和启动桌宠应用
"""
from PyQt5.QtWidgets import QApplication
import sys
import os


from config import PetConfig

from desktop_pet_ui import DesktopPetUI
from desktop_pet_controller import DesktopPetController
from desktop_pet import DesktopPet
from mood import Mood
from mouse_event_handler import MouseEventHandler
from Bubble import Msg

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    try:
        # 配置参数
        initial_mood_type = PetConfig.MoodType.POOR_CONDITION
        pet_id = 1
        initial_position = (100, 100)  # 设置初始位置
        
        print(f"初始化桌宠，ID: {pet_id}, 心情: {initial_mood_type}")
        
        # 初始化宠物数据模型
        mood = Mood(initial_mood_type)
        pet = DesktopPet(
            position=initial_position,
            mood=mood,
            actions=["idle", "jump", "study", "down"],
            pet_id=pet_id
        )
        
        # 获取初始动画路径
        frame_folder = PetConfig.get_animation_path(
            pet_id, 
            PetConfig.AnimationType.STAND, 
            initial_mood_type
        )
        
        print(f"使用动画路径: {frame_folder}")
        
        # 检查动画路径是否存在
        if not os.path.exists(frame_folder):
            print(f"警告：动画路径不存在: {frame_folder}")
            # 尝试使用备用路径
            backup_folder = os.path.join(PetConfig.STATIC_PATH, f"charactor/{pet_id}/stand")
            if os.path.exists(backup_folder):
                frame_folder = backup_folder
                print(f"使用备用动画路径: {frame_folder}")
            else:
                print("错误：找不到有效的动画文件夹")
                return 1
        
        # 初始化UI界面
        ui = DesktopPetUI(frame_folder=frame_folder)
        
        # 设置UI的初始位置
        ui.move(initial_position[0], initial_position[1])
        
        # 初始化控制器
        controller = DesktopPetController(pet, ui)
        
        # 初始化鼠标事件处理器
        mouse_handler = MouseEventHandler(controller)
        
        # 绑定鼠标事件
        ui.mousePressEvent = mouse_handler.handle_click
        ui.mouseReleaseEvent = mouse_handler.handle_drag_end
        ui.mouseMoveEvent = mouse_handler.handle_mouse_move
        ui.mouseDoubleClickEvent = mouse_handler.handle_double_click
        
        print("桌宠初始化完成，开始运行...")
        
        # 运行应用
        return app.exec_()
        
    except Exception as e:
        print(f"启动桌宠时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)