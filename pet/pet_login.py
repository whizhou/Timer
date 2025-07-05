import sys
import requests
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout,
                             QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QColor


def get_session_id() -> str:
    """从本地文件中读取会话ID"""
    session_path = Path(__file__).parent.resolve() / 'data'
    session_file = session_path / 'session.txt'
    if session_file.exists():
        with open(session_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return ''


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 窗口基础设置
        self.setWindowTitle('用户登录系统')
        self.setWindowIcon(QIcon(':/icons/login.png'))  # 需替换为实际图标路径
        # 增大窗口尺寸
        self.setFixedSize(600, 450)
        
        # 整体背景渐变
        self.setStyleSheet("""
            QWidget#background {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6a11cb, stop:1 #2575fc);
            }
            QFrame#card {
                background-color: white;
                border-radius: 12px;
            }
            QLabel#title {
                color: #333;
                font-size: 32px;
                font-weight: bold;
            }
            QLabel {
                color: #555;
                font-size: 16px;
                min-width: 90px;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 28px 8px 8px;
                font-size: 16px;
                background: #fafafa;
            }
            QLineEdit:focus {
                border: 1px solid #6a11cb;
                background: #fff;
            }
            QPushButton {
                background-color: #6a11cb;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 14px 28px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #5b0fb8;
            }
            QPushButton:pressed {
                background-color: #4a0d93;
            }
            QPushButton#resetBtn {
                background-color: #e53935;
            }
            QPushButton#resetBtn:hover {
                background-color: #d32f2f;
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
        # 相应增加卡片尺寸
        card.setFixedSize(480, 360)
        shadow = QGraphicsDropShadowEffect(blurRadius=20, xOffset=0, yOffset=8)
        shadow.setColor(QColor(0, 0, 0, 80))
        card.setGraphicsEffect(shadow)

        # 卡片内部布局
        form_layout = QVBoxLayout(card)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(25)

        # 标题
        title = QLabel('欢迎登录')
        title.setObjectName('title')
        title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title)

        # 用户名
        user_layout = QHBoxLayout()
        lbl_user = QLabel('用户名:')
        edit_user = QLineEdit()
        edit_user.setPlaceholderText('请输入用户名')
        # 添加图标Action
        user_icon = QIcon(':/icons/user.png')  # 替换为实际路径
        edit_user.addAction(user_icon, QLineEdit.LeadingPosition)
        user_layout.addWidget(lbl_user)
        user_layout.addWidget(edit_user)

        # 密码
        pwd_layout = QHBoxLayout()
        lbl_pwd = QLabel('密码:')
        edit_pwd = QLineEdit()
        edit_pwd.setPlaceholderText('请输入密码')
        edit_pwd.setEchoMode(QLineEdit.Password)
        pwd_icon = QIcon(':/icons/lock.png')  # 替换为实际路径
        edit_pwd.addAction(pwd_icon, QLineEdit.LeadingPosition)
        pwd_layout.addWidget(lbl_pwd)
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
                'http://127.0.0.1:5000/auth/login',
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
                    session_path = Path(__file__).parent.resolve() / 'data'
                    session_path.mkdir(parents=True, exist_ok=True)
                    session_file = session_path / 'session.txt'
                    with open(session_file, 'w', encoding='utf-8') as f:
                        f.write(session_cookie)
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