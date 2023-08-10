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
    # return False # 完全ランダム
    return True # 対戦回数重視
    # return index > 0 # 途中から対戦回収重視

### チーム名 ###
TEAM_LIST = { 0:'A', 1:'B', 2:'C', 3:'D', 4:'E', 5:'F', 6:'G', 7:'H' }
def get_team_name(index:int):
    if index in TEAM_LIST.keys():
        return str(TEAM_LIST[index])
    else:
        return str(index)

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
    a_score = -a.get_match_num() + (can_player_sit(a, tables, table_index) if 0 else -999)
    b_score = -b.get_match_num() + (can_player_sit(b, tables, table_index) if 0 else -999)
    return a_score - b_score
def compare_name(player:Player):
    return player.team * TEAM_PLAYER_NUM + int(player.name)

### ルール, 条件チェック
def can_player_sit(target:Player, tables:list, table_index:int):
    return not_duplicate_player(target=target, tables=tables) and can_player_sit_to_table(target=target, table=tables[table_index])
def can_player_sit_to_table(target:Player, table:list, ignore_history:bool=FALSE, ignore_team:bool=FALSE):
    for p in table:
        if (target in table) or (target.team == p.team and ignore_team == FALSE) or (target.is_contain_history(p) and ignore_history == FALSE):
            return False
    return True
def not_duplicate_player(target:Player, tables:list):
    for table in tables:
        if target in table:
            return False
    return True
def not_duplicate_table(tables:list, target_table:list):
    for p in target_table:
        if not_duplicate_player(p, tables) == False:
            return False
    return True
def duplicate_player_count(table1:list, table2:list):
    count = 0
    for p in table1:
        if p in table2:
            count += 1
    return count

### 文字列出力
# 対戦履歴を全て出力
def print_history(player_list:list):
    for p in player_list:
        print(p.to_string(), '->', collections.Counter([h.to_string() for h in sorted(p.history, key=compare_name)]))
def print_hisotry_again(matchs_tables:list):
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
    v = [k for k, v in collections.Counter(l).items() if v > 1]
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
    print('tables_count:', created_table_count)
    print('all_tables_count', sum(created_table_count))

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
        print(player_to_name_table(table))
    print('remain_player', player_to_name_table(get_remain_player(tables)))
    return tables
# 対戦回数が等しくなるように配置する
def get_tables_from_history(player_list:list, tables_num=TABLE_NUM, table_player_num=TABLE_PLAYER_NUM):
    tables = [[] for i in range(tables_num)]
    for i in range(tables_num):
        for k in range(table_player_num):
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
def get_tables_can_be_inserted(tables:list) -> list:
    tables = [t for t in get_all_tables(get_remain_player(tables)) if not_duplicate_table([t for t in tables if len(t) >= TABLE_PLAYER_NUM], t)]
    return tables
# 余ったプレイヤーを取得する
def get_remain_player(tables:list) -> list:
    remain_player_list = []
    for table in tables:
        if len(table) < TABLE_PLAYER_NUM:
            remain_player_list.extend(table)
    return remain_player_list

# 隙間を埋める
def fill_match_tables_blank(match_tables:list):
    for i, table in enumerate(match_tables):
        table_candidates = get_tables_can_be_inserted(tables=match_tables)
        if len(table_candidates) <= 0:
            break
        if len(table) < TABLE_PLAYER_NUM:
            v = match_tables[i]
            match_tables[i] = table_candidates[0]
            print(player_to_name_table(v), '->', player_to_name_table(match_tables[i]))

def change_matchs_tables_from_tables_diff(matchs_tables:list, table_params:list, add_not_remove:bool = True):
    for table_param in table_params:
        if add_not_remove == True:
            matchs_tables[table_param[TABLE_PARAM.MATCH_INDEX]][table_param[TABLE_PARAM.TABLE_INDEX]] = table_param[TABLE_PARAM.NEW_TABLE]
            add_history_each(matchs_tables[table_param[TABLE_PARAM.MATCH_INDEX]][table_param[TABLE_PARAM.TABLE_INDEX]])
        else:
            remove_history_each(matchs_tables[[table_params[TABLE_PARAM.NEW_TABLE]]])
            matchs_tables[table_param[TABLE_PARAM.MATCH_INDEX]][table_param[TABLE_PARAM.TABLE_INDEX]] = []


