#!/usr/bin/env python
# encoding: utf-8


from flask import request, current_app, Blueprint
from research.utils.result_json import success
from research.utils.db_util import DbUtil
import re
from itertools import combinations
import copy
from collections import Counter
import datetime

data_bp = Blueprint('data', __name__)
link = []  # [data1,data2,type]
entity_dic = {}  # {name:type}
attr_table = {}  # table:attrlist  attrlist={attr:[type,key]}
weak_table = {}  # table:attrlist  attrlist=[name, type]
key_ref = {}  # table: [parent, key, parentkey]
pic_weak = [0]  # [1(weak)2(1tom), parent, weak]
relation_m2m = [] #{name,link,item}
tablelist = []



@data_bp.route('/database', methods=['GET'])
def database():
    sql = "show databases"
    db = DbUtil().Select(sql)
    database_list = list(map(lambda x: x[0], db))
    # print(database_list)
    return success(data=database_list)


@data_bp.route('/table', methods=['POST'])
def table():
    params = request.form.to_dict()
    sql = "use {}".format(params["database_code"])
    DbUtil().Change(sql)
    # print(params)
    database_code = params["database_code"]
    sql = '''
           select table_name from information_schema.tables where table_schema='{}'
          '''.format(database_code)
    table = DbUtil().Select(sql)
    # print(table)
    table_list = list(map(lambda x: x[0], table))
    for i in range(len(table_list)-1,-1,-1):
        if table_list[i] == 'user_table':
            table_list.pop(i)
    # print(table_list)
    return success(data=table_list)


