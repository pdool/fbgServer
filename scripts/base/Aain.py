# -*- coding: utf-8 -*-
import datetime
from _ctypes import *

import util

class Person:
    def __init__(self):
        self.__funcMap = {
            1:self.func1
        }
        pass

    def dFunc(self,num):
        func = self.funcMap[num]
        func()
    def func1(self):
        print("111")




if __name__ == '__main__':
    s = "dasbn,c,d,"
    print(s[:-1])