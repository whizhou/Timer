import sys
import requests
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout,
                             QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QColor
import os

from config import PetConfig
BASE_URL = PetConfig.BASE_URL


def get_resource_path(relative_path):
    """获取资源文件的绝对路径，兼容 PyInstaller 打包后的路径"""
    try:
        # PyInstaller 创建临时文件夹，将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        # 如果不是 PyInstaller 打包的环境，使用当前文件所在目录
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def get_data_dir():
    """获取数据目录路径，兼容 PyInstaller 运行时"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后的情况
        # 使用exe文件同目录下的应用数据文件夹
        data_dir = os.path.join(os.path.dirname(sys.executable), "data")
    else:
        # 开发环境，使用当前文件所在目录下的 data 文件夹
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    
    # 确保目录存在
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_session_id() -> str:
    """从本地文件中读取会话ID"""
    session_file = os.path.join(get_data_dir(), 'session.txt')
    if os.path.exists(session_file):
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"读取会话文件失败: {e}")
    return ''


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 窗口基础设置
        self.setWindowTitle('用户登录系统')
        
        # 获取图标路径，兼容 PyInstaller
        icon_path = get_resource_path(os.path.join('static', 'charactor', '1', '头像', 'image.png'))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setFixedSize(500, 400)
        
        # 整体背景浅色
        self.setStyleSheet("""
            QWidget#background {
                background-color: #F2F3F5;
            }
            QFrame#card {
                background-color: #FFFFFF;
                border-radius: 18px;
            }
            QLabel#title {
                color: #333333;
                font-size: 28px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'SimHei', 'sans-serif';
            }
            QLabel {
                color: #555555;
                font-size: 15px;
                min-width: 90px;
                font-family: 'Microsoft YaHei', 'SimHei', 'sans-serif';
            }
            QLineEdit {
                border: none;
                border-radius: 12px;
                padding: 10px 36px 10px 12px;
                font-size: 15px;
                background: #F2F3F5;
                color: #333333;
                font-family: 'Microsoft YaHei', 'SimHei', 'sans-serif';
            }
            QLineEdit:focus {
                background: #FFFFFF;
                border: 1.5px solid #5F6DF9;
            }
            QPushButton {
                background-color: #5F6DF9;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 10px 28px;
                font-size: 15px;
                font-family: 'Microsoft YaHei', 'SimHei', 'sans-serif';
            }
            QPushButton:hover {
                background-color: #4F5DD9;
            }
            QPushButton:pressed {
                background-color: #3F4DC9;
            }
            QPushButton#resetBtn {
                background-color: #E6E6E6;
                color: #555555;
            }
            QPushButton#resetBtn:hover {
                background-color: #CCCCCC;
            }
        """)

        # 背景容器
        background = QFrame(self)
        background.setObjectName('background')
        bg_layout = QVBoxLayout(background)
        bg_layout.setContentsMargins(0, 0, 0, 0)

        # 卡片容器
        card = QFrame()
        card.setObjectName('card')
        card.setFixedSize(380, 300)
        shadow = QGraphicsDropShadowEffect(blurRadius=30, xOffset=0, yOffset=10)
        shadow.setColor(QColor(0, 0, 0, 60))
        card.setGraphicsEffect(shadow)

        # 卡片内部布局
        form_layout = QVBoxLayout(card)
        form_layout.setContentsMargins(36, 36, 36, 36)
        form_layout.setSpacing(22)

        # 标题
        title = QLabel('欢迎登录')
        title.setObjectName('title')
        title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title)

        # 用户名
        user_layout = QHBoxLayout()
        lbl_user = QLabel('用户名:')
        # user_icon_label = QLabel('👤')
        # user_icon_label.setFixedWidth(10)
        # user_icon_label.setAlignment(Qt.AlignCenter)
        # user_icon_label.setStyleSheet('font-size: 18px;')
        edit_user = QLineEdit()
        edit_user.setPlaceholderText('请输入用户名')
        user_layout.addWidget(lbl_user)
        # user_layout.addWidget(user_icon_label)
        user_layout.addWidget(edit_user)

        # 密码
        pwd_layout = QHBoxLayout()
        lbl_pwd = QLabel('密码:')
        # pwd_icon_label = QLabel('🔒')
        # pwd_icon_label.setFixedWidth(10)
        # pwd_icon_label.setAlignment(Qt.AlignCenter)
        # pwd_icon_label.setStyleSheet('font-size: 18px;')
        edit_pwd = QLineEdit()
        edit_pwd.setPlaceholderText('请输入密码')
        edit_pwd.setEchoMode(QLineEdit.Password)
        pwd_layout.addWidget(lbl_pwd)
        # pwd_layout.addWidget(pwd_icon_label)
        pwd_layout.addWidget(edit_pwd)

        # 按钮行
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        btn_login = QPushButton('登 录')
        btn_login.clicked.connect(lambda: self.handle_login(edit_user, edit_pwd, btn_login))
        btn_login.setCursor(Qt.PointingHandCursor)
        btn_reset = QPushButton('重 置')
        btn_reset.setObjectName('resetBtn')
        btn_reset.clicked.connect(lambda: (edit_user.clear(), edit_pwd.clear()))
        btn_reset.setCursor(Qt.PointingHandCursor)
        btn_layout.addWidget(btn_login)
        btn_layout.addWidget(btn_reset)
        btn_layout.addStretch(1)

        # 添加到表单
        form_layout.addLayout(user_layout)
        form_layout.addLayout(pwd_layout)
        form_layout.addLayout(btn_layout)

        # 将卡片居中
        container_layout = QVBoxLayout()
        container_layout.addStretch(1)
        container_layout.addWidget(card, alignment=Qt.AlignCenter)
        container_layout.addStretch(1)
        bg_layout.addLayout(container_layout)

        self.setLayout(bg_layout)

    def handle_login(self, user_edit, pwd_edit, login_btn):
        username = user_edit.text().strip()
        password = pwd_edit.text().strip()
        if not username or not password:
            QMessageBox.warning(self, '输入错误', '用户名和密码不能为空!')
            return
        login_btn.setText('登录中...')
        login_btn.setEnabled(False)
        QApplication.processEvents()

        try:
            response = requests.post(
                BASE_URL + '/auth/login',
                json={'username': username, 'password': password},
                timeout=5
            )
            login_btn.setText('登 录')
            login_btn.setEnabled(True)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    QMessageBox.information(self, '登录成功', f'欢迎, {username}!')
                else:
                    QMessageBox.information(self, '登录失败', result.get('error', '用户名或密码错误!'))
                session_cookie = response.cookies.get('session')
                # 将会话ID存储在本地
                if session_cookie:
                    session_file = os.path.join(get_data_dir(), 'session.txt')
                    try:
                        with open(session_file, 'w', encoding='utf-8') as f:
                            f.write(session_cookie)
                    except Exception as e:
                        print(f"保存会话文件失败: {e}")
            else:
                try:
                    error_message = response.json().get('error', '未知错误')
                except:
                    error_message = '无法解析服务器响应'
                # QMessageBox.critical(self, '错误', f'服务器错误: {response.status_code}', f'错误信息: {error_message}')
        except requests.exceptions.RequestException as e:
            login_btn.setText('登 录')
            login_btn.setEnabled(True)
            QMessageBox.critical(self, '网络错误', f'无法连接到服务器: {e}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont('Microsoft YaHei', 11)
    app.setFont(font)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())