@data_bp.route('/vstable', methods=['POST'])
def vstable():
    global link
    link = []  # [data1,data2,type]
    global entity_dic
    entity_dic = {}  # {name:type}
    global weak_table
    weak_table = {}  # table:attrlist  attrlist=[name, type]
    global key_ref
    key_ref = {}  # table: [parent, key, parentkey]
    global relation_m2m
    relation_m2m = []  # {name,link,item}
    params = request.form.to_dict()
    print(params)
    sql = "use {}".format(params["database_code"])
    DbUtil().Change(sql)
    table = params['database_code']
    dict_return = []
    sql = '''
                   select table_name from information_schema.tables where table_schema='{}'
                  '''.format(table)
    # print(sql)
    result = DbUtil().Select(sql)
    table_list = list(map(lambda x: x[0], result))
    # print(table_list)
    if 'located' in table_list:
        table_list.remove('located')
    # print(table_list)
    for i in range(len(table_list)):
        table_attri = {}
        sql = '''
                    desc {}
            '''.format(table_list[i])
        result = DbUtil().Select(sql)
        item = list(map(lambda x: [x[0], x[3]], result))
        primary_key = []
        for j in range(len(item)):
            if item[j][1] == 'PRI':
                item[j][1] = True
                primary_key.append(item[j][0])
            else:
                item[j][1] = False
        table_attri['key'] = table_list[i]
        # table_attri['item'] = item
        # dict_return.append(table_attri)
        sql = '''
                            show create table {}
                    '''.format(table_list[i])
        result = DbUtil().Select(sql)
        foreignkey = result[0][1]
        # print(foreignkey)
        foreignkey = re.findall(r"^(.+?)FOREIGN KEY \(`(.+?)`\) REFERENCES `(.+?)` \(`(.+?)`\)", foreignkey, re.M)
        # print(foreignkey, len(foreignkey))
        foreign_key = []
        isrelation = []
        refer = []
        for j in range(len(foreignkey)):
            for_key = []
            ref_key = []
            # print(foreignkey, [foreignkey[j][1], foreignkey[j][2], foreignkey[j][3]])
            foreign = foreignkey[j][1].replace('`', '')
            foreign = foreign.replace(' ', '')
            foreign = foreign.split(',')
            ref = foreignkey[j][3].replace('`', '')
            ref = ref.replace(' ', '')
            ref = ref.split(',')
            if [foreignkey[j][1], foreignkey[j][2], foreignkey[j][3]] not in isrelation:
                isrelation.append([foreignkey[j][1], foreignkey[j][2], foreignkey[j][3]])
            # print(foreign)
            if len(foreign) > 0:
                for k in range(len(foreign)):
                    foreign_key.append(foreign[k])
                    for_key.append(foreign[k])
            if len(ref) > 0:
                for k in range(len(ref)):
                    ref_key.append(ref[k])

            refer.append([foreignkey[j][2], for_key, ref_key])
        key_ref[table_list[i]] = refer
        foreign_key = set(foreign_key)
        primary_key = set(primary_key)
        # print(foreign_key, primary_key)
        intersection = list(foreign_key & primary_key)
        if len(isrelation) > 1 and len(intersection) > 0:
                # print(table_list[i], d)
            if foreign_key.issuperset(primary_key):
                nodetype = 'mtom'
            else:
                nodetype = '1to1'
        else:
            if foreign_key == primary_key:
                nodetype = 'subset'
                entity_dic[table_list[i]] = 'subset'
            elif primary_key.issuperset(foreign_key) and len(foreign_key) > 0:
                nodetype = 'weak'
                entity_dic[table_list[i]] = 'weak'
                for j in range(len(isrelation)):
                    link.append([isrelation[j][1], table_list[i], '1tom'])  #(parent, weak)
                    # print([isrelation[j][1], table_list[i], '1tom'])
            else:
                nodetype = 'basic'
                entity_dic[table_list[i]] = 'basic'
                for j in range(len(isrelation)):
                    link.append([isrelation[j][1], table_list[i], '1tom'])
                    # print([isrelation[j][1], table_list[i], '1tom'])
        if nodetype == 'mtom' or nodetype == '1to1':
            for j in range(len(item) - 1, -1, -1):
                if item[j][0] in foreign_key:
                    item.pop(j)
        if len(isrelation) > 1 and len(intersection) > 0 and len(item) > 0 and primary_key.issuperset(foreign_key) and foreign_key.issuperset(primary_key):
            rela = list(map(lambda x: x[1], isrelation))
            for c in combinations(rela, 2):
                d = list(c)
                relation_m2m.append({'name': table_list[i], 'link':list(c), 'item':item})
                d.append('mtom')
                link.append(d)
        if nodetype == 'weak':
            w = copy.deepcopy(item)
            for j in range(len(w) - 1, -1, -1):
                if w[j][0] in foreign_key:
                    w.pop(j)
            weak_table[table_list[i]] = w
        # print(table_list[i], primary_key, foreign_key, nodetype, item)
        table_attri['item'] = item
        table_attri['type'] = nodetype
        # print(table_attri)
        dict_return.append(table_attri)

    for i in range(len(link)):
        if (link[i][0] in entity_dic) and (link[i][1] in entity_dic):
            if entity_dic[link[i][0]] == 'basic' and entity_dic[link[i][1]] == 'weak' and link[i][2] != 'mtom':
                link[i][2] = 'weak'
            elif entity_dic[link[i][0]] == 'weak' and entity_dic[link[i][1]] == 'weak' and link[i][2] != 'mtom':
                link[i][2] = 'weak'
    for i in range(len(link) - 1):
        for j in range(len(link) - 1, i, -1):
            if (link[i][0] == link[j][0] and link[i][1] == link[j][1]) or (
                    link[i][1] == link[j][0] and link[i][0] == link[j][1]):
                # print(link[i], link[j])
                link.pop(j)
    # print(link)
    # print(entity_dic)
    # print(relation_m2m)
    # print(dict_return)
    return success(data=list(entity_dic.keys()))


@data_bp.route('/vstable2', methods=['POST'])
def vstable2():
    params = request.form.to_dict()
    # print(params)
    table = params['value']
    table_list = set()
    for i in range(len(link)):
        if link[i][0] == table:
            table_list.add(link[i][1]+'('+link[i][2]+')')
        # if link[i][1] == table:
        #     table_list.add(link[i][0]+'('+link[i][2]+')')
    return success(data=list(table_list))


