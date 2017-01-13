# -*- coding: utf-8 -*-
import util

__author__ = 'chongxin'
import badWords

def checkHasBadWords(message):
    for word in badWords.badWords:
        if message.find(word) != -1:
            print("--------bad-------")
            return True
    return False

def te():
    rowValueMap = {}
    to_dbid =1
    # TODO： 验证玩家有效性



    mailType = 2
    title = "das"
    from_name ="chong"
    text ="text"
    time = util.getCurrentTime()
    attachment = "sd"
    state= 1
    extern_info= "adsdasd"


    sql = "insert into tbl_Mails(sm_to_dbid,sm_mail_type,sm_title,sm_from_name,sm_text,sm_time,sm_attachment,sm_state,sm_extern_info) " \
          "select '" + str(to_dbid) + "','"\
          +str(mailType) +"','"\
          +title+"','"\
          +from_name+"','"\
          +text +"','"\
          +str(util.getCurrentTime())+"','"\
          +attachment +"','"\
          +str(state)+"','"\
          +extern_info + \
          "' from dual where exists (select * from tbl_Avatar where id = " + str(to_dbid) +")"
    print(sql)
if __name__ == "__main__":
    colTupe = ("sm_UUID", "sm_itemID,sm_amount,sm_color")
    filterMap = {"sm_roleID": 2}
    sql = util.getSelectSql("tbl_ItemPieces", colTupe, filterMap)
    print(sql)