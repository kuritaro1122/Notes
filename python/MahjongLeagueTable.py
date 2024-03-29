# 麻雀を8回戦行います。条件は以下の通りで、卓組表を8個作ってください。
# ・麻雀は8チーム×4人の計32人で行います。
# ・チームAからHまで、チーム名に数字を続けてプレイヤーを表します。例：A1,D3
# ・1つの卓組表では8卓使用します。
# ・1つの卓組表には32人全員入れてください。
# ・同じチームの選手が同じ卓に座ってはいけません。
# ・8回戦のなかで、1度同じ卓に座った相手とは2度同じ卓に座ってはいけません。
# ・チームごとの対戦数がなるべく同じになるようにしてください。

from enum import Enum
import copy
from importlib import invalidate_caches
from os import remove
import random
import collections
import itertools

### ルールのパラメータ ###
MATCH_NUM = 8
TABLE_NUM = 8
TABLE_PLAYER_NUM = 4
TEAM_NUM = 8
TEAM_PLAYER_NUM = 4

# 試合回数を等しくするようにするか、ランダムに振り分けるか
def use_history_or_random(index:int) -> bool:
    return False # 完全ランダム
    # return True # 対戦回数重視
    # return index > 0 # 途中から対戦回収重視

### チーム名 ###
TEAM_LIST = { 0:'A', 1:'B', 2:'C', 3:'D', 4:'E', 5:'F', 6:'G', 7:'H', 8:'I', 9:'J', 10:'K', 11:'L', 12:'M', 13:'N', 14:'O', 15:'P', 16:'Q', 17:'R', 18:'S', 19:'T', 20:'U', 21:'V', 22:'W', 23:'X' }
def get_team_name(index:int):
    if index in TEAM_LIST.keys():
        return str(TEAM_LIST[index])
    else:
        return str(index) + ':'

### ログ表示用 ###
class LOG_LEVEL:
    L0_RESULT_ONLY = 0
    L1_DETAIL = 1
    L2_CALUCULATION_LOG = 2
    L3_CALUCULATION_DETAIL = 3

CURRENT_LOG_LEVEL = LOG_LEVEL.L1_DETAIL

def print_debug(*arg:object, log_level:int):
    if log_level <= CURRENT_LOG_LEVEL:
        print(*arg)

### テーブル配列用定数 ###
class TABLE_PARAM:
    MATCH_INDEX = 0
    TABLE_INDEX = 1
    NEW_TABLE = 2

### プレイヤー
class Player:
    def __init__(self, team:int, name:int) -> None:
        self.team = team
        self.name = name
        self.history = []
    def add_history(self, player):
        self.history.append(player)
    def add_history_range(self, player_list:list):
        self.history.extend(player_list)
    def remove_history_range(self, player_list:list):
        for p in player_list:
            if self.history.__contains__(p):
                self.history.remove(p)
    def clear_history(self):
        self.history.clear()
    def is_contain_history(self, player):
        return player in self.history
    def get_match_num(self):
        return len(self.history)
    def to_string(self):
        return get_team_name(self.team) + str(self.name + 1)

# お互いに対戦履歴を記録する
def add_history_each(table:list):
    for player in table:
        player.add_history_range([p for p in table if p != player])
def remove_history_each(table:list):
    for player in table:
        player.remove_history_range([p for p in table if p != player])
# どちらの方を選ぶか比較する
def compare(a:Player, b:Player, tables:list, table_index:int):
    a_score = get_score(a, tables[table_index])
    b_score = get_score(b, tables[table_index])
    return a_score - b_score
def get_score(player:Player, table:list):
    temp_player = copy.deepcopy(player)
    temp_player.add_history_range(table)
    c = collections.Counter([h.to_string() for h in sorted(temp_player.history, key=compare_name)])
    duplicate_score = -sum([pow(a, 2) for a in c.values() if a > 1])
    return -player.get_match_num() + duplicate_score + (can_player_sit_to_table(player, table) if 0 else -999)
def compare_name(player:Player):
    return player.team * TEAM_PLAYER_NUM + int(player.name)
# def get_table_compared(tables:list):
#     index = 0
#     score = sum([get_score(p, [t for t in tables[index] if t != p]) for p in tables[index]])
#     for i, table in enumerate(tables):
#         s = sum([get_score(p, [t for t in table if t != p]) for p in table])
#         if s > score:
#             score = s
#             index = i
#     return tables[index]

### ルール, 条件チェック
def can_player_sit(target:Player, tables:list, table_index:int, ignore_history:bool=False, ignore_team:bool=False):
    return is_player_exist(player=target, tables=[t for t in tables if len(t) >= TABLE_PLAYER_NUM]) == False and can_player_sit_to_table(target=target, table=tables[table_index], ignore_history=ignore_history, ignore_team=ignore_team)
def can_player_sit_to_table(target:Player, table:list, ignore_history:bool=False, ignore_team:bool=False):
    for p in table:
        if (target in table) or (target.team == p.team and ignore_team == False) or (target.is_contain_history(p) and ignore_history == False):
            return False
    return True
# プレイヤーがどのテーブルにも所属していない
def is_player_exist(tables:list, player:Player):
    for table in tables:
        if player in table:
            #print('True:', player.to_string(), player_to_name_table(table))
            return True
    #print('False:', player.to_string(), tables)
    #print('False:', player.to_string(), player_to_name_tables(tables))
    return False
# target_tableのプレイヤーに対して、複数のテーブルに所属していない
def is_players_exist(tables:list, players:list):
    for p in players:
        if is_player_exist(tables=tables, player=p):
            return True
    return False
def duplicate_player_count(table1:list, table2:list):
    count = 0
    for p in table1:
        if p in table2:
            count += 1
    return count

### 文字列出力
# 対戦履歴を全て出力
def print_history(player_list:list):
    print_debug('match history:', log_level=LOG_LEVEL.L1_DETAIL)
    for p in player_list:
        c = collections.Counter([h.to_string() for h in sorted(p.history, key=compare_name)])
        print_debug(p.to_string(), '->', c, 'total_match_count:', int(sum(c.values())/3), 'duplicate:', sum([a - 1 for a in c.values() if a > 1]),log_level=LOG_LEVEL.L1_DETAIL)
