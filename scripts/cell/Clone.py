# -*- coding: utf-8 -*-
import KBEngine
import random
import cloneConfig
import monsterConfig
import formationConfig
import playerAtkPosition
import positionConfig
import util
from KBEDebug import *

class Clone(KBEngine.Entity):

#========================KBE方法=================================================
    """
    游戏房间
    """
    def __init__(self):
        KBEngine.Entity.__init__(self)
        print("Cell::clone.__init__")
        KBEngine.globalData["room_%i" % self.spaceID] = self.base



        # 注册clone管理的属性
        self.initProp()

        self.initMonster()

    def initProp(self):
        """
        clone管理的副本全局数据
        """
        self.avartaID = -1
        # 总的回合次数
        self.totalAttackTimes = 0
        # 当前进攻序列
        self.curAttackIndex = 0
        # 当前控制者(玩家或者副本)
        self.curControllerID = 0
        # 当前回合的第几轮
        self.curRound = 1



        # --------------------------------------------------------------------------------------------------------------
        """
        clone 管理的 怪的数据
        """
        self.totalAttackValue = 0.0
        self.totalDefendValue =0.0
        self.totalControllValue = 0.0
        # 当前怪的id list
        self.inTeamcardIDList = []
        # 上一轮的攻击者
        self.preAttackId = -1
        # 当前进攻者ID
        self.curAttackID = -1
        # 上一轮的防守者 列表
        self.preDefIds = -1
        # 怪的攻击序列
        self.monsterAttackList = []
        # 当前防守者list
        self.a.curDefIdList = []
        # 上一轮是否完美助攻的射门系数
        self.o1 = 1


        # 门将id
        self.keeperID = -1

        pass


    def initMonster(self):

        cloneNpcConfig = cloneConfig.CloneConfig[self.cloneID]

        npcTuple = cloneNpcConfig["npcTuple"]

        formationTuple = cloneNpcConfig["formationTuple"]

        ERROR_MSG("--------spaceID-------------------" + str(self.spaceID))
        for i in range(11):
            npcID = npcTuple[i]
            if npcID not in monsterConfig.MonsterConfig:
                ERROR_MSG("wrong config")
                continue
            baseProp = monsterConfig.MonsterConfig[npcID]

            ERROR_MSG("--------npcID-------------------" + str(npcID))

            param = {"monsterID"    : npcID,
                     "shoot"        : baseProp["shoot"],
                     "defend"       : baseProp["defend"],
                     "passBall"     : baseProp["pass"],
                     "trick"         : baseProp["trick"],
                     "reel"          : baseProp["reel"],
                     "steal"         : baseProp["steal"],
                     "controll"      : baseProp["controll"],
                     "keep"          : baseProp["keep"],
                     "tech"          : baseProp["tech"],
                     "health"        : baseProp["health"],
                     "pos"            : formationTuple[i],
                    }


            position = (0.0,0.0,0.0)
            direction = (0.0,0.0,0.0)
            e = KBEngine.createEntity("Monster",self.spaceID,position,direction,param)
            # 门将
            if e.pos == 1:
                self.keeperID = e.id
            self.inTeamcardIDList.append(e)




    def beginFight(self):

        avatar = KBEngine.entities[self.avartaID]

        self.calcBaseData()


    def calcBaseData(self):
        avatar = KBEngine.entities[self.avartaID]


        # 玩家总的攻击系数 和 防御系数  和 控球系数
        avatar.totalAttackValue,avatar.totalDefendValue,avatar.totalControllValue = self.__calMyAtkAndDefendAndControllValue()

        # 怪总的攻击系数 和 防御系数 和 控球系数
        self.totalAttackValue, self.totalDefendValue, self.totalControllValue = self.__calMonsterAtkAndDefendAndControllValue()

        myattackTimes = self.__calcMyAttackTimes(self.avartaID,self.id)
        monsterAttackTimes = self.__calcMyAttackTimes(self.id,self.avartaID)

        self.totalAttackTimes = myattackTimes + monsterAttackTimes

        self.monsterAttackList =  random.sample(range(self.totalAttackTimes), monsterAttackTimes)

    # 计算玩家的进攻次数
    def __calcMyAttackTimes(self,aID,bID):

        # A队进攻次数MA=max(round(回合设定基数*(A队攻击系数+B队攻击系数-5)/(A队防御系数+B队防御系数-5)*(A队控球系数)/(A队控球系数+B队控球系数)*(0.1*rand(1)+0.95),0),1)
        roundBase = 6
        seed = random.random()

        a = KBEngine.entities[aID]
        b = KBEngine.entities[bID]

        attackTimes = max(round(roundBase * (a.totalAttackValue + b.totalAttackValue - 5) / (a.totalDefendValue + b.totalDefendValue - 5) * (a.totalControllValue) / (a.totalControllValue + b.totalControllValue) * (0.1 * seed + 0.95), 0), 1)

        return  attackTimes

    # 计算玩家总的攻击系数 和 防守次数 和控球系数
    def __calMyAtkAndDefendAndControllValue(self):
        avartar = KBEngine.entities[self.avatarID]
        if avartar is None:
            return 0,0,0
        myFormation = avartar.baseProp["fromation"]

        attack = 0.0
        defend = 0.0
        controll = 0.0

        posList = formationConfig.FormationConfig[myFormation]


        for pos in posList:

            posConfig = positionConfig.PositionConfig[pos]

            if posConfig["attackEnable"] == 1:
                attack = attack + posConfig["attack"]
            defend = defend + posConfig["defend"]
            controll = controll + posConfig["controll"]

        return  attack,defend,controll

    # 计算怪的总的攻击系数 和 防守次数 和控球系数
    def __calMonsterAtkAndDefendAndControllValue(self):
        attack = 0.0
        defend = 0.0
        controll = 0.0
        for monster in self.inTeamcardIDList:
            pos = monster.pos
            posConfig = positionConfig.PositionConfig[pos]
            if posConfig["attackEnable"] == 1:
                attack = attack + posConfig["attack"]
            defend = defend + posConfig["defend"]
            controll = controll + posConfig["controll"]

        return attack,defend,controll

    #  判定进攻发起者Atk1Player
    def __calAtkPlayer(self):
        # 默认是副本
        controllerObj = self
        if self.curAttackindex in self.monsterAttackList:
            controller = KBEngine.entities[self.avartaID]








    # 计算每个球员的发起进攻值C1
    def __calcObjAttckValue(self,objID ):
        obj = KBEngine.entities[objID]
        if obj is None:
            return 0.0
        pos = obj.pos
        posConfig = positionConfig.PositionConfig[pos]
        # 发起进攻值C1 = 球员的控球值 * 球员所处位置的控球系数 + 球员传球值 * 球员所处位置的传球系数
        controll = obj.controll * posConfig["controll"] + obj.passBall * posConfig["pass"]
        return controll

    """
    step 4.1 判定进攻发起者Atk1Player
	4.11 判定阵型中的参与进攻球员=a1、a2、a3……an<-可参与进攻球员见属性设定sheet中的【隐性属性】
	4.12 发起进攻值C1=球员的控球值*球员所处位置的控球系数+球员传球值*球员所处位置的传球系数
	4.13 参与进攻的球员参与进攻的概率为Ca/(Ca1+Ca2+……+Can)
	4.14 根据参与进攻的球员随机一个球员判定为【进攻发起者】Atk1Player

    """
    def __GetAttackerID(self,id):
        attackObj = KBEngine.entities[id]

        # 所有已经参与过进攻的参与者
        if hasattr(attackObj,"preAttackId") is False:
            attackObj.preAttackId = -1

        sumAttack = 0
        stepList = []
        rangeId = []
        for id in attackObj.inTeamcardIDList:
            if id == attackObj.preAttackId:
                continue
            c1 = self.__calcObjAttckValue(id)
            sumAttack = sumAttack + c1

            stepList.append(sumAttack)
            rangeId.append(id)

        seed = random.uniform(0.0,sumAttack)

        for i in range(len(stepList)):
            if seed >= stepList[i]:
                if i == 0:
                    attackObj.curAttackID = rangeId[i]
                    attackObj.preAttackId = rangeId[i]
                else:
                    attackObj.curAttackID = rangeId[i-1]
                    attackObj.preAttackId = rangeId[i-1]




    """
    step 4.2 判定进攻发起者的防守者Def1Player1、Def1Player2
	4.21 判定当前轮次的防守人数： 根据(H-1)随机在区间(0,1]，若随机区间在(0，H-1]则为防守人数S为2，若随机区间>H-1,则防守人数S为1 <-H为step3中计算的防守强度系数
	4.22 判定当前阵型中可参与防守Atk1Player的球员=d1、d2、d3……dn   <-可参与防守球员见攻防对位sheet中的【防守对应逻辑】
	4.23 若可参与防守球员数量>S，则从可参与防守球员中随机S人判定为该轮防守者Def1Player1、Def1Player2
	4.24 若可参与防守球员数量<=S，则所有可参与防守的球员都判定为该轮防守者Def1Player1、Def1Player2
	4.25 若没有可参与防守的球员，则该轮无防守球员
    """
    def __getDefPlayer(self,aID,bID):

        a = KBEngine.entities[aID]
        b = KBEngine.entities[bID]

        aH = a.totalDefendValue/b.totalAttackValue

        # 所有已经参与过进攻的参与者
        if hasattr(a,"preDefIds") is False:
            a.preDefIds = []

        seed = random.random()
        if seed == 0.0:
            seed = 1.0
        s = 1
        if seed  <= aH -1:
            s = 2

        curAttackCardObj = KBEngine.entities[self.curAttackID]

        pos = curAttackCardObj.pos

        posConfig = positionConfig.PositionConfig[pos]

        if "adaptDef" not in posConfig.keys():
            return []

        adaptDefList = posConfig["adaptDef"]

        canDefList =[]
        for id in a.inTeamcardIDList:
            if id in a.preDefIds:
                continue

            card = KBEngine.entities[id]

            if card.pos in adaptDefList:
              canDefList.append(id)

        a.curDefIdList = random.sample(canDefList,s)

        a.preDefIds = a.curDefIdList


    """
    step 4.7 判定Atk1Player、Atk2Player、Atk3Player的进攻位置；根据进攻队员位置判定Def1Player1、Def1Player2、Def2Player1、Def2Player2、Def3Player1、Def3Player2的防守位置
	4.71 根据【射门位置及系数sheet】中逻辑，将4.1~4.6所获得的球员随机到相应进攻/防守位置上

    """

    """
    step 4.8 第一轮PK为传球轮：判定【进攻发起者Atk1Player VS 进攻发起者的防守者Def1Player】回合结果，若进攻成功进入下一流程step 4.9，若失败跳出这一回合，进入step5
	4.81 若该轮有1个防守者时，判断是否被抢断，若被抢断则进攻结束，直接跳出Step4
		P1=(防守者1抢断值-进攻者盘带值*0.8)*(1-进攻者技术值+防守者身体值)/进攻者等级抢断系数   <-等级抢断系数待定
		根据P1在区间(0,1 ]， 随机结果判断是否被抢断
	4.82 若该轮有2个防守者时，判断是否被第2个防守者抢断，若被抢断则进攻结束，直接跳出Step4；若无第2个防守者则进入4.83
		P2=(防守者2抢断值-进攻者盘带值*0.8)*(1-进攻者技术值+防守者身体值)/进攻者等级抢断系数
		根据P2在区间(0,1 ]， 随机结果判断是否被抢断


    """
    def __canSteal(self):

        defObj = self
        if self.curControllerID != self.avartaID:
            defObj = KBEngine.entities[self.avartaID ]

        attackId = KBEngine.entities[self.curControllerID ].curAttackID
        attackObj = KBEngine.entities[attackId]

        defList = defObj.curDefIdList

        result = False
        for id in defList:
            defPlayer = KBEngine.entities[id]
            # P1 =(防守者1抢断值 - 进攻者盘带值) * (1 - 进攻者技术值 + 防守者身体值) / 进攻者等级抢断系数

            p = (defPlayer.steal - attackObj.reel * 0.8) * (1 - attackObj.tech + defPlayer.health)/ attackObj.levelSteal

            seed = util.randFunc()

            if p <= seed:
                result = True
                break

        return  result

    """
    4.83 计算传球后的结果O1
		P3=(进攻者传球值-防守者拦截值*0.8)*(1+进攻者技术值-防守者身体值)/进攻者等级传球系数  <-等级传球系数待定
		防守者拦截值=(防守者1拦截值+防守者2拦截值)*防守人数拦截系数 <-防守人数拦截系数：1人防守时为 1   ，2人防守时为 0.75
		防守者身体值=(防守者1身体值+防守者2身体值)*防守人数身体系数<-防守人数身体系数：1人防守时为 1   ，2人防守时为 0.75
		根据P3在区间(0,1]，随机结果判断是否传出【完美助攻】，若结果为完美助攻，下一个接球者传球、射门值均提高20%，O1=1.2；否则O1=1
    """
    def __isPerfectPassBall(self):
        defObj = self
        if self.curControllerID != self.avartaID:
            defObj = KBEngine.entities[self.avartaID]

        controllerObj = KBEngine.entities[self.curControllerID]

        attackId = controllerObj.curAttackID
        attackObj = KBEngine.entities[attackId]

        defList = defObj.curDefIdList

        defCount = len(defList)
        # 防守者拦截值 防守者身体值
        defTrickSum = 0.0
        defHealthSum = 0.0

        # 防守人数拦截系数
        trickRatio = 1
        healthRatio = 1
        if defCount == 2:
            trickRatio = 0.75
            healthRatio =0.75

        for id in defList:
            defPlayer = KBEngine.entities[id]

            defTrickSum  = defTrickSum + defPlayer.trick * trickRatio
            defHealthSum = defHealthSum + defPlayer.health * healthRatio

        # P3 =(进攻者传球值 - 防守者拦截值 * 0.8) * (1 + 进攻者技术值 - 防守者身体值) / 进攻者等级传球系数 < -等级传球系数待定
        p = (attackObj.passBall - defTrickSum * 0.8) * (1 + attackObj.tech - defHealthSum) / attackObj.levelPass

        seed = util.randFunc()


        controllerObj.o1 = 1.0
        if p <= seed:
            controllerObj.o1 = 1.2


    """
    4.93 计算射门结果
	P3=(进攻者射门值*O1*L1-防守者防守值)*(1+进攻者技术值-防守者身体值)*(0.95*rand()+0.1)/门将守门值  <O1为4.83中计算的完美助攻系数；L1为射门位置的射门威力系数，系数见【射门位置及系数sheet】
	防守者防守值=(防守者1防守值+防守者2防守值+门将防守值)*防守人数防守系数  <-防守人数防守系数：1人防守时为 1   ，2人防守时为 0.75  ，3人防守时为 0.6 (人数为算上门将的人数)
	防守者身体值=(防守者1身体值+防守者2身体值+门将身体值)*防守人数防守系数  <-防守人数防守系数：1人防守时为 1   ，2人防守时为 0.75  ，3人防守时为 0.6 (人数为算上门将的人数)
	根据P3在区间(0,1]，随机结果判断是否进球

    """
    def __isShootSucc(self):

        defObj = self
        if self.curControllerID != self.avartaID:
            defObj = KBEngine.entities[self.avartaID]

        controllerObj = KBEngine.entities[self.curControllerID]

        attackId = controllerObj.curAttackID
        attackObj = KBEngine.entities[attackId]
        # 门将
        keeperObj = KBEngine.entities[controllerObj.keeperID ]

        defList = defObj.curDefIdList

        defCount = len(defList) + 1 # +1 为门将

        # 防守人数拦截系数
        defRatio = 1
        if defCount == 2:
            defRatio = 0.75
        elif defCount == 3:
            defRatio = 0.6

        # 防守者防守值 防守者身体值
        defSum = keeperObj.defend * defRatio
        defHealth = keeperObj.health * defRatio
        # 防守者防守值=(防守者1防守值+防守者2防守值+门将防守值)*防守人数防守系数
        # 防守者身体值=(防守者1身体值+防守者2身体值+门将身体值)*防守人数防守系数
        for id in defList:
            defPlayer = KBEngine.entities[id]

            defSum  = defSum + defPlayer.defend * defRatio
            defHealth = defHealth + defPlayer.health * defRatio

    #     P3=(进攻者射门值*O1*L1-防守者防守值)*(1+进攻者技术值-防守者身体值)*(0.95*rand()+0.1)/门将守门值

        p = (attackObj.shoot * attackObj.o1 * L1- defSum)*(1+attackObj.tech-defHealth)*(0.95*random.random()+0.1)/keeperObj.keep

        seed = util.randFunc()

        shootSucc = False
        if p <= seed:
            shootSucc = True

        return  shootSucc
    """
    step 4.7 判定Atk1Player、Atk2Player、Atk3Player的进攻位置；根据进攻队员位置判定Def1Player1、Def1Player2、Def2Player1、Def2Player2、Def3Player1、Def3Player2的防守位置
	4.71 根据【射门位置及系数sheet】中逻辑，将4.1~4.6所获得的球员随机到相应进攻/防守位置上
    """
    def __getAtkCoordinate(self):

        controllerObj = KBEngine.entities[self.curControllerID]
        attackId = controllerObj.curAttackID
        attackObj = KBEngine.entities[attackId]

        pos = attackObj.pos

        curRound = "round" + str(self.curRound)
        # 候选的攻击点
        candidateList = playerAtkPosition.PlayerAtkPosition[pos][curRound]
        # 选中的坐标
        coordinate = random.choice(candidateList)
        
        attackObj.coordinate = coordinate


















    def onTimer(self, tid, userArg):
        """
        KBEngine method.
        引擎回调timer触发
        """
        DEBUG_MSG(tid, userArg)

    def onDestroy(self):
        """
        KBEngine method.
        """
        del KBEngine.globalData["room_%i" % self.spaceID]
        self.destroySpace()

#========================房间内事件=================================================

    def onEnter(self, entityMailbox):
        """
        进入场景
        """
        print("Cell::Room.onEnter")

    def onLeave(self, entityID):
        """
        离开场景
        """
        print("Cell::Room.onLeave")