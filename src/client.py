import socket
import pymysql

conn = pymysql.connect(host = "127.0.0.1", user = "root", password = "123456", db = "users", charset = "utf8")
cursor = conn.cursor()
info = []

cursor.execute("select * from info where name='a' and password='a'")
user_info = list(cursor.fetchall()[0])
info_str = user_info[0] + " " + str(user_info[2]) + " " + str(user_info[3])
info.append(info_str)

rival_info = info[0].split()

num = int(user_info[3])+1
cursor.execute("update info set lose=%s where name=%s", [str(num), user_info[0]])
conn.commit()

num_ = int(rival_info[1])+1
cursor.execute("update info set win=%s where name=%s", [str(num_), rival_info[0]])
conn.commit()

str = 'aaa'

str += '1'
print(str)