def print_history_again(matchs_tables:list):
    temp_matchs_tables = copy.deepcopy(matchs_tables)
    for match_tables in temp_matchs_tables:
        for table in match_tables:
            for p in table:
                p.clear_history()
    for match_tables in temp_matchs_tables:
        for table in match_tables:
            if len(table) >= TABLE_PLAYER_NUM:
                add_history_each(table)
    l = list(itertools.chain.from_iterable(itertools.chain.from_iterable(temp_matchs_tables)))
    v = [k for k, v in collections.Counter(sorted(l, key=compare_name)).items() if v > 1]
    print_history(sorted(v, key=compare_name))

def player_to_name_table(table:list) -> list:
    return [p.to_string() for p in table]
def player_to_name_tables(tables:list) -> list:
    return [[p.to_string() for p in table] for table in tables]
def player_to_name_table_param(table_param:list):
    return [table_param[0], table_param[1], player_to_name_table(table_param[2])]
def player_to_name_table_params(table_params:list):
    return [player_to_name_table_param(p) for p in table_params]
def print_table_count(matchs_tables:list):
    created_table_count = [len([len(table) for table in match_tables if len(table) >= TABLE_PLAYER_NUM]) for match_tables in matchs_tables]
    print_debug('tables_count:', created_table_count, log_level=LOG_LEVEL.L0_RESULT_ONLY)
    print_debug('all_tables_count:', sum(created_table_count), log_level=LOG_LEVEL.L0_RESULT_ONLY)

### プレイヤーを配置する
def generate_match_tables(player_list:list):
    tables = []
    if use_history_or_random(i):
        tables = get_tables_from_history(player_list)
    else:
        tables = get_tables_from_random(player_list)
    for table in tables:
        if len(table) >= TABLE_PLAYER_NUM:
            add_history_each(table)
    return tables
# 対戦回数が等しくなるように配置する
def get_tables_from_history(player_list:list, tables_num=TABLE_NUM, table_player_num=TABLE_PLAYER_NUM):
    tables = [[] for i in range(tables_num)]
    for i in range(tables_num):
        for _ in range(table_player_num):
            cp = None
            for p in player_list:
                if can_player_sit(p, tables, i) and (cp == None or compare(p, cp, tables, i) > 0):
                    cp = p
            if cp != None:
                tables[i].append(cp)
    return tables
# ランダムに配置する
def get_tables_from_random(player_list:list, tables_num=TABLE_NUM, table_player_num=TABLE_PLAYER_NUM):
    tables = [[] for i in range(tables_num)]
    for i in range(tables_num):
        for k in range(table_player_num):
            temp_player_list = [p for p in player_list]
            while len(temp_player_list) > 0:
                p = temp_player_list.pop(random.randint(0, len(temp_player_list) - 1))
                if can_player_sit(p, tables, i):
                    break
            if can_player_sit(p, tables, i):
                tables[i].append(p)
    return tables
# 作成可能なテーブルを全取得する
def get_all_tables_conbination(player_list:list, table_player_num=TABLE_PLAYER_NUM, current_table=[], ignore_history:bool=False, ignore_team:bool=False):
    if len(current_table) >= table_player_num:
        return [current_table]
    all_tables_conbination = [] # current_tableに1人加えた複数のテーブル
    for p in player_list:
        if len(current_table) > 0 and compare_name(current_table[len(current_table) - 1]) > compare_name(p):
            continue
        if can_player_sit_to_table(p, current_table, ignore_history=ignore_history, ignore_team=ignore_team):
            table = [p for p in current_table]
            table.append(p)
            next_tables = get_all_tables_conbination(player_list=player_list, table_player_num=table_player_num, current_table=table, ignore_history=ignore_history)
            all_tables_conbination.extend(next_tables)
    return all_tables_conbination
# 全ての条件から現在のtablesに挿入可能なtablesを返す
def get_tables_can_be_inserted(tables:list, player_list:list) -> list:
    v = get_all_tables_conbination(get_remain_player(tables=tables, player_list=player_list))
    tables = [t for t in v if (is_players_exist(tables=[t for t in tables if len(t) >= TABLE_PLAYER_NUM], players=t) == False)]
    return tables
# 余ったプレイヤーを取得する
def get_remain_player(tables:list, player_list:list) -> list:
    remain_player_list = [p for p in player_list]
    for p in player_list:
        for table in tables:
            if len(table) >= TABLE_PLAYER_NUM and p.to_string() in player_to_name_table(table):
                remain_player_list.remove(p)
                break
    return remain_player_list

# 隙間を埋める
# def fill_match_tables_blank(match_tables:list, player_list:list):
#     for i, table in enumerate(match_tables):
#         table_candidates = get_tables_can_be_inserted(tables=match_tables, player_list=player_list)
#         if len(table_candidates) <= 0:
#             break
#         if len(table) < TABLE_PLAYER_NUM:
#             v = match_tables[i]
#             match_tables[i] = table_candidates[0]
#             print_debug('replace:', player_to_name_table(v), '->', player_to_name_table(match_tables[i]), log_level=LOG_LEVEL.L3_CALUCULATION_DETAIL)

# def change_matchs_tables_from_tables_diff(matchs_tables:list, table_params:list, add_not_remove:bool = True):
#     for table_param in table_params:
#         if add_not_remove == True:
#             matchs_tables[table_param[TABLE_PARAM.MATCH_INDEX]][table_param[TABLE_PARAM.TABLE_INDEX]] = table_param[TABLE_PARAM.NEW_TABLE]
#             add_history_each(matchs_tables[table_param[TABLE_PARAM.MATCH_INDEX]][table_param[TABLE_PARAM.TABLE_INDEX]])
#         else:
#             remove_history_each(matchs_tables[table_param[TABLE_PARAM.MATCH_INDEX]][table_param[TABLE_PARAM.TABLE_INDEX]])
#             matchs_tables[table_param[TABLE_PARAM.MATCH_INDEX]][table_param[TABLE_PARAM.TABLE_INDEX]] = []

