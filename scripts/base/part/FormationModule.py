# -*- coding: utf-8 -*-
import datetime
import traceback

import TimerDefine
import ballerRelateConfig
import benchOpenConfig
import formationConfig
import formationSysStrongConfig
import formationSystemConfig
from BagConfig import BagConfig
from ErrorCode import CardMgrModuleError
from benchConfig import BenchConfig
from itemsConfig import itemsIndex
from KBEDebug import *
"""
阵型模块
__author__ = 'wangl'
__createTime__  = '2017年4月1日'
"""
class FormationModule:

    def __init__(self):
        self.formationIDList=[]

        self.initFormationSys()
        self.fomationPropContainer = {}
        self.relatPropContainer={}

        pass

    def onEntitiesEnabled(self):
        # 球员羁绊属性
        self.relatPropContainer={}

        # 阵型系统属性加成
        self.fomationPropContainer={}

        # self.ballerRelationProp()

        self.initFormationSysProp()

        self.fomationFight()

        # self.onClientForamtAndRelateProp()

        pass


    # --------------------------------------------------------------------------------------------
    #                              客户端调用函数
    # --------------------------------------------------------------------------------------------

    #客户端请求阵型和羁绊属性
    def onClientForamtAndRelateProp(self):
        for id, value in  self.relatPropContainer.items():
            self.client.getRelateProp(id, value)

        for id, value in self.fomationPropContainer.items():
            self.client.getFormationProp(id, value)

        pass


    # 球员羁绊属性处理
    def ballerRelationProp(self):

        self.relatPropContainer = {}

        # ERROR_MSG("--FormationRelatPropinTeamcardIDList--"+str(len(self.inTeamcardIDList)))

        for inTeamCardId in self.inTeamcardIDList:

            card = KBEngine.entities.get(inTeamCardId)

            cardConfigID = card.configID

            # ERROR_MSG("==cardConfigID=="+str(cardConfigID))

            if cardConfigID not in  ballerRelateConfig.BallerRelateConfig:
                continue

            # ERROR_MSG("==relatePlayerID=="+str(cardConfigID))
            relatInfo = ballerRelateConfig.BallerRelateConfig[cardConfigID]

            relateBaller= relatInfo["relateBaller"]

            propList = []
            for i in range(len(relateBaller)):

                relate = relateBaller[i]
                # ERROR_MSG("==relate==" + str(relate))
                ballerArr = str(relate).split(",")
                isHas = 1
                # 羁绊球员是否上阵和在替补席
                for ballerId in ballerArr :

                    if int(ballerId) <=0 :
                        continue
                    isExit = self.relateBallerIsExit(int(ballerId))
                    if isExit == 0 :
                        isHas = 0
                        break

                if isHas == 0 :
                    continue

                propKey = "prop"+str(i+1)
                propValue = relatInfo[propKey]
                for name ,value in propValue.items():
                    val = {}
                    val[RelatePropKey.propName] = name
                    val[RelatePropKey.value] = value

                # ERROR_MSG("--propKey--"+propKey)
                propList.append(val)

            self.relatPropContainer[inTeamCardId]  = propList
            card.calcFightValue()
            self.client.getRelateProp(inTeamCardId,card.fightValue, propList)

        pass

    # 羁绊球员是否存在
    def relateBallerIsExit(self, configID):

        isExit = 0

        for id in self.cardIDList:
            cardInfo = KBEngine.entities.get(id)
            if cardInfo.configID == int(configID):
                if cardInfo.inTeam == 1 or cardInfo.bench == 1:
                    isExit = 1
                    return isExit

        return isExit


    # 初始化替补席数量
    def initBench(self):
        benchInfo = BenchConfig[1]
        self.benchSize = benchInfo["defaultOpen"]
        pass


    # 初始化玩家开放阵型系统
    def initFormationSys(self):

        if len(self.formationSystem) > 0:
            return

        for id,sysInfo in formationSystemConfig.FormationSystemConfig.items():

            INFO_MSG("----FormationSysId-----" + str(id))

            value = {}
            value["id"] = id
            value["active"] = 0
            value["strongLevel"] = 0
            if sysInfo["needLevel"] <= self.level:
                value["open"] = 1
            else:
                value["open"] = 0
            # ERROR_MSG("---formationSysOpen---" + str(value["open"]))


            self.formationSystem.append(value)

        pass


    # 获取阵型系统信息
    def onClientFormationSystem(self):

       for sysInfo in self.formationSystem:

           sysId = sysInfo["id"]
           formationSys = formationSystemConfig.FormationSystemConfig[sysId]

           if self.level >= formationSys["needLevel"] :
               sysInfo["open"] = 1
               for id, formationInfo in formationConfig.FormationConfig.items():
                   if formationInfo["type"] == sysId and formationInfo["unlockLevel"]==0:
                       if id in self.formationIDList:
                           continue
                       self.formationIDList.append(id)
           else:
               sysInfo["open"] = 0

           self.formationSysPropActive(sysInfo)

           # INFO_MSG("---formationSystrongLevel---" + str(sysInfo["strongLevel"]))


       self.client.getFormationSysList(self.formationSystem)

       pass

    # 获取已经解锁阵型ID
    def onClientActiveFormationIDList(self):

        self.client.getForamtionIDList(self.formationIDList)

        pass

    # 客户端请求使用阵型
    def onClientUseFormation(self,formationId):

        if formationId not in self.formationIDList:
            return

        self.formation = formationId

        self.writeToDB()

        # self.client.onUseFormationSucc(formationId)

        pass

    # 客户端请求替补席处理 type==0 离开替补  type==1 进入替补
    def onClientBenchBaller(self,type ,cardID):

        if cardID not in self.cardIDList :
            # self.onCardError(CardMgrModuleError.Card_not_exist)
            return

        if cardID in self.benchBallerIDList:
            return

        card = KBEngine.entities.get(cardID)
        card.bench = type
        self.benchBallerIDList.append(cardID)

        self.writeToDB()

        self.client.benchResult(type,cardID)

        self.ballerRelationProp()
        pass

    # 客户端请求替补席交换
    def onClientExchangeBench(self,changeId,cardId):

        if changeId not in self.cardIDList:
            # self.onCardError(CardMgrModuleError.Card_not_exist)
            return

        WARNING_MSG("-- self.benchBallerIDList--"+str(len(self.benchBallerIDList)))
        if changeId not in self.benchBallerIDList:
            # self.onCardError(CardMgrModuleError.Card_not_exist)
            WARNING_MSG("--BenchchangeId--"+str(changeId))
            return

        if cardId in self.benchBallerIDList:
            WARNING_MSG("--BenchcardId--"+str(cardId))
            return

        index =  self.benchBallerIDList.index(changeId)

        self.benchBallerIDList.pop(index)

        self.benchBallerIDList.append(cardId)

        # ERROR_MSG("--ExchangeBench-index----:"+str(index))

        card = KBEngine.entities.get(cardId)
        card.bench = 1

        change =  KBEngine.entities.get(changeId)
        change.bench = 0

        self.ballerRelationProp()

        self.client.benchChangeSucc(changeId,cardId)

        pass



    # 替补席开启

    def onClientOpenBench(self,index):

        benchInfo = BenchConfig[1]

        if self.benchSize>=benchInfo["maxNum"]:
            return

        benchopenInfo = benchOpenConfig.BenchOpenConfig[index]

        if self.diamond < benchopenInfo["needmoney"]:
            ERROR_MSG("diamond isnot enough-----" + str( benchopenInfo["needmoney"]) + "-----self.diamond has----" + str(self.diamond))
            return

        INFO_MSG("self.bagSize------"+str(self.benchSize))

        self.diamond = self.diamond - benchopenInfo["needmoney"]

        self.benchSize = self.benchSize + 1

        INFO_MSG("self.bagSize------" + str(self.benchSize))

        self.client.benchBoxOpen(self.benchSize)

        self.writeToDB()


        pass


    # 客户端请求阵型激活
    def onClientActiveFormation(self,id):

        formation = formationConfig.FormationConfig[id]

        typeId = formation["type"]

        if  id  in self.formationIDList:
            return

        strongLevel = 0

        for formation_sys in self.formationSystem:
            if formation_sys["id"] == typeId:
                strongLevel = formation_sys["strongLevel"]
                INFO_MSG("---strongLevel---" + str(strongLevel))
                if formation_sys["open"] == 0 :
                    return
                break


        # 判断阵型需要的强化等级
        if formation["unlockLevel"] > strongLevel:
            return

        self.formationIDList.append(id)

        self.writeToDB()

        self.client.activeFormationSucc(id)


        pass

    # 修改上阵球员位置

    def onChangeBallerPos(self,cardId,pos):
        if cardId not in self.cardIDList:
            # ERROR_MSG("       cardID       " + str(cardId))
            self.client.onBallerCallBack(CardMgrModuleError.Card_not_exist)
            return

        card = KBEngine.entities.get(cardId)
        card.pos = pos

        self.client.changeBallerPosSucc(cardId,pos)

        pass



    # 球员上阵
    def onBallerEnterTeam(self,cardId,exchangeId,pos):

        if cardId not in self.cardIDList:
            # ERROR_MSG("       cardID       " + str(cardId))
            self.client.onBallerCallBack(CardMgrModuleError.Card_not_exist)
            return

        card = KBEngine.entities.get(cardId)

        exChangeCardId = -1

        for inTeamCardId in self.inTeamcardIDList:

            teamCard = KBEngine.entities.get(inTeamCardId)

            if teamCard.isSelf == 1 :
                continue

            if teamCard.id == exchangeId :
                teamCard.pos = 0
                teamCard.inTeam = 0
                card.inTeam = 1
                card.bench = 0
                card.pos = pos
                self.inTeamcardIDList.remove(inTeamCardId)
                exChangeCardId = inTeamCardId
                teamCard.subBallerFightValue()
                teamCard.writeToDB()
                break

        self.inTeamcardIDList.append(cardId)

        # INFO_MSG("---cardId---"+str(card.configID)+"---pos---"+str(card.pos))

        self.client.onBallerInTeamSucc(int(cardId),int(exChangeCardId),pos)

        card.addBallerFightValue()
        card.writeToDB()
        self.ballerRelationProp()

        pass

    # 上阵球员交换位置
    def onClientBallerExchangePos(self,cardId,exchangeId):

        if cardId not in self.cardIDList:
            ERROR_MSG("       cardID       " + str(cardId))
            self.client.onBallerCallBack(CardMgrModuleError.Card_not_exist)
            return

        if exchangeId not in self.cardIDList:
            ERROR_MSG("       exchangeId       " + str(exchangeId))
            self.client.onBallerCallBack(CardMgrModuleError.Card_not_exist)
            return

        card = KBEngine.entities.get(cardId)
        teamCard = KBEngine.entities.get(exchangeId)

        pos = card.pos
        card.pos = teamCard.pos
        teamCard.pos = pos;

        self.client.onBallerExchangeSucc(cardId,exchangeId)


        pass

    #阵型系统升级
    def onClientFormationStrong(self, formationSysId):

        INFO_MSG("---SysId---"+ str(formationSysId))
        fomationInfo = formationSystemConfig.FormationSystemConfig[formationSysId]

        costInfo = fomationInfo["material"]

        for itemId, num in costInfo.items():
             have = self.getItemNumByItemID(itemId)
             if have < num:
                # ERROR_MSG("--- num bu zu--- have   " + str(have) + "   need  " + str(num) + "   " + str(itemId))
                return

        for itemId, num in costInfo.items():
            self.decItem(itemId, num)


        for formationSys in self.formationSystem:
            if formationSys["id"] == formationSysId:

                if  formationSys["strongLevel"] >= fomationInfo["maxStrongLevel"] :
                    return

                formationSys["strongLevel"] = formationSys["strongLevel"] + 1
                self.formationSysPropActive(formationSys)
                self.client.onFormationStrongSucc(formationSys)
                break

        self.fomationFight()

        pass

    # 阵型系统属性激活
    def formationSysPropActive(self, sysInfo ):
        proplist=[]
        sysId = sysInfo["id"]
        strongLevel = sysInfo["strongLevel"]
        WARNING_MSG("--formationSysPropActive-sysId-" + str(sysId)+"---"+str(strongLevel))

        formationSysConfig =  formationSystemConfig.FormationSystemConfig[sysId]
        activeCondition = formationSysConfig["activeCondition"]
        addProp = formationSysConfig["addProp"]
        propName = formationSysConfig["valueType"]

        #系统加成
        for i in range(len(activeCondition)):

            level = activeCondition[i]
            if self.level < level:

                index =  i-1
                if index < 0:
                    continue

                sysInfo["active"] = index
                propValue = addProp[index]
                value ={}
                value[RelatePropKey.propName] = propName
                value[RelatePropKey.value] = propValue
                proplist.append(value)
                break

        WARNING_MSG("--getFormationProp-strongLevel-" + str(strongLevel))

                # 强化加成
        if strongLevel  not in formationSysStrongConfig.FormationSysStrongConfig:
            return

        formationSysStrong = formationSysStrongConfig.FormationSysStrongConfig[strongLevel]

        propStr = formationSysStrong["prop"]
        propStrArr = propStr.split(";")

        for prop in propStrArr:
            name = prop.split(":")[0]
            propVal = int(prop.split(":")[1])
            obj={}
            obj[RelatePropKey.propName] = name
            obj[RelatePropKey.value] = propVal
            proplist.append(obj)

        self.fomationPropContainer[sysId] = proplist
        self.client.getFormationProp(sysId,proplist)
        WARNING_MSG("--getFormationProp--"+str(sysId)+"---"+str(len(proplist)))
        pass

    # 初始化阵型加成属性
    def initFormationSysProp(self):
        for sysInfo in self.formationSystem:
            self.formationSysPropActive(sysInfo)


    # 计算阵型加成战斗力
    def fomationFight(self):
        for id in self.inTeamcardIDList:
            cardInfo = KBEngine.entities.get(id)
            cardInfo.calcFightValue()

        pass




              # --------------------------------------------------------------------------------------------
    #                              工具函数调用函数
    # --------------------------------------------------------------------------------------------


if __name__ == "__main__":
    print(__file__)
    pass

class RelatePropKey :

    propName = "propName"
    value = "value"



















