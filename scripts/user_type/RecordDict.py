# -*- coding: utf-8 -*-
import KBEngine
import GlobalConst
from KBEDebug import *

# 最多只支持26个字段，如果超过请自定义类型
class TRecordDict(dict):
    """
    """

    def __init__(self):
        """
        """
        list.__init__(self)

    def asDict(self):

        data ={}
        for i in range(len(self)):
            keyStr = str(chr(ord('a') + i))
            data[keyStr] = self[i]

        return data

    def createFromDict(self, dictData):
        keys = dictData.keys()
        keyList = sorted(keys)

        for k in keyList:
            self.append(dictData[k])
        # self.extend([dictData["DBID"], dictData["photoIndex"], dictData["name"], dictData["level"], dictData["vipLevel"], dictData["fightValue"], dictData["clubName"], dictData["onlineState"]])
        return self


class Record_ITEM_PICKLER:
    def __init__(self):
        pass

    def createObjFromDict(self, dct):
        return TRecord().createFromDict(dct)

    def getDictFromObj(self, obj):
        return obj.asDict()

    def isSameType(self, obj):
        return isinstance(obj, TRecord)


Record_info_inst = Record_ITEM_PICKLER()


class TRecordList(dict):
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
            DEBUG_MSG("-------------------------" + str(val))
            datas.append(val)

        return dct

    def createFromDict(self, dictData):
        for data in dictData["values"]:
            self[data[0]] = data
        return self


class REC_DICT_PICKLER:
    def __init__(self):
        pass

    def createObjFromDict(self, dct):
        return TRecordList().createFromDict(dct)

    def getDictFromObj(self, obj):
        return obj.asDict()

    def isSameType(self, obj):
        return isinstance(obj, TRecordList)


RecDict_inst = REC_DICT_PICKLER()