@data_bp.route('/list', methods=['POST'])
def attr_list():
    params = request.form.to_dict()
    print(params)
    db = params['database']
    global tablelist
    table = params['value']
    if len(tablelist) == 0:
        tablelist.append(table)
    elif len(tablelist) == 1 and '(' in table:
        tablelist.append(table)
    elif len(tablelist) == 2 and '(' in table:
        tablelist.pop(-1)
        tablelist.append(table)
    else:
        tablelist = []
        tablelist.append(table)

    if 'mtom' in table and len(tablelist) == 2:
        for i in range(len(relation_m2m)):
            if (tablelist[0] == relation_m2m[i]['link'][0] and table.split('(')[0] == relation_m2m[i]['link'][1]) or (tablelist[0] == relation_m2m[i]['link'][1] and table.split('(')[0] == relation_m2m[i]['link'][0]):
                table = relation_m2m[i]['name']
        sql = '''select COLUMN_NAME, DATA_TYPE, COLUMN_KEY from information_schema.columns where table_schema = '{}' and table_name = '{}'
                       '''.format(db, table)
        result = DbUtil().Select(sql, ('name', 'type', 'key'))
        a_dic = {}
        for i in range(len(result)):
            a_dic[result[i]['name']] = [result[i]['type'], result[i]['key']]
        attr_table[table] = a_dic
        for i in range(len(result) - 1, -1, -1):
            if result[i]['key'] == 'PRI':
                result.pop(i)
    else:
        if '(' in table:
            table = table.split('(')[0]
        sql = '''select COLUMN_NAME, DATA_TYPE, COLUMN_KEY from information_schema.columns where table_schema = '{}' and table_name = '{}'
               '''.format(db, table)
        result = DbUtil().Select(sql, ('name', 'type', 'key'))
        a_dic = {}
        for i in range(len(result)):
            a_dic[result[i]['name']] = [result[i]['type'], result[i]['key']]
        attr_table[table] = a_dic
        for i in range(len(result) - 1, -1, -1):
            if result[i]['key'] == 'PRI':
                result.pop(i)
    # print(result)
    return success(data=result)


