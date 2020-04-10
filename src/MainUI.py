WIDTH = 540
HEIGHT = 540
MARGIN = 22
GRID = (WIDTH - 2 * MARGIN) / (15 - 1)
PIECE = 34
EMPTY = 0
BLACK = 1
WHITE = 2

import time
from AIThread import AI
from SearchThread import Searcher
from Board import ChessBoard
import socket
import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import QSound

skt = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
skt.settimeout(1)


########################主页面#############################
class MainWindow(QWidget):
    def __init__(self, skt, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.skt = skt
        self.setWindowTitle('五子棋')

        self.hlayout = QHBoxLayout()
        
        self.resize(813, 591)
        self.layout = QVBoxLayout(self)
        self.palette1 = QPalette()  # 设置棋盘背景
        self.palette1.setBrush(QPalette.Background, QtGui.QBrush(QtGui.QPixmap('newback.jpg')))
        self.setPalette(self.palette1)


        self.label = QLabel(self)
        self.label.setText("Welcome!")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.button1 = QPushButton('单人模式')
        self.button1.resize(50,10)
        self.hlayout.addWidget(self.button1)

        
        self.button2 = QPushButton('联机模式')
        self.button2.resize(50,10)
        self.hlayout.addWidget(self.button2)

        self.button3 = QPushButton('退出')
        self.button3.resize(50,10)
        self.hlayout.addWidget(self.button3)

        self.layout.addLayout(self.hlayout)

        self.button1.clicked.connect(self.onButtonClick1)
        self.button2.clicked.connect(self.onButtonClick2)
        self.button3.clicked.connect(self.onButtonClick3)

    def onButtonClick1(self):
        self.hide()
        self.single = single_player()
        self.single.show()
    
    def onButtonClick2(self):
        self.hide()
        self.dialog = logindialog(self.skt)
        self.dialog.show()

    def onButtonClick3(self):
        self.skt.send('logout'.encode('utf-8'))
        QCoreApplication.instance().quit()

########################注册页面#############################
class logindialog(QDialog):
    def __init__(self, skt, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.skt = skt
        self.setWindowTitle('登录界面')
        self.resize(200, 200)
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        self.frame = QFrame(self)
        self.verticalLayout = QVBoxLayout(self.frame)

        self.lineEdit_account = QLineEdit()
        self.lineEdit_account.setPlaceholderText("请输入账号")
        self.verticalLayout.addWidget(self.lineEdit_account)

        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setPlaceholderText("请输入密码")
        self.verticalLayout.addWidget(self.lineEdit_password)

        self.pushButton_enter = QPushButton("确定")
        self.verticalLayout.addWidget(self.pushButton_enter)

        self.pushButton_register = QPushButton("注册新用户")
        self.verticalLayout.addWidget(self.pushButton_register)

        self.pushButton_back = QPushButton("返回")

        self.verticalLayout.addWidget(self.pushButton_back)

        self.pushButton_enter.clicked.connect(self.on_pushButton_enter_clicked)
        self.pushButton_register.clicked.connect(self.on_pushButton_register_clicked)
        self.pushButton_back.clicked.connect(self.on_pushButton_back_clicked)

    def on_pushButton_back_clicked(self):
        #self.skt.close()

        self.close()
        self.mainwindow = MainWindow(skt)
        self.mainwindow.show()

    def on_pushButton_register_clicked(self):
        self.close()
        self.dialog = registerdialog(skt)
        self.dialog.show()

    def on_pushButton_enter_clicked(self):

        self.data = "login " + self.lineEdit_account.text() + " " +self.lineEdit_password.text()
        self.skt.send(self.data.encode("utf-8"))
        self.recv_data = self.skt.recv(1024)

        if self.recv_data.decode('utf-8') == '0':
            QMessageBox.information(self, '提示', '登录失败：用户名或密码错误')
        else:
            self.recv_data = self.recv_data.decode('utf-8')
            self.recv_data = self.recv_data.split()
            self.online = online_hall(skt, self.recv_data)
            self.online.show()
            self.close()

########################在线游戏大厅#############################
class online_hall(QWidget):
    def __init__(self, skt, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.skt = skt
        self.data = data

        self.thread = Searcher(skt, 1)
        self.thread.signal.connect(self.load)
        self.thread.success_signal.connect(self.game_start)

        self.palette1 = QPalette()  # 设置棋盘背景
        self.palette1.setBrush(QPalette.Background, QtGui.QBrush(QtGui.QPixmap('newback.jpg')))
        self.setPalette(self.palette1)

        self.name = str(self.data[0])
        self.wins = str(self.data[1])
        self.loses = str(self.data[2])

        self.setWindowTitle('游戏大厅')
        self.resize(813, 591)

        #self.layout = QGridLayout(self)

        self.table1 = QPushButton(self)
        self.table1.setText("开始匹配")
        self.table1.move(100,100)
        self.table1.clicked.connect(self.select_table)

        self.table3 = QPushButton(self)
        self.table3.setText("取消匹配")
        self.table3.move(100,100)
        self.table3.hide()
        self.table3.clicked.connect(self.cancel_table)


        self.table2 = QPushButton(self)
        self.table2.setText("返回")
        self.table2.move(100,450)
        self.table2.clicked.connect(self.exit)

        self.label1 = QLabel(self)
        self.label1.setText("用户名：" + self.name + "\n胜场：" + self.wins + "\n输场：" + self.loses)
        self.label1.move(600,100)

        self.label2 = QLabel(self)
        self.label2.setText("搜索对手中。。。")
        self.label2.move(100,200)
        self.label2.hide()

    def cancel_table(self):
        self.thread.terminate()
        self.skt.send('stopsearching'.encode('utf-8'))
        self.table3.hide()
        self.table2.show()
        self.label2.hide()

    def load(self, text):
        print(text)

    def game_start(self, data):
        self.thread.terminate()
        self.close()
        data = data.split()
        print(data)
        self.gamer = multi_player(skt, data, self.data)
        self.gamer.show()

    def select_table(self):
        self.thread.start()
        self.table2.hide()
        self.table3.show()
        self.label2.show()

    def exit(self):
        self.close()
        self.mainwindow = MainWindow(skt)
        self.mainwindow.show()

########################注册页面#############################
class registerdialog(QDialog):
    def __init__(self, skt, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.skt = skt
        self.setWindowTitle('注册界面')
        self.resize(200, 200)
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        self.frame = QFrame(self)
        self.verticalLayout = QVBoxLayout(self.frame)

        self.lineEdit_account = QLineEdit()
        self.lineEdit_account.setPlaceholderText("请输入账号")
        self.verticalLayout.addWidget(self.lineEdit_account)

        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setPlaceholderText("请输入密码")
        self.verticalLayout.addWidget(self.lineEdit_password)

        self.lineEdit_password_confirm = QLineEdit()
        self.lineEdit_password_confirm.setPlaceholderText("请再次输入密码")
        self.verticalLayout.addWidget(self.lineEdit_password_confirm)

        self.pushButton_enter = QPushButton("确定")
        self.verticalLayout.addWidget(self.pushButton_enter)

        self.pushButton_back = QPushButton("返回")
        self.verticalLayout.addWidget(self.pushButton_back)

        self.pushButton_enter.clicked.connect(self.on_pushButton_enter_clicked)
        self.pushButton_back.clicked.connect(self.on_pushButton_back_clicked)

    def on_pushButton_back_clicked(self):

        self.close()
        self.dialog = logindialog(skt)
        self.dialog.show()

    def on_pushButton_enter_clicked(self):

        self.data = "register " + self.lineEdit_account.text() + " " +self.lineEdit_password.text()+ " " + self.lineEdit_password_confirm.text()
        self.skt.send(self.data.encode("utf-8"))
        self.recv_data = self.skt.recv(1024)

        if self.recv_data.decode('utf-8') == '1':
            QMessageBox.information(self, '提示', '注册成功')
            self.login = logindialog(skt)
            self.login.show()
            self.close()
        elif self.recv_data.decode('utf-8') == '2':
            QMessageBox.information(self, '提示', '注册失败：两次输入的密码不一致')
        else:
            QMessageBox.information(self, '提示', '注册失败：用户名已存在')

########################单人游戏页面#############################
class single_player(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.chessboard = ChessBoard()  # 棋盘类
        self.palette1 = QPalette()  # 设置棋盘背景
        self.palette1.setBrush(QPalette.Background, QtGui.QBrush(QtGui.QPixmap('new board.jpg')))
        self.setPalette(self.palette1)
        # self.setStyleSheet("board-image:url(img/chessboard.jpg)")  # 不知道这为什么不行
        self.setCursor(Qt.PointingHandCursor)  # 鼠标变成手指形状
        self.sound_piece = QSound("luozi.wav")  # 加载落子音效
        self.sound_win = QSound("win.wav")  # 加载胜利音效
        self.sound_defeated = QSound("defeated.wav")  # 加载失败音效
        self.thread = Searcher(skt, 0)
        self.resize(813, 591)  # 固定大小 540*540
        #self.setMinimumSize(QtCore.QSize(WIDTH, HEIGHT))
        #self.setMaximumSize(QtCore.QSize(WIDTH, HEIGHT))

        self.setWindowTitle("单人模式")  
        self.setWindowIcon(QIcon('black.png'))  

        self.pushButton_back = QPushButton(self)
        self.pushButton_back.setText("退出游戏")
        self.pushButton_back.move(10,550)
        self.pushButton_back.clicked.connect(self.on_pushButton_back_clicked)


        self.black = QPixmap('black.png')
        self.white = QPixmap('white.png')

        self.piece_now = BLACK  
        self.my_turn = True  
        self.step = 0  
        self.x, self.y = 1000, 1000

#        self.mouse_point = LaBel(self)  
#       self.mouse_point.setScaledContents(True)
#       self.mouse_point.setPixmap(self.black)  
#        self.mouse_point.setGeometry(270, 270, PIECE, PIECE)
        self.pieces = [QLabel(self) for i in range(225)]  
        for piece in self.pieces:
            piece.setVisible(True)  
            piece.setScaledContents(True)  

#        self.mouse_point.raise_()  
        self.ai_down = True  

#        self.setMouseTracking(True)
        self.show()

    def on_pushButton_back_clicked(self):
        self.close()

    def paintEvent(self, event): 
        self.qp = QPainter()
        self.qp.begin(self)
        self.drawLines(self.qp)
        self.qp.end()

    #def mouseMoveEvent(self, e):
        # self.lb1.setText(str(e.x()) + ' ' + str(e.y()))
    #    self.mouse_point.move(e.x() - 16, e.y() - 16)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and self.ai_down == True:
            x, y = e.x(), e.y()  
            i, j = self.coordinate_transform_pixel2map(x, y)  
            if not i is None and not j is None:  
                if self.chessboard.get_xy_on_logic_state(i, j) == EMPTY: 
                    self.draw(i, j)
                    self.ai_down = False
                    board = self.chessboard.board()
                    self.AI = AI(board)
                    self.AI.finishSignal.connect(self.AI_draw)
                    self.AI.start()

    def AI_draw(self, i, j):
        if self.step != 0:
            self.draw(i, j)
            self.x, self.y = self.coordinate_transform_map2pixel(i, j)
        self.ai_down = True
        self.update()

    def draw(self, i, j):
        x, y = self.coordinate_transform_map2pixel(i, j)

        if self.piece_now == BLACK:
            self.pieces[self.step].setPixmap(self.black)
            self.piece_now = WHITE
            self.chessboard.draw_xy(i, j, BLACK)
        else:
            self.pieces[self.step].setPixmap(self.white)
            self.piece_now = BLACK
            self.chessboard.draw_xy(i, j, WHITE)

        self.pieces[self.step].setGeometry(x, y, PIECE, PIECE)
        self.sound_piece.play() 
        self.step += 1

        self.winner = self.chessboard.anyone_win(i, j)
        if self.winner != EMPTY:
           # self.mouse_point.clear()
            self.gameover(self.winner)

    def drawLines(self, qp): 
        if self.step != 0:
            pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawLine(self.x - 5, self.y - 5, self.x + 3, self.y + 3)
            qp.drawLine(self.x + 3, self.y, self.x + 3, self.y + 3)
            qp.drawLine(self.x, self.y + 3, self.x + 3, self.y + 3)

    def coordinate_transform_map2pixel(self, i, j):
        return MARGIN + j * GRID - PIECE / 2, MARGIN + i * GRID - PIECE / 2

    def coordinate_transform_pixel2map(self, x, y):
        i, j = int(round((y - MARGIN) / GRID)), int(round((x - MARGIN) / GRID))
        if i < 0 or i >= 15 or j < 0 or j >= 15:
            return None, None
        else:
            return i, j

    def gameover(self, winner):
        if winner == BLACK:
            self.sound_win.play()
            reply = QMessageBox.question(self, '你赢了!', '开始新的一局?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        else:
            self.sound_defeated.play()
            reply = QMessageBox.question(self, '你输了!', '开始新的一局?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:  # 复位
            self.piece_now = BLACK
           # self.mouse_point.setPixmap(self.black)
            self.step = 0
            for piece in self.pieces:
                piece.clear()
            self.chessboard.reset()
            self.update()
        else:
            self.close()

########################多人游戏页面#############################
class multi_player(single_player):
    def __init__(self, skt, rival_data , self_data):
        self.skt = skt
        super().__init__()
        self.rival_data = rival_data
        self.self_data = self_data

        self.rival_name = str(self.rival_data[0])
        self.rival_wins = int(self.rival_data[1])
        self.rival_loses = int(self.rival_data[2])
        
        self.my_name = str(self.self_data[0])
        self.my_wins = int(self.self_data[1])
        self.my_loses = int(self.self_data[2])

        self.rival_confirm = True
        self.rival_quit = False
        if self.rival_data[3] == "1":
            self.my_color = "黑"
            self.rival_color = "白"
        else:
            self.my_color = "白"
            self.rival_color = "黑"
            self.ai_down = False


        
        self.label1 = QLabel(self)
        self.label1.move(600,50)
        
        self.label2 = QLabel(self)
        self.label2.move(600,500)
        
        self.set_info()
        self.label1.show()
        self.label2.show()

        self.thread.success_signal.connect(self.analysis)
        self.thread.signal.connect(self.load)
        self.thread.start()

        self.label3 = QLabel(self)
        self.switch()
        

        self.label4 = QLabel(self)
        self.label4.setText("等待对手确认")
        self.label4.move(400,400)
        self.label4.hide()

        self.lineEdit_message = QLineEdit(self)
        self.lineEdit_message.move(120,550)
        self.lineEdit_message.show()

        self.send_button = QPushButton(self)
        self.send_button.setText("发送")
        self.send_button.move(300,550)
        self.send_button.show()
        self.send_button.clicked.connect(self.send_message)

        self.browser = QTextBrowser(self)
        self.browser.move(580,120)
        self.browser.show()
    def send_message(self):
        msg = "message " + self.my_name + ":" + self.lineEdit_message.text()
        self.browser.append(self.my_name + ":" + self.lineEdit_message.text())
        self.lineEdit_message.clear()
        self.skt.send(msg.encode('utf-8'))

    def set_info(self):
        self.label1.setText('对手：'+self.rival_name+'\n赢：'+str(self.rival_wins)+'\n输：'+str(self.rival_loses))
        self.label2.setText('我：'+self.my_name+'\n赢：'+str(self.my_wins)+'\n输：'+str(self.my_loses))

    def switch(self):
        print(self.ai_down)
        if self.ai_down == True:
            self.label3.move(600,450)
        else:
            self.label3.move(600,150)
        if self.piece_now == BLACK:
            self.label3.setText("下棋：黑")
        else:
            self.label3.setText("下棋：白")
        self.label3.show()

    def load(self, data):
        print(data)


    def draw(self, i, j, flag):
        x, y = self.coordinate_transform_map2pixel(i, j)

        if self.piece_now == BLACK:
            self.pieces[self.step].setPixmap(self.black)
            self.piece_now = WHITE
            self.chessboard.draw_xy(i, j, BLACK)
        else:
            self.pieces[self.step].setPixmap(self.white)
            self.piece_now = BLACK
            self.chessboard.draw_xy(i, j, WHITE)

        self.pieces[self.step].setGeometry(x, y, PIECE, PIECE)
        self.sound_piece.play() 
        self.step += 1

        if flag:
            cord = "gaming " + str(i) + " " + str(j)
            self.skt.send(cord.encode('utf-8'))
            self.ai_down = False
        else:
            self.ai_down = True
        self.switch()    
        self.winner = self.chessboard.anyone_win(i, j) 
        if self.winner != EMPTY:
            if not flag:
                self.skt.send('gameover'.encode('utf-8'))
            self.gameover(self.winner)



    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and self.ai_down == True and self.rival_confirm == True:
            x, y = e.x(), e.y()  
            i, j = self.coordinate_transform_pixel2map(x, y)  
            if not i is None and not j is None:  
                if self.chessboard.get_xy_on_logic_state(i, j) == EMPTY: 
                    self.draw(i, j, 1)


    def analysis(self, data):
        data = data.split()
        if data[0] == 'escaped':
            self.thread.terminate()
            QMessageBox.information(self, '提示', '对方已逃跑！')
            #self.self_data[1] += 1
            self.my_wins += 1
            self.close()
            self.hall = online_hall(skt, [self.my_name, self.my_wins, self.my_loses])
            self.hall.show()
        elif data[0] == "restart":
            self.label4.hide()
            self.rival_confirm = True
        elif data[0] == "quit":
            self.thread.terminate()
            QMessageBox.information(self, '提示', '对方已离开！')
            self.rival_quit = True
            self.close()
            self.hall = online_hall(skt, [self.my_name, self.my_wins, self.my_loses])
            self.hall.show()
        elif data[0] == "message":
            self.browser.append(data[1])
        else:
            self.draw(int(data[0]), int(data[1]), 0)
            
    def on_pushButton_back_clicked(self):
        reply = QMessageBox.question(self, '警告', '你确定要逃跑吗?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.skt.send('escape'.encode('utf-8'))
            self.thread.terminate()
            self.my_loses += 1
            self.close() 
            self.hall = online_hall(skt, [self.my_name, self.my_wins, self.my_loses])
            self.hall.show()
        else:
            return

    def gameover(self, winner):
        self.rival_confirm = False
        self.label4.show()
        if (winner == BLACK and self.my_color == "黑") or (winner == WHITE and self.my_color == "白"):
            self.my_wins += 1
            self.rival_loses += 1
            self.set_info()
        else:
            self.my_loses += 1
            self.rival_wins += 1
            self.set_info()
            
        if winner == BLACK:
            self.sound_win.play()
            reply = QMessageBox.question(self, '黑棋获胜!', '开始新的一局?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        else:
            self.sound_win.play()
            reply = QMessageBox.question(self, '白棋获胜!', '开始新的一局?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:  # 复位
            self.skt.send('restart'.encode('utf-8'))
            self.piece_now = BLACK
           # self.mouse_point.setPixmap(self.black)

            self.step = 0
            for piece in self.pieces:
                piece.clear()
            self.chessboard.reset()

            if self.my_color == "黑":
                self.ai_down == True
            else:
                self.ai_down == False
            print(self.ai_down)
        else:
            self.thread.terminate()
            if not self.rival_quit:
                self.skt.send('quit'.encode('utf-8'))
            self.close()
            self.hall = online_hall(skt, [self.my_name, self.my_wins, self.my_loses])
            self.hall.show()
        
########################服务器繁忙页面#############################
class server_busy(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(300,300)
        self.setWindowTitle("error")
        self.sub_layout = QHBoxLayout()
        self.main_layout = QVBoxLayout(self)

        self.button_single = QPushButton(self)
        self.button_single.setText("单人游戏")
        self.sub_layout.addWidget(self.button_single)

        self.button_exit = QPushButton(self)
        self.button_exit.setText("退出")
        self.sub_layout.addWidget(self.button_exit)
        
        self.label = QLabel(self)
        self.label.setText("抱歉，当前服务器繁忙，您可以选择进行单人游戏")
        self.main_layout.addWidget(self.label)

        self.main_layout.addLayout(self.sub_layout)

        self.button_exit.clicked.connect(self.on_button_exit_clicked)
        self.button_single.clicked.connect(self.on_button_single_clicked)

    def on_button_exit_clicked(self):
        self.close()

    def on_button_single_clicked(self):
        self.play = single_player()
        self.play.show()
        self.close()


if __name__ == "__main__":
    try:
        skt.connect(('127.0.0.1', 28170))
        #skt.connect(('127.0.0.1', 37777)) 
        app = QApplication(sys.argv)
        the_window = MainWindow(skt)
        the_window.show()
        sys.exit(app.exec_())
    except:
        print("server is busy")
        app = QApplication(sys.argv)
        the_window = server_busy()
        the_window.show()
        sys.exit(app.exec_())
    