# 対戦履歴を無視して最適化を行う
def adjust_matchs_tables(matchs_tables:list):
    for i in range(TABLE_NUM):
        index = (TABLE_NUM - 1) - i
        added_tables_param, remove_tables_param = adjust_match_table(matchs_tables, index, added_tables=[])
        if len(added_tables_param) > 0 or len(remove_tables_param) > 0:
            print('修正', i,'週目 -', index, '回戦 から修正')
            print('add:', [(t[0], t[1], player_to_name_table(t[TABLE_PARAM.NEW_TABLE])) for t in added_tables_param], 'len:', len(added_tables_param))
            print('rem:', [(t[0], t[1], player_to_name_table(t[TABLE_PARAM.NEW_TABLE])) for t in remove_tables_param], 'len:', len(remove_tables_param))
            ### これの追加タイミングがおかしい...
            if len(added_tables_param) > len(remove_tables_param):
                # for t in remove_tables:
                #     remove_history_each(matchs_tables[t[TABLE_PARAM.MATCH_INDEX]][t[TABLE_PARAM.TABLE_INDEX]])
                #     matchs_tables[t[TABLE_PARAM.MATCH_INDEX]][t[TABLE_PARAM.TABLE_INDEX]] = []
                # for t in added_tables:
                #     matchs_tables[t[TABLE_PARAM.MATCH_INDEX]][t[TABLE_PARAM.TABLE_INDEX]] = t[TABLE_PARAM.NEW_TABLE]
                #     add_history_each(matchs_tables[t[TABLE_PARAM.MATCH_INDEX]][t[TABLE_PARAM.TABLE_INDEX]])
                change_matchs_tables_from_tables_diff(matchs_tables, added_tables_param, add_not_remove=True)
                change_matchs_tables_from_tables_diff(matchs_tables, remove_tables_param, add_not_remove=False)
# added_tables -> [0, 0, [Player, Player, Player]]
# return -> 0, [matches_index, table_index, [Player, Player, Player], ok:bool]
def adjust_match_table(matchs_tables:list, match_index:int, removed_tables:list=[], added_tables:list=[]):
    temp_matchs_tables = copy.deepcopy(matchs_tables)
    temp_added_tables = copy.deepcopy(added_tables)
    temp_removed_tables = copy.deepcopy(removed_tables)
    invalidated_table_indexes = []
    for i, table in enumerate(temp_matchs_tables[match_index]):
        for added_table in added_tables:
            if duplicate_player_count(table, added_table[TABLE_PARAM.NEW_TABLE]) >= 2:
                invalidated_table_indexes.append(i)
                remove_table_param = [match_index, i, temp_matchs_tables[match_index][i]]
                temp_removed_tables.append(remove_table_param)
                change_matchs_tables_from_tables_diff(temp_matchs_tables, [remove_table_param], add_not_remove=FALSE)
    for i, table in enumerate(temp_matchs_tables[match_index]):
        if len(table) < TABLE_PLAYER_NUM:
            invalidated_table_indexes.append(i)
    # print(match_index, '回戦 無効なtable_index:', invalidated_table_indexes)
    if len(invalidated_table_indexes) <= 0:
        return added_tables, temp_removed_tables
    # print('added_tables:', player_to_name_tables([table[ADDED_TABLE_PARAM.NEW_TABLE] for table in added_tables]))
    # candidates_add_tables = [t for t in get_all_tables(get_remain_player(temp_matchs_tables[match_index]), ignore_history=TRUE) if not_duplicate_table(temp_matchs_tables[match_index], t)]
    candidates_add_tables = get_all_tables(get_remain_player(temp_matchs_tables[match_index]), ignore_history=TRUE)
    if len(candidates_add_tables) > 0:
        # ランダムな空欄にランダムな候補を挿入する
        add_table_param = [match_index, invalidated_table_indexes[random.randint(0, len(invalidated_table_indexes) - 1)], candidates_add_tables[random.randint(0, len(candidates_add_tables) - 1)]]
        temp_added_tables.append(add_table_param)
        change_matchs_tables_from_tables_diff(temp_matchs_tables, [add_table_param], add_not_remove=TRUE)
        added_tables, temp_removed_tables = adjust_match_table(matchs_tables=temp_matchs_tables, match_index=match_index-1, removed_tables=temp_removed_tables, added_tables=temp_added_tables)
    return added_tables, temp_removed_tables
    
