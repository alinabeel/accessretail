from typing import ValuesView
from core.utils import cdebug
import json
import csv
import os
import sys

from django.contrib import messages
from django.db import models
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Avg, Count, Min,Max, Sum
from decimal import Decimal
from django.http import (HttpResponseRedirect,HttpResponse,JsonResponse)
from master_data.models import *
from master_setups.models import *
from core.utils import camelTerms

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

def modelForeignFields(modelname):
    valid_fields = []
    skip_cols = ['id','pk','country','created','updated','upload']
    for field in eval(f'{modelname}')._meta.get_fields():
        field_name = field.name
        if(field_name not in skip_cols):
            if(field_name in skip_cols): continue
            if isinstance(field, models.ForeignKey):
                valid_fields.append(field_name)
    return valid_fields

def modelValidFields(modelname):
    valid_fields = []
    skip_cols = ['id','pk','country','created','updated',]
    modelname_prefix = camelTerms(modelname)
    modelname_prefix = "_".join(modelname_prefix)
    for field in eval(f'{modelname}')._meta.get_fields():
        field_name = field.name
        if(field_name not in skip_cols):
            if(field_name in skip_cols): continue
            if isinstance(field, models.ForeignKey): continue
            if isinstance(field, models.ManyToManyRel): continue
            if isinstance(field, models.ManyToOneRel): continue
            if field == 'name': field_name = f"{modelname_prefix}_{field}"
            if field == 'code': field_name = f"{modelname_prefix}_{field}"
            valid_fields.append(field_name)
    return valid_fields

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

def uploadStatusMessage(self,country_id,frommodel):
    upload = Upload.objects.filter(
        country__id = country_id, frommodel=frommodel
    ).last()

    if upload is not None:
        if upload.is_processing in (Upload.ERROR,Upload.FAILED):
            messages.add_message(self.request, messages.ERROR, str(upload.is_processing +' : '+ upload.process_message))
        elif upload.is_processing in (Upload.PROCESSING,Upload.UPLOADING):
            messages.add_message(self.request, messages.INFO, str(upload.is_processing +' : '+ upload.process_message))

def IdCodeModel(country_qs,model):
    objs = eval(f"{model}").objects.filter(country=country_qs).values('id','code')
    result = dict()
    for obj in objs:
        result[str(obj['code']).lower()] = obj['id']
    return result

def getCode2AnyModelFieldList(country_qs,model,field):
    objs = eval(f"{model}").objects.filter(country=country_qs).values('code',f"{field}")
    result = dict()
    for obj in objs:
        result[str(obj['code']).lower()] = obj[f"{field}"]
    return result


def chkMonthLocked(country_qs):
    objs = Month.objects.filter(country=country_qs).values('code','is_locked')
    result = dict()
    for obj in objs:
        result[str(obj['code']).lower()] = obj['is_locked']
    return result

def getPrvMonthDate(country_qs,current_month_id,outlet_id):

    # NOW = datetime.date.today().replace(day=1)
    # previous_month = NOW + relativedelta(months=-1)

    current_month_qs = Month.objects.filter(country=country_qs, id=current_month_id).values('code','date').first()


    current_month = current_month_qs.date
    previous_month = current_month + relativedelta(months=-1)

    try:
        previous_month_qs = Month.objects.get(country=country_qs, date=previous_month)
    except Month.DoesNotExist:
        previous_month_qs = None

def calculateSales(total_purchase,opening_stock,total_stock,vd_factor):
    # =ROUND(SUM(N6:R6)*AM6,0)
    purchase = round(total_purchase * vd_factor,0)

    # =IF((T6+AN6-U6-V6)>0,AN6,-1*(T6+AN6-U6-V6)+AN6)
    rev_purchase_cond1 = opening_stock + purchase - total_stock
    rev_purchase_cond2 = -1*(opening_stock + purchase - total_stock)+purchase

    rev_purchase = purchase if rev_purchase_cond1 > 0 else rev_purchase_cond2

    # =+T6+AO6-U6-V6
    sales = (opening_stock + rev_purchase) - total_stock

    return purchase,rev_purchase,sales

def getTwoMonthFromDate(country_id, month_date):
    try:
        #Calculate Previous Month, Next Month
        audit_date_qs = AuditData.objects.all() \
            .filter(Q(country_id = country_id) & Q(month__date__lte = month_date) ) \
            .values('month__date','month__code') \
            .annotate(current_month=Max("month__date")) \
            .order_by('-month__date')[0:2]

        # audit_date_qs = PanelProfile.objects.all().filter(country_id = country_id).values('month__date').annotate(current_month=Max('audit_date')).order_by('month__date')[0:3]

        date_arr = []

        for instance in audit_date_qs:
            date_arr.append(instance['month__date'])

        is_first_month = False
        month_1 = month_2  = None
        current_month = previous_month = None

        if(len(date_arr)==2):
            month_1 , month_2 = date_arr
            current_month = Month.objects.get(date=month_1)
            previous_month  = Month.objects.get(date=month_2)
            cdebug('2-Month data')
        else:
            cdebug('1-Month data')
            is_first_month = True
            month_1 = date_arr[0]
            current_month = Month.objects.get(date=month_1)

        print(f"{is_first_month},{current_month}, {previous_month}")
        return is_first_month,current_month, previous_month
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)


def updateUploadStatus(id,msg,is_processing,log=''):
    upload = Upload.objects.get(pk=id)
    upload.is_processing = Upload.ERROR
    upload.process_message = msg
    upload.log  = log
    upload.save()
    print(msg)
