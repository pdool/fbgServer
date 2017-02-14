# -*- coding: utf-8 -*-

cardLevelUpgradeConfig = {
    1: {'shoot': 0, 'maxExp': 0, 'reel': 0, 'trick': 0, 'levelStealRatio': 100, 'controll': 0, 'keep': 0,
        'levelPassRatio': 100, 'id': 1, 'defend': 0, 'pass': 0, 'steal': 0},
    2: {'shoot': 1, 'maxExp': 500, 'reel': 3, 'trick': 3, 'levelStealRatio': 100, 'controll': 3, 'keep': 3,
        'levelPassRatio': 100, 'id': 2, 'defend': 3, 'pass': 3, 'steal': 3},
    3: {'shoot': 2, 'maxExp': 800, 'reel': 2, 'trick': 2, 'levelStealRatio': 100, 'controll': 2, 'keep': 2,
        'levelPassRatio': 100, 'id': 3, 'defend': 2, 'pass': 2, 'steal': 2}}
levelIniConfig = {0: {'id': 0, 'maxLevel': 100}}

allDatas = {
    '球员升级经验表': cardLevelUpgradeConfig,
    '零散配置': levelIniConfig,
}