def change_match_order(matchs_tables:list):
    temp_arr = []
    temp_indexes = [i for i in range(len(matchs_tables))]
    while len(temp_indexes) > 0:
        i = random.randint(0, len(temp_indexes) - 1)
        del temp_indexes[i]
        temp_arr.append(matchs_tables[i])
    return temp_arr

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
    matchs_tables = [[] for i in range(MATCH_NUM)]
    for i, match_tables in enumerate(matchs_tables):
        print(i+1,'回戦')
        match_tables.extend(generate_match_tables(player_list))
    print_table_count(matchs_tables=matchs_tables)
    # ② 隙間を埋める
    for i, match_tables in enumerate(matchs_tables):
        print(i+1,'回戦')
        fill_match_tables_blank(match_tables)
        for table in match_tables:
            print(player_to_name_table(table))
    print_table_count(matchs_tables=matchs_tables)
    exit()
    # ③ 入れ替えて隙間を埋める
    for i in range(100):
        adjust_matchs_tables(matchs_tables)
        change_match_order(matchs_tables)
    for i, match_tables in enumerate(matchs_tables):
        print(i+1,'回戦')
        for table in match_tables:
            print(player_to_name_table(table))
    print_table_count(matchs_tables=matchs_tables)
    print_history(player_list)
    print('again')
    print_hisotry_again(matchs_tables, player_list)

