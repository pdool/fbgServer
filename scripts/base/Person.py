# -*- coding: utf-8 -*-
__author__ = 'chongxin'
import KBEngine
import util

class Person(KBEngine.Base):
    def __init__(self):
        KBEngine.Base.__init__(self)
        KBEngine.globalData["Person"] = self

    def _onPersonSaved(self, result, rownum, error):
        print("success")

    def makeInsert(self):
        rowValue ={"sm_mail_type":1,"sm_title":'重新22'}
        whereValue = {"sm_mail_type":1,'id':'15'}
        sql = util.getUpdateSql("tbl_Person",rowValue,whereValue)
        # sql = "  insert into tbl_Person(sm_mail_type,sm_title) values('1',b'111')"
        KBEngine.executeRawDatabaseCommand(sql,self._onPersonSaved)





