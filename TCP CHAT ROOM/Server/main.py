import sys
from PyQt5.QtWidgets import QApplication
from ServerGUI import ServerGUI
from ServerBackend import ChatServer

def main():
    app = QApplication(sys.argv)
    gui = ServerGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()