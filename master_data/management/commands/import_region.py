import time
from django.core.management.base import BaseCommand
from csv import DictReader
from master_data.models import *
from master_setups.models import *
import json
from collections import OrderedDict
from core.settings import MEDIA_ROOT
import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('upload_id', type=int)

    def handle(self, *args, **options):

        start_time = time.time()

        upload_id = options['upload_id']
        upload = Upload.objects.get(pk=upload_id)
        country = Country.objects.get(pk=upload.country.id)

        if(upload.import_mode == Upload.REFRESH):
            Region.objects.filter(country=upload.country).delete()



        # print(Colors.BRIGHT_PURPLE,form_obj.file)
        try:
            with open(MEDIA_ROOT+'/'+str(upload.file), 'r',encoding='utf-8-sig') as read_obj:
                csv_reader = DictReader(read_obj)
                print(".....I am in .....")
                n=0
                print("csv.DictReader took %s seconds" % (time.time() - start_time))
                valid_heads = ['category_code','urbanity','outlet_type','outlet_type_code','is_active','description']

                for row in csv_reader:
                    print(n,end=' ',flush=True)
                    row = {k.strip(): v.strip() for (k, v) in row.items()}

                    # data_head = list(row.keys())
                    # data_values = list(row.values())

                    print("csv_reader took %s seconds" % (time.time() - start_time))

                    if(row['is_active'].lower() in ['t','y','yes','',1,'1','']):
                        is_active = True
                    else:
                        is_active = False

                    name = row['outlet_type']
                    code = row['outlet_type_code']

                    category_code = row['category_code']
                    urbanity = row['urbanity']
                    description = row['description']
                    parent = None
                    if(row['parent'] != ''):
                        try:
                            parent = Region.objects.get(country=upload.country, code=row['parent'])
                        except Region.DoesNotExist:
                            parent = None


                    category = ''
                    if(category_code != ''):
                        try:
                            category = Category.objects.get(country=upload.country, code__iexact=category_code)
                        except Region.DoesNotExist:
                            category = ''



                    if(upload.import_mode == Upload.APPEND or upload.import_mode == Upload.REFRESH ):
                        # In this case, if the Person already exists, its existing name is preserved
                        category, created = Region.objects.get_or_create(

                            country = upload.country, code=code,
                            defaults={
                                'upload': upload,
                                'category': category,
                                'name': name,
                                'description': description,
                                'is_active': is_active,
                                'parent': parent,
                                'urbanity' : urbanity
                            },

                        )


                    if(upload.import_mode == Upload.APPENDUPDATE ):
                        # In this case, if the Person already exists, its name is updated
                        category, created = Region.objects.update_or_create(
                            country=upload.country,code=code,
                            defaults={
                                'upload': upload,
                                'category': category,
                                'name': name,
                                'description': description,
                                'is_active': is_active,
                                'parent': parent,
                                'urbanity' : urbanity
                            },
                        )

                    n+=1

            logger.error('CSV file processed successfully.')
            upload.is_processing = Upload.COMPLETED
            upload.process_message = "CSV file processed successfully."
            upload.save()
        except Exception as e:
            logger.error('CSV file processing failed. Error Msg:'+ str(e))
            upload.is_processing = Upload.ERROR
            upload.process_message = "CSV file processing failed. Error Msg:"+str(e)
            upload.save()