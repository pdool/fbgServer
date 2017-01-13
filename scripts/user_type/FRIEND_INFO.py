# -*- coding: utf-8 -*-
import KBEngine
import GlobalConst
from KBEDebug import *


class TFriendInfo(list):
    """
    """

    def __init__(self):
        """
        """
        list.__init__(self)

    def asDict(self):
        data = {
            "DBID"                 : self[0],
            "photoIndex"          : self[1],
            "name"                 : self[2],
            "level"                : self[3],
            "vipLevel"             : self[4],
            "fightValue"           : self[5],
            "clubName"             : self[6],
            "onlineState"          : self[7],
        }

        return data

    def createFromDict(self, dictData):
        self.extend([dictData["DBID"], dictData["photoIndex"], dictData["name"], dictData["level"], dictData["vipLevel"], dictData["fightValue"], dictData["clubName"], dictData["onlineState"]])
        return self


class Friend_INFO_PICKLER:
    def __init__(self):
        pass

    def createObjFromDict(self, dct):
        return TFriendInfo().createFromDict(dct)

    def getDictFromObj(self, obj):
        return obj.asDict()

    def isSameType(self, obj):
        return isinstance(obj, TFriendInfo)


Friend_info_inst = Friend_INFO_PICKLER()


class TFriendInfoList(dict):
    """
    """

    def __init__(self):
        """
        """
        dict.__init__(self)

    def asDict(self):
        datas = []
        dct = {"values": datas}

        for key, val in self.items():
            datas.append(val)

        return dct

    def createFromDict(self, dictData):
        for data in dictData["values"]:
            self[data[0]] = data
        return self


class FRIEND_INFO_LIST_PICKLER:
    def __init__(self):
        pass

    def createObjFromDict(self, dct):
        return TFriendInfoList().createFromDict(dct)

    def getDictFromObj(self, obj):
        return obj.asDict()

    def isSameType(self, obj):
        return isinstance(obj, TFriendInfoList)


Friend_info_list_inst = FRIEND_INFO_LIST_PICKLER()
