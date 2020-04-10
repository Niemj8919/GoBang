import socket
import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class Searcher(QThread):
    signal = pyqtSignal(str)
    success_signal = pyqtSignal(str)
    def __init__(self, skt, flag, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.skt = skt
        self.flag = flag
        if self.flag:
            self.method = 'search'
        else:
            self.method = 'gaming'
    
    def run(self):
        if self.flag:
            self.skt.send('search'.encode('utf-8'))
        while True:
            try:
                self.recv_data = self.skt.recv(1024)
                self.success_signal.emit(self.recv_data.decode('utf-8'))
                if self.flag: break
            except:
                self.signal.emit(self.method)