import logging
import socket
import select
import uuid
from PyQt5.QtCore import QObject, pyqtSignal


logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')
HEADER_LENGTH = 10
def read_config():
    try:
        with open('config.txt', 'r') as f:
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


class ChatServer(QObject):
    update_text_signal = pyqtSignal(str, int)
    update_online_list_signal = pyqtSignal(list)

    def __init__(self, gui):
        super().__init__()
        self.gui = gui
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((IP, PORT))
        self.server_socket.listen()
        self.sockets_list = [self.server_socket]
        self.clients = {}
        self.gui_sides = {1: None, 2: None}
        self.message_count = 0

    def receive_message(self, client_socket):
        try:
            message_header = client_socket.recv(HEADER_LENGTH)
            if not len(message_header):
                return False
            message_length = int(message_header.decode('utf-8').strip())
            message_data = b''
            while len(message_data) < message_length:
                message_data += client_socket.recv(message_length - len(message_data))
            return {'header': message_header, 'data': message_data, 'id': str(uuid.uuid4())}
        except Exception as e:
            logging.error(f'Error receiving message: {str(e)}')
            return False

    def update_clients(self, notified_socket):
        self.release_gui_side(notified_socket)
        client_info = self.clients.pop(notified_socket, None)
        client_username_with_id = f"{client_info['data'].decode('utf-8')}#{client_info['id']}" if client_info else 'Unknown'
        self.gui.update_chat_display(f"{client_username_with_id} went offline", client_info['gui_side'])
        self.sockets_list.remove(notified_socket)
        self.update_online_users()

    def update_online_users(self):
        online_users = [f"{client['data'].decode('utf-8')}#{client['id']}" for client in self.clients.values()]
        self.update_online_list_signal.emit(online_users)

    def assign_gui_side(self, client_socket):
        for side in self.gui_sides:
            if self.gui_sides[side] is None:
                self.gui_sides[side] = client_socket
                return side
        return None

    def release_gui_side(self, client_socket):
        for side, socket in self.gui_sides.items():
            if socket == client_socket:
                self.gui_sides[side] = None
                break
            
    def run(self):
        while True:
            try:
                read_sockets, _, exception_sockets = select.select(self.sockets_list, [], self.sockets_list)
                for notified_socket in read_sockets:
                    if notified_socket == self.server_socket:
                        client_socket, client_address = self.server_socket.accept()
                        gui_side = self.assign_gui_side(client_socket)
                        if gui_side is None:
                            logging.info("No GUI side available, connection refused.")
                            client_socket.close()
                            continue
                        user = self.receive_message(client_socket)
                        if user is False:
                            continue
                        user_id = user['id'][:8]
                        user_name_with_id = f"{user['data'].decode('utf-8')}#{user_id}"
                        self.clients[client_socket] = {'data': user['data'], 'gui_side': gui_side, 'id': user_id}
                        self.update_text_signal.emit(f"{user_name_with_id} is now online!", gui_side)
                        self.sockets_list.append(client_socket)
                        self.update_online_users()
                    else:
                        message = self.receive_message(notified_socket)
                        if message is False:
                            self.update_clients(notified_socket)
                            continue
                        self.message_count += 1
                        user = self.clients[notified_socket]
                        received_message = f"-->{user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}"
                        self.update_text_signal.emit(received_message, user['gui_side'])

                for notified_socket in exception_sockets:
                    self.update_clients(notified_socket)
                    if notified_socket in self.sockets_list:
                        self.sockets_list.remove(notified_socket)
                    if notified_socket in self.clients:
                        del self.clients[notified_socket]
            except Exception as e:
                logging.error(f"An error occurred: {e}")