# -*- coding: utf-8 -*-
__author__ = 'chongxin'

class HalfEnum:
    first = 0
    sencond = 1

#邮件类型枚举
class MailTypeEnum:
    # 玩家私人邮件
    Mail_Type_Player = 0   # 玩家
    # 公会邮件
    Mail_Type_Guild = 1
    # GM命令
    Mail_Type_GM = 2

class ActionTypeEnum:
    action_none = 0
    # 副本
    action_clone = 1
    # 世界boss
    action_world_boss = 2
    # 官员晋升
    official_promotion = 3
    # 玩家对战 官员晋升
    official_promotion_player = 4
    # 竞技场
    action_arena = 5
    # 联赛玩家和玩家
    league_player = 6
    # 联赛玩家和机器人
    league_clone = 7


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

class CloneChapterGiftEnum:
    # 未领取
    not_get = 0
    # 已领取
    get = 1


class AutoControllEnum:
    # AI控制
    AI_Controll = 0
    # 客户端控制
    Client_Controll = 1



























