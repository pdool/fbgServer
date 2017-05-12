# -*- coding: utf-8 -*-

__author__ = 'chongxin'
import KBEngine
import util

Mail_max_count				= 100		# 最大邮件数


# --------------------------------------------------------------------------------------------
#          提取附件 直接切换到0
#          没提取已读 1
# --------------------------------------------------------------------------------------------
Mail_State_read = 0
Mail_State_Has_Open_Not_Get = 1
Mail_State_Not_Open = 2    # 未读未领取()


# --------------------------------------------------------------------------------------------
#
#
# --------------------------------------------------------------------------------------------



class Mails(KBEngine.Base):
    def __init__(self):
        KBEngine.Base.__init__(self)


    def sendMailToPlayer(self,mailInfo):
        mailType = mailInfo["mail_type"]
        title = mailInfo["title"]
        fromName = mailInfo["from_name"]
        to_dbid = mailInfo["to_dbid"]
        text =mailInfo["text"]
        time = util.getCurrentTime()
        attachment = mailInfo["attachment"]
        state = MailState.Unread
        extern_info = mailInfo["extern_info"]

        sql = util.getInsertSql("tbl_Mails",mailInfo)
    #     插入语句

    def getMailByType(self,playerDbid,mailType):
        pass

        # 查询语句

    # noinspection PyInterpreter
    def readMail(self,mailId):
        pass
#     更新状态
    def delMail(self,mailId):
        pass
#     删除语句

    def delAllMail(self,playerDbid):
        pass
#     删除语句

    def getAllAttachment(self,playerDbid):
        pass
#