# # 対戦履歴を無視して最適化を行う
# def adjust_matchs_tables(matchs_tables:list, player_list:list):
#     for i in range(TABLE_NUM):
#         index = (TABLE_NUM - 1) - i
#         added_tables_param, remove_tables_param = adjust_match_table(matchs_tables=matchs_tables, player_list=player_list, match_index=index, added_tables=[])
#         if len(added_tables_param) > 0 or len(remove_tables_param) > 0:
#             print_debug('修正', i,'週目 -', index, '回戦 から修正', log_level=LOG_LEVEL.L3_CALUCULATION_DETAIL)
#             print_debug('add:', [(t[0], t[1], player_to_name_table(t[TABLE_PARAM.NEW_TABLE])) for t in added_tables_param], 'len:', len(added_tables_param), log_level=LOG_LEVEL.L3_CALUCULATION_DETAIL)
#             print_debug('rem:', [(t[0], t[1], player_to_name_table(t[TABLE_PARAM.NEW_TABLE])) for t in remove_tables_param], 'len:', len(remove_tables_param), log_level=LOG_LEVEL.L3_CALUCULATION_DETAIL)
#             if len(added_tables_param) > len(remove_tables_param):
#                 change_matchs_tables_from_tables_diff(matchs_tables, added_tables_param, add_not_remove=True)
#                 change_matchs_tables_from_tables_diff(matchs_tables, remove_tables_param, add_not_remove=False)
#     return all([len(t) == TABLE_PLAYER_NUM for t in match_tables])
# # added_tables -> [0, 0, [Player, Player, Player]]
# # return -> 0, [matches_index, table_index, [Player, Player, Player], ok:bool]
# def adjust_match_table(matchs_tables:list, player_list:list, match_index:int, removed_tables:list=[], added_tables:list=[]):
#     temp_matchs_tables = copy.deepcopy(matchs_tables)
#     #temp_matchs_tables = [[[player for player in table] for table in match_tables] for match_tables in matchs_tables]
#     temp_added_tables = [t for t in added_tables]
#     temp_removed_tables = [t for t in removed_tables]
#     invalidated_table_indexes = []
#     for i, table in enumerate(temp_matchs_tables[match_index]):
#         for added_table in temp_added_tables:
#             if duplicate_player_count(table, added_table[TABLE_PARAM.NEW_TABLE]) >= 2:
#                 invalidated_table_indexes.append(i)
#                 remove_table_param = [match_index, i, temp_matchs_tables[match_index][i]]
#                 temp_removed_tables.append(remove_table_param)
#                 change_matchs_tables_from_tables_diff(temp_matchs_tables, [remove_table_param], add_not_remove=False)
#     for i, table in enumerate(temp_matchs_tables[match_index]):
#         if len(table) < TABLE_PLAYER_NUM:
#             invalidated_table_indexes.append(i)
#             change_matchs_tables_from_tables_diff(temp_matchs_tables, [[match_index, i, []]], add_not_remove=False)
#     print_debug(match_index+1, '回戦 無効なtable_index:', invalidated_table_indexes, log_level=LOG_LEVEL.L2_CALUCULATION_LOG)
#     if len(invalidated_table_indexes) <= 0:
#         return temp_added_tables, temp_removed_tables
#     print_debug(player_to_name_tables(temp_matchs_tables[match_index]), log_level=LOG_LEVEL.L3_CALUCULATION_DETAIL)
#     r = get_remain_player(tables=temp_matchs_tables[match_index], player_list=player_list)
#     print_debug('remain:', player_to_name_table(r), log_level=LOG_LEVEL.L2_CALUCULATION_LOG)
#     candidates_add_tables = get_all_tables_conbination(r, ignore_history=True)
#     print_debug('candidates1:', len(candidates_add_tables), [v for i, v in enumerate(player_to_name_tables(candidates_add_tables)) if i < 100], '...', log_level=LOG_LEVEL.L3_CALUCULATION_DETAIL)
#     #candidates_add_tables = [t for t in candidates_add_tables if (is_players_exist(tables=temp_matchs_tables[match_index], players=t))]
#     #print('candidates2:', len(candidates_add_tables))#, player_to_name_tables(candidates_add_tables))
#     if len(candidates_add_tables) > 0:
#         # 候補からテーブルを選ぶ
#         add_table_param = [match_index, invalidated_table_indexes[random.randint(0, len(invalidated_table_indexes) - 1)], get_table_compared(candidates_add_tables)]
#         temp_added_tables.append(add_table_param)
#         change_matchs_tables_from_tables_diff(temp_matchs_tables, [add_table_param], add_not_remove=True)
#         print_debug('current_match:', player_to_name_tables(temp_matchs_tables[match_index]), log_level=LOG_LEVEL.L2_CALUCULATION_LOG)
#         print_debug('added_tables:', player_to_name_table_params(temp_added_tables), log_level=LOG_LEVEL.L2_CALUCULATION_LOG)
#         print_debug('removed_tables:', player_to_name_table_params(temp_removed_tables), log_level=LOG_LEVEL.L2_CALUCULATION_LOG)
#         for i in range(len(matchs_tables)):
#             print_debug('match', i+1, player_to_name_tables(temp_matchs_tables[i]), log_level=LOG_LEVEL.L3_CALUCULATION_DETAIL)
#         added_tables, temp_removed_tables = adjust_match_table(matchs_tables=temp_matchs_tables, player_list=player_list, match_index=match_index-1, removed_tables=temp_removed_tables, added_tables=temp_added_tables)
#     return added_tables, temp_removed_tables

# def change_match_order(matchs_tables:list):
#     temp_arr = []
#     temp_indexes = [i for i in range(len(matchs_tables))]
#     while len(temp_indexes) > 0:
#         i = random.randint(0, len(temp_indexes) - 1)
#         del temp_indexes[i]
#         temp_arr.append(matchs_tables[i])
#     return temp_arr

def fill_match_tables_blank_swap(match_tables:list, player_list:list):
    remain_players = get_remain_player(match_tables, player_list)    
    for k, table in enumerate(match_tables):
        if len(table) < TABLE_PLAYER_NUM:
            table.clear()
        else:
            continue
        temp_indexes = []
        for i, p in enumerate(remain_players):
            print_debug('check remain_player', i, p.to_string(), log_level=LOG_LEVEL.L2_CALUCULATION_LOG)
            if len(table) < TABLE_PLAYER_NUM:
                if can_player_sit(p, match_tables, k, ignore_history=True):
                    print_debug('ok!', log_level=LOG_LEVEL.L2_CALUCULATION_LOG)
                    table.append(p)
                    temp_indexes.append(i)
                else:
                    print_debug('no...', log_level=LOG_LEVEL.L2_CALUCULATION_LOG)
                    swap_table_index, swap_player_index = get_swap_player(match_tables, k, p)
                    print_debug('get:', swap_table_index, swap_player_index, log_level=LOG_LEVEL.L3_CALUCULATION_DETAIL)
                    if swap_table_index >= 0 and swap_player_index >= 0:
                        temp = match_tables[swap_table_index][swap_player_index]
                        match_tables[swap_table_index][swap_player_index] = p
                        table.append(temp)
                        temp_indexes.append(i)
                        print_debug('swap:', p.to_string(), '-', temp.to_string(), log_level=LOG_LEVEL.L2_CALUCULATION_LOG)
            else:
                break
        remain_players = [p for i, p in enumerate(remain_players) if i not in temp_indexes]