@data_bp.route('/judgepic', methods=['POST'])
def judgepic():
    global pic_weak
    pic_weak = [0]
    params = request.form.to_dict()
    print(params)
    table = params['table'].split(',')
    attr = params['attr'].split(',')
    if not params['attr']:
        table = []
    flag = True
    type = []
    attr_type = []
    if len(table) == 1:
        for i in range(len(attr)):
            attr[i] = attr[i].split('+')[1]
        attr_all = attr_table[table[0]]
        # print(attr_all)
        lexical = 0
        numeric = 0
        for i in range(len(attr)):
            # print(attr_all[attr[i]][0])
            if attr_all[attr[i]][0] == 'int' or attr_all[attr[i]][0] == 'decimal':
                attr_type.append([attr[i], 'numeric'])
                numeric += 1
            elif attr_all[attr[i]][0] == 'varchar':
                attr_type.append([attr[i], 'lexical'])
                lexical += 1
            else:
                flag = False
        total = lexical + numeric
        # print(lexical, numeric)
        if total == 1:
            if numeric == 1:
                type.append('Bar Chart')
                type.append('Word Clouds')
        elif total == 2:
            if numeric == 2:
                type.append('Scatter Diagram')
        elif total == 3:
            if numeric == 3:
                type.append('Bubble Charts')
                type.append('Scatter Diagram')
            elif lexical == 1:
                type.append('Scatter Diagram')
        elif total == 4:
            if numeric >= 3:
                type.append('Bubble Charts')
        if len(type) == 0:
            flag = False
        if flag == False:
            type = ('Please choose one to four kinds of valid data')
    else:
        rela = None
        for i in range(len(link)):
            if (link[i][0] == table[0] and link[i][1] == table[1]) or (
                    link[i][1] == table[0] and link[i][0] == table[1]):
                rela = link[i][2]
                if rela == 'weak':
                    table1 = link[i][0]
                    table2 = link[i][1]
                if rela == '1tom':
                    table1 = link[i][0]
                    table2 = link[i][1]
                if rela == 'mtom':
                    table1 = table[0]
                    table2 = table[1]

        # print(link)
        # print(rela)
        if rela == 'weak':
            weak_attr = weak_table[table2]
            attr_data = attr_table[table2]
            weak_flag = True
            weak_key = []
            for j in range(len(weak_attr)):
                for k, v in attr_data.items():
                    if v[1] == 'PRI' and weak_attr[j][0] == k:
                        if v[0] == 'int' or v[0] == 'decimal':
                            weak_key.append(k)
                        else:
                            weak_flag = False
            if len(weak_key) != 1:
                weak_flag = False
            attr_all = attr_table[table2]
            lexical = 0
            numeric = 0
            for i in range(len(attr)):
                a = attr[i].split('+')
                if a[0] == table1:
                    flag = False
                    break
                if attr_all[a[1]][0] == 'int' or attr_all[a[1]][0] == 'decimal':
                    attr_type.append([a[1], 'numeric'])
                    numeric += 1
                elif attr_all[a[1]][0] == 'varchar':
                    attr_type.append([a[1], 'lexical'])
                    lexical += 1
                else:
                    flag = False
            # print(numeric, lexical)
            if numeric == 1 and lexical == 0:
                if weak_flag:
                    type.append('Line Chart')
                type.append('Stacked Bar Chart')
                type.append('Grouped Bar Chart')
                type.append('Spider Chart')
                pic_weak[0] = 1
                pic_weak.append(table1)
                pic_weak.append(table2)
            # elif numeric == 2 and lexical == 0 and weak_flag:
            #     type.append('Line Chart')
            #     pic_weak[0] = 1
            #     pic_weak.append(table1)
            #     pic_weak.append(table2)
        elif rela == '1tom':
            attr_all = attr_table[table2]
            lexical = 0
            numeric = 0
            for i in range(len(attr)):
                a = attr[i].split('+')
                if a[0] == table1:
                    flag = False
                    break
                if attr_all[a[1]][0] == 'int' or attr_all[a[1]][0] == 'decimal':
                    attr_type.append([a[1], 'numeric'])
                    numeric += 1
                elif attr_all[a[1]][0] == 'varchar':
                    attr_type.append([a[1], 'lexical'])
                    lexical += 1
                else:
                    flag = False
            # print(numeric, lexical)
            if numeric == 1 and lexical == 0:
                type.append('Tree Map')
                type.append('Hierarchy Tree')
                # type.append('Circle Packing')
                pic_weak[0] = 2
                pic_weak.append(table1)
                pic_weak.append(table2)
            elif numeric == 2 and lexical == 0:
                type.append('Tree Map')
                pic_weak[0] = 2
                pic_weak.append(table1)
                pic_weak.append(table2)
        elif rela == 'mtom':
            table0 = None
            for i in range(len(relation_m2m)):
                if (relation_m2m[i]['link'][0] == table[0] and relation_m2m[i]['link'][1] == table[1]) or (
                        relation_m2m[i]['link'][1] == table[0] and relation_m2m[i]['link'][0] == table[1]):
                    table0 = relation_m2m[i]['name']
            attr_all = attr_table[table0]
            # print(attr_all)
            lexical = 0
            numeric = 0
            for i in range(len(attr)):
                a = attr[i].split('+')
                if attr_all[a[1]][0] == 'int' or attr_all[a[1]][0] == 'decimal':
                    attr_type.append([a[1], 'numeric'])
                    numeric += 1
                elif attr_all[a[1]][0] == 'varchar':
                    attr_type.append([a[1], 'lexical'])
                    lexical += 1
                else:
                    flag = False
            # print(numeric, lexical)
            if numeric == 1 and lexical == 0:
                type.append('Sankey Diagram')
                # type.append('Chord Diagram')
                pic_weak[0] = 3
                pic_weak.append(table0)
        if len(type) == 0:
            flag = False
        if flag == False:
            type = ('Please choose one valid data')
    # print(type)

    print([flag, type, attr_type])
    return success(data=[flag, type, attr_type])


