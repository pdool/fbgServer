# -*- coding: utf-8 -*-
import datetime
from _ctypes import *
import ArenaReward
import pymysql
import util
import  guildShopConfig
import time
class Person:
    def __init__(self):
      pass


def funcDiamond(mapDict, dctData, chilidDict, data):
    dic = {}
    if data == None:
        return dic
    for pair in data.split(";"):
        if pair == "":
            continue
        id = int(pair.split(":")[0])
        content = str(pair.split(":")[1])
        dic[id] =  tuple([index for index in content.split(',') if index != ''])
    return dic
# 打印出函数运行时间
def methodRunTime(func):
    def __deco(*args,**kwargs):

        b = time.time()
        result = func(*args,**kwargs)
        print(str(func) + "     run time is  " + str(time.time() - b))
        return result
    return __deco

@methodRunTime
def testManyParam(a1,a2):
    print(a1 + a2)
    print(a2)




if __name__ == '__main__':
    # try:
    #     # 获取一个数据库连接，注意如果是UTF-8类型的，需要制定数据库
    #     conn = pymysql.connect(host='localhost', user='root', passwd='root', db='kbe', port=3306, charset='utf8')
    #     cur = conn.cursor()  # 获取一个游标
    #     cur.execute('select * from tbl_Card')
    #     data = cur.fetchall()
    #     for d in data:
    #         # 注意int类型需要使用str函数转义
    #         print(d.__str__())
    #
    #     cur.close()  # 关闭游标
    #     conn.close()  # 释放数据库资源
    # except  Exception:
    #     print("发生异常")

    # x = "xxxx"
    # y = "%i chongxin "
    # b = util.getCurrentTime()
    # for i in range(100000000):
    #     s = y%i
    #
    # print(util.getCurrentTime() - b)
    # y = "{0} chongxin"
    # b = util.getCurrentTime()
    # for i in range(100000000):
    #     s = y.format(i)
    #
    # print(util.getCurrentTime() - b)

    x  = 3
    y = 7

    z = x if x == 7 else y

    print(z)

















