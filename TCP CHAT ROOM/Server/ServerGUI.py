import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton, QLabel, QListWidget, QHBoxLayout, QSystemTrayIcon, QMenu
from PyQt5.QtCore import pyqtSlot, QTimer,pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtMultimedia import QSound
from ServerBackend import ChatServer


def read_config():
    try:
        with open('D:/Python/TCP CHAT ROOM/Server/config.txt', 'r') as f:
            lines = f.read().splitlines()
        ip = lines[0].strip()
        port = int(lines[1].strip())
        return ip, port
    except FileNotFoundError:
        print("Error: The config.txt file was not found.")
        raise
    except IndexError:
        print("Error: The config.txt file does not contain enough data.")
        raise
    except ValueError:
        print("Error: The port number is not a valid integer.")
        raise

IP, PORT = read_config()

class ServerGUI(QMainWindow):
    update_text_signal = pyqtSignal(str, int)
    update_online_list_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.server = ChatServer(self)
        self.server.update_text_signal.connect(self.update_chat_display)
        self.update_online_list_signal.connect(self.update_online_list)
        self.server.update_online_list_signal.connect(self.update_online_list)
        threading.Thread(target=self.server.run, daemon=True).start()
        self.notification_sound = QSound("mixkit-correct-answer-reward-952.wav")
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('D:/Python/UpdatedChat/data-center.png')) 
        self.initTray()

    def initUI(self):
        self.setWindowTitle("Server Panel")
        self.setGeometry(100, 100, 1200, 600)
        self.setWindowIcon(QIcon('data-center.png'))
        font = QFont('Helvetica', 12)
        self.setStyleSheet("""
        QMainWindow {
            background-color: #2B2B2B;
        }
        QTextEdit, QListWidget, QLabel {
            background-color: #323232;
            color: #DDD;
            border: 2px solid #555;
            border-radius: 4px;
            padding: 5px;
        }
        QPushButton {
            background-color: #5C94BD;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            padding: 10px;
            min-width: 100px;
        }
        QPushButton:hover {
            background-color: #5085A5;
        }
        """)
        self.chat_display_left = QTextEdit(self)
        self.chat_display_left.setFont(font)
        self.chat_display_left.setReadOnly(True)
        self.chat_display_right = QTextEdit(self)
        self.chat_display_right.setFont(font)
        self.chat_display_right.setReadOnly(True)
        self.stop_button = QPushButton('Stop Server', self)
        self.stop_button.clicked.connect(self.stop_server)
        self.online_users_list = QListWidget()
        self.server_info_label = QLabel(f'Server running at IP: {IP} Port: {PORT}')
        self.server_stats_label = QLabel('Server Stats: 0 messages processed')
        
        layout = QVBoxLayout()
        side_layout = QVBoxLayout()
        main_layout = QHBoxLayout()
        widget = QWidget()

        online_users_label = QLabel("Online Users")
        online_users_label.setFont(font)
        chat_display_left_label = QLabel(f"Chat Display")
        chat_display_left_label.setFont(font)
        chat_display_right_label = QLabel("Chat Display - Right")
        chat_display_right_label.setFont(font)
        
        side_layout.addWidget(online_users_label)
        side_layout.addWidget(self.online_users_list)
        side_layout.addWidget(self.server_info_label)
        side_layout.addWidget(self.server_stats_label)
        side_layout.addWidget(self.stop_button)
        
        layout.addWidget(chat_display_left_label)
        layout.addWidget(self.chat_display_left)
        layout.addWidget(chat_display_right_label)
        layout.addWidget(self.chat_display_right)
        
        main_layout.addLayout(layout, 75)
        main_layout.addLayout(side_layout, 25)
        
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)
        self.update_text_signal.connect(self.update_chat_display)

    def update_chat_display(self, message, client_id):
        chat_display = self.chat_display_left if client_id == 1 else self.chat_display_right
        original_color = '#DDD'
        if "went offline" in message:
            temp_color = '#FF6347'
            self.notification_sound.play()
        elif "is now online!" in message:
            temp_color = '#32CD32'
            self.notification_sound.play()  
        else:
            temp_color = '#bbff33'
        message_formatted = f'<span style="color: {temp_color};">{message}</span>'
        chat_display.append(message_formatted)
        QTimer.singleShot(4000, lambda: self.revert_color(chat_display, message, original_color))

    def revert_color(self, chat_display, message, original_color):
        chat_display.undo()
        chat_display.append(f'<span style="color: {original_color};">{message}</span>')

    def update_online_list(self, users):
        self.online_users_list.clear()
        for user in users:
            self.online_users_list.addItem(user)
        self.server_stats_label.setText(f'Server Stats: {self.server.message_count} messages processed')

    def stop_server(self):
        for client_socket in list(self.server.clients.keys()):
            client_socket.close()
        if self.server.server_socket:
            self.server.server_socket.close()
        QApplication.instance().quit()
    def initTray(self):
        self.tray_icon = QSystemTrayIcon(QIcon('server_icon.png'), self)
        tray_menu = QMenu()
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(QApplication.instance().quit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()