@data_bp.route('/picdata', methods=['POST'])
def picdata():
    params = request.form.to_dict()
    print(params)
    print(pic_weak)
    table = params['table'].split(',')
    attr = params['attr'].split(',')
    result = []
    head = []
    if len(table) == 1:
        key = []
        for i in range(len(attr)):
            attr[i] = attr[i].split('+')[1]
        attr_all = attr_table[table[0]]
        for k, v in attr_all.items():
            if v[1] == 'PRI':
                key.append(k)
        head.append(' '.join(key))
        head = head + attr
        sqlin = ', '.join(key + attr)
        # print(sqlin)
        sqlnull = []
        for i in range(len(attr)):
            sqlnull.append(attr[i] + ' is not null')
        sqlnull = ' and '.join(sqlnull)
        sql = '''select {} from {} where {} limit 300
               '''.format(sqlin, table[0], sqlnull)
        # print(sql)
        result_sql = DbUtil().Select(sql)
        # print(result_sql[:5])
        for i in range(len(result_sql)):
            onedata = []
            sql_one = list(result_sql[i])
            if len(key) > 1:
                for j in range(len(key)):
                    sql_one[j] = str(sql_one[j])
            if len(key) > 1:
                strkey = ' '.join(sql_one[:len(key)])
            else:
                strkey = sql_one[0]
            onedata.append(strkey)
            for j in range(len(attr)):
                if attr_all[attr[j]][0] == 'decimal':
                    onedata.append(float(sql_one[j + len(key)]))
                else:
                    onedata.append(sql_one[j + len(key)])
            result.append(onedata)
    else:
        # print(pic_weak)
        if pic_weak[0] == 1:
            for i in range(len(attr)):
                attr[i] = attr[i].split('+')[1]
            key1 = []
            attr_all1 = attr_table[pic_weak[1]]
            for k, v in attr_all1.items():
                if v[1] == 'PRI':
                    key1.append(k)
            key2 = []
            attr_all2 = weak_table[pic_weak[2]]
            # print(attr_all2)
            for i in range(len(attr_all2)):
                if attr_all2[i][1]:
                    key2.append(attr_all2[i][0])
            head.append(' '.join(key1))
            head.append(' '.join(key2))
            head = head + attr
            for i in range(len(key1)):
                key1[i] = pic_weak[1] + '.' + key1[i]
            for i in range(len(key2)):
                key2[i] = pic_weak[2] + '.' + key2[i]
            for i in range(len(attr)):
                attr[i] = pic_weak[2] + '.' + attr[i]
            sqlin = ', '.join(key1 + key2 + attr)
            # print(sqlin)
            ref = key_ref[pic_weak[2]]
            for i in range(len(ref)):
                if pic_weak[1] == ref[i][0]:
                    weakkey = ref[i][1]
                    parentkey = ref[i][2]
            sqlon = []
            for i in range(len(weakkey)):
                # print(weakkey[i], parentkey[i])
                sqlon.append(pic_weak[2] + '.' + weakkey[i] + '=' + pic_weak[1] + '.' + parentkey[i])
            sqlon = ' and '.join(sqlon)
            sqlnull = []
            for i in range(len(attr)):
                sqlnull.append(attr[i] + ' is not null')
            sqlnull = ' and '.join(sqlnull)
            sql = '''select {} from {} join {} on {} where {} limit 10000
                           '''.format(sqlin, pic_weak[1], pic_weak[2], sqlon, sqlnull)
            # print(sql)
            result_sql = DbUtil().Select(sql)
            # print(result_sql[:5])
            result_mid = []
            for i in range(len(result_sql)):
                onedata = []
                sqlone = result_sql[i]
                if len(key1) > 1:
                    strkey = ' '.join(sqlone[:len(key1)])
                else:
                    strkey = str(sqlone[0])
                onedata.append(strkey)
                if not isinstance(sqlone[len(key1)], str):
                    if isinstance(sqlone[len(key1)], datetime.date):
                        strkey = str(sqlone[len(key1)])
                    else:
                        strkey = int(sqlone[len(key1)])
                else:
                    strkey = ' '.join(sqlone[len(key1):len(key1) + len(key2)])
                onedata.append(strkey)
                for j in range(len(attr)):
                    if attr_table[pic_weak[2]][attr[j].split('.')[1]][0] == 'decimal':
                        onedata.append(float(sqlone[j + len(key1) + len(key2)]))
                    else:
                        onedata.append(sqlone[j + len(key1) + len(key2)])
                result_mid.append(onedata)
            # print(result_mid[:10])
            result_mid1 = [i[1] for i in result_mid]
            limit_num = 10
            count = Counter(result_mid1).most_common(limit_num)
            if not (isinstance(count[0][0],str)):
                for i in range(len(count)-1,-1,-1):
                    if count[i][0] % 10 !=0:
                        count.pop(i)
            # print(count)
            count1 = {}
            for i in range(len(result_mid)):
                for j in range(len(count)):
                    if result_mid[i][1] == count[j][0]:
                        if result_mid[i][0] in count1.keys():
                            count1[result_mid[i][0]] += 1
                        else:
                            count1[result_mid[i][0]] = 1

            # print(count1)
            key1_ok = []
            if count[0][1]<10:
                for k, v in count1.items():
                    if v > 4:
                        key1_ok.append(k)
                    if len(key1_ok) == 10:
                        break

            for k, v in count1.items():
                if v == len(count):
                    key1_ok.append(k)
                if len(key1_ok) == 10:
                    break
            # print(key1_ok)
            key1_txt = [i[0] for i in count]
            for i in range(len(result_mid)):
                if result_mid[i][0] in key1_ok and result_mid[i][1] in key1_txt:
                    result.append(result_mid[i])

        if pic_weak[0] == 2:
            for i in range(len(attr)):
                attr[i] = attr[i].split('+')[1]
            key1 = []
            attr_all1 = attr_table[pic_weak[1]]
            for k, v in attr_all1.items():
                if v[1] == 'PRI':
                    key1.append(k)
            key2 = []
            attr_all2 = attr_table[pic_weak[2]]
            # print(attr_all2)
            for k, v in attr_all2.items():
                if v[1] == 'PRI':
                    key2.append(k)
            head.append(' '.join(key1))
            head.append(' '.join(key2))
            head = head + attr
            for i in range(len(key1)):
                key1[i] = pic_weak[1] + '.' + key1[i]
            for i in range(len(key2)):
                key2[i] = pic_weak[2] + '.' + key2[i]
            for i in range(len(attr)):
                attr[i] = pic_weak[2] + '.' + attr[i]
            sqlin = ', '.join(key1 + key2 + attr)
            # print(sqlin)
            ref = key_ref[pic_weak[2]]
            for i in range(len(ref)):
                if pic_weak[1] == ref[i][0]:
                    weakkey = ref[i][1]
                    parentkey = ref[i][2]
            sqlon = []
            for i in range(len(weakkey)):
                # print(weakkey[i], parentkey[i])
                sqlon.append(pic_weak[2] + '.' + weakkey[i] + '=' + pic_weak[1] + '.' + parentkey[i])
            sqlon = ' and '.join(sqlon)
            sqlnull = []
            for i in range(len(attr)):
                sqlnull.append(attr[i] + ' is not null')
            sqlnull = ' and '.join(sqlnull)
            sql = '''select {} from {} join {} on {} where {}
                           '''.format(sqlin, pic_weak[1], pic_weak[2], sqlon, sqlnull)
            # print(sql)
            result_sql = DbUtil().Select(sql)
            for i in range(len(result_sql)):
                onedata = []
                strkey = ' '.join(result_sql[i][:len(key1)])
                onedata.append(strkey)
                strkey = ' '.join(result_sql[i][len(key1):len(key1) + len(key2)])
                onedata.append(strkey)
                for j in range(len(attr)):
                    if attr_all2[attr[j].split('.')[1]][0] == 'decimal':
                        onedata.append(float(result_sql[i][j + len(key1) + len(key2)]))
                    else:
                        onedata.append(result_sql[i][j + len(key1) + len(key2)])
                result.append(onedata)
        if pic_weak[0] == 3:
            for i in range(len(attr)):
                attr[i] = attr[i].split('+')[1]
            key = []
            attr_all = attr_table[pic_weak[1]]
            for k, v in attr_all.items():
                if v[1] == 'PRI':
                    key.append(k)
            head = head + key + attr
            sqlin = ', '.join(key + attr)
            # print(sqlin)
            sqlnull = []
            for i in range(len(attr)):
                sqlnull.append(attr[i] + ' is not null')
            sqlnull = ' and '.join(sqlnull)
            sql = '''select {} from {} where {}
                           '''.format(sqlin, pic_weak[1], sqlnull)
            # print(sql)
            result_sql = DbUtil().Select(sql)
            for i in range(len(result_sql)):
                onedata = []
                onedata.append(result_sql[i][0])
                onedata.append(result_sql[i][1])
                for j in range(len(attr)):
                    if attr_all[attr[j]][0] == 'decimal':
                        onedata.append(float(result_sql[i][j + len(key)]))
                    else:
                        onedata.append(result_sql[i][j + len(key)])
                result.append(onedata)
    print(result[:5])
    print(head)
    return success(data=[head, result])
