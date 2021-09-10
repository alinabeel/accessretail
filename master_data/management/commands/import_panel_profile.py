import re
import time
import datetime
import sys, os
import json
import logging
from pprint import pprint
from var_dump import var_dump,var_export
from dateutil import parser
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.core.management.base import BaseCommand
from csv import DictReader
from master_data.models import *
from master_setups.models import *
from core.colors import Colors
from core.settings import MEDIA_ROOT
from core.utils import cdebug, csvHeadClean,printr,replaceIndex,convertSecond2Min

logger = logging.getLogger(__name__)




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
            PanelProfile.objects.filter(country=upload.country).delete()



        # printr(Colors.BRIGHT_PURPLE,form_obj.file)
        try:
            with open(MEDIA_ROOT+'/'+str(upload.file), 'r',encoding='utf-8-sig') as read_obj:
                csv_reader = DictReader(read_obj)
                log += printr(".....Panel Profile Read Successfully.....")
                n=0
                log += printr("csv.DictReader took %s seconds" % (time.time() - start_time))

                for row in csv_reader:
                    n+=1
                    print(n,end=' ',flush=True)
                    row = {replaceIndex(k): v.strip() for (k, v) in row.items()}

                    row["upload"] = upload

                    # month = row['month']
                    # year = row['year']
                    month_code = row['month_code']
                    category = row['category']
                    index = row['index']
                    city_village_code = row['city_village_code']

                    audit_date = row['audit_date']
                    outlet_code = row['outlet_code']
                    outlet_type_code = row['outlet_type_code']
                    outlet_status_code = row['outlet_status_code']


                    del row["month"]
                    del row["year"]
                    del row["month_code"]
                    del row["index"]
                    del row["category"]
                    del row["outlet_code"]
                    del row["outlet_type_code"]
                    del row["outlet_status_code"]
                    del row["city_village_code"]



                    """First Get or Create Outlet Object"""
                    outlet_obj, created = Outlet.objects.get_or_create(
                        country=upload.country, code=outlet_code,
                        defaults={
                        },
                    )

                    row['outlet'] = outlet_obj


                    # """ Select Month OR Create """
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
                        log += ('month code not exist, csv row: '+ str(n))
                        skiped_records += 1
                        continue

                    row['month'] = month_obj

                    # month_obj = datetime.datetime.strptime(month, "%B")
                    # month_number = month_obj.month
                    # month_year = datetime.date(int(year), int(month_number), 1)
                    # row['month_year'] = month_year

                    """ Manuplae Audit Date """
                    audit_date = audit_date.split('/')
                    ymd2 = parser.parse(str(audit_date[0].strip())+' '+str(audit_date[1].strip())+' '+str(audit_date[2].strip()))
                    audit_date_obj = datetime.datetime(int(ymd2.strftime("%Y")), int(ymd2.strftime("%m")), int(ymd2.strftime("%d")))
                    # audit_date_obj = datetime.datetime(int(ymd.strftime("%Y")), int(ymd.strftime("%m")), int(ymd.strftime("%d")))
                    # # print(audit_date_obj)
                    row['audit_date'] = audit_date_obj
                    # exit()


                    """ Select Outlet Type or Skip  """
                    if(outlet_type_code != ''):
                        try:
                            outlet_type_qs = OutletType.objects.filter(
                                                Q(country=upload.country) &
                                                Q(code=outlet_type_code) | Q(name=outlet_type_code)).get()
                        except OutletType.DoesNotExist:
                            outlet_type_qs = None
                            log += printr('OutletType code not exist: '+outlet_type_code)
                            skiped_records+=1
                            continue
                    else:
                        log += printr('outlet code is empty: '+outlet_type_code)
                        skiped_records+=1
                        continue

                    row['outlet_type'] = outlet_type_qs



                    """ Select Outlet Status or Skip  """
                    outlet_status_qs = None
                    if(outlet_status_code != ''):
                        try:
                            outlet_status_qs = OutletStatus.objects.filter(
                                                Q(country=upload.country) &
                                                Q(code__iexact=outlet_status_code)).get()
                        except OutletStatus.DoesNotExist:
                            log += printr('OutletStatus code not exist: '+outlet_status_qs)
                            skiped_records+=1
                            continue
                    else:
                        log += printr('outlet status is empty: '+outlet_status_code)
                        skiped_records+=1
                        continue

                    row['outlet_status'] = outlet_status_qs

                    """ Select Inex or Skip  """
                    index_qs = None
                    if(index != ''):
                        try:
                            index_qs = IndexSetup.objects.filter(
                                                Q(country=upload.country) &
                                                Q(code__iexact = index)).get()
                        except IndexSetup.DoesNotExist:
                            log += printr('index code not exist: '+index)
                            skiped_records+=1
                            continue
                    else:
                        skiped_records+=1
                        log += printr('index code is empty: '+index)
                        continue

                    row['index'] = index_qs

                    """ Select Category or Skip  """
                    category_qs = None
                    if(category != ''):
                        try:
                            category_qs = Category.objects.filter(
                                                Q(country=upload.country) &
                                                Q(code__iexact=category)).get()
                        except Category.DoesNotExist:
                            log += printr('category code not exist: '+category)
                            skiped_records+=1
                            continue
                    else:
                        skiped_records+=1
                        log += printr('category code is empty: '+category)
                        continue

                    row['category'] = category_qs




                    """ Select CityVillage or Skip  """
                    city_village_qs = None
                    if(city_village_code != ''):
                        try:
                            city_village_qs = CityVillage.objects.filter(
                                                Q(country=upload.country) &
                                                Q(code__iexact=city_village_code)).get()
                        except CityVillage.DoesNotExist:
                            log += printr('CityVillage code not exist csv line: '+str(n))
                            skiped_records+=1
                            continue
                    else:
                        log += printr('CityVillage is empty: '+city_village_code)
                        skiped_records+=1
                        continue

                    row['city_village'] = city_village_qs


                    if(upload.import_mode == Upload.APPEND or upload.import_mode == Upload.REFRESH ):

                        """In this case, if the Person already exists, its existing name is preserved"""
                        obj, created = PanelProfile.objects.get_or_create(
                            country=upload.country, outlet=outlet_obj, month=month_obj,
                            defaults=row
                        )
                        if(created): created_records+=1


                    if(upload.import_mode == Upload.APPENDUPDATE ):
                        """In this case, if the Person already exists, its name is updated"""
                        obj, created = PanelProfile.objects.update_or_create(
                            country=upload.country, outlet=outlet_obj, month=month_obj,
                            defaults=row
                        )
                        if(created): created_records+=1
                        else: updated_records+=1

                    upload.skiped_records = skiped_records
                    upload.created_records = created_records
                    upload.updated_records = updated_records
                    upload.save()





            logger.error('CSV file processed successfully.')
            log += 'CSV file processed successfully.'
            log += printr("Total time spent: %s seconds" % (convertSecond2Min(time.time() - start_time)))
            upload.is_processing = Upload.COMPLETED
            upload.process_message = "CSV file processed successfully."
            upload.log  = log
            upload.save()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'CSV file processing failed. Error Msg:'+ str(e)+Colors.WHITE )

            log += 'CSV file processing failed. Error Msg:'+ str(e)
            upload.is_processing = Upload.ERROR
            upload.process_message = "CSV file processing failed. Error Msg:"+str(e)
            upload.log  = log
            upload.save()

