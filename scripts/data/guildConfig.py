# -*- coding: utf-8 -*-

GuildConfig = {1: {'nameLenMin': 2, 'id': 1, 'noticeLen': 100, 'maxMemberNum': 50, 'changeNameDiamond': 1900,
                   'createNeedDiamond': 100, 'introductionLen': 50, 'nameLenMax': 5, 'impeachTime': 7}}
PowerConfig = {
    1: {'advisor': 0, 'editNotice': 0, 'admit': 0, 'upgradeBuild': 0, 'kick': 0, 'senior': 0, 'mail': 0, 'id': 1,
        'dismiss': 0, 'trans': 0, 'spy': 0, 'num': -1, 'junior': 0, 'intermediate': 0, 'impeach': 0},
    2: {'advisor': 0, 'editNotice': 0, 'admit': 0, 'upgradeBuild': 0, 'kick': 0, 'senior': 0, 'mail': 0, 'id': 2,
        'dismiss': 0, 'trans': 0, 'spy': 0, 'num': 6, 'junior': 0, 'intermediate': 0, 'impeach': 0},
    3: {'advisor': 1, 'editNotice': 0, 'admit': 1, 'upgradeBuild': 0, 'kick': 0, 'senior': 0, 'mail': 0, 'id': 3,
        'dismiss': 0, 'trans': 0, 'spy': 0, 'num': 3, 'junior': 1, 'intermediate': 0, 'impeach': 1},
    4: {'advisor': 0, 'editNotice': 1, 'admit': 1, 'upgradeBuild': 1, 'kick': 0, 'senior': 0, 'mail': 0, 'id': 4,
        'dismiss': 0, 'trans': 0, 'spy': 0, 'num': 3, 'junior': 1, 'intermediate': 0, 'impeach': 1},
    5: {'advisor': 1, 'editNotice': 1, 'admit': 1, 'upgradeBuild': 1, 'kick': 1, 'senior': 0, 'mail': 1, 'id': 5,
        'dismiss': 0, 'trans': 0, 'spy': 1, 'num': 2, 'junior': 1, 'intermediate': 1, 'impeach': 1},
    6: {'advisor': 1, 'editNotice': 1, 'admit': 1, 'upgradeBuild': 1, 'kick': 1, 'senior': 1, 'mail': 1, 'id': 6,
        'dismiss': 1, 'trans': 1, 'spy': 1, 'num': 1, 'junior': 1, 'intermediate': 1, 'impeach': 1}}

allDatas = {
    '配置表': GuildConfig,
    '职位权限': PowerConfig,
}
