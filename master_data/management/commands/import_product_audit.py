import decimal
from dateutil.relativedelta import *
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *

from decimal import *
import re
import time
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
from core.settings import MEDIA_ROOT

logger = logging.getLogger(__name__)
def printr(str):
    print(str)
    return str+"\n"
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
                    print(n,end=' ',flush=True)
                    csv_indx += 1
                    row = {k.strip(): v.strip() for (k, v) in row.items()}
                    # period	month	year	category	outlelt_code	product_code	product_details	avaibility	facing_empty	facing_not_empty	forward	reserve	total_none_empty_facing_forward_reserve	purchaseother1	purchaseother2	purchasediary	purchaseinvoice	price_in_unit	price_in_pack	priceother	cash_discount	product_foc	gift_with_purchase	appreciation_award	other_trade_promotion	pack_without_graphic_health_warning	no_of_pack_without_graphic_health_warning_facing	no_of_pack_without_graphic_health_warning_total_stock	no_of_pack_without_none_tax_stamp	point_of_sales_signboard	point_of_sales_poster	point_of_sales_counter_shield	point_of_sales_price_sticker	point_of_sales_umbrella	point_of_sales_counter_top_display	point_of_sales_lighter	point_of_sales_others	point_of_sales_none

                    # ('country', 'upload', 'month_year', 'month', 'year', 'period', 'category', 'shop_code', 'avaibility', 'facing_empty', 'facing_not_empty', 'forward', 'reserve', 'total_none_empty_facing_forward_reserve', 'purchaseother1', 'purchaseother2', 'purchasediary', 'purchaseinvoice', 'price_in_unit', 'price_in_pack', 'priceother', 'cash_discount', 'product_foc', 'gift_with_purchase', 'appreciation_award', 'other_trade_promotion', 'pack_without_graphic_health_warning', 'no_of_pack_without_graphic_health_warning_facing', 'no_of_pack_without_graphic_health_warning_total_stock', 'no_of_pack_without_none_tax_stamp', 'point_of_sales_signboard', 'point_of_sales_poster', 'point_of_sales_counter_shield', 'point_of_sales_price_sticker', 'point_of_sales_umbrella', 'point_of_sales_counter_top_display', 'point_of_sales_lighter', 'point_of_sales_others', 'point_of_sales_none', 'pack_type', 'aggregation_level', 'company', 'brand', 'family', 'flavour_type', 'weight', 'price_segment', 'length_range', 'number_in_pack', 'price_per_stick', )
                    # for (k, v) in row.items():
                    #     # k = re.sub('[^A-Za-z0-9]+', '_', k).lower().strip('_')
                    #     v = str(v.strip())
                    #     if(str(v.lower()) in ['true','t','y','yes']):
                    #         v = True
                    #     elif(str(v.lower()) in ['false','f','n','no']):
                    #         v = False
                    #     elif(str(v.lower()) in ['na','nill','','null','n/a']):
                    #         v = None
                    #     elif(v.replace('.','',1).isdigit()):
                    #         v = float(v)
                    #     else:
                    #         v = str(v)
                    #     row[k] = v

                    # print(row)
                    # exit()



                    month = row['month']
                    year = row['year']
                    outlet_code = row['outlet_code']
                    product_code = row['product_code']
                    category_code = row['category_code']

                    del row["month"]
                    del row["year"]
                    del row["outlet_code"]
                    del row["product_code"]
                    del row["category_code"]

                    """ Select Month OR Create """
                    ymd = parser.parse('1 '+str(month)+' '+str(year))
                    mcode = ymd.strftime("%b").upper() + ymd.strftime("%y")
                    """Get or Create Outlet Month"""
                    month_obj, created = Month.objects.get_or_create(
                        country=upload.country, code=mcode,
                        defaults={
                            'code':mcode,
                            'name':ymd.strftime("%B"),
                            'month':ymd.strftime("%m"),
                            'year':ymd.strftime("%Y")
                        },
                    )

                    row['month'] = month_obj
                    row["upload"] = upload



                    """ Select Outlet Code """
                    if(outlet_code != ''):
                        try:
                            outlet_qs = Outlet.objects.get(country=upload.country, code=outlet_code)
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
                            product_qs = Product.objects.get(country=upload.country, code=product_code)
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
                    if(category_code != ''):
                        try:
                            category_qs = Category.objects.filter(
                                                Q(country=upload.country) &
                                                Q(code=category_code) | Q(name=category_code)).get()
                        except Category.DoesNotExist:
                            category_qs = None
                            log += printr('Category code not exist: ' + category_code)
                            skiped_records+=1
                            continue
                    else:
                        log += printr('Category code is empty at csv index: ' + str(csv_indx))
                        skiped_records+=1
                        continue

                    row['category'] = category_qs





                    """---------------Calculate Projected/Unprojected Sales  """

                    purchaseother1 = int(row['purchaseother1'])
                    purchaseother2 = int(row['purchaseother2'])
                    purchasediary = int(row['purchasediary'])
                    purchaseinvoice = int(row['purchaseinvoice'])
                    price_in_pack = float(row['price_in_pack'])
                    price_in_unit = float(row['price_in_unit'])

                    total_none_empty_facing_forward_reserve = int(row['total_none_empty_facing_forward_reserve'])

                    sales_unprojected_volume = sales_unprojected_value = sales_unprojected_units = sales_projected_volume = sales_projected_value = sales_projected_units = 0
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
                    print(type(product_qs.weight))
                    product_weight = 0 if(product_qs.weight == None) else float(product_qs.weight)


                    if(product_weight !=0 ):
                        total_purchase = purchaseother1 + purchaseother2 + purchasediary + purchaseinvoice

                        if previous_month_qs is None:
                            sales_unprojected_volume = total_purchase
                        else:
                            try:
                                product_audit_qs = ProductAudit.objects.get(country=upload.country, product=product_qs,outlet=outlet_qs ,month = previous_month_qs)
                                total_none_empty_facing_forward_reserve_previous = product_audit_qs.total_none_empty_facing_forward_reserve
                            except ProductAudit.DoesNotExist:
                                total_none_empty_facing_forward_reserve_previous = 0

                            sales_unprojected_volume = (total_none_empty_facing_forward_reserve_previous + total_purchase - total_none_empty_facing_forward_reserve)*product_weight


                        sales_unprojected_value =  float(price_in_pack * sales_unprojected_volume)/float(product_weight)
                        sales_unprojected_units = price_in_unit * sales_unprojected_volume


                        try:
                            panel_profile_qs = PanelProfile.objects.get(country=upload.country, outlet=outlet_qs ,month = current_month_qs)
                        except PanelProfile.DoesNotExist:
                            num_factor = 1

                        num_factor = float(panel_profile_qs.num_factor)

                        sales_projected_volume = (float(sales_unprojected_volume) * num_factor) * product_weight
                        sales_projected_value =  (float(sales_unprojected_value) * num_factor) / product_weight
                        sales_projected_units = float(sales_unprojected_units) * num_factor





                        if(total_purchase==0 and total_none_empty_facing_forward_reserve == 0):
                            log += printr('total_purchase and  total_none_empty_facing_forward_reserve is 0:')
                            skiped_records+=1
                            continue


                    row['sales_unprojected_volume'] = (round(sales_unprojected_volume,4))
                    row['sales_unprojected_value'] = (round(sales_unprojected_value,4))
                    row['sales_unprojected_units'] = (round(sales_unprojected_units,4))
                    row['sales_projected_volume'] = (round(sales_projected_volume,4))
                    row['sales_projected_value'] = (round(sales_projected_value,4))
                    row['sales_projected_units'] = (round(sales_projected_units,4))

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
            print(csv_indx)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'CSV file processing failed. Error Msg:'+ str(e)+Colors.WHITE )
            print(row)
            print(csv_indx)

            log += 'CSV file processing failed. Error Msg:'+ str(e)
            upload.is_processing = Upload.ERROR
            upload.process_message = "CSV file processing failed. Error Msg:"+str(e)
            upload.log  = log
            upload.save()