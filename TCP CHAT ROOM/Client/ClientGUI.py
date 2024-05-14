import sys
import socket
import threading
import logging
import errno
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QFont, QIcon

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

class ChatClient(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat Client")
        self.setWindowIcon(QIcon("comment.png")) 
        self.resize(400, 600)
        self.logged_in = False
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((IP, PORT))
        self.client_socket.setblocking(False)
        self.init_ui()
        self.show()

    def init_ui(self):
        font = QFont("Arial", 10)
        self.setFont(font)
        self.setStyleSheet("QWidget { background-color: #333; color: #EEE; }")
        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.username_entry = QLineEdit(self)
        self.username_entry.setPlaceholderText("Enter your username...")
        self.username_entry.setStyleSheet("QLineEdit { border: 2px solid #555; border-radius: 10px; padding: 5px; background: #222; color: #EEE; }")
        self.username_button = QPushButton("Login", self)
        self.username_button.setStyleSheet("QPushButton { border: 2px solid #555; border-radius: 10px; padding: 5px; background: #05C; color: #EEE; }")
        self.username_button.clicked.connect(self.send_login)
        self.message_text = QLineEdit(self)
        self.message_text.setPlaceholderText("Type your message here...")
        self.message_text.setEnabled(False)
        self.message_text.setStyleSheet("QLineEdit { border: 2px solid #555; border-radius: 10px; padding: 5px; background: #222; color: #EEE; }")
        self.send_button = QPushButton("Send", self)
        self.send_button.setEnabled(False)
        self.send_button.setStyleSheet("QPushButton { border: 2px solid #555; border-radius: 10px; padding: 5px; background: #05C; color: #EEE; }")
        self.send_button.clicked.connect(self.send_message)
        self.chat_history = QTextEdit(self)
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("QTextEdit { border: 2px solid #555; border-radius: 10px; padding: 5px; background: #222; color: #EEE; }")
        self.offline_button = QPushButton("Offline", self)
        self.offline_button.setStyleSheet("QPushButton { border: 2px solid #555; border-radius: 10px; padding: 5px; background: #C00; color: #EEE; }")
        self.offline_button.clicked.connect(self.go_offline)
        self.layout.addWidget(self.username_entry)
        self.layout.addWidget(self.username_button)
        self.layout.addWidget(self.message_text)
        self.layout.addWidget(self.send_button)
        self.layout.addWidget(self.chat_history)
        self.layout.addWidget(self.offline_button)
        self.setLayout(self.layout)
        self.tray_icon = QSystemTrayIcon(QIcon('comment.png'), self)  
        tray_menu = QMenu()
        open_action = tray_menu.addAction("Open")
        exit_action = tray_menu.addAction("Exit")
        open_action.triggered.connect(self.show)
        exit_action.triggered.connect(self.close)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    

    def send_login(self):
        username = self.username_entry.text()
        if username:
            username = username.encode("utf-8")
            username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
            self.client_socket.send(username_header + username)
            self.logged_in = True
            self.enable_message_sending()

    def enable_message_sending(self):
        self.message_text.setEnabled(True)
        self.send_button.setEnabled(True)
        self.username_entry.hide()
        self.username_button.hide()
        threading.Thread(target=self.receive_messages, daemon=True).start()
    
    def go_offline(self):
        if self.client_socket:
            self.client_socket.close()
            logging.info("You are now offline.")
        self.logged_in = False
        self.message_text.setEnabled(False)
        self.send_button.setEnabled(False)
    
    def send_message(self):
        if not self.logged_in:
            logging.error("Attempted to send message without logging in.")
            return
        message = self.message_text.text()
        if message:
            message = message.encode("utf-8")
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
            self.client_socket.send(message_header + message)
            self.message_text.clear()

    def receive_messages(self):
        while True:
            try:
                username_header = self.client_socket.recv(HEADER_LENGTH)
                if not username_header:
                    logging.info("Connection closed by the server.")
                    break 
                username_length = int(username_header.decode('utf-8').strip())
                username = self.client_socket.recv(username_length).decode('utf-8')

                message_header = self.client_socket.recv(HEADER_LENGTH)
                if not message_header:
                    logging.info("Connection closed by the server.")
                    break  
                message_length = int(message_header.decode('utf-8').strip())
                message = self.client_socket.recv(message_length).decode('utf-8')
                self.display_message(username, message)
            except IOError as e:
                if e.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                    continue
                logging.error(f"Read error: {str(e)}")
                break  
            except Exception as e:
                logging.error(f"General error: {str(e)}")
                break  

        self.go_offline()