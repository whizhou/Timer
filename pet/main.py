from PyQt5.QtWidgets import QApplication
import sys
import os

# 获取当前脚本的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # 项目根目录

# 使用相对导入
from desktop_pet_ui import DesktopPetUI
from desktop_pet_controller import DesktopPetController
from desktop_pet import DesktopPet
from mood import Mood
from mouse_event_handler import MouseEventHandler
from Bubble import Msg  # 导入Bubble中的Msg类

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mood = "PoorCondition"  # 设置初始心情
    # 初始化宠物
    pet = DesktopPet(position=(0, 0), mood=Mood(mood), actions=["idle", "jump", "study", "down"])
    
    # 使用正确的绝对路径
    # 检查是否有static目录在pet目录下
    pet_static_path = os.path.join(current_dir, "static")
    if os.path.exists(pet_static_path):
        # 如果pet目录下有static，使用它
        frame_folder = os.path.join(pet_static_path, f"charactor/{pet.id}/stand/{mood}")
    else:
        # 否则使用项目根目录下的static
        frame_folder = os.path.join(project_root, f"static/charactor/{pet.id}/stand/{mood}")
    
    print(f"使用帧目录: {frame_folder}")
    ui = DesktopPetUI(frame_folder=frame_folder)
    
    controller = DesktopPetController(pet, ui)
    ui.controller = controller  # 将controller传递给UI
    mouseHandler = MouseEventHandler(controller)

    # 绑定鼠标事件
    ui.mousePressEvent = mouseHandler.handleClick  # 修改为点击事件
    ui.mouseReleaseEvent = mouseHandler.handleDragEnd
    ui.mouseMoveEvent = mouseHandler.handleMouseMove
    ui.mouseDoubleClickEvent = mouseHandler.handleDoubleClick  # 添加双击事件

    sys.exit(app.exec_())

