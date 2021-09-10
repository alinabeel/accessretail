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

        # printr(Colors.BRIGHT_PURPLE,form_obj.file)
        try:
            with open(MEDIA_ROOT+'/'+str(upload.file), 'r',encoding='utf-8-sig') as read_obj:
                csv_reader = DictReader(read_obj)
                log += printr(".....CSV Read Successfully.....")
                n=0
                log += printr("csv.DictReader took %s seconds" % (time.time() - start_time))

                for row in csv_reader:
                    # printr(n,end=' ',flush=True)
                    row = {k.strip(): v.strip() for (k, v) in row.items()}

                    row["upload"] = upload

                    month = row['month']
                    year = row['year']


                    """ Select Month """
                    ymd = parser.parse('1 '+str(month)+' '+str(year))
                    mcode = ymd.strftime("%b").upper() + ymd.strftime("%y")


                    """Get or Create Outlet Month"""
                    try:
                        month_obj = Month.objects.get(country=upload.country, month=ymd.strftime("%m"),year=ymd.strftime("%Y"))
                    except Month.DoesNotExist:
                        log += printr('Month not exist: '+mcode)
                        skiped_records+=1
                        continue

                    #Check if month is locked
                    if(month_obj.is_locked==True):
                        log += printr('Month Locked:'+mcode)
                        skiped_records+=1
                        continue

                    row['month'] = month_obj


                    # del row["index"]
                    # del row["outlet_code"]
                    # del row["outlet_type_code"]

                    """First Get  Outlet Object"""
                    if('outlet_code' in row):
                        try:
                            outlet_obj= Outlet.objects.get(country=upload.country, code=row["outlet_code"])
                        except Outlet.DoesNotExist:
                            log += printr('Master Outlet not exist: '+row["outlet_code"])
                            skiped_records+=1
                            continue
                        row['outlet'] = outlet_obj


                    """ Manuplae Audit Date """
                    if 'audit_date' in row:
                        audit_date = audit_date.split('/')
                        ymd2 = parser.parse(str(audit_date[0].strip())+' '+str(audit_date[1].strip())+' '+str(audit_date[2].strip()))
                        # # print('audit_date: ',ymd2.strftime("%Y"),ymd2.strftime("%m"),ymd2.strftime("%d"))
                        audit_date_obj = datetime.datetime(int(ymd2.strftime("%Y")), int(ymd2.strftime("%m")), int(ymd2.strftime("%d")))
                        # # print(audit_date_obj)
                        row['audit_date'] = audit_date_obj



                    """ Select Outlet Type or Skip  """
                    if "outlet_type_code" in row:

                        try:
                            outlet_type_qs = OutletType.objects.filter(
                                                Q(country=upload.country) &
                                                Q(code=row["outlet_type_code"]) | Q(name=row["outlet_type_code"])).get()
                        except OutletType.DoesNotExist:
                            outlet_type_qs = None
                            log += printr('OutletType code not exist: '+row["outlet_type_code"])
                            skiped_records+=1
                            continue

                        row['outlet_type'] = outlet_type_qs

                    """ Select Inex or Skip  """
                    if("index" in row):
                        try:
                            index_qs = IndexSetup.objects.filter(
                                                Q(country=upload.country) &
                                                Q(code=row["index"]) | Q(name=row["index"])).get()
                        except IndexSetup.DoesNotExist:
                            index_qs = None
                            log += printr('index code not exist: '+row["index"])
                            skiped_records+=1
                            continue

                        row['index'] = index_qs





                    if(upload.import_mode == Upload.UPDATE ):
                        """In this case, if the Person already exists, its name is updated"""
                        try:
                            PanelProfile.objects.get(country=upload.country, outlet=outlet_obj, month=month_obj)
                        except PanelProfile.DoesNotExist:
                            log += printr('Outlet code not exist in Panel Profile: '+row["outlet_code"])
                            skiped_records+=1
                            continue

                        # PanelProfile.objects.filter(country=upload.country, outlet=outlet_obj, month=month_obj).update(
                        #     defaults=row
                        # )
                        defaults=row
                        obj = PanelProfile.objects.get(country=upload.country, outlet=outlet_obj, month=month_obj)
                        for key, value in defaults.items():
                            setattr(obj, key, value)
                        obj.save()
                        updated_records+=1

                    upload.skiped_records = skiped_records
                    upload.created_records = created_records
                    upload.updated_records = updated_records
                    upload.save()
                    n+=1


            logger.error('CSV file processed successfully.')
            log += 'CSV file processed successfully.'
            log += printr("Total time spent: %s seconds" % (convert(time.time() - start_time)))
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