def get_swap_player(match_tables:list, swap_match_index:int, swap_player:Player):
    temp_match_index = -1
    temp_table_index = -1
    temp_score = 0
    for match_table_index, match_table in enumerate(match_tables):
        if match_table_index == swap_match_index:
            continue
        print_debug('search:', match_table_index, player_to_name_table(match_table), log_level=LOG_LEVEL.L2_CALUCULATION_LOG)
        # すでに同じTeamが存在している
        if swap_player.team in [t.team for t in match_table]:
            print_debug('- duplicate:', get_team_name(swap_player.team), log_level=LOG_LEVEL.L3_CALUCULATION_DETAIL)
            continue
        else:
            print_debug('- try', player_to_name_table(match_tables[swap_match_index]), player_to_name_table(match_table), log_level=LOG_LEVEL.L3_CALUCULATION_DETAIL)
            for match_player_index, match_player in enumerate(match_table):
                # match_playerをswap_matchの中に入れられるか
                if match_player.team not in [q.team for q in match_tables[swap_match_index]]:
                    print_debug('ok:', match_player.to_string(), log_level=LOG_LEVEL.L3_CALUCULATION_DETAIL)
                    score = get_score(match_player, [a for a in match_tables[swap_match_index] if a != swap_player]) + get_score(swap_player, [a for a in match_table if a != match_player])
                    if (temp_match_index < 0 or temp_table_index < 0) or score > temp_score:
                        temp_match_index = match_table_index
                        temp_table_index = match_player_index
                        temp_score = score
                else:
                    print_debug('no:', match_player.to_string(), log_level=LOG_LEVEL.L3_CALUCULATION_DETAIL)
    return (temp_match_index, temp_table_index)
                
def fast_check_match_tables(match_tables:list):
    for k, table in enumerate(match_tables):
        if len(table) < TABLE_PLAYER_NUM:
            match_tables[k] = []
            table = []
        print_debug(player_to_name_table(table), log_level=LOG_LEVEL.L0_RESULT_ONLY)
    r = get_remain_player(match_tables, player_list)
    print_debug('remain_player:', player_to_name_table(r), 'len:', len(r), log_level=LOG_LEVEL.L1_DETAIL)
    c = collections.Counter(sorted(itertools.chain.from_iterable(player_to_name_tables(match_tables))))
    print_debug('player_count:', c, log_level=LOG_LEVEL.L1_DETAIL)
    print_debug('player ok:', all(count == 1 for count in c.values()), log_level=LOG_LEVEL.L0_RESULT_ONLY)
    print_debug('table_count ok:', len(c) == TABLE_NUM * TABLE_PLAYER_NUM, log_level=LOG_LEVEL.L0_RESULT_ONLY)
def fast_check_matchs(matchs_tables:list):
    print_table_count(matchs_tables=matchs_tables)
    print_history_again(matchs_tables)
    #print_history(matchs_tables)

if __name__ == '__main__':
    # プレイヤーリストの作成
    player_list = []
    for i in range(TEAM_NUM):
        for k in range(TEAM_PLAYER_NUM):
            player = Player(i, k)
            player_list.append(player)

    names = player_to_name_table(player_list)
    print('メンバー')
    print(names)
    # ① とりあえず配置
    print('# first step')
    matchs_tables = [[] for i in range(MATCH_NUM)]
    for i, match_tables in enumerate(matchs_tables):
        print(i+1,'回戦')
        match_tables.extend(generate_match_tables(player_list))
        fast_check_match_tables(match_tables)
    fast_check_matchs(matchs_tables)

    # print('# second step')
    # # ② 隙間を埋める
    # for i, match_tables in enumerate(matchs_tables):
    #     print(i+1,'回戦')
    #     fill_match_tables_blank(match_tables, player_list)
    #     fast_check_match_tables(match_tables)
    # fast_check_matchs(matchs_tables)

    # print('# third step')
    # # ③ 入れ替えて隙間を埋める
    # for i in range(100):
    #     change_match_order(matchs_tables)
    #     finish = adjust_matchs_tables(matchs_tables, player_list)
    #     if finish:
    #         break
    # for i, match_tables in enumerate(matchs_tables):
    #     print(i+1,'回戦')
    #     fast_check_match_tables(match_tables)
    # fast_check_matchs(matchs_tables)

    print('# forth step')
    # ④ 埋められない隙間を入れ替えて入れる
    for i, match_tables in enumerate(matchs_tables):
        print(i+1,'回戦')
        fill_match_tables_blank_swap(match_tables, player_list)
        fast_check_match_tables(match_tables)
    fast_check_matchs(matchs_tables)

