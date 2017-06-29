# -*- coding: utf-8 -*-
import time
import datetime
import KBEDebug
import random
import sys
import os
def printStackTrace(info):
    retStr = ""
    curindex=0
    f = sys._getframe()
    f = f.f_back        # first frame is detailtrace, ignore it
    while hasattr(f, "f_code"):
        co = f.f_code
        retStr = "%s(%s:%s)->"%(os.path.basename(co.co_filename),
                  co.co_name,
                  f.f_lineno) + retStr
        f = f.f_back
    return retStr + info

# 获取当前时间 秒级时间戳
def getCurrentTime():
    timestamp = time.time()#返回浮点数
    return int(timestamp)
# （0,1 ]
def randFunc():
    seed = random.Random().random()
    if seed == 0.0:
        seed = 1.0
    return seed

# 返回[0,100]
def randInHundred():
    return random.randint(0,100)


# 字符串操作

def splitParam(origin, flag=','):
    return origin.split(flag)


    # 时间


##获取今天周几
def getWeekDay():
    return datetime.datetime.now().weekday() + 1

# 获取当前时间小时
def getNowHour():
    return datetime.datetime.now().hour

# print(getWeekDay())

## 等待到下个几分钟的秒数 min_interval <= 60
def getLeftSecsToNextMins(min_interval):
    if min_interval > 60:
        min_interval = 60
    sec_int = min_interval * 60
    now_secs = getCurrentTime() % 60
    left = sec_int - now_secs
    return left


# print(getLeftSecsToNextMins(1))

###获取当前时间到下一个hh:mi:ss的剩余秒数
def getLeftSecsToNextHMS(nh, nm, ns):
    now = datetime.datetime.now()
    s1 = now.hour * 3600 + now.minute * 60 + now.second
    s2 = nh * 3600 + nm * 60 + ns * 60
    delta_s = s2 - s1
    if delta_s < 0:
        delta_s += 86400
    return delta_s


# print(getLeftSecsToNextHMS(14,0,0))

###获取当前时间到本周末hh:mi:ss的剩余秒数
def getLeftSecsToWeekEndHMS(nh, nm, ns):
    now = datetime.datetime.now()
    weekDay = getWeekDay()
    delta_d = 7 - weekDay
    s1 = now.hour * 3600 + now.minute * 60 + now.second
    s2 = nh * 3600 + nm * 60 + ns * 60
    delta_s = s2 - s1
    if delta_d == 0:
        delta_s += 86400 * 7
    else:
        delta_s += 86400 * delta_d
    return delta_s




    # 获取本周一的时间


def getMondayOnCurWeek():
    week = datetime.datetime.now().weekday()
    tomorrow = datetime.datetime.replace(datetime.datetime.now() + datetime.timedelta(days=1), hour=0, minute=0,
                                         second=0)
    t = tomorrow - datetime.timedelta(days=(week + 1))  # 明天凌晨-周几
    timeStamp = int(time.mktime(t.timetuple()))
    return timeStamp


    # 这礼拜的周日是哪一天


def getSunDayOnCurWeek():
    week = datetime.datetime.now().weekday()
    tomorrow = datetime.datetime.replace(datetime.datetime.now() + datetime.timedelta(days=1), hour=0, minute=0,
                                         second=0)
    t = tomorrow + datetime.timedelta(days=(6 - week))  # 明天凌晨+剩余天数
    timeStamp = int(time.mktime(t.timetuple()))
    return timeStamp


# print(getLeftSecsToWeekEndHMS(0, 0, 0))

# 获取上次时间和现在时间的间隔
def getIntervalDayFromNow(pretime):
    prezerotime = datetime.datetime.replace(
        datetime.datetime.utcfromtimestamp(pretime) + datetime.timedelta(days=0, hours=8), hour=0, minute=0,
        second=0)  # 凌晨时间
    nowzerotime = datetime.datetime.replace(datetime.datetime.now() + datetime.timedelta(days=0), hour=0, minute=0,
                                            second=0)
    nprezerotime = int(time.mktime(prezerotime.timetuple()))
    nnowzerotime = int(time.mktime(nowzerotime.timetuple()))
    onedaytime = 24 * 60 * 60
    intervaltime = (nnowzerotime - nprezerotime) / onedaytime
    return int(intervaltime)


