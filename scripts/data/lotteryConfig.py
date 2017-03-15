# -*- coding: utf-8 -*-

lottery = {1: {'dropIds': (101102, 101101), 'cdTime': 600, 'moneyType': 0, 'freeTime': 5, 'id': 1, 'moneyCount': 100,
               'tenDropIds': (), 'firstCall': 0},
           2: {'dropIds': (101102,), 'cdTime': 86400, 'moneyType': 2, 'freeTime': 1, 'id': 2, 'moneyCount': 100,
               'tenDropIds': (), 'firstCall': 3},
           3: {'dropIds': (101102,), 'cdTime': -1, 'moneyType': 2, 'freeTime': 0, 'id': 3, 'moneyCount': 900,
               'tenDropIds': (101102,), 'firstCall': 0}}
baseConfig = {1: {'id': 1, 'resetTime': 0}}

allDatas = {
    '抽奖': lottery,
    '基本配置': baseConfig,
}
