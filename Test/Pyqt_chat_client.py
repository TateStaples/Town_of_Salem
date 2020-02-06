from PySide2.QtCore import *
from PySide2.QtWidgets import *
import socket
import threading
import time

game_over = False
byte_type = "utf-8"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client = None


def receive_input():
    global game_over
    time.sleep(.1)  # delay until text area exists
    while not game_over:
        msg = s.recv(2048)
        msg = msg.decode(byte_type)
        if msg != "":
            client.text_area.append(msg)
            if msg == "Server: game over!":
                game_over = True


def send_message():
    client.message.returnPressed.connect(send_message)
    s.send(bytes(client.message.text(), byte_type))
    client.message.clear()


class Login(QWidget):
    doing_login = True
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Login Form')
        self.resize(500, 400)

        layout = QGridLayout()

        label_name = QLabel('<font size="4"> Username </font>')
        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setPlaceholderText('username')
        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.lineEdit_username, 0, 1)

        ip_label = QLabel('<font size="4"> IP </font>')
        self.ip = QLineEdit()
        self.ip.setPlaceholderText('Copy and paste your ip here')
        layout.addWidget(ip_label, 1, 0)
        layout.addWidget(self.ip, 1, 1)

        port_label = QLabel('<font size="4"> Port </font>')
        self.port = QLineEdit()
        self.port.setPlaceholderText('port(normally 1234)')
        layout.addWidget(port_label, 1, 2)
        layout.addWidget(self.port, 1, 3)

        button_login = QPushButton('Login')
        button_login.clicked.connect(self.play)
        layout.addWidget(button_login, 2, 0, 1, 2)
        layout.setRowMinimumHeight(2, 75)

        self.setLayout(layout)

    def play(self):
        global name, ip, port
        name = self.lineEdit_username.text()
        port = int(self.port.text())
        ip = self.ip.text()
        game = Client(ip, port, name)
        self.doing_login = False
        self.hide()


class Client:
    ip = ""
    port = 0
    name = ""
    has_connected = False

    def __init__(self, ip, port, name):
        global client
        client = self
        if not self.has_connected:
            self.connect(ip, port, name)
        self.create_window()

    def connect(self, ip, port, name):
        print(ip, port, name)

        s.connect((ip, port))  # host and code
        msg = s.recv(128)  # this is data amount received
        print(msg.decode(byte_type))  # this is a

        msg = s.recv(128)
        print(msg.decode(byte_type))

        s.send(bytes(name[:10], byte_type))  # confines username to shorter than 10
        t1 = threading.Thread(target=receive_input)  # create a thread to receive input
        t1.start()

    def create_window(self):
        self.text_area = QTextEdit()  # stuff (list)
        self.text_area.setFocusPolicy(Qt.NoFocus)
        self.message = QLineEdit()  # input region
        self.layout = QVBoxLayout()  # layout of the window object
        self.layout.addWidget(self.text_area)  # widget for output area
        self.layout.addWidget(self.message)  # widget for input area
        self.window = QWidget()  # the window
        self.window.setFixedHeight(500)
        self.window.setFixedWidth(800)
        self.window.setLayout(self.layout)  # set layout to box
        self.window.show()  # display the window

        # Signals:
        self.message.returnPressed.connect(send_message)  # if hit enter, send input


if __name__ == "__main__":
    app = QApplication()
    login = Login()
    login.show()
    app.exec_()
