import socket
import pymysql
import threading
import random

conn = pymysql.connect(host = "127.0.0.1", user = "root", password = "123456", db = "users", charset = "utf8")   #连接Mysql数据库

cursor = conn.cursor()
    
skt = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

skt.setblocking(False)


skt.bind(('127.0.0.1', 28170)) 


skt.listen(100)



def echo(client_skt, client_addr, socks, addr, info):
    global cursor
    while True:
        try:
            recv_data = client_skt.recv(1024)
            recv_data = recv_data.decode('utf-8')
            recv_data = recv_data.split()
        
            if recv_data[0] == "login":  #登录
                params = [recv_data[1], recv_data[2]]
                reply = cursor.execute("select * from info where name=%s and password=%s",params)
                if(reply):
                    user_info = list(cursor.fetchall()[0])
                    info_str = user_info[0] + " " + str(user_info[2]) + " " + str(user_info[3]) #返回用户名、赢、输
                    client_skt.send(info_str.encode('utf-8'))
                else:                                                           #用户名或密码错误
                    client_skt.send(str(reply).encode('utf-8'))
                    
            elif recv_data[0] == "logout":  #登出
                client_skt.close()
                break
                
            elif recv_data[0] == "register":  #注册
                params = [recv_data[1], recv_data[2]]
                if cursor.execute("select * from info where name=%s",params[0]): #用户名已经存在
                    client_skt.send(str('0').encode('utf-8'))
                elif recv_data[2] != recv_data[3]:                           #两次密码不一致
                    client_skt.send(str('2').encode('utf-8'))
                else:
                    cursor.execute("insert into info(name,password,win,lose) values(%s, %s,'0','0')", params)
                    conn.commit()
                    client_skt.send(str('1').encode('utf-8'))
                    
            elif recv_data[0] == "search":   #搜索对手
                flag = False
                if client_addr not in socks:
                    socks.append(client_addr)
                    addr.append(client_skt)
                    info.append(info_str)                    #加入搜索队列
                #client_skt.send(str(socks).encode('utf-8'))
                while True:
                    print("aaa")
                    for i in range(0, len(socks)):
                        if socks[i] != client_addr:                         #在搜索队列中匹配对手
                            flag = True
                            rival = addr[i]
                            rival_info = info[i].split()
                            if rival_info[0] > user_info[0]:
                                info_string = info_str + " 0"
                            else:
                                info_string = info_str + " 1"
                            rival.send(info_string.encode('utf-8'))
                            break
                        
                    if flag:
                        for i in range(0,len(addr)):
                            if addr[i] == rival:
                                addr.pop(i)
                                socks.pop(i)
                                info.pop(i)                               #对战双方退出搜索队列，开始游戏
                                break
                    try:
                        client_skt.recv(1024)
                        flag = True
                        for i in range(0, len(socks)):
                            if client_addr == socks[i]:
                                addr.pop(i)
                                socks.pop(i)
                                info.pop(i)
                    except BlockingIOError:
                        pass
                    
                    if flag:
                        break
                
            elif recv_data[0] == "stopsearching":  #停止搜索
                for i in range(0, len(socks)):
                    if client_addr == socks[i]:
                        addr.pop(i)
                        socks.pop(i)
                        info.pop(i)                               #退出搜索队列

            elif recv_data[0] == "escape" or recv_data[0] == "gameover":    #逃跑或是游戏结束
                if recv_data[0] == "escape":
                    rival.send('escaped'.encode('utf-8'))
                num = int(user_info[3])+1
                num_ = int(rival_info[1])+1
                r = cursor.execute("update info set lose=%s where name=%s", [str(num), user_info[0]])  #自己输+1
                print(r)
                cursor.execute("update info set win=%s where name=%s", [str(num_), rival_info[0]]) #对方赢+1
                conn.commit()

            elif recv_data[0] == "gaming":    #游戏中
                cord = recv_data[1] + " " + recv_data[2]                            #传输落子坐标
                rival.send(cord.encode('utf-8'))

            elif recv_data[0] == "restart":
                rival.send('restart'.encode('utf-8'))

            elif recv_data[0] == "quit":
                rival.send('quit'.encode('utf-8'))

            elif recv_data[0] == "message":
                msg = recv_data[0] + " " + recv_data[1]
                rival.send(msg.encode('utf-8'))

        except BlockingIOError:
            pass



if __name__ == '__main__':
    socks = []             #搜索队列             
    addr = []              #搜索队列中用户的IP地址、端口
    info = []              #搜索队列中用户的信息
    while True:
        try:
            client_skt, client_addr = skt.accept()
            print(client_skt,client_addr)
            p = threading.Thread(target=echo, args=(client_skt, client_addr, socks, addr, info))   #对于每一个用户的连接，启动一个线程
            p.start()
        except BlockingIOError:
            pass 
        
        #client_skt.close()
    skt.close()
