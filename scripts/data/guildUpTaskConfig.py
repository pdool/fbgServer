# -*- coding: utf-8 -*-

GuildUpTaskConfig = {1: {'openType': (0,), 'id': 1, 'needTime': 1, 'addNum': 2, 'needFunds': 300000},
                     2: {'openType': (1,), 'id': 2, 'needTime': 3, 'addNum': 3, 'needFunds': 600000},
                     3: {'openType': (1, 2), 'id': 3, 'needTime': 6, 'addNum': 3, 'needFunds': 2000000},
                     4: {'openType': (1, 2), 'id': 4, 'needTime': 12, 'addNum': 4, 'needFunds': 4000000},
                     5: {'openType': (1, 2, 3), 'id': 5, 'needTime': 24, 'addNum': 4, 'needFunds': 6000000},
                     6: {'openType': (1, 2, 3), 'id': 6, 'needTime': 48, 'addNum': 5, 'needFunds': 22000000},
                     7: {'openType': (1, 2, 3, 4), 'id': 7, 'needTime': 96, 'addNum': 5, 'needFunds': 40000000},
                     8: {'openType': (1, 2, 3, 4), 'id': 8, 'needTime': 0, 'addNum': 6, 'needFunds': 0}}

allDatas = {
    '公会任务升级配置': GuildUpTaskConfig,
}
