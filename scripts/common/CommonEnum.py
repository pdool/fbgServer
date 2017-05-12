# -*- coding: utf-8 -*-
__author__ = 'chongxin'

#邮件类型枚举
class MailTypeEnum:
    # 玩家私人邮件
    Mail_Type_Player = 0   # 玩家
    # 公会邮件
    Mail_Type_Guild = 1
    # GM命令
    Mail_Type_GM = 2

class ActionTypeEnum:
    # 副本
    action_clone = 1

class PlayerOp:
    defendOp = -1
    passball = 1
    shoot = 2

class LastRoundEnmu:
    #
    gameOver = -1
    # 上半场
    firstHalf = -2
    # 下半场
    secondHalf = -3

class OpResult:
    # 抢断成功
    trickSucc = 1
    # 普通传球
    passBall = 2
    # 完美传球
    perfectPassBall = 3
    # 射门成功
    shootSucc = 4
    # 射门失败
    shootFail = 5
    # 选择射门还是传球
    select = 6

class ImpactTypeEnum:
    # 增益
    gain = 1
    # 减益
    debuffs = 2

    #不可驱散
    notDel = 3