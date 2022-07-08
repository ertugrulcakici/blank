import sys
from socket import socket
from threading import Thread

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from firebase_manager import FirebaseManager


class App(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.got_screen_size = False
        

        self.firebase_manager = FirebaseManager()
        connection_data = self.firebase_manager.get_tree("socket/watch_screen")
        ip, port = connection_data["ip"], connection_data["port"]
        soket = socket()
        soket.bind((ip, port))
        soket.listen(1)
        print("Dinleme başladı: ", ip, port)
        self.client, _ = soket.accept()


        self.image_label = QLabel(text="deneme")
        self.setCentralWidget(self.image_label)

        self.run()
        

    def run(self):
        while True:
            length = int(self.client.recv(10).decode())
            buff = b''
            while len(buff) != length:
                    buff += self.client.recv(length - len(buff))
            pixmap = QPixmap()
            pixmap.loadFromData(buff)
            self.image_label.setPixmap(pixmap)

            if not self.got_screen_size:
                self.setFixedSize(pixmap.width(), pixmap.height())
                self.got_screen_size = True
try:
    app = QApplication(sys.argv)
    main = App()
    main.show()
    sys.exit(app.exec_())
except Exception as e:
    print(e)
    input("Press Enter to continue...")
