# -*- coding: utf-8 -*-
import datetime
from _ctypes import *
import ArenaReward
import util
import  guildShopConfig
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

def fbqn(x):
    if x == 0:
        return 0
    elif x == 1:
        return 1
    else:
        return  fbqn(x-1)+ fbqn(x-2)

if __name__ == '__main__':
    n = fbqn(4)
    print(n)












