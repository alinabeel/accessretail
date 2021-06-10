from django.db.models import Q, Avg, Count, Min,Max, Sum

def getDictArray(post, name):
    array =  []
    for k, value in post.items():
        if k.startswith(name):
            rest = k[len(name):]
            # split the string into different components
            parts = [p[:-1] for p in rest.split('[')][1:]
            parts.append(value)
            array.append(parts)
    return array

def getDicGroupList(new_list):
    new_dic = dict()
    for k in range(0,len(new_list)):
        group_id = int(new_list[k][0])
        new_dic.setdefault(group_id, []).append(new_list[k])
    return new_dic

def getGroupFilter(new_dic):
    group_filter = Q()
    for i,and_list in new_dic.items():
        temp_group_filter = Q()
        for k in range(0,len(and_list),3):
            cols = and_list[k][4]
            operator = and_list[k+1][4]
            filter_val = and_list[k+2][4]
            # print(Colors.BLUE)
            if isinstance(cols, list):
                cols = cols[0]
            if isinstance(operator, list):
                operator = operator[0]
            if isinstance(filter_val, list):
                filter_val = filter_val[0]

            # print(Colors.WHITE)
            temp_group_filter &= Q(**{cols+'__'+operator: filter_val})
            # print(str(group_filter))

        group_filter |= Q(temp_group_filter)
    return group_filter