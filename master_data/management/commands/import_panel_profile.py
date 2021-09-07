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
            PanelProfile.objects.filter(country=upload.country).delete()



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

                    month = row['month']
                    year = row['year']
                    index = row['index']
                    outlet_code = row['outlet_code']
                    audit_date = row['audit_date']
                    outlet_type_code = row['outlet_type_code']
                    outlet_status = row['outlet_status']


                    del row["month"]
                    del row["year"]
                    del row["index"]
                    del row["outlet_code"]
                    del row["outlet_type_code"]

                    """First Get or Create Outlet Object"""
                    outlet_obj, created = Outlet.objects.get_or_create(
                        country=upload.country, code=outlet_code,
                        defaults={
                        },
                    )

                    row['outlet'] = outlet_obj

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

                    # month_obj = datetime.datetime.strptime(month, "%B")
                    # month_number = month_obj.month
                    # month_year = datetime.date(int(year), int(month_number), 1)
                    # row['month_year'] = month_year

                    """ Manuplae Audit Date """
                    # audit_date = audit_date.split('/')
                    # ymd2 = parser.parse(str(audit_date[0].strip())+' '+str(audit_date[1].strip())+' '+str(audit_date[2].strip()))
                    # # print('audit_date: ',ymd2.strftime("%Y"),ymd2.strftime("%m"),ymd2.strftime("%d"))
                    audit_date_obj = datetime.datetime(int(ymd.strftime("%Y")), int(ymd.strftime("%m")), int(ymd.strftime("%d")))
                    # # print(audit_date_obj)
                    row['audit_date'] = audit_date_obj
                    # exit()
                    row["upload"] = upload

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

                    """ Select Inex or Skip  """
                    if(index != ''):
                        try:
                            index_qs = IndexSetup.objects.filter(
                                                Q(country=upload.country) &
                                                Q(code=index) | Q(name=index)).get()
                        except IndexSetup.DoesNotExist:
                            index_qs = None
                            log += printr('index code not exist: '+index)
                            skiped_records+=1
                            continue
                    else:
                        skiped_records+=1
                        log += printr('index code is empty: '+index)
                        continue

                    row['index'] = index_qs


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