"""
% python3 MahjongLeagueTable.py
メンバー
['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4', 'C1', 'C2', 'C3', 'C4', 'D1', 'D2', 'D3', 'D4', 'E1', 'E2', 'E3', 'E4', 'F1', 'F2', 'F3', 'F4', 'G1', 'G2', 'G3', 'G4', 'H1', 'H2', 'H3', 'H4']
1 回戦
['A1', 'B1', 'C1', 'D1']
['A2', 'B2', 'C2', 'D2']
['A3', 'B3', 'C3', 'D3']
['A4', 'B4', 'C4', 'D4']
['E1', 'F1', 'G1', 'H1']
['E2', 'F2', 'G2', 'H2']
['E3', 'F3', 'G3', 'H3']
['E4', 'F4', 'G4', 'H4']
remain_player []
2 回戦
['A1', 'B2', 'C3', 'D4']
['A2', 'B1', 'C4', 'D3']
['A3', 'B4', 'C1', 'D2']
['A4', 'B3', 'C2', 'D1']
['E1', 'F2', 'G3', 'H4']
['E2', 'F1', 'G4', 'H3']
['E3', 'F4', 'G1', 'H2']
['E4', 'F3', 'G2', 'H1']
remain_player []
3 回戦
['A1', 'B3', 'C4', 'D2']
['A2', 'B4', 'C3', 'D1']
['A3', 'B1', 'C2', 'D4']
['A4', 'B2', 'C1', 'D3']
['E1', 'F3', 'G4', 'H2']
['E2', 'F4', 'G3', 'H1']
['E3', 'F1', 'G2', 'H4']
['E4', 'F2', 'G1', 'H3']
remain_player []
4 回戦
['A1', 'B4', 'C2', 'D3']
['A2', 'B3', 'C1', 'D4']
['A3', 'B2', 'C4', 'D1']
['A4', 'B1', 'C3', 'D2']
['E1', 'F4', 'G2', 'H3']
['E2', 'F3', 'G1', 'H4']
['E3', 'F2', 'G4', 'H1']
['E4', 'F1', 'G3', 'H2']
remain_player []
5 回戦
['A1', 'E1']
['A2', 'E2']
['A3', 'E3']
['A4', 'E4']
['B1', 'F1']
['B2', 'F2']
['B3', 'F3']
['B4', 'F4']
remain_player ['A1', 'E1', 'A2', 'E2', 'A3', 'E3', 'A4', 'E4', 'B1', 'F1', 'B2', 'F2', 'B3', 'F3', 'B4', 'F4']
6 回戦
['A1', 'E1']
['A2', 'E2']
['A3', 'E3']
['A4', 'E4']
['B1', 'F1']
['B2', 'F2']
['B3', 'F3']
['B4', 'F4']
remain_player ['A1', 'E1', 'A2', 'E2', 'A3', 'E3', 'A4', 'E4', 'B1', 'F1', 'B2', 'F2', 'B3', 'F3', 'B4', 'F4']
7 回戦
['A1', 'E1']
['A2', 'E2']
['A3', 'E3']
['A4', 'E4']
['B1', 'F1']
['B2', 'F2']
['B3', 'F3']
['B4', 'F4']
remain_player ['A1', 'E1', 'A2', 'E2', 'A3', 'E3', 'A4', 'E4', 'B1', 'F1', 'B2', 'F2', 'B3', 'F3', 'B4', 'F4']
8 回戦
['A1', 'E1']
['A2', 'E2']
['A3', 'E3']
['A4', 'E4']
['B1', 'F1']
['B2', 'F2']
['B3', 'F3']
['B4', 'F4']
remain_player ['A1', 'E1', 'A2', 'E2', 'A3', 'E3', 'A4', 'E4', 'B1', 'F1', 'B2', 'F2', 'B3', 'F3', 'B4', 'F4']
tables_count: [8, 8, 8, 8, 0, 0, 0, 0]
all_tables_count 32
1 回戦
['A1', 'B1', 'C1', 'D1']
['A2', 'B2', 'C2', 'D2']
['A3', 'B3', 'C3', 'D3']
['A4', 'B4', 'C4', 'D4']
['E1', 'F1', 'G1', 'H1']
['E2', 'F2', 'G2', 'H2']
['E3', 'F3', 'G3', 'H3']
['E4', 'F4', 'G4', 'H4']
2 回戦
['A1', 'B2', 'C3', 'D4']
['A2', 'B1', 'C4', 'D3']
['A3', 'B4', 'C1', 'D2']
['A4', 'B3', 'C2', 'D1']
['E1', 'F2', 'G3', 'H4']
['E2', 'F1', 'G4', 'H3']
['E3', 'F4', 'G1', 'H2']
['E4', 'F3', 'G2', 'H1']
3 回戦
['A1', 'B3', 'C4', 'D2']
['A2', 'B4', 'C3', 'D1']
['A3', 'B1', 'C2', 'D4']
['A4', 'B2', 'C1', 'D3']
['E1', 'F3', 'G4', 'H2']
['E2', 'F4', 'G3', 'H1']
['E3', 'F1', 'G2', 'H4']
['E4', 'F2', 'G1', 'H3']
4 回戦
['A1', 'B4', 'C2', 'D3']
['A2', 'B3', 'C1', 'D4']
['A3', 'B2', 'C4', 'D1']
['A4', 'B1', 'C3', 'D2']
['E1', 'F4', 'G2', 'H3']
['E2', 'F3', 'G1', 'H4']
['E3', 'F2', 'G4', 'H1']
['E4', 'F1', 'G3', 'H2']
5 回戦
['A1', 'E1']
['A2', 'E2']
['A3', 'E3']
['A4', 'E4']
['B1', 'F1']
['B2', 'F2']
['B3', 'F3']
['B4', 'F4']
6 回戦
['A1', 'E1']
['A2', 'E2']
['A3', 'E3']
['A4', 'E4']
['B1', 'F1']
['B2', 'F2']
['B3', 'F3']
['B4', 'F4']
7 回戦
['A1', 'E1']
['A2', 'E2']
['A3', 'E3']
['A4', 'E4']
['B1', 'F1']
['B2', 'F2']
['B3', 'F3']
['B4', 'F4']
8 回戦
['A1', 'E1']
['A2', 'E2']
['A3', 'E3']
['A4', 'E4']
['B1', 'F1']
['B2', 'F2']
['B3', 'F3']
['B4', 'F4']
tables_count: [8, 8, 8, 8, 0, 0, 0, 0]
all_tables_count 32
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [0, 1, 2, 3, 4, 5, 6, 7]
added_tables: []
6 回戦 無効なtable_index: [0, 1, 2, 3, 4, 5, 6, 7]
added_tables: [['B4', 'F2', 'E3', 'A4']]
5 回戦 無効なtable_index: [0, 1, 2, 3, 4, 5, 6, 7]
added_tables: [['B4', 'F2', 'E3', 'A4'], ['B3', 'A4', 'E1', 'F1']]
4 回戦 無効なtable_index: [0, 1, 2, 3, 4, 5, 6, 7]
added_tables: [['B4', 'F2', 'E3', 'A4'], ['B3', 'A4', 'E1', 'F1'], ['A2', 'F2', 'B1', 'E1']]
3 回戦 無効なtable_index: []
add: [(7, 3, ['B4', 'F2', 'E3', 'A4']), (6, 2, ['B3', 'A4', 'E1', 'F1']), (5, 6, ['A2', 'F2', 'B1', 'E1']), (4, 6, ['F4', 'E3', 'A4', 'B3'])] len: 4
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [0, 1, 3, 4, 5, 6, 7]
added_tables: []
5 回戦 無効なtable_index: [0, 1, 2, 3, 4, 5, 7]
added_tables: [['E1', 'F1', 'A1', 'B1']]
4 回戦 無効なtable_index: [0, 1, 2, 3, 4, 5, 7]
added_tables: [['E1', 'F1', 'A1', 'B1'], ['F4', 'B1', 'E1', 'A1']]
3 回戦 無効なtable_index: []
add: [(6, 1, ['E1', 'F1', 'A1', 'B1']), (5, 0, ['F4', 'B1', 'E1', 'A1']), (4, 1, ['F4', 'A3', 'B2', 'E4'])] len: 3
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [1, 2, 3, 4, 5, 7]
added_tables: []
4 回戦 無効なtable_index: [0, 2, 3, 4, 5, 7]
added_tables: [['F1', 'E4', 'B2', 'A2']]
3 回戦 無効なtable_index: []
add: [(5, 4, ['F1', 'E4', 'B2', 'A2']), (4, 3, ['B2', 'E1', 'A1', 'F4'])] len: 2
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [0, 2, 4, 5, 7]
added_tables: []
3 回戦 無効なtable_index: []
add: [(4, 0, ['E3', 'B1', 'F2', 'A3'])] len: 1
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [0, 1, 2, 4, 5, 6, 7]
added_tables: []
6 回戦 無効なtable_index: [0, 3, 4, 5, 6, 7]
added_tables: [['F4', 'A3', 'B4', 'E3']]
5 回戦 無効なtable_index: [1, 2, 3, 5, 7]
added_tables: [['F4', 'A3', 'B4', 'E3'], ['F4', 'E1', 'B1', 'A1']]
4 回戦 無効なtable_index: [2, 4, 5, 7]
added_tables: [['F4', 'A3', 'B4', 'E3'], ['F4', 'E1', 'B1', 'A1'], ['A2', 'B4', 'E2', 'F4']]
3 回戦 無効なtable_index: []
add: [(7, 7, ['F4', 'A3', 'B4', 'E3']), (6, 6, ['F4', 'E1', 'B1', 'A1']), (5, 7, ['A2', 'B4', 'E2', 'F4']), (4, 7, ['A3', 'F4', 'E3', 'B4'])] len: 4
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [0, 3, 4, 5, 7]
added_tables: []
5 回戦 無効なtable_index: [1, 2, 3, 5]
added_tables: [['F4', 'B4', 'E4', 'A1']]
4 回戦 無効なtable_index: [2, 4, 5]
added_tables: [['F4', 'B4', 'E4', 'A1'], ['A2', 'F2', 'B2', 'E4']]
3 回戦 無効なtable_index: []
add: [(6, 0, ['F4', 'B4', 'E4', 'A1']), (5, 2, ['A2', 'F2', 'B2', 'E4']), (4, 4, ['E3', 'A3', 'F1', 'B2'])] len: 3
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [1, 3, 5]
added_tables: []
4 回戦 無効なtable_index: [2, 5]
added_tables: [['E4', 'A2', 'B2', 'F2']]
3 回戦 無効なtable_index: []
add: [(5, 3, ['E4', 'A2', 'B2', 'F2']), (4, 5, ['B2', 'A3', 'F2', 'E3'])] len: 2
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [0, 1, 2, 4, 5, 6]
added_tables: []
6 回戦 無効なtable_index: [3, 4, 5, 7]
added_tables: [['E3', 'F1', 'B1', 'A3']]
5 回戦 無効なtable_index: [1, 5]
added_tables: [['E3', 'F1', 'B1', 'A3'], ['B1', 'E4', 'A4', 'F2']]
4 回戦 無効なtable_index: [2]
added_tables: [['E3', 'F1', 'B1', 'A3'], ['B1', 'E4', 'A4', 'F2'], ['F2', 'B2', 'E2', 'A2']]
add: [(7, 1, ['E3', 'F1', 'B1', 'A3']), (6, 7, ['B1', 'E4', 'A4', 'F2']), (5, 1, ['F2', 'B2', 'E2', 'A2'])] len: 3
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [3, 4, 5]
added_tables: []
5 回戦 無効なtable_index: [5]
added_tables: [['B1', 'E4', 'F2', 'A4']]
add: [(6, 5, ['B1', 'E4', 'F2', 'A4'])] len: 1
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [0, 2, 4, 5, 6]
added_tables: []
6 回戦 無効なtable_index: [3, 4]
added_tables: [['A3', 'E1', 'F2', 'B1']]
5 回戦 無効なtable_index: [5]
added_tables: [['A3', 'E1', 'F2', 'B1'], ['F1', 'E4', 'B1', 'A4']]
add: [(7, 0, ['A3', 'E1', 'F2', 'B1']), (6, 3, ['F1', 'E4', 'B1', 'A4'])] len: 2
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2, 4, 5, 6]
added_tables: []
6 回戦 無効なtable_index: [4]
added_tables: [['A3', 'F3', 'E3', 'B2']]
add: [(7, 5, ['A3', 'F3', 'E3', 'B2'])] len: 1
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2, 4, 6]
added_tables: []
6 回戦 無効なtable_index: [4]
added_tables: [['A3', 'F3', 'E3', 'B1']]
add: [(7, 4, ['A3', 'F3', 'E3', 'B1'])] len: 1
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2, 6]
added_tables: []
6 回戦 無効なtable_index: [4]
added_tables: [['E3', 'B3', 'A3', 'F3']]
add: [(7, 6, ['E3', 'B3', 'A3', 'F3'])] len: 1
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 0 週目 - 7 回戦 から修正
7 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 1 週目 - 6 回戦 から修正
6 回戦 無効なtable_index: [4]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 2 週目 - 5 回戦 から修正
5 回戦 無効なtable_index: [5]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 3 週目 - 4 回戦 から修正
4 回戦 無効なtable_index: [2]
added_tables: []
add: [] len: 0
rem: [] len: 0
修正 4 週目 - 3 回戦 から修正
3 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 5 週目 - 2 回戦 から修正
2 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 6 週目 - 1 回戦 から修正
1 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
修正 7 週目 - 0 回戦 から修正
0 回戦 無効なtable_index: []
add: [] len: 0
rem: [] len: 0
1 回戦
['A1', 'B1', 'C1', 'D1']
['A2', 'B2', 'C2', 'D2']
['A3', 'B3', 'C3', 'D3']
['A4', 'B4', 'C4', 'D4']
['E1', 'F1', 'G1', 'H1']
['E2', 'F2', 'G2', 'H2']
['E3', 'F3', 'G3', 'H3']
['E4', 'F4', 'G4', 'H4']
2 回戦
['A1', 'B2', 'C3', 'D4']
['A2', 'B1', 'C4', 'D3']
['A3', 'B4', 'C1', 'D2']
['A4', 'B3', 'C2', 'D1']
['E1', 'F2', 'G3', 'H4']
['E2', 'F1', 'G4', 'H3']
['E3', 'F4', 'G1', 'H2']
['E4', 'F3', 'G2', 'H1']
3 回戦
['A1', 'B3', 'C4', 'D2']
['A2', 'B4', 'C3', 'D1']
['A3', 'B1', 'C2', 'D4']
['A4', 'B2', 'C1', 'D3']
['E1', 'F3', 'G4', 'H2']
['E2', 'F4', 'G3', 'H1']
['E3', 'F1', 'G2', 'H4']
['E4', 'F2', 'G1', 'H3']
4 回戦
['A1', 'B4', 'C2', 'D3']
['A2', 'B3', 'C1', 'D4']
['A3', 'B2', 'C4', 'D1']
['A4', 'B1', 'C3', 'D2']
['E1', 'F4', 'G2', 'H3']
['E2', 'F3', 'G1', 'H4']
['E3', 'F2', 'G4', 'H1']
['E4', 'F1', 'G3', 'H2']
5 回戦
['E3', 'B1', 'F2', 'A3']
['F4', 'A3', 'B2', 'E4']
['A3', 'E3']
['B2', 'E1', 'A1', 'F4']
['E3', 'A3', 'F1', 'B2']
['B2', 'A3', 'F2', 'E3']
['F4', 'E3', 'A4', 'B3']
['A3', 'F4', 'E3', 'B4']
6 回戦
['F4', 'B1', 'E1', 'A1']
['F2', 'B2', 'E2', 'A2']
['A2', 'F2', 'B2', 'E4']
['E4', 'A2', 'B2', 'F2']
['F1', 'E4', 'B2', 'A2']
['B2', 'F2']
['A2', 'F2', 'B1', 'E1']
['A2', 'B4', 'E2', 'F4']
7 回戦
['F4', 'B4', 'E4', 'A1']
['E1', 'F1', 'A1', 'B1']
['B3', 'A4', 'E1', 'F1']
['F1', 'E4', 'B1', 'A4']
['B1', 'F1']
['B1', 'E4', 'F2', 'A4']
['F4', 'E1', 'B1', 'A1']
['B1', 'E4', 'A4', 'F2']
8 回戦
['A3', 'E1', 'F2', 'B1']
['E3', 'F1', 'B1', 'A3']
['A3', 'E3']
['B4', 'F2', 'E3', 'A4']
['A3', 'F3', 'E3', 'B1']
['A3', 'F3', 'E3', 'B2']
['E3', 'B3', 'A3', 'F3']
['F4', 'A3', 'B4', 'E3']
tables_count: [8, 8, 8, 8, 7, 7, 7, 7]
all_tables_count 60
A1 -> Counter({'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1})
A2 -> Counter({'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1})
A3 -> Counter({'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1})
A4 -> Counter({'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1})
B1 -> Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1})
B2 -> Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1})
B3 -> Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1})
B4 -> Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1})
C1 -> Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1})
C2 -> Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1})
C3 -> Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1})
C4 -> Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'D1': 1, 'D2': 1, 'D3': 1, 'D4': 1})
D1 -> Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1})
D2 -> Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1})
D3 -> Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1})
D4 -> Counter({'A1': 1, 'A2': 1, 'A3': 1, 'A4': 1, 'B1': 1, 'B2': 1, 'B3': 1, 'B4': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1})
E1 -> Counter({'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
E2 -> Counter({'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
E3 -> Counter({'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
E4 -> Counter({'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
F1 -> Counter({'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
F2 -> Counter({'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
F3 -> Counter({'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
F4 -> Counter({'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
G1 -> Counter({'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
G2 -> Counter({'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
G3 -> Counter({'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
G4 -> Counter({'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'H1': 1, 'H2': 1, 'H3': 1, 'H4': 1})
H1 -> Counter({'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1})
H2 -> Counter({'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1})
H3 -> Counter({'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1})
H4 -> Counter({'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1, 'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'G1': 1, 'G2': 1, 'G3': 1, 'G4': 1})
"""