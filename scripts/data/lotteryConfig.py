# -*- coding: utf-8 -*-

baseConfig = {1: {'resetTime': 0, 'id': 1}}
lottery = {
    1: {'tenDropIds': (), 'moneyType': 0, 'cdTime': 600, 'freeTime': 5, 'firstCall': 0, 'id': 1, 'moneyCount': 100,
        'dropIds': (101102, 102024)},
    2: {'tenDropIds': (), 'moneyType': 2, 'cdTime': 86400, 'freeTime': 1, 'firstCall': 3, 'id': 2, 'moneyCount': 100,
        'dropIds': (101102, 102024, 103504, 103505)},
    3: {'tenDropIds': (101102, 102024, 103504, 103505, 103506, 103507, 103508, 103509, 103001, 103002), 'moneyType': 2,
        'cdTime': -1, 'freeTime': 0, 'firstCall': 0, 'id': 3, 'moneyCount': 900,
        'dropIds': (101102, 102024, 103504, 103505, 103506, 103507, 103508, 103509, 103001, 103002)}}

allDatas = {
    '基本配置': baseConfig,
    '抽奖': lottery,
}
