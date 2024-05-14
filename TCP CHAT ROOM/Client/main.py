import sys
from  ClientGUI import ChatClient
from PyQt5.QtWidgets import QApplication
def main():
    app = QApplication(sys.argv)
    ex = ChatClient()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()