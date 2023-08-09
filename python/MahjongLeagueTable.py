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
from pickle import FALSE, TRUE
import random
import collections
import itertools


MATCH_NUM = 8
TABLE_NUM = 8
TABLE_PLAYER_NUM = 4
TEAM_NUM = 8
TEAM_PLAYER_NUM = 4

TEAM_LIST = { 0:'A', 1:'B', 2:'C', 3:'D', 4:'E', 5:'F', 6:'G', 7:'H' }
def get_team_name(index:int):
    if index in TEAM_LIST.keys():
        return str(TEAM_LIST[index])
    else:
        return str(index)

class Player:
    def __init__(self, team:int, name:int) -> None:
        self.team = team
        self.name = name
        self.history = []
    def add_history(self, player):
        self.history.append(player)
    def add_history_range(self, player_list:list):
        self.history.extend(player_list)
    def clear_history(self):
        self.history.clear()
    def is_contain_history(self, player):
        return player in self.history
    def get_match_num(self):
        return len(self.history)
    def to_string(self):
        return get_team_name(self.team) + str(self.name + 1)

def compare(a:Player, b:Player, tables:list, table_index:int):
    #a_score = -a.get_match_num() + (is_can_sit(a, tables, table_index) if 0 else -999)
    #b_score = -b.get_match_num() + (is_can_sit(b, tables, table_index) if 0 else -999)
    #return a_score - b_score
    
    ng_player_list = []
    for p in tables[table_index]:
        ng_player_list.extend(p.history)
    ng_player_list_a = [p for p in ng_player_list]
    ng_player_list_a.extend(a.history)
    ng_player_list_a = [p for p, v in collections.Counter(ng_player_list_a).items() if v > 0]
    ng_player_list_b = [p for p in ng_player_list]
    ng_player_list_b.extend(b.history)
    ng_player_list_b = [p for p, v in collections.Counter(ng_player_list_b).items() if v > 0]
    #print('ng', [p.to_string() for p in ng_player_list])
    #print('ng_a', [p.to_string() for p in ng_player_list_a])
    #print('ng_b', [p.to_string() for p in ng_player_list_b])
    a_score = -len(ng_player_list_a)
    b_score = -len(ng_player_list_b)
    return a_score - b_score
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
def add_history_each(table:list):
    for player in table:
        player.add_history_range([p for p in table if p != player])
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

### 重複なし、ヒストリーやチームを参照して挿入可能なテーブルを選択する
def all_tables_search(player_list:list, table_player_num=TABLE_PLAYER_NUM, current_table=[], ignore_history:bool=FALSE, ignore_team:bool=FALSE):
    if len(current_table) >= table_player_num:
        return [current_table]
    next_all_tables = [] # current_tableに1人加えた複数のテーブル
    for p in player_list:
        if can_player_sit_to_table(p, current_table, ignore_history=ignore_history, ignore_team=ignore_team):
            table = [p for p in current_table]
            table.append(p)
            next_tables = all_tables_search(player_list=player_list, table_player_num=table_player_num, current_table=table, ignore_history=ignore_history)
            next_all_tables.extend(next_tables)
    return next_all_tables

def id(player:Player):
    return player.team * TEAM_PLAYER_NUM + int(player.name)

# スコアマックス探索とランダム探索の使い分け
def use_history_or_random(index:int) -> bool:
    return False
    # return True
    # return index > 0
def print_history(player_list:list):
    for p in player_list:
        print(p.to_string(), '->', collections.Counter([h.to_string() for h in sorted(p.history, key=id)]))
def player_to_name_table(table:list) -> list:
    return [p.to_string() for p in table]
def player_to_name_tables(tables:list) -> list:
    return [[p.to_string() for p in table] for table in tables]
def print_table_count(matchs_tables:list):
    created_table_count = [len([len(table) for table in match_tables if len(table) >= TABLE_PLAYER_NUM]) for match_tables in matchs_tables]
    print('tables_count:', created_table_count)
    print('all_tables_count', sum(created_table_count))

# 全ての条件から現在のtablesに挿入可能なtablesを返す
def get_tables_can_be_inserted(tables:list) -> list:
    tables = [t for t in all_tables_search(get_remain_player(tables)) if not_duplicate_table([t for t in tables if len(t) >= TABLE_PLAYER_NUM], t)]
    return tables
def get_remain_player(tables:list) -> list:
    remain_player_list = []
    for table in tables:
        if len(table) < TABLE_PLAYER_NUM:
            remain_player_list.extend(table)
    return remain_player_list

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

