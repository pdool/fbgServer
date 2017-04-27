# -*- coding: utf-8 -*-
__author__ = 'chongxin'


class ActionTypeEnum:
    # 副本
    action_clone = 1

class PlayerOp:
    defendOp = -1
    passball = 1
    shoot = 2

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