"""
% python3 MahjongLeagueTable.py 
メンバー
['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4', 'C1', 'C2', 'C3', 'C4', 'D1', 'D2', 'D3', 'D4', 'E1', 'E2', 'E3', 'E4', 'F1', 'F2', 'F3', 'F4', 'G1', 'G2', 'G3', 'G4', 'H1', 'H2', 'H3', 'H4']
# first step
1 回戦
['F3', 'A4', 'G3', 'B3']
['D3', 'A2', 'B1', 'H3']
['H4', 'C3', 'G2', 'E2']
['C2', 'E3', 'F2', 'B4']
['F4', 'H1', 'G1', 'A3']
['A1', 'E1', 'F1', 'G4']
['B2', 'D2', 'E4', 'H2']
[]
remain_player: ['C1', 'C4', 'D1', 'D4'] len: 4
player_count: Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C2': 1, 'C3': 1, 'D2': 1, 'D3': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
player ok: True
table_count ok: False
2 回戦
['D1', 'B3', 'H3', 'A1']
['E1', 'D2', 'B4', 'A4']
['G1', 'D3', 'H4', 'F1']
['E4', 'F4', 'G2', 'B1']
['G3', 'C1', 'H2', 'D4']
['E2', 'A2', 'C4', 'F3']
['E3', 'G4', 'A3', 'B2']
[]
remain_player: ['C2', 'C3', 'F2', 'H1'] len: 4
player_count: Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H2': 1, 'H3': 1, 'H4': 1})
player ok: True
table_count ok: False
3 回戦
['E3', 'H3', 'G3', 'F1']
['A2', 'D4', 'H4', 'B3']
['H1', 'E1', 'B2', 'C4']
['D2', 'F3', 'A1', 'G2']
['D3', 'C1', 'G4', 'E2']
['B1', 'F2', 'D1', 'A4']
[]
['B4', 'G1', 'H2', 'C3']
remain_player: ['A3', 'C2', 'E4', 'F4'] len: 4
player_count: Counter({'A1': 1, 'A2': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
player ok: True
table_count ok: False
4 回戦
['H3', 'C3', 'F2', 'B2']
['H1', 'G4', 'B4', 'A2']
['F1', 'E2', 'B3', 'D2']
['A4', 'C1', 'H4', 'E4']
['A3', 'H2', 'C4', 'G2']
['E1', 'D4', 'F3', 'B1']
['A1', 'C2', 'F4', 'G3']
[]
remain_player: ['D1', 'D3', 'E3', 'G1'] len: 4
player_count: Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D2': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
player ok: True
table_count ok: False
5 回戦
['G4', 'F3', 'H2', 'C2']
['H1', 'D3', 'G2', 'E3']
['G1', 'B2', 'A4', 'D4']
['D1', 'A3', 'E2', 'G3']
['H4', 'F2', 'D2', 'C4']
[]
['C1', 'B3', 'F4', 'E1']
['A2', 'C3', 'F1', 'E4']
remain_player: ['A1', 'B1', 'B4', 'H3'] len: 4
player_count: Counter({'A2': 1, 'A3': 1, 'A4': 1, 'B2': 1, 'B3': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H4': 1})
player ok: True
table_count ok: False
6 回戦
['F3', 'C3', 'H1', 'D1']
['H2', 'A1', 'E2', 'F2']
['D2', 'E3', 'C1', 'A2']
['G3', 'B4', 'C4', 'E4']
['E1', 'D3', 'A3', 'C2']
[]
[]
[]
remain_player: ['A4', 'B1', 'B2', 'B3', 'D4', 'F1', 'F4', 'G1', 'G2', 'G4', 'H3', 'H4'] len: 12
player_count: Counter({'A1': 1, 'A2': 1, 'A3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F2': 1, 'F3': 1, 'G3': 1, 'H1': 1, 'H2': 1})
player ok: True
table_count ok: False
7 回戦
['D4', 'G4', 'C4', 'H3']
['D1', 'E4', 'G1', 'C2']
['A3', 'F3', 'H4', 'B4']
['E1', 'G2', 'F2', 'A2']
['A1', 'B1', 'E3', 'C3']
[]
[]
[]
remain_player: ['A4', 'B2', 'B3', 'C1', 'D2', 'D3', 'E2', 'F1', 'F4', 'G3', 'H1', 'H2'] len: 12
player_count: Counter({'A1': 1, 'A2': 1, 'A3': 1, 'B1': 1, 'B4': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D4': 1, 'E1': 1, 'E3': 1, 'E4': 1, 'F2': 1, 'F3': 1, 'G1': 1, 'G2': 1, 'G4': 1, 'H3': 1, 'H4': 1})
player ok: True
table_count ok: False
8 回戦
['H4', 'G4', 'D1', 'F4']
['G3', 'H1', 'B1', 'D2']
[]
['E4', 'B3', 'F2', 'A3']
[]
[]
[]
[]
remain_player: ['A1', 'A2', 'A4', 'B2', 'B4', 'C1', 'C2', 'C3', 'C4', 'D3', 'D4', 'E1', 'E2', 'E3', 'F1', 'F3', 'G1', 'G2', 'H2', 'H3'] len: 20
player_count: Counter({'A3': 1, 'B1': 1, 'B3': 1, 'D1': 1, 'D2': 1, 'E4': 1, 'F2': 1, 'F4': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H4': 1})
player ok: True
table_count ok: False
tables_count: [7, 7, 7, 7, 7, 5, 5, 3]
all_tables_count: 48
match history:
A1 -> Counter({'B1': 1, 'B3': 1, 'C2': 1, 'C3': 1, 'D1': 1, 'D2': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H2': 1, 'H3': 1}) total_match_count: 6 duplicate: 0
A2 -> Counter({'B1': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C3': 1, 'C4': 1, 'D2': 1, 'D3': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'G2': 1, 'G4': 1, 'H1': 1, 'H3': 1, 'H4': 1}) total_match_count: 7 duplicate: 0
A3 -> Counter({'B2': 1, 'B3': 1, 'B4': 1, 'C2': 1, 'C4': 1, 'D1': 1, 'D3': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H4': 1}) total_match_count: 7 duplicate: 0
A4 -> Counter({'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'D1': 1, 'D2': 1, 'D4': 1, 'E1': 1, 'E4': 1, 'F2': 1, 'F3': 1, 'G1': 1, 'G3': 1, 'H4': 1}) total_match_count: 5 duplicate: 0
B1 -> Counter({'A1': 1, 'A2': 1, 'A4': 1, 'C3': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1, 'E1': 1, 'E3': 1, 'E4': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G2': 1, 'G3': 1, 'H1': 1, 'H3': 1}) total_match_count: 6 duplicate: 0
B2 -> Counter({'A3': 1, 'A4': 1, 'C3': 1, 'C4': 1, 'D2': 1, 'D4': 1, 'E1': 1, 'E3': 1, 'E4': 1, 'F2': 1, 'G1': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H3': 1}) total_match_count: 5 duplicate: 0
B3 -> Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'C1': 1, 'D1': 1, 'D2': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G3': 1, 'H3': 1, 'H4': 1}) total_match_count: 6 duplicate: 0
B4 -> Counter({'A2': 1, 'A3': 1, 'A4': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D2': 1, 'E1': 1, 'E3': 1, 'E4': 1, 'F2': 1, 'F3': 1, 'G1': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H4': 1}) total_match_count: 6 duplicate: 0
C1 -> Counter({'A2': 1, 'A4': 1, 'B3': 1, 'D2': 1, 'D3': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F4': 1, 'G3': 1, 'G4': 1, 'H2': 1, 'H4': 1}) total_match_count: 5 duplicate: 0
C2 -> Counter({'A1': 1, 'A3': 1, 'B4': 1, 'D1': 1, 'D3': 1, 'E1': 1, 'E3': 1, 'E4': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G3': 1, 'G4': 1, 'H2': 1}) total_match_count: 5 duplicate: 0
C3 -> Counter({'A1': 1, 'A2': 1, 'B1': 1, 'B2': 1, 'B4': 1, 'D1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'G1': 1, 'G2': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1}) total_match_count: 6 duplicate: 0
C4 -> Counter({'A2': 1, 'A3': 1, 'B2': 1, 'B4': 1, 'D2': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'E4': 1, 'F2': 1, 'F3': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1}) total_match_count: 6 duplicate: 0
D1 -> Counter({'A1': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B3': 1, 'C2': 1, 'C3': 1, 'E2': 1, 'E4': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H3': 1, 'H4': 1}) total_match_count: 6 duplicate: 0
D2 -> Counter({'A1': 1, 'A2': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C4': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'G2': 1, 'G3': 1, 'H1': 1, 'H2': 1, 'H4': 1}) total_match_count: 7 duplicate: 0
D3 -> Counter({'A2': 1, 'A3': 1, 'B1': 1, 'C1': 1, 'C2': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'F1': 1, 'G1': 1, 'G2': 1, 'G4': 1, 'H1': 1, 'H3': 1, 'H4': 1}) total_match_count: 5 duplicate: 0
D4 -> Counter({'A2': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'C1': 1, 'C4': 1, 'E1': 1, 'F3': 1, 'G1': 1, 'G3': 1, 'G4': 1, 'H2': 1, 'H3': 1, 'H4': 1}) total_match_count: 5 duplicate: 0
E1 -> Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C4': 1, 'D2': 1, 'D3': 1, 'D4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G2': 1, 'G4': 1, 'H1': 1}) total_match_count: 7 duplicate: 0
E2 -> Counter({'A1': 1, 'A2': 1, 'A3': 1, 'B3': 1, 'C1': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H2': 1, 'H4': 1}) total_match_count: 6 duplicate: 0
E3 -> Counter({'A1': 1, 'A2': 1, 'A3': 1, 'B1': 1, 'B2': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'D2': 1, 'D3': 1, 'F1': 1, 'F2': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H3': 1}) total_match_count: 6 duplicate: 0
E4 -> Counter({'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'F1': 1, 'F2': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'H2': 1, 'H4': 1}) total_match_count: 7 duplicate: 0
F1 -> Counter({'A1': 1, 'A2': 1, 'B3': 1, 'C3': 1, 'D2': 1, 'D3': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'G1': 1, 'G3': 1, 'G4': 1, 'H3': 1, 'H4': 1}) total_match_count: 5 duplicate: 0
F2 -> Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'G2': 1, 'H2': 1, 'H3': 1, 'H4': 1}) total_match_count: 7 duplicate: 0
F3 -> Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B3': 1, 'B4': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H4': 1}) total_match_count: 7 duplicate: 0
F4 -> Counter({'A1': 1, 'A3': 1, 'B1': 1, 'B3': 1, 'C1': 1, 'C2': 1, 'D1': 1, 'E1': 1, 'E4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H4': 1}) total_match_count: 5 duplicate: 0
G1 -> Counter({'A3': 1, 'A4': 1, 'B2': 1, 'B4': 1, 'C2': 1, 'C3': 1, 'D1': 1, 'D3': 1, 'D4': 1, 'E4': 1, 'F1': 1, 'F4': 1, 'H1': 1, 'H2': 1, 'H4': 1}) total_match_count: 5 duplicate: 0
G2 -> Counter({'A1': 1, 'A2': 1, 'A3': 1, 'B1': 1, 'C3': 1, 'C4': 1, 'D2': 1, 'D3': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'H1': 1, 'H2': 1, 'H4': 1}) total_match_count: 6 duplicate: 0
G3 -> Counter({'A1': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D4': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F3': 1, 'F4': 1, 'H1': 1, 'H2': 1, 'H3': 1}) total_match_count: 7 duplicate: 0
G4 -> Counter({'A1': 1, 'A2': 1, 'A3': 1, 'B2': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C4': 1, 'D1': 1, 'D3': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'F1': 1, 'F3': 1, 'F4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1}) total_match_count: 7 duplicate: 0
H1 -> Counter({'A2': 1, 'A3': 1, 'B1': 1, 'B2': 1, 'B4': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'E1': 1, 'E3': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1}) total_match_count: 6 duplicate: 0
H2 -> Counter({'A1': 1, 'A3': 1, 'B2': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D2': 1, 'D4': 1, 'E2': 1, 'E4': 1, 'F2': 1, 'F3': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1}) total_match_count: 6 duplicate: 0
H3 -> Counter({'A1': 1, 'A2': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D3': 1, 'D4': 1, 'E3': 1, 'F1': 1, 'F2': 1, 'G3': 1, 'G4': 1}) total_match_count: 5 duplicate: 0
H4 -> Counter({'A2': 1, 'A3': 1, 'A4': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1, 'E2': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G4': 1}) total_match_count: 7 duplicate: 0
# forth step
1 回戦
['F3', 'A4', 'G3', 'B3']
['D3', 'A2', 'B1', 'C4']
['H4', 'C3', 'G2', 'E2']
['C2', 'E3', 'F2', 'D4']
['F4', 'H1', 'G1', 'A3']
['A1', 'E1', 'F1', 'G4']
['B2', 'D2', 'E4', 'H2']
['C1', 'H3', 'D1', 'B4']
remain_player: [] len: 0
player_count: Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
player ok: True
table_count ok: True
2 回戦
['D1', 'B3', 'H3', 'A1']
['E1', 'D2', 'B4', 'C3']
['G1', 'D3', 'H4', 'F1']
['E4', 'F4', 'G2', 'B1']
['G3', 'C1', 'H2', 'D4']
['E2', 'A2', 'C4', 'F3']
['E3', 'G4', 'A3', 'B2']
['C2', 'A4', 'F2', 'H1']
remain_player: [] len: 0
player_count: Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
player ok: True
table_count ok: True
3 回戦
['E3', 'H3', 'G3', 'F1']
['A2', 'D4', 'H4', 'B3']
['H1', 'E1', 'B2', 'C4']
['D2', 'F3', 'A1', 'G2']
['D3', 'C1', 'G4', 'E2']
['B1', 'F2', 'D1', 'A4']
['A3', 'C2', 'E4', 'F4']
['B4', 'G1', 'H2', 'C3']
remain_player: [] len: 0
player_count: Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
player ok: True
table_count ok: True
4 回戦
['D3', 'C3', 'F2', 'B2']
['H1', 'G4', 'B4', 'A2']
['F1', 'E2', 'B3', 'D2']
['A4', 'C1', 'H4', 'E4']
['A3', 'H2', 'C4', 'G2']
['E1', 'D4', 'F3', 'B1']
['A1', 'C2', 'F4', 'G3']
['D1', 'H3', 'E3', 'G1']
remain_player: [] len: 0
player_count: Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
player ok: True
table_count ok: True
5 回戦
['G4', 'F3', 'H2', 'C2']
['B4', 'D3', 'G2', 'E3']
['G1', 'B2', 'A4', 'D4']
['D1', 'A3', 'E2', 'G3']
['H4', 'F2', 'D2', 'C4']
['A1', 'B1', 'H1', 'C1']
['H3', 'B3', 'F4', 'E1']
['A2', 'C3', 'F1', 'E4']
remain_player: [] len: 0
player_count: Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
player ok: True
table_count ok: True
6 回戦
['F3', 'C3', 'H1', 'D1']
['G4', 'A1', 'E2', 'F2']
['D2', 'E3', 'F4', 'A2']
['G3', 'B4', 'C4', 'E4']
['E1', 'B3', 'A3', 'H4']
['A4', 'B1', 'H2', 'D3']
['D4', 'F1', 'C1', 'G1']
['G2', 'B2', 'H3', 'C2']
remain_player: [] len: 0
player_count: Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
player ok: True
table_count ok: True
7 回戦
['D4', 'G4', 'C4', 'B3']
['D1', 'E4', 'G1', 'C2']
['A3', 'F3', 'H4', 'B4']
['E1', 'G2', 'F2', 'A2']
['A1', 'B1', 'E3', 'C3']
['A4', 'H2', 'D3', 'C1']
['D2', 'H3', 'E2', 'F1']
['F4', 'G3', 'H1', 'B2']
remain_player: [] len: 0
player_count: Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
player ok: True
table_count ok: True
8 回戦
['A2', 'E3', 'C2', 'H3']
['G3', 'C3', 'A4', 'D2']
['A1', 'H4', 'B1', 'G4']
['E4', 'D4', 'F2', 'A3']
['B4', 'C1', 'F3', 'H1']
['C4', 'D3', 'B3', 'E1']
['G2', 'B2', 'F1', 'D1']
['G1', 'E2', 'H2', 'F4']
remain_player: [] len: 0
player_count: Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
player ok: True
table_count ok: True
tables_count: [8, 8, 8, 8, 8, 8, 8, 8]
all_tables_count: 64
match history:
A1 -> Counter({'B1': 3, 'G4': 3, 'B3': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'D1': 1, 'D2': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G2': 1, 'G3': 1, 'H1': 1, 'H3': 1, 'H4': 1}) total_match_count: 8 duplicate: 6
A2 -> Counter({'C4': 2, 'E3': 2, 'B1': 1, 'B3': 1, 'B4': 1, 'C2': 1, 'C3': 1, 'D2': 1, 'D3': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G2': 1, 'G4': 1, 'H1': 1, 'H3': 1, 'H4': 1}) total_match_count: 8 duplicate: 4
A3 -> Counter({'E4': 2, 'F4': 2, 'H4': 2, 'B2': 1, 'B3': 1, 'B4': 1, 'C2': 1, 'C4': 1, 'D1': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'F2': 1, 'F3': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1}) total_match_count: 8 duplicate: 6
A4 -> Counter({'B1': 2, 'C1': 2, 'D3': 2, 'F2': 2, 'G3': 2, 'H2': 2, 'B2': 1, 'B3': 1, 'C2': 1, 'C3': 1, 'D1': 1, 'D2': 1, 'D4': 1, 'E4': 1, 'F3': 1, 'G1': 1, 'H1': 1, 'H4': 1}) total_match_count: 8 duplicate: 12
B1 -> Counter({'A1': 3, 'A4': 2, 'D3': 2, 'A2': 1, 'C1': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D4': 1, 'E1': 1, 'E3': 1, 'E4': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G2': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H4': 1}) total_match_count: 8 duplicate: 7
B2 -> Counter({'G2': 2, 'H1': 2, 'A3': 1, 'A4': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1, 'E1': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F4': 1, 'G1': 1, 'G3': 1, 'G4': 1, 'H2': 1, 'H3': 1}) total_match_count: 8 duplicate: 4
B3 -> Counter({'E1': 3, 'C4': 2, 'D4': 2, 'H3': 2, 'H4': 2, 'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'E2': 1, 'F1': 1, 'F3': 1, 'F4': 1, 'G3': 1, 'G4': 1}) total_match_count: 8 duplicate: 11
B4 -> Counter({'C1': 2, 'C3': 2, 'F3': 2, 'H1': 2, 'A2': 1, 'A3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'E1': 1, 'E3': 1, 'E4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H2': 1, 'H3': 1, 'H4': 1}) total_match_count: 8 duplicate: 8
C1 -> Counter({'A4': 2, 'B4': 2, 'D3': 2, 'D4': 2, 'H1': 2, 'H2': 2, 'A1': 1, 'B1': 1, 'D1': 1, 'E2': 1, 'E4': 1, 'F1': 1, 'F3': 1, 'G1': 1, 'G3': 1, 'G4': 1, 'H3': 1, 'H4': 1}) total_match_count: 8 duplicate: 12
C2 -> Counter({'E3': 2, 'E4': 2, 'F2': 2, 'F4': 2, 'H3': 2, 'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B2': 1, 'D1': 1, 'D4': 1, 'F3': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1}) total_match_count: 8 duplicate: 10
C3 -> Counter({'B4': 2, 'D2': 2, 'A1': 1, 'A2': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'D1': 1, 'D3': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'H1': 1, 'H2': 1, 'H4': 1}) total_match_count: 8 duplicate: 4
C4 -> Counter({'A2': 2, 'B3': 2, 'D3': 2, 'E1': 2, 'A3': 1, 'B1': 1, 'B2': 1, 'B4': 1, 'D2': 1, 'D4': 1, 'E2': 1, 'E4': 1, 'F2': 1, 'F3': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H4': 1}) total_match_count: 8 duplicate: 8
D1 -> Counter({'H3': 3, 'G1': 2, 'A1': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'G2': 1, 'G3': 1, 'H1': 1}) total_match_count: 8 duplicate: 5
D2 -> Counter({'C3': 2, 'E2': 2, 'F1': 2, 'A1': 1, 'A2': 1, 'A4': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C4': 1, 'E1': 1, 'E3': 1, 'E4': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G2': 1, 'G3': 1, 'H2': 1, 'H3': 1, 'H4': 1}) total_match_count: 8 duplicate: 6
D3 -> Counter({'A4': 2, 'B1': 2, 'C1': 2, 'C4': 2, 'H2': 2, 'A2': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C3': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'F1': 1, 'F2': 1, 'G1': 1, 'G2': 1, 'G4': 1, 'H4': 1}) total_match_count: 8 duplicate: 10
D4 -> Counter({'B3': 2, 'C1': 2, 'F2': 2, 'G1': 2, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'C2': 1, 'C4': 1, 'E1': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F3': 1, 'G3': 1, 'G4': 1, 'H2': 1, 'H4': 1}) total_match_count: 8 duplicate: 8
E1 -> Counter({'B3': 3, 'C4': 2, 'A1': 1, 'A2': 1, 'A3': 1, 'B1': 1, 'B2': 1, 'B4': 1, 'C3': 1, 'D2': 1, 'D3': 1, 'D4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G2': 1, 'G4': 1, 'H1': 1, 'H3': 1, 'H4': 1}) total_match_count: 8 duplicate: 5
E2 -> Counter({'D2': 2, 'F1': 2, 'G4': 2, 'A1': 1, 'A2': 1, 'A3': 1, 'B3': 1, 'C1': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D3': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'H2': 1, 'H3': 1, 'H4': 1}) total_match_count: 8 duplicate: 6
E3 -> Counter({'H3': 3, 'A2': 2, 'C2': 2, 'A1': 1, 'A3': 1, 'B1': 1, 'B2': 1, 'B4': 1, 'C3': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1, 'F1': 1, 'F2': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1}) total_match_count: 8 duplicate: 7
E4 -> Counter({'A3': 2, 'C2': 2, 'F4': 2, 'A2': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B4': 1, 'C1': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D4': 1, 'F1': 1, 'F2': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'H2': 1, 'H4': 1}) total_match_count: 8 duplicate: 6
F1 -> Counter({'D2': 2, 'E2': 2, 'G1': 2, 'H3': 2, 'A1': 1, 'A2': 1, 'B2': 1, 'B3': 1, 'C1': 1, 'C3': 1, 'D1': 1, 'D3': 1, 'D4': 1, 'E1': 1, 'E3': 1, 'E4': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H4': 1}) total_match_count: 8 duplicate: 8
F2 -> Counter({'A4': 2, 'C2': 2, 'D4': 2, 'A1': 1, 'A2': 1, 'A3': 1, 'B1': 1, 'B2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'G2': 1, 'G4': 1, 'H1': 1, 'H4': 1}) total_match_count: 8 duplicate: 6
F3 -> Counter({'B4': 2, 'H1': 2, 'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B3': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H2': 1, 'H4': 1}) total_match_count: 8 duplicate: 4
F4 -> Counter({'A3': 2, 'C2': 2, 'E4': 2, 'G1': 2, 'G3': 2, 'H1': 2, 'A1': 1, 'A2': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'D2': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'G2': 1, 'H2': 1, 'H3': 1}) total_match_count: 8 duplicate: 12
G1 -> Counter({'D1': 2, 'D4': 2, 'F1': 2, 'F4': 2, 'H2': 2, 'A3': 1, 'A4': 1, 'B2': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'D3': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'H1': 1, 'H3': 1, 'H4': 1}) total_match_count: 8 duplicate: 10
G2 -> Counter({'B2': 2, 'A1': 1, 'A2': 1, 'A3': 1, 'B1': 1, 'B4': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'H2': 1, 'H3': 1, 'H4': 1}) total_match_count: 8 duplicate: 2
G3 -> Counter({'A4': 2, 'F4': 2, 'A1': 1, 'A3': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D4': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F3': 1, 'H1': 1, 'H2': 1, 'H3': 1}) total_match_count: 8 duplicate: 4
G4 -> Counter({'A1': 3, 'E2': 2, 'A2': 1, 'A3': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C4': 1, 'D3': 1, 'D4': 1, 'E1': 1, 'E3': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'H1': 1, 'H2': 1, 'H4': 1}) total_match_count: 8 duplicate: 5
H1 -> Counter({'B2': 2, 'B4': 2, 'C1': 2, 'F3': 2, 'F4': 2, 'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'E1': 1, 'F2': 1, 'G1': 1, 'G3': 1, 'G4': 1}) total_match_count: 8 duplicate: 10
H2 -> Counter({'A4': 2, 'C1': 2, 'D3': 2, 'G1': 2, 'A3': 1, 'B1': 1, 'B2': 1, 'B4': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D2': 1, 'D4': 1, 'E2': 1, 'E4': 1, 'F3': 1, 'F4': 1, 'G2': 1, 'G3': 1, 'G4': 1}) total_match_count: 8 duplicate: 8
H3 -> Counter({'D1': 3, 'E3': 3, 'B3': 2, 'C2': 2, 'F1': 2, 'A1': 1, 'A2': 1, 'B2': 1, 'B4': 1, 'C1': 1, 'D2': 1, 'E1': 1, 'E2': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1}) total_match_count: 8 duplicate: 12
H4 -> Counter({'A3': 2, 'B3': 2, 'A1': 1, 'A2': 1, 'A4': 1, 'B1': 1, 'B4': 1, 'C1': 1, 'C3': 1, 'C4': 1, 'D2': 1, 'D3': 1, 'D4': 1, 'E1': 1, 'E2': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'G1': 1, 'G2': 1, 'G4': 1}) total_match_count: 8 duplicate: 4
"""