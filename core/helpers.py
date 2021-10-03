from core.utils import cdebug
import json
import csv
from django.db.models import Q, Avg, Count, Min,Max, Sum
from decimal import Decimal
from django.http import (HttpResponseRedirect,HttpResponse,JsonResponse)
from master_data.models import Category, Month

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

            if (cols == '' or operator == ''): continue
            if(operator == '~'):
                temp_group_filter &= ~Q(**{cols:filter_val})
            else:
                temp_group_filter &= Q(**{cols+'__'+operator: filter_val})
            # print(str(group_filter))

        group_filter |= Q(temp_group_filter)

    return group_filter


condition = {'iexact':'Equals to',
             'istartswith':'Starts with',
             'iendswith':'Ends with',
             'icontains':'Contains',
             '~':'Not Equal to',
             'isnull':'Not Set or Blank',
             'gt':'Greater than',
             'gte':'Greater than or Equals to',
             'lt':'Less than',
             'lte':'Less than or Equals to',
            }
def getGroupFilterHuman(new_dic):
    group_filter = ""
    for i,and_list in new_dic.items():
        temp_group_filter = ""
        for k in range(0,len(and_list),3):
            cols = and_list[k][4]
            operator = and_list[k+1][4]
            filter_val = and_list[k+2][4]

            if isinstance(cols, list):
                cols = cols[0]
            if isinstance(operator, list):
                operator = operator[0]
            if isinstance(filter_val, list):
                filter_val = filter_val[0]

            if (cols == '' or operator == ''): continue
            if k==0: cand = ''
            else: cand = ' AND '
            temp_group_filter +=  "{}({} {} '{}')".format(cand,cols,condition[operator],filter_val)
            # print(str(group_filter))
        if i==0: cor = ''
        else: cor = 'OR \n'
        group_filter += "{}({})\n".format(cor,temp_group_filter)
    return group_filter

def dropzeros(number):
    mynum = Decimal(number).normalize()
    mynum = mynum.__trunc__() if not mynum % 1 else float(mynum)
    return "{:,}".format(mynum)

def remove_exponent(d):
    ret = d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize()
    return "{:,}".format(ret)

def getCategories(self):
    queryset = Category.objects.filter(country__code=self.kwargs['country_code']).order_by('name')
    # cdebug(queryset)
    html = '<select name="category">'
    for obj in queryset:
        html += '<option value="'+str(obj.id)+'" >' + str(obj.name)+'('+str(obj.code)+')</option>'
    html += '</select">'
    return html

def getMonths(self):
    queryset = Month.objects.filter(country__code=self.kwargs['country_code']).order_by('date')
    # cdebug(queryset)
    html = '<select name="month">'
    for obj in queryset:
        html += '<option value="'+str(obj.id)+'" >' + str(obj.name)+' : '+str(obj.name)+'('+str(obj.year)+')</option>'
    html += '</select">'
    return html