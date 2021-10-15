from core.utils import cdebug
import re
import time
import datetime
import sys, os
import dateutil.parser
from django.utils.dateparse import parse_date
from django.core.management.base import BaseCommand
from csv import DictReader
from master_data.models import Category,Outlet ,OutletType,Upload,Product,ColLabel
from master_setups.models import Country,IndexSetup
import json
from collections import OrderedDict
from core.settings import MEDIA_ROOT
from core.utils import cdebug, csvHeadClean,printr

import logging
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
            Product.objects.filter(country=upload.country).delete()

        product_fields = []
        skip_cols = ['id','pk','country','category','productaudit','upload','created','updated',]
        for v in Product._meta.get_fields():
            if(v.name not in skip_cols):
                product_fields.append(v.name)

        # printr(Colors.BRIGHT_PURPLE,form_obj.file)
        try:
            with open(MEDIA_ROOT+'/'+str(upload.file), 'r',encoding='utf-8-sig') as read_obj:
                csv_reader = DictReader(read_obj)
                log += printr(".....CSV Read Successfully.....")
                n=0
                log += printr("csv.DictReader took %s seconds" % (time.time() - start_time))

                for row in csv_reader:
                    n+=1
                    temp_row = dict()
                    # printr(n,end=' ',flush=True)
                    row = {csvHeadClean(k): v.strip() for (k, v) in row.items()}

                    temp_row = row
                    # product_code	product	pack_type	aggregation_level	category_code	company	brand	family	flavour_type	weight	price_segment	length_range	number_in_pack	price_per_stick
                    # ('pack_type', 'aggregation_level', 'category_code', 'company', 'brand', 'family', 'flavour_type', 'weight', 'price_segment', 'length_range', 'number_in_pack', 'price_per_stick', )
                    for (k, v) in row.items():
                        # k = re.sub('[^A-Za-z0-9]+', '_', k).lower().strip('_')
                        v = str(v.strip())
                        if(str(v.lower()) in ['-','na','nill','','null','n/a']):
                            v = None
                        else:
                            v = str(v)
                        row[k] = v
                    # cdebug(row,'Line:70')
                    product_code = row['product_code']
                    product_name = row.pop("product_name", "")
                    category_code = row['category_code']
                    row['code'] = product_code
                    row['name'] = product_name
                    row["upload"] = upload

                    row.pop("product_code", None)
                    row.pop("category_code", None)
                    row.pop("category_name", None)

                    #remove extra fields
                    for v in product_fields:
                        if(v not in row.keys()):
                            row.pop(v, None)
                    cdebug(row,'Line:86')
                    cdebug(product_fields)

                    category_qs = None
                    if(category_code != ''):
                        try:
                            category_qs = Category.objects.get(country=upload.country, code__iexact=category_code)
                        except Category.DoesNotExist:
                            category_qs = None

                    if(category_qs is None):
                        log += printr('skip category: ' + category_code)
                        skiped_records+=1
                        continue

                    row['category'] = category_qs

                    extra_count = 1
                    max_extra = 30
                    for key, val in list(temp_row.items()):
                        if('extra' in key and extra_count <= max_extra):
                            # print(key,val)
                            extra  = key.replace('extra_','')
                            extra  = extra.replace('_', ' ')
                            extra  = extra.title()

                            col_name = 'extra_'+str(extra_count)

                            row[col_name] = val
                            cdebug(key,'row')
                            del row[key]
                            if n==1:
                                col_label_qs, created = ColLabel.objects.update_or_create(
                                    country=upload.country, model_name=ColLabel.Product,col_name=col_name,
                                    defaults={'col_label':extra},
                                )

                            extra_count += 1


                    cdebug(row)
                    if(upload.import_mode == Upload.APPEND or upload.import_mode == Upload.REFRESH ):

                        # In this case, if the Person already exists, its existing name is preserved
                        obj, created = Product.objects.get_or_create(
                            country=upload.country, code=product_code,
                            defaults=row
                        )
                        if(created): created_records+=1


                    if(upload.import_mode == Upload.APPENDUPDATE ):
                        # In this case, if the Person already exists, its name is updated
                        obj, created = Product.objects.update_or_create(
                            country=upload.country, code=product_code,
                            defaults=row
                        )
                        if(created): created_records+=1
                        else: updated_records+=1



            logger.error('CSV file processed successfully.')
            log += 'CSV file processed successfully.'
            log += printr("Total time spent: %s seconds" % (time.time() - start_time))
            upload.is_processing = Upload.COMPLETED
            upload.process_message = "CSV file processed successfully."
            upload.log  = log
            upload.skiped_records = skiped_records
            upload.created_records = created_records
            upload.updated_records = updated_records
            upload.save()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            logger.error('CSV file processing failed. Error Msg:'+ str(e))
            log += 'CSV file processing failed. Error Msg:'+ str(e)
            upload.is_processing = Upload.ERROR
            upload.process_message = "CSV file processing failed. Error Msg:"+str(e)
            upload.log  = log
            upload.save()

