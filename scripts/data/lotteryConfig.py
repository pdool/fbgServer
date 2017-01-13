# -*- coding: utf-8 -*-

lottery = {
    1: {'freeTime': 5, 'moneyCount': 100, 'cdTime': 600, 'tenDropIds': (), 'dropIds': (1, 2), 'id': 1, 'moneyType': 0,
        'firstCall': 0},
    2: {'freeTime': 1, 'moneyCount': 100, 'cdTime': 86400, 'tenDropIds': (), 'dropIds': (3,), 'id': 2, 'moneyType': 2,
        'firstCall': 3},
    3: {'freeTime': 0, 'moneyCount': 900, 'cdTime': -1, 'tenDropIds': (3,), 'dropIds': (2,), 'id': 3, 'moneyType': 2,
        'firstCall': 0}}
baseConfig = {1: {'resetTime': 0, 'id': 1}}

allDatas = {
    '基本配置': baseConfig,
    '抽奖': lottery,
}
