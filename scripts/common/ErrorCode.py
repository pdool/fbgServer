# -*- coding: utf-8 -*-
__author__ = 'chongxin'


class LotteryError:
    Success=0
    Money_not_enough =1
    Diamond_not_enough = 2

class FriendError:
    # 玩家不存在
    Player_not_exist = 1
    # 请输入正确的ID
    Pls_input_correct_Id = 2
    # 玩家列表已满
    Friend_list_is_full = 3
    # 已经是好友
    Friend_already_is_friend = 4
    # 在黑名单中
    Friend_he_is_in_black = 5
    # 没有申请过
    Friend_has_not_apply = 6
    # 不是好友不能加黑名单
    Friend_is_not_friend = 7
    # 已经在黑名单
    Friend_already_in_black = 8

class BodyPowerEroor:
    # 没有购买次数
    has_not_enough_buy_times = 1
    # 没有足够的钻石
    has_not_enough_diamond = 2

class ChatError:
    # 消息超过规定长度
    Chat_message_is_overflow = 1
    # 世界频道等级不够
    Chat_world_level_not_enough = 2
    # 世界频道CD
    Chat_world_cd = 3

    # 玩家不在线
    Chat_player_offline = 4
    # 没有足够的钻石
    has_not_enough_diamond = 5
    # 不文明发言
    has_bad_words = 6

class PieceCombineError:
    # 碎片不存在
    Piece_not_exist = 1
    # 碎片不够
    Piece_not_enough = 2
class DiamondModuleError:
    # 宝石不存在
    Diamond_not_exist = 1
    # 宝石不够
    Diamond_not_enough = 2
class EquipModuleError:
    # 装备不存在
    Equip_not_exist = 1
    # 装备不够
    Equip_not_enough = 2
class GiftModuleError:
    # 礼包不存在
    Gift_not_exist = 1
    # 礼包不够
    Gift_not_enough = 2
    # 操作数据库出错
    Gift_db_error = 3
class UseModuleError:
    # 礼包不存在
    Use_not_exist = 1
    # 礼包不够
    Use_not_enough = 2
    # 操作数据库出错
    Use_db_error = 3
class MaterialModuleError:
    # 礼包不存在
    Material_not_exist = 1
    # 礼包不够
    Material_not_enough = 2
    # 操作数据库出错
    Material_db_error = 3
