def fill_match_tables_blank(match_tables:list):
    for i, table in enumerate(match_tables):
        table_candidates = get_tables_can_be_inserted(tables=match_tables)
        if len(table_candidates) <= 0:
            break
        if len(table) < TABLE_PLAYER_NUM:
            v = match_tables[i]
            match_tables[i] = table_candidates[0]
            print(player_to_name_table(v), '->', player_to_name_table(match_tables[i]))

def adjust_matchs_tables(matchs_tables:list):
    for i in range(TABLE_NUM):
        print(i,'週目')
        #adjust_match_table(matchs_tables, (TABLE_NUM-1)-i, added_tables=[[0, 0, matchs_tables[0][0]]])
        added_tables, remove_tables = adjust_match_table(matchs_tables, (TABLE_NUM-1)-i, added_tables=[])
        print('add:', [(t[0], t[1], player_to_name_table(t[ADDED_TABLE_PARAM.NEW_TABLE])) for t in added_tables], len(added_tables))
        print('rem:', [(t[0], t[1], player_to_name_table(t[ADDED_TABLE_PARAM.NEW_TABLE])) for t in remove_tables], len(remove_tables))
        if len(added_tables) > len(remove_tables):
            for t in added_tables:
                matchs_tables[t[ADDED_TABLE_PARAM.MATCH_INDEX]][t[ADDED_TABLE_PARAM.TABLE_INDEX]] = t[ADDED_TABLE_PARAM.NEW_TABLE]

class ADDED_TABLE_PARAM:
    MATCH_INDEX = 0
    TABLE_INDEX = 1
    NEW_TABLE = 2

# 参照するために...
# added_tables -> [0, 0, [Player, Player, Player]]
# return -> 0, [matches_index, table_index, [Player, Player, Player]]
def adjust_match_table(matchs_tables:list, match_index:int, removed_tables:list=[], added_tables:list=[]):
    # beforeがafterになったことで無効になるテーブルを列挙する or 無効なテーブルを列挙する
    invalidated_table_indexes = []
    for i, table in enumerate(matchs_tables[match_index]):
        for added_table in added_tables:
            #print('table', table, len(table))
            #print('added_table:', player_to_name_table(added_table[ADDED_TABLE_PARAM.NEW_TABLE]))
            if duplicate_player_count(table, added_table[ADDED_TABLE_PARAM.NEW_TABLE]) >= 2:
                invalidated_table_indexes.append(i)
                removed_tables.append([match_index, i, matchs_tables[match_index][i]])
    #print(match_index, 'invalidated:', invalidated_table_indexes)
    for i, table in enumerate(matchs_tables[match_index]):
        if len(table) < TABLE_PLAYER_NUM:
            invalidated_table_indexes.append(i)
    print(match_index, 'invalidated:', invalidated_table_indexes)

    if len(invalidated_table_indexes) <= 0:
        return added_tables, removed_tables
    print('added_tables:', player_to_name_tables([table[ADDED_TABLE_PARAM.NEW_TABLE] for table in added_tables]))

    candidates_add_tables = all_tables_search(get_remain_player(matchs_tables[match_index]), ignore_history=TRUE)
    #print('candidates_add_tables', player_to_name_tables(candidates_add_tables))
    if len(candidates_add_tables) > 0:
        temp_added_tables = copy.deepcopy(added_tables)
        #print(temp_added_tables)
        # ランダムな空欄にランダムな候補を挿入する
        v = [match_index, invalidated_table_indexes[random.randint(0, len(invalidated_table_indexes) - 1)], candidates_add_tables[random.randint(0, len(candidates_add_tables) - 1)]]
        #print('v', v)
        temp_added_tables.append(v)

        #print(temp_added_tables)
        added_tables, removed_tables = adjust_match_table(matchs_tables=matchs_tables, match_index=match_index-1, removed_tables=copy.deepcopy(removed_tables), added_tables=copy.deepcopy(temp_added_tables))
    return added_tables, removed_tables
    
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

    #t = all_tables_search(player_list, TABLE_PLAYER_NUM)
    #print([[b.to_string() for b in a] for a in t])
    #print('table_num:', len(t))
    #exit()
    
    # ① とりあえず配置
    matchs_tables = [[] for i in range(MATCH_NUM)]
    for i, match_tables in enumerate(matchs_tables):
        print(i+1,'回戦')
        match_tables.extend(generate_match_tables(player_list))
        # print_history(player_list)
    print_table_count(matchs_tables=matchs_tables)
    # ② 隙間を埋める
    for i, match_tables in enumerate(matchs_tables):
        print(i+1,'回戦')
        fill_match_tables_blank(match_tables)
        for table in match_tables:
            print(player_to_name_table(table))
    print_table_count(matchs_tables=matchs_tables)
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
    print_history(player_list)