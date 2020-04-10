from ai import searcher
from PyQt5 import QtCore
from PyQt5.QtCore import *

class AI(QtCore.QThread):
    finishSignal = QtCore.pyqtSignal(int, int)

    def __init__(self, board, parent=None):
        super(AI, self).__init__(parent)
        self.board = board

    def run(self):
        self.ai = searcher()
        self.ai.board = self.board
        score, x, y = self.ai.search(2, 2)
        self.finishSignal.emit(x, y)
