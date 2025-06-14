# -*-  coding: utf-8 -*-

from time import sleep
from PyQt5.QtCore import  Qt,QRect,QPoint,QTimer
from PyQt5.QtWidgets import QDialog,QLabel,QApplication,QHBoxLayout,QDesktopWidget, QVBoxLayout
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
 
 
class Msg(QDialog):
    def __init__(self):
        super(Msg, self).__init__()
        self.ini_ui()
 
 
    def ini_ui(self):
        # 宠物估计尺寸和位置调整（根据需要调整这些值）
        self.pet_width = 300  # 宠物宽度估计值
        self.pet_height = 300  # 宠物高度估计值
        self.offset_x = 0  # 水平位置微调
        self.offset_y = 36  # 垂直位置微调（正值向下移动）
        self.setWindowModality(Qt.NonModal)
        self.setWindowOpacity(1.0)  # 设置为完全不透明
        self.setStyleSheet("""
                QDialog{
                border: 2px solid black;
                border-radius: 0px;  /* 像素风格：去除圆角 */
                background: #FFFFFF;}  /* 纯白背景 */
                """)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        
        # 设置一个默认的小尺寸
        self.setFixedSize(100, 48)  # 固定大小，适合展示一段简短文字
        
        # 创建垂直布局
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.setContentsMargins(15, 15, 15, 15)  # 设置内边距
        
        # 创建消息标签
        self.msg_label = QLabel()
        self.msg_label.setWordWrap(True)  # 允许文本自动换行
        self.msg_label.setAlignment(Qt.AlignCenter)  # 文本居中对齐
        self.msg_label.setStyleSheet("""
        QLabel{
            color: #000000;  /* 黑色文字 */
            text-align: center;
            border: none;
            border-image: none;
            font-size: 14px;  /* 较小的字体 */
            font-weight: 400;
            font-family: "Courier New", "Consolas", monospace;  /* 像素风格字体 */
            letter-spacing: 1px;  /* 增加字母间距 */
        }
        """)
        self.main_layout.addWidget(self.msg_label)
 
        # 定时器用于淡出效果
        self.fade_timer = QTimer()
        self.fade_timer.setInterval(2000)
        self.fade_timer.timeout.connect(self.faded_out)
        
        # 设置像素风箭头绘制标志
        self.draw_arrow = True
        self.arrow_direction = "up"  # 默认箭头方向指向上方
 
    # (中心展示)只能在show方法后调用
    def center_show(self, offset):
        geo = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()  # 获取显示器分辨率，并找到中间点
        if offset:
            print("窗口偏置")
            geo.moveCenter(cp + offset)  # 将窗口中点偏置
        else:
            geo.moveCenter(cp)  # 将窗口中点放在屏幕中间
        self.move(geo.topLeft())
 
    def show_msg(self,text = "hello world"):
        self.fade_timer.start()
        self.msg_label.setText(text)
        self.msg_label.repaint()
        self.raise_()
        self.show()
        self.center_show(QPoint(75,0))
        self.exec_()  # 动画弹出
        sleep(0.5)
 
    def set_style_by_mood(self, mood):
        """根据宠物心情设置气泡样式
        
        Args:
            mood: 宠物心情类型
        """
        # 像素风格的对话框样式
        dialog_styles = {
            "happy": """
                QDialog{
                    border: 3px solid #4CAF50;
                    border-radius: 0px;
                    background: #E6FFE6;
                }
            """,
            "sad": """
                QDialog{
                    border: 3px solid #2196F3;
                    border-radius: 0px;
                    background: #E3F2FD;
                }
            """,
            "angry": """
                QDialog{
                    border: 3px solid #F44336;
                    border-radius: 0px;
                    background: #FFEBEE;
                }
            """,
            "tired": """
                QDialog{
                    border: 3px solid #FFC107;
                    border-radius: 0px;
                    background: #FFF8E1;
                }
            """,
            "excited": """
                QDialog{
                    border: 3px solid #9C27B0;
                    border-radius: 0px;
                    background: #F3E5F5;
                }
            """
        }
        
        # 像素风格的文字样式
        label_styles = {
            "happy": """
                QLabel{
                    color: #2E7D32;
                    text-align: center;
                    border: none;
                    border-image: none;
                    font-size: 14px;
                    font-weight: 400;
                    font-family: "Courier New", "Consolas", monospace;
                    letter-spacing: 1px;
                }
            """,
            "sad": """
                QLabel{
                    color: #0D47A1;
                    text-align: center;
                    border: none;
                    border-image: none;
                    font-size: 14px;
                    font-weight: 400;
                    font-family: "Courier New", "Consolas", monospace;
                    letter-spacing: 1px;
                }
            """,
            "angry": """
                QLabel{
                    color: #B71C1C;
                    text-align: center;
                    border: none;
                    border-image: none;
                    font-size: 14px;
                    font-weight: 400;
                    font-family: "Courier New", "Consolas", monospace;
                    letter-spacing: 1px;
                }
            """,
            "tired": """
                QLabel{
                    color: #FF6F00;
                    text-align: center;
                    border: none;
                    border-image: none;
                    font-size: 14px;
                    font-weight: 400;
                    font-family: "Courier New", "Consolas", monospace;
                    letter-spacing: 1px;
                }
            """,
            "excited": """
                QLabel{
                    color: #4A148C;
                    text-align: center;
                    border: none;
                    border-image: none;
                    font-size: 14px;
                    font-weight: 400;
                    font-family: "Courier New", "Consolas", monospace;
                    letter-spacing: 1px;
                }
            """
        }
        
        # 保存当前mood用于绘制正确颜色的箭头
        self.current_mood = mood
        
        # 设置对话框样式
        self.setStyleSheet(dialog_styles.get(mood, dialog_styles.get("happy", """
            QDialog{
                border: 3px solid black;
                border-radius: 0px;
                background: #FFFFFF;
            }
        """)))
        
        # 设置标签样式
        self.msg_label.setStyleSheet(label_styles.get(mood, label_styles.get("happy")))
        
    def show_above_pet(self, text, pet_position, mood=None):
        """在桌宠中下部分显示气泡消息
        
        Args:
            text: 要显示的消息
            pet_position: 桌宠的位置 (x, y)
            mood: 宠物心情类型
        """
        # 确保窗口完全不透明
        self.setWindowOpacity(1.0)
        
        # 启动淡出定时器
        self.fade_timer.start()
        
        # 设置消息文本
        self.msg_label.setText(text)
        
        # 设置气泡样式
        if mood:
            # 不需要那么多样式！默认设置为happy
            self.set_style_by_mood("happy")
            
        self.msg_label.repaint()
        
        # 根据文本内容自动调整大小
        text_length = len(text)
        if text_length > 30:  # 如果文本非常长
            self.setFixedSize(260, 120)  # 较大尺寸
        elif text_length > 20:  # 如果文本较长
            self.setFixedSize(240, 100)  # 增加气泡大小
        else:
            self.setFixedSize(220, 90)  # 默认大小
        
        # 获取宠物位置
        x, y = pet_position
        
        
        
        # 计算气泡框位置
        # 气泡框水平居中对齐在宠物上方
        bubble_x = max(0, x + self.pet_width // 2 - self.width() // 2 + self.offset_x)
        
        # 气泡框顶部位于宠物的中部位置
        bubble_y = max(0, y + self.offset_y + self.pet_height // 2 - self.height() // 2)
        
        # 确保箭头方向为向上
        self.arrow_direction = "up"
        
        # 移动窗口到计算出的位置
        self.move(bubble_x, bubble_y)
        
        # 确保窗口在最前面
        self.raise_()
        self.activateWindow()  # 激活窗口
        self.show()
        
        # 运行对话框
        self.exec_()
        
        # 短暂延迟
        sleep(0.3)
 
    def faded_out(self):
        """窗口渐隐效果"""
        print("窗口渐隐")
        # 使用更少的步骤，但增加每步的停留时间，使效果更平滑
        for i in range(100, 0, -10):  # 步长从-1改为-10
            opacity = i / 100
            self.setWindowOpacity(opacity)  # 设置窗口透明度
            self.repaint()
            QApplication.processEvents()
            sleep(0.03)  # 减少停留时间为30毫秒
 
        self.fade_timer.stop()
        self.close()
    
    def paintEvent(self, event):
        """重写绘制事件，添加像素风格边框和箭头"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)  # 关闭抗锯齿，保持像素风格
        
        # 根据心情获取颜色
        mood_colors = {
            "happy": QColor("#4CAF50"),
            "sad": QColor("#2196F3"),
            "angry": QColor("#F44336"),
            "tired": QColor("#FFC107"),
            "excited": QColor("#9C27B0")
        }
        
        
        # 获取当前边框颜色
        border_color = mood_colors.get(getattr(self, 'current_mood', None), QColor("#000000"))
        
        # 绘制像素风边角装饰
        corner_size = 8
        # 左上角
        painter.fillRect(0, 0, corner_size, corner_size, border_color)
        # 右上角
        painter.fillRect(self.width() - corner_size, 0, corner_size, corner_size, border_color)
        # 左下角
        painter.fillRect(0, self.height() - corner_size, corner_size, corner_size, border_color)
        # 右下角
        painter.fillRect(self.width() - corner_size, self.height() - corner_size, corner_size, corner_size, border_color)
        
        # 绘制像素风箭头
        if self.draw_arrow:
            if self.arrow_direction == "down":
                # 绘制指向下方的箭头（指向宠物）
                arrow_width = 10
                arrow_height = 5
                
                # 箭头位置在底部居中
                arrow_x = (self.width() - arrow_width) // 2
                arrow_y = self.height() - 2  # 靠近底部边框
                
                # 绘制像素风箭头
                painter.setPen(QPen(border_color, 2))
                painter.setBrush(QBrush(border_color))
                
                # 绘制矩形作为箭头
                points = [
                    QPoint(arrow_x, arrow_y),
                    QPoint(arrow_x + arrow_width, arrow_y),
                    QPoint(arrow_x + arrow_width // 2, arrow_y + arrow_height)
                ]
                
                # 绘制填充三角形
                for i in range(2):
                    painter.drawLine(points[i], points[i+1])
                painter.drawLine(points[2], points[0])
            
            elif self.arrow_direction == "up":
                # 绘制指向上方的箭头（从宠物指向气泡）
                arrow_width = 16
                arrow_height = 8
                
                # 箭头位置在顶部居中
                arrow_x = (self.width() - arrow_width) // 2
                arrow_y = 2  # 稍微偏离顶部边框
                
                # 绘制像素风箭头
                painter.setPen(QPen(border_color, 2))
                painter.setBrush(QBrush(border_color))
                
                # 绘制箭头点
                points = [
                    QPoint(arrow_x, arrow_y),
                    QPoint(arrow_x + arrow_width, arrow_y),
                    QPoint(arrow_x + arrow_width // 2, arrow_y - arrow_height)
                ]
                
                # 绘制填充三角形
                painter.drawPolygon(points)
        
        painter.end()
 
 

    