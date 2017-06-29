# -*- coding: utf-8 -*-
import time
import socket
import struct
import BabyTouchItemConfig
import gc
import initCardConfig
import util
from KBEDebug import *


class Account(KBEngine.Proxy):
    """
    账号实体
    客户端登陆到服务端后，服务端将自动创建这个实体，通过这个实体与客户端进行交互
    """
    def __init__(self):
        KBEngine.Proxy.__init__(self)
        self.activeAvatar = None
        self.relogin = time.time()

    """
    废弃
    """
    def reqAvatarList(self):
        """
        exposed.
        客户端请求查询角色列表
        """
        # DEBUG_MSG("Account[%i].reqAvatarList: size=%i." % (self.id, len(self.roleList)))
        # roleListDic = {'values': self.roleList}
        # # 调用客户端方法
        # self.client.onReqAvatarList(roleListDic)

    def reqCreateAvatar(self, job, name):
        """
        exposed.
        客户端请求创建一个角色
        """
        print("storing----------2")
        # if self.lastSelCharacter is not None:
        #     return
        # 判断是否重名

        if "kbe_bot_" in name:
            ERROR_MSG("kbe_bot_                                           " + name)

        colTuple=("id",)
        sql = util.getSelectSql("tbl_avatar",colTuple,filterValueMap={"sm_name":name})

        def queryResult(result, rownum, error):
            #         创建失败
            if result is None:
                return
            # 重名
            if len(result) >= 1:
                DEBUG_MSG("onCreateAvatarFail--------------------------------------------------")
                # self.client.onCreateAvatarFail()
                return

            otherConfig = initCardConfig.OtherConfig[1]
            bagSize = otherConfig["bagSize"]

            cardConfig = initCardConfig.InitCardConfig[job]
            initFomation = cardConfig["initFomation"]

            param = {
                "name"          : name,
                "job"           : job,
                "bagSize"       : bagSize,
                "formation"     : initFomation
            }
            avatar = KBEngine.createBaseLocally("Avatar", param)
            if avatar is not None:
                # avatar.name = name
                # avatar.job = job
                # avatar.bagSize = 200
                avatar.writeToDB(self._onAvatarSaved)

        KBEngine.executeRawDatabaseCommand(sql, queryResult)

        # DEBUG_MSG("Account[%i].reqCreateAvatar:%s. spaceUType=%i, spawnPos=%s.\n" % (self.id, name, avatar.cellData["spaceUType"], spaceData.get("spawnPos", (0,0,0))))

    def reqRemoveAvatar(self):
        """
        exposed.
        客户端请求删除一个角色
        """
        print(" call me baby")
        # del self.activeAvatar
        # self.lastSelCharacter =None




    #--------------------------------------------------------------------------------------------
    #                              Callbacks
    #--------------------------------------------------------------------------------------------
    def onEntitiesEnabled(self):
        """
        KBEngine method.
        该entity被正式激活为可使用， 此时entity已经建立了client对应实体， 可以在此创建它的
        cell部分。
        """
        # INFO_MSG("Account[%i]::onEntitiesEnabled:entities enable. mailbox:%s, clientType(%i), clientDatas=(%s), hasAvatar=%s, accountName=%s" % \
        #     (self.id, self.client, self.getClientType(), self.getClientDatas(), self.activeAvatar, self.__ACCOUNT_NAME__))

        self.lastClientIpAddr = socket.inet_ntoa(struct.pack('I', socket.htonl(self.clientAddr[0])))

        DEBUG_MSG("ip address ----------" + self.lastClientIpAddr)
        self.writeToDB()

        if self.lastSelCharacter != 0:
            avatar = KBEngine.createBaseAnywhereFromDBID("Avatar",self.lastSelCharacter,self.__onAvatarCreated)


    def __onAvatarCreated(self, baseRef, dbid, wasActive):
        """
                选择角色进入游戏时被调用
        """
        if wasActive:
            ERROR_MSG("Account::__onAvatarCreated:(%i): this character is in world now!" % (self.id))
            return
        if baseRef is None:
            ERROR_MSG("Account::__onAvatarCreated:(%i): the character you wanted to created is not exist!" % (self.id))
            return

        avatar = KBEngine.entities.get(baseRef.id)
        if avatar is None:
            ERROR_MSG("Account::__onAvatarCreated:(%i): when character was created, it died as well!" % (self.id))
            return

        if self.isDestroyed:
            ERROR_MSG("Account::__onAvatarCreated:(%i): i dead, will the destroy of Avatar!" % (self.id))
            avatar.destroySelf()
            return
        self.activeAvatar = avatar
        avatar.roleId = avatar.databaseID
        self.giveClientTo(avatar)
        avatar.accountEntity = self

    def onLogOnAttempt(self, ip, port, password):
        """
        KBEngine method.
        客户端登陆失败时会回调到这里
        """
        INFO_MSG("Account[%i]::onLogOnAttempt: ip=%s, port=%i, selfclient=%s" % (self.id, ip, port, self.client))
        """
        if self.activeAvatar != None:
            return KBEngine.LOG_ON_REJECT

        if ip == self.lastClientIpAddr and password == self.password:
            return KBEngine.LOG_ON_ACCEPT
        else:r
            return KBEngine.LOG_ON_REJECT
        """

        # 如果一个在线的账号被一个客户端登陆并且onLogOnAttempt返回允许
        # 那么会踢掉之前的客户端连接
        # 那么此时self.activeAvatar可能不为None， 常规的流程是销毁这个角色等新客户端上来重新选择角色进入
        if self.activeAvatar:
            self.activeAvatar.giveClientTo(self)
            self.relogin = time.time()
            self.activeAvatar.destroySelf()
            self.activeAvatar = None

        return KBEngine.LOG_ON_ACCEPT

    def onClientDeath(self):
        """
        KBEngine method.
        客户端对应实体已经销毁
        """
        if self.activeAvatar:
            self.activeAvatar.accountEntity = None
            self.activeAvatar = None

        # DEBUG_MSG("Account[%i].onClientDeath:" % self.id)
        self.destroy()


    def _onAvatarSaved(self, success, avatar):
        """
        新建角色写入数据库回调
        """
        # INFO_MSG('Account::_onAvatarSaved:(%i) create avatar state: %i, %s, %i' % (self.id, success, avatar.cellData["name"], avatar.databaseID))

        # 如果此时账号已经销毁， 角色已经无法被记录则我们清除这个角色
        if self.isDestroyed and avatar != None:
            avatar.destroy(True)
            return
        if success:
            avatar.onCreateRole()
            self.lastClientIpAddr = socket.inet_ntoa(struct.pack('I', socket.htonl(self.clientAddr[0])))
            self.lastSelCharacter = avatar.databaseID
            avatar.roleId = avatar.databaseID
            self.writeToDB()
            self.activeAvatar = avatar
            avatar.accountEntity = self
            self.giveClientTo(self.activeAvatar)

            cardConfig = initCardConfig.InitCardConfig[avatar.job]

            initRoleCardId = cardConfig["initRoleCardId"]
            initRoleCardIdPos = cardConfig["initRoleCardIdPos"]

            avatar.addCard(initRoleCardId,initRoleCardIdPos,1, 1)
            initCardIdList = cardConfig["initCardIdList"]
            initCardPosList = cardConfig["initCardPosList"]
            for index in range(len(initCardIdList)):
                cardId = initCardIdList[index]
                pos = initCardPosList[index]
                avatar.addCard(cardId,pos, 1,0)

            avatar.ballerRelationProp()

            self.createBaby(avatar)

        else:
            avatar.client.onCreateAvatarFail()


    def createBaby(self,avatar):

        param = {}
        baby = KBEngine.createBaseLocally("Baby",param)
        baby.roleID = avatar.databaseID
        baby.playerID = avatar.id
        def __createBabyCB(success, baby):
            avatar.babyDBID = baby.databaseID
            avatar.babyID = baby.id
            baby.closeTouch = BabyTouchItemConfig.BabyTouchItemConfig[102034]["times"]
            baby.putItemInfoInBaby(1,1)
            baby.putItemInfoInBaby(2,0)
            avatar.writeToDB()
            INFO_MSG("create Baby success  " + str(baby.databaseID))

        baby.writeToDB(__createBabyCB)

    def onDestroy( self ):

        refs = gc.get_referents(self)
        ERROR_MSG("  Account   onDestroy    " + refs.__str__())