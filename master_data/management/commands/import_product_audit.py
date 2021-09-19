import decimal
from dateutil.relativedelta import *
from dateutil.rrule import *
from dateutil.parser import *

import time
import datetime
import re
import sys, os
import json
import logging
from pprint import pprint
from var_dump import var_dump,var_export
from dateutil import parser
from django.db.models import Q, Avg, Count, Min,Max, Sum
from django.utils.dateparse import parse_date
from django.core.management.base import BaseCommand
from csv import DictReader





from master_data.models import *
from master_setups.models import *
from core.colors import Colors
from core.utils import cdebug, csvHeadClean,printr,replaceIndex
from core.settings import MEDIA_ROOT

logger = logging.getLogger(__name__)

def convert(seconds):
    return time.strftime("%H:%M:%S", time.gmtime(seconds))

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('upload_id', type=int)

    def handle(self, *args, **options):

        skiped_records = 0
        updated_records = 0
        created_records = 0

        start_time = time.time()
        upload_id = options['upload_id']
        upload = Upload.objects.get(pk=upload_id)
        country = Country.objects.get(pk=upload.country.id)
        log = ""



        if(upload.import_mode == Upload.REFRESH):
            ProductAudit.objects.filter(country=upload.country).delete()

        valid_fields = []
        skip_cols = ['id','pk','country','category','month','outlet','product','audit_date','upload','created','updated',]
        for v in ProductAudit._meta.get_fields():
            if(v.name not in skip_cols):
                valid_fields.append(v.name)

        # cdebug(valid_fields,'valid_fields')
        # printr(Colors.BRIGHT_PURPLE,form_obj.file)
        try:
            with open(MEDIA_ROOT+'/'+str(upload.file), 'r',encoding='utf-8-sig') as read_obj:
                csv_reader = DictReader(read_obj)
                log += printr(".....CSV Read Successfully.....")
                n=0
                log += printr("csv.DictReader took %s seconds" % (time.time() - start_time))
                csv_indx = 0
                for row in csv_reader:
                    # loop_start_time = time.time()
                    n+=1
                    print(n,end=' ',flush=True)
                    csv_indx += 1
                    row = {replaceIndex(k): v.strip() for (k, v) in row.items()}

                    row['purchase_1'] = int(row['purchase_1']) if row['purchase_1']!='' else 0
                    row['purchase_2'] = int(row['purchase_2']) if row['purchase_2']!='' else 0
                    row['purchase_3'] = int(row['purchase_3']) if row['purchase_3']!='' else 0
                    row['purchase_4'] = int(row['purchase_4']) if row['purchase_4']!='' else 0
                    row['purchase_5'] = int(row['purchase_5']) if row['purchase_5']!='' else 0


                    row['opening_stock'] = int(row['opening_stock']) if row['opening_stock']!='' else 0
                    row['stock_1'] = int(row['stock_1']) if row['stock_1']!='' else 0
                    row['stock_2'] = int(row['stock_2']) if row['stock_2']!='' else 0
                    row['stock_3'] = int(row['stock_3']) if row['stock_3']!='' else 0
                    row['total_stock'] = int(row['total_stock']) if row['total_stock']!='' else 0
                    row['price'] = float(row['price']) if row['price']!='' else 0


                    # for k in row:
                    #     if(k not in skip_cols):
                    #         print(isinstance(row[k], int))
                    #         print(isinstance(row[k], float))

                    #         if(row[k].replace('.','',1).isdigit()):
                    #             print(row[k] )
                    #             row[k] = float(v)
                    #         else:
                    #             row[k] = str(v)
                    # exit()
                    # ('country', 'upload', 'month', 'week', 'period', 'category', 'outlet', 'product', 'audit_date',
                    # 'purchase_1', 'purchase_2', 'purchase_3', 'purchase_4', 'purchase_5',
                    # 'opening_stock', 'stock_1', 'stock_2', 'stock_3', 'total_stock', 'price',
                    # 'vd_factor', 'total_purchase', 'rev_purchase', 'sales', 'sales_vol', 'sales_val', )


                    outlet_code = row['outlet_code']
                    product_code = row['product_code']
                    category = row['category']
                    month_code = row['month_code']
                    audit_date = row['audit_date']

                    del row["outlet_code"]
                    del row["product_code"]
                    del row["category"]
                    del row["month_code"]
                    # del row["week"]

                    # cdebug(row)
                    # print(row.keys())
                    # trow = row.keys()
                    # for v in row.keys():
                    #     if(v    ot in valid_fields):
                    #         print('not found: ',v)
                    #         # row.pop(v, None)
                    #         del row[v]


                    """ Manuplae Audit Date """
                    audit_date = audit_date.split('/')
                    ymd2 = parser.parse(str(audit_date[0].strip())+' '+str(audit_date[1].strip())+' '+str(audit_date[2].strip()))
                    audit_date_obj = datetime.datetime(int(ymd2.strftime("%Y")), int(ymd2.strftime("%m")), int(ymd2.strftime("%d")))
                    # audit_date_obj = datetime.datetime(int(ymd.strftime("%Y")), int(ymd.strftime("%m")), int(ymd.strftime("%d")))
                    # # print(audit_date_obj)
                    row['audit_date'] = audit_date_obj


                    """ Select Month OR Create """
                    # ymd = parser.parse('1 '+str(month)+' '+str(year))
                    # mcode = ymd.strftime("%b").upper() + ymd.strftime("%y")
                    # """Get or Create Outlet Month"""
                    # month_obj, created = Month.objects.get_or_create(
                    #     country=upload.country, code=mcode,
                    #     defaults={
                    #         'code':mcode,
                    #         'name':ymd.strftime("%B"),
                    #         'month':ymd.strftime("%m"),
                    #         'year':ymd.strftime("%Y")
                    #     },
                    # )
                    try:
                        month_obj = Month.objects.get(country=country, code=month_code)
                    except Month.DoesNotExist:
                        month_obj = None
                        log += printr('month code not exist, csv row: '+ str(n))
                        skiped_records += 1
                        continue

                    row['month'] = month_obj
                    row["upload"] = upload


                    """ Select Outlet Code """
                    if(outlet_code != ''):
                        try:
                            outlet_qs = Outlet.objects.get(country=upload.country, code__iexact=outlet_code)
                        except Outlet.DoesNotExist:
                            outlet_qs = None
                            log += printr('Outlet not exist: ' + str(outlet_code))
                            skiped_records+=1
                            continue
                    else:
                        log += printr('Outlet is empty at csv index: ' + str(csv_indx))
                        skiped_records+=1
                        continue


                    """ Select Product Code """
                    if(product_code != ''):
                        try:
                            product_qs = Product.objects.get(country=upload.country, code__iexact=product_code)
                        except Product.DoesNotExist:
                            product_qs = None
                            log += printr('Product code not exist: ' + product_code)
                            skiped_records+=1
                            continue
                    else:
                        log += printr('Product code is empty at csv index: ' + str(csv_indx))
                        skiped_records+=1
                        continue

                    # row['product'] = product_qs



                    """ Select Category Code """
                    if(category != ''):
                        try:
                            category_qs = Category.objects.filter(
                                                Q(country=upload.country) &
                                                Q(code__iexact=category)).get()
                        except Category.DoesNotExist:
                            category_qs = None
                            log += printr('Category code not exist: ' + category)
                            skiped_records+=1
                            continue
                    else:
                        log += printr('Category code is empty at csv index: ' + str(csv_indx))
                        skiped_records+=1
                        continue

                    row['category'] = category_qs





                    """--------------- Calculate Total Purchase ---------------"""

                    purchase_1 = row['purchase_1']
                    purchase_2 = row['purchase_2']
                    purchase_3 = row['purchase_3']
                    purchase_4 = row['purchase_4']
                    purchase_5 = row['purchase_5']

                    total_purchase = purchase_1 + purchase_2 + purchase_3 + purchase_4 + purchase_5


                    """--------------- Calculate Total Stock ---------------"""
                    opening_stock = row['opening_stock']
                    stock1 = row['stock_1']
                    stock2 = row['stock_2']
                    stock3 = row['stock_3']

                    total_stock = stock1 + stock2 + stock3

                    price = row['price']

                    # =IF((T6+AN6-U6-V6)>0, AN6, -1*(T6+AN6-U6-V6)+AN6)

                    # price_in_unit = float(row['price_in_unit'])
                    # total_none_empty_facing_forward_reserve = int(row['total_none_empty_facing_forward_reserve'])
                    # sales_unprojected_volume = sales_unprojected_value = sales_unprojected_units = sales_projected_volume = sales_projected_value = sales_projected_units = 0
                    #Calculate Previous Month, Next Month
                    # month = Month.objects.get(pk=month_obj.pk)
                    # max_date = Month.objects.all().filter(country = country).aggregate(month = Max('date'))

                    current_month_qs = month_obj

                    current_month = current_month_qs.date
                    previous_month = current_month + relativedelta(months=-1)

                    try:
                        previous_month_qs = Month.objects.get(date=previous_month)
                    except Month.DoesNotExist:
                        previous_month_qs = None

                    # print(type(product_qs.weight))

                    product_weight = 0 if(product_qs.weight == None) else float(product_qs.weight)


                    if previous_month_qs is not None:
                        delta = current_month_qs.date - previous_month_qs.date
                        vd_factor= delta.days/30.5
                        sales = opening_stock + rev_purchase - total_stock
                    else:
                        vd_factor = 1
                        sales = total_purchase

                    total_purchase = round(total_purchase * vd_factor,0)
                    rev_purchase_cond1 = opening_stock + total_purchase - total_stock
                    rev_purchase_cond2 = -1*(opening_stock + total_purchase - total_stock)+total_purchase
                    rev_purchase = rev_purchase_cond1 if rev_purchase_cond1 > 0 else rev_purchase_cond2

                    # multiply sales with weight(from Product table) * Q6
                    sales_vol = sales * float(product_qs.weight)
                    # Multiply Sales Vol with price (column P) *Q6
                    sales_val = sales * price

                    row['vd_factor'] = vd_factor
                    row['total_stock'] = total_stock
                    row['total_purchase'] = total_purchase
                    row['rev_purchase'] = rev_purchase

                    row['sales'] = sales
                    row['sales_vol'] = sales_vol
                    row['sales_val'] = sales_val





                    # if(product_weight !=0 ):
                    #

                    #     if previous_month_qs is None:
                    #         sales_unprojected_volume = total_purchase
                    #     else:
                    #         try:
                    #             product_audit_qs = ProductAudit.objects.get(country=upload.country, product=product_qs,outlet=outlet_qs ,month = previous_month_qs)
                    #             total_none_empty_facing_forward_reserve_previous = product_audit_qs.total_none_empty_facing_forward_reserve
                    #         except ProductAudit.DoesNotExist:
                    #             total_none_empty_facing_forward_reserve_previous = 0

                    #         sales_unprojected_volume = (total_none_empty_facing_forward_reserve_previous + total_purchase - total_none_empty_facing_forward_reserve)*product_weight


                    #     sales_unprojected_value =  float(price_in_pack * sales_unprojected_volume)/float(product_weight)
                    #     sales_unprojected_units = price_in_unit * sales_unprojected_volume


                    #     try:
                    #         panel_profile_qs = PanelProfile.objects.get(country=upload.country, outlet=outlet_qs ,month = current_month_qs)
                    #     except PanelProfile.DoesNotExist:
                    #         num_factor = 1

                    #     num_factor = float(panel_profile_qs.num_factor)

                    #     sales_projected_volume = (float(sales_unprojected_volume) * num_factor) * product_weight
                    #     sales_projected_value =  (float(sales_unprojected_value) * num_factor) / product_weight
                    #     sales_projected_units = float(sales_unprojected_units) * num_factor





                    #     if(total_purchase==0 and total_none_empty_facing_forward_reserve == 0):
                    #         log += printr('total_purchase and  total_none_empty_facing_forward_reserve is 0:')
                    #         skiped_records+=1
                    #         continue


                    # row['sales_unprojected_volume'] = (round(sales_unprojected_volume,4))
                    # row['sales_unprojected_value'] = (round(sales_unprojected_value,4))
                    # row['sales_unprojected_units'] = (round(sales_unprojected_units,4))
                    # row['sales_projected_volume'] = (round(sales_projected_volume,4))
                    # row['sales_projected_value'] = (round(sales_projected_value,4))
                    # row['sales_projected_units'] = (round(sales_projected_units,4))

                    if(upload.import_mode == Upload.APPEND or upload.import_mode == Upload.REFRESH ):
                        print(csv_indx,outlet_code)
                        # In this case, if the Person already exists, its existing name is preserved
                        obj, created = ProductAudit.objects.get_or_create(
                            country=upload.country, product=product_qs,outlet=outlet_qs ,month=month_obj,
                            defaults=row
                        )
                        if(created): created_records+=1


                    if(upload.import_mode == Upload.APPENDUPDATE ):
                        # In this case, if the Person already exists, its name is updated
                        obj, created = ProductAudit.objects.update_or_create(
                            country=upload.country, product=product_qs,outlet=outlet_qs,month=month_obj,
                            defaults=row
                        )
                        if(created): created_records+=1
                        else: updated_records+=1
                    # print("Loop  took %s seconds" % (time.time() - loop_start_time))

                    upload.skiped_records = skiped_records
                    upload.created_records = created_records
                    upload.updated_records = updated_records
                    upload.save()
                    n+=1


            logger.error('CSV file processed successfully.')
            log += 'CSV file processed successfully.'
            log += printr("Total time spent: %s seconds" % (time.time() - start_time))
            upload.is_processing = Upload.COMPLETED
            upload.process_message = "CSV file processed successfully."
            upload.log  = log
            upload.save()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'CSV file processing failed. Line: '+str(n)+' - Error Msg:'+ str(e)+Colors.WHITE )
            print(row)
            log += 'CSV file processing failed. Error Msg:'+ str(e)
            upload.is_processing = Upload.ERROR
            upload.process_message = "CSV file processing failed. Error Msg:"+str(e)
            upload.log  = log
            upload.save()