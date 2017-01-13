# -*- coding: utf-8 -*-
import util
from KBEDebug import *
from ErrorCode import ChatError
import chatConfig
from badWords import badWords

__author__ = 'chongxin'
__createTime__  = '2017年1月13日'
"""
    属性管理模块
"""

class PropMgrModule:

    def __init__(self):
        pass

    def onEntitiesEnabled(self):
        pass

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------
    def addPropValue(self,propName,value):
        # 特殊限制的特殊处理。暂时不做处理

        if hasattr(self,propName):
            DEBUG_MSG("-------addPropValue----------------------------" + propName +"----------"+ str(value))
            setattr(self,propName,value)

        pass
    # --------------------------------------------------------------------------------------------
    #                              服务器内部函数调用函数
    # --------------------------------------------------------------------------------------------

    # --------------------------------------------------------------------------------------------
    #                              工具函数调用函数
    # --------------------------------------------------------------------------------------------



class MessageInfoEnum:

    message = "message"
    photoIndex = "photoIndex"
    name = "name"
    level = "level"
    vipLevel = "vipLevel"
    sendTime = "sendTime"
    clubPosition = "clubPosition"