def getIntervalDayByDay(starttime, endtime):
    startzerotime = datetime.datetime.replace(
        datetime.datetime.utcfromtimestamp(starttime) + datetime.timedelta(days=0, hours=8), hour=0, minute=0,
        second=0)  # 凌晨时间
    endzerotime = datetime.datetime.replace(
        datetime.datetime.utcfromtimestamp(endtime) + datetime.timedelta(days=0, hours=8), hour=0, minute=0,
        second=0)  # 凌晨时间
    nstartzerotime = int(time.mktime(startzerotime.timetuple()))
    nendzerotime = int(time.mktime(endzerotime.timetuple()))
    onedaytime = 24 * 60 * 60
    intervaltime = (nendzerotime - nstartzerotime) / onedaytime
    return int(intervaltime)


    # 获取凌晨时间


def getDawnTime(pretime):
    t = datetime.datetime.replace(datetime.datetime.utcfromtimestamp(pretime) + datetime.timedelta(days=0, hours=8),
                                  hour=0, minute=0, second=0)  # 凌晨时间
    timeStamp = int(time.mktime(t.timetuple()))
    return timeStamp


    # 获取次日


def getNextDawnTime(pretime):
    t = datetime.datetime.replace(datetime.datetime.utcfromtimestamp(pretime) + datetime.timedelta(days=1, hours=8),
                                  hour=0, minute=0, second=0)  # 凌晨时间
    timeStamp = int(time.mktime(t.timetuple()))
    return timeStamp


"""
    获得插入语句
    tableName  表名
    rowValueMap 名值对 （列名：列值）
"""
def getInsertSql(tableName, rowValueMap,hasIndex = True):
    if rowValueMap is None:
        ERROR_MSG("you rowValueMap is None!")
        return
    indexStr = ""
    if hasIndex is True:
        indexStr = "sm_"
    rowStr = "("
    valueStr = "values("
    for k, v in rowValueMap.items():
        if v is not None:
            rowStr += indexStr + k + ","
            valueStr += "'" + str(v) + "'" + ","

    rowStr = rowStr[:-1]
    valueStr = valueStr[:-1]
    rowStr += ") "
    valueStr += ")"
    sql = """insert into """ + tableName + rowStr + valueStr + """;"""

    print("now run insert sql  " + sql)
    return sql


# 获得更新sql
def getUpdateSql(tableName, setValueMap, filterValueMap,hasIndex=True):
    if setValueMap is None:
        KBEDebug.ERROR_MSG("you setValueMap is None!")
        return
    indexStr = ""
    if hasIndex:
        indexStr = "sm_"
    setStr = ""
    whereStr = ""

    for k, v in setValueMap.items():
        setStr += "sm_"+ k + "='" + str(v) + "',"

    for k, v in filterValueMap.items():
        whereStr += "sm_"+ k + "='" + str(v) + "' and "

    setStr = setStr[:-1]
    if whereStr !="":
        whereStr = whereStr[:-4]

    sql = "update " + tableName + " set " + setStr + ' where '+ whereStr
    print("now run update sql  " + sql)
    return sql

# 刪除sql
def getDelSql(tableName,filterValueMap,hasIndex=True):
    indexStr = ""
    if hasIndex:
        indexStr = "sm_"
    whereStr = ""
    for k, v in filterValueMap.items():
        whereStr += indexStr+ k + " = '" + str(v) + "' and "

    if whereStr !="":
        whereStr = whereStr[:-4]
    sql = """ delete from """ + tableName +" where " + whereStr

    print("now run del sql  " + sql)
    return sql

def getSelectSql(tableName,colTuple=None,filterValueMap=None):

    colStr = ""
    whereStr = ""

    if colTuple is None:
        colStr ="*"
    else:
        for col in colTuple:
            colStr += col + ","
        colStr = colStr[:-1]
    if filterValueMap is not None:
        whereStr = " where "
        for k, v in filterValueMap.items():
            whereStr +=  k + "='" + str(v) + "' and "
        whereStr = whereStr[:-4]

    sql = "select "+colStr +" from "+tableName  + whereStr
    print("now run select sql  " + sql)

    return sql


def dbDeco(func):
    def __deco(result,rowNum,error):
        if error is not None:
            KBEDebug.ERROR_MSG(str(func) + "     error is  " + error)
        # 调用原方法，不打断流程
        func(result,rowNum,error)

    return __deco

# 打印出函数运行时间
def methodRunTime(func):
    def __deco(*args,**kwargs):

        b = getCurrentTime()
        result = func(*args,**kwargs)
        KBEDebug.ERROR_MSG(str(func) + "     run time is  " + str(getCurrentTime() - b))
        return result
    return __deco



