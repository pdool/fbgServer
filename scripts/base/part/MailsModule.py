# -*- coding: utf-8 -*-
import KBEngine
import Mails
import util
from KBEDebug import DEBUG_MSG
# 不需要使用def,继承就可以使用，def可以用来生成数据库的表
# 如何使用回调
__author__ = 'chongxin'
"""
意识模块
"""
class MailsModule:
    def __init__(self):
        self.mails = []

    def initMail(self):

        filterMap = {"sm_to_dbid": self.databaseID}
        sql = util.getSelectSql("tbl_Mails", filterValueMap=filterMap)

        @util.dbDeco
        def onMailsLoadCB( result, rownum, error):
            """
            加载邮件
            """
            if result is None:
                return

            for i in range(len(result)):
                mail = {}
                mail["mail_type"] = int(result[i][3])
                mail["title"] = result[i][4].decode('utf-8')
                mail["from_name"] = result[i][5].decode('utf-8')
                mail["text"] = result[i][6].decode('utf-8')
                mail["time"] = int(result[i][7])
                mail["attachment"] = result[i][8].decode('utf-8')
                mail["state"] = int(result[i][9])
                mail["extern_info"] = result[i][10].decode('utf-8')

                self.mails.insert(i, mail)

            DEBUG_MSG("mails load complete!")
        KBEngine.executeRawDatabaseCommand(sql, onMailsLoadCB)

    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------
    def sendMail(self, to_dbid, mailType, title, text, attachment=None, extern_info=None):
        rowValueMap = {}
        rowValueMap["to_dbid"] = to_dbid
        rowValueMap["mail_type"] = mailType
        rowValueMap["title"] = title
        rowValueMap["from_name"] = self.name
        rowValueMap["text"] = text
        rowValueMap["time"] = util.getCurrentTime()
        rowValueMap["attachment"] = attachment
        rowValueMap["state"] = Mails.Mail_State_Not_Open
        rowValueMap["extern_info"] = extern_info

        sql = "insert into tbl_Mails(sm_to_dbid,sm_mail_type,sm_title,sm_from_name,sm_text,sm_time,sm_attachment,sm_state,sm_extern_info) " \
          "select '" + str(to_dbid) + "','"\
          +str(mailType) +"','"\
          +title+"','"\
          +self.name+"','"\
          +text +"','"\
          +str(util.getCurrentTime())+"','"\
          +attachment +"','"\
          +str(Mails.Mail_State_Not_Open)+"','"\
          +extern_info + \
          "' from dual where exists (select * from tbl_Avatar where id = " + str(to_dbid) +")"

        DEBUG_MSG("sendMail             " + sql)

        @util.dbDeco
        def onMailsSaveCB(result, rownum, error):

            if rownum == 1:
                del rowValueMap["to_dbid"]
                KBEngine.globalData["PlayerMgr"].onCmdByDBID(self.databaseID, "recNewMail", rowValueMap)
                # self.recNewMail(mailType, self.name, rowValueMap["time"], title, text, attachment, extern_info)
                # 通知另外一个人
                self.client.onOperateSuc("sendMail")
            else:

                DEBUG_MSG("----------sendMail 茶如失败-------------------------")





        KBEngine.executeRawDatabaseCommand(sql, onMailsSaveCB)

    #     发送成功

    # 获取邮件
    def getMail(self):
        mails = {}
        mails["values"] = self.mails


        self.client.onGetMails(mails)


    def readMail(self, mailTime):
        findKey = -1
        mailsCount = len(self.mails)

        state = Mails.Mail_State_read

        @util.dbDeco
        def updateSucCB(result, rownum, error):
            if findKey != -1:
                self.mails[findKey]["state"] = state

                self.client.onOperateSuc("readMail")


        for i in range(mailsCount):
            mail = self.mails[i]

            if mail["time"] == mailTime:
                if mail["state"] != Mails.Mail_State_Not_Open:
                    return
                findKey = i
                if mail["attachment"] != "":
                    state = Mails.Mail_State_Has_Open_Not_Get

                setValueMap = {"state": state}
                filterValueMap = {"to_dbid": self.databaseID, "time": mailTime}
                sql = util.getUpdateSql("tbl_Mails", setValueMap, filterValueMap)
                KBEngine.executeRawDatabaseCommand(sql, updateSucCB)

                break

    def delAllMailByType(self, mailType):
        @util.dbDeco
        def delSucCB(result, rownum, error):
            for i in range(len(self.mails) - 1, -1, -1):
                if self.mails[i]["state"] == Mails.Mail_State_read:
                    del self.mails[i]
            self.getMail()

        filterValueMap = {"to_dbid": self.databaseID, "state": Mails.Mail_State_read}
        sql = util.getDelSql("tbl_Mails", filterValueMap)
        KBEngine.executeRawDatabaseCommand(sql, delSucCB)

    def delMail(self, mailTime):
        @util.dbDeco
        def delSucCB(result, rownum, error):
            for i in range(len(self.mails)):
                if self.mails[i]["time"] == mailTime:
                    del self.mails[i]
                    break

        filterValueMap = {"to_dbid": self.databaseID, "time": mailTime}
        sql = util.getDelSql("tbl_Mails", filterValueMap)
        KBEngine.executeRawDatabaseCommand(sql, delSucCB)

    def sayHello(self):
        DEBUG_MSG(" wo shi hello")

    # --------------------------------------------------------------------------------------------
    #                              服务器内部调用函数
    # --------------------------------------------------------------------------------------------
    # def isPlayerExist(self,argsDict):
    #     isExist = argsDict["playerExist"]
    #     if isExist == 1:
    #
    #     else:




    def recNewMail(self, mail):
        # mail = {}
        # mail["mail_type"] = mailType
        # mail["title"] = title
        # mail["from_name"] = from_name
        # mail["text"] = text
        # mail["time"] = time
        # mail["attachment"] = attachment
        # mail["state"] = Mails.Mail_State_Not_Open
        # mail["extern_info"] = extern_info

        DEBUG_MSG("recNewMail--------------------" + mail["title"])
        self.mails.append(mail)
    # --------------------------------------------------------------------------------------------
    #                              回调函数调用函数
    # --------------------------------------------------------------------------------------------


    # --------------------------------------------------------------------------------------------
    #                              工具函数调用函数
    # --------------------------------------------------------------------------------------------

    def callMeBaby(self):
        print("baby iiiiiiii")

