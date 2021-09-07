import re
import time
import datetime
import sys, os
import dateutil.parser
from django.utils.dateparse import parse_date
from django.core.management.base import BaseCommand
from csv import DictReader
from master_data.models import Upload,Province,District,Tehsil,CityVillage,Player,Tag,PlayerTag
from master_setups.models import Country,IndexSetup
import json
from collections import OrderedDict
from core.settings import MEDIA_ROOT
from core.utils import cdebug, csvHeadClean,printr
import logging
logger = logging.getLogger(__name__)

def cleanTemp(c):
    # c = c.replace('(','')
    # c = c.replace(')','')
    # c = c.replace(',','')
    c = c.strip()

    return c

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

        # TODO: Add refresh functionality
        # if(upload.import_mode == Upload.REFRESH):
        #     Product.objects.filter(country=upload.country).delete()

        # printr(Colors.BRIGHT_PURPLE,form_obj.file)
        try:
            with open(MEDIA_ROOT+'/'+str(upload.file), 'r',encoding='utf-8-sig') as read_obj:
                csv_reader = DictReader(read_obj)
                log += printr(".....CSV Read Successfully.....")
                n = 0
                row_count = 0
                log += printr("csv.DictReader took %s seconds" % (time.time() - start_time))

                for row in csv_reader:
                    n+=1
                    if n<5300: continue
                    print(n,end=' ',flush=True)
                    row = {csvHeadClean(k): cleanTemp(v) for (k, v) in row.items()}


                    province_code = row['province_code']
                    province_name = row['province_name']
                    district_code = row['district_code']
                    district_name = row['district_name']
                    tehsil_code = row['tehsil_code']
                    tehsil_name = row['tehsil_name']
                    urbanity = row['urbanity'] if row['urbanity'] else ''
                    city_village_code = row['city_village_code']
                    city_village_name = row['city_village_name']
                    rc_cut = row['rc_cut']



                    # print(province_name,district_name,tehsil_name,rc_cut)
                    # row["upload"] = upload
                    if(province_code != '' and province_name != '' and
                        district_code != '' and district_name != '' and
                        tehsil_code != '' and tehsil_name != '' and
                        city_village_code != '' and city_village_name != ''):

                        log += ('mising information, ignore csv row: '+ str(n))

                    # Get / Add Province
                    province_qs = None
                    # Get / Add Distric

                    district_qs = None
                    if(upload.import_mode == Upload.APPEND or upload.import_mode == Upload.REFRESH ):
                        province_qs, created = Province.objects.get_or_create(
                            country=upload.country, code=province_code,
                            defaults={'name':province_name},
                        )

                        district_qs, created = District.objects.get_or_create(
                            country=upload.country, code=district_code,
                            defaults={'name':district_name,'province':province_qs}
                        )

                        tehsil_qs, created = Tehsil.objects.get_or_create(
                            country=upload.country, code=tehsil_code,
                            defaults={'urbanity' : urbanity,
                                    'district' : district_qs,
                                    'name' : tehsil_name}
                        )

                        city_village_qs, created = CityVillage.objects.get_or_create(
                            defaults={'name' : city_village_name,
                                    'rc_cut' : rc_cut,
                                    'tehsil' : tehsil_qs,
                                    'upload':upload}
                        )




                    if(upload.import_mode == Upload.APPENDUPDATE ):
                        province_qs, created = Province.objects.update_or_create(
                            country=upload.country, code=province_code,
                            defaults={'name':province_name},
                        )

                        # Get / Add District
                        district_qs, created = District.objects.update_or_create(
                            country=upload.country, code=district_code,
                            defaults={'name':district_name,'province':province_qs}
                        )

                        # Get / Add Tehsil
                        tehsil_qs, created = Tehsil.objects.update_or_create(
                            country=upload.country, code=tehsil_code,
                            defaults={'urbanity' : urbanity,
                                    'district' : district_qs,
                                    'name' : tehsil_name}
                        )

                        # Get / Add CityVillage
                        city_village_qs, created = CityVillage.objects.update_or_create(
                            country=upload.country, code=city_village_code,
                            defaults={'name' : city_village_name,
                                    'rc_cut' : rc_cut,
                                    'tehsil' : tehsil_qs,
                                    'upload':upload}
                        )


                    for v in row:
                        if('player' in v):
                            player  = v.replace('player_','')
                            player  = player.replace('_', ' ')
                            player  = player.title()
                            tag  = row[v]


                            if(upload.import_mode == Upload.APPEND or upload.import_mode == Upload.REFRESH ):
                                if(player != ''):
                                    player_qs, created = Player.objects.get_or_create(
                                        country=upload.country, name=player,
                                    )
                                if(tag != ''):
                                    tag_qs, created = Tag.objects.get_or_create(
                                        country=upload.country, name=tag,
                                    )

                            if(upload.import_mode == Upload.APPENDUPDATE ):
                                if(player != ''):
                                    player_qs, created = Player.objects.update_or_create(
                                        country=upload.country, name=player,
                                    )
                                    # print('player:',player_qs, player_qs.id)
                                if(tag != ''):
                                    tag_qs, created = Tag.objects.update_or_create(
                                        country=upload.country, name=tag,
                                    )
                                    # print('tag:',tag_qs, tag_qs.id)
                                if(tag != '' and player != ''):
                                    pt,created  = PlayerTag.objects.get_or_create(country = upload.country,player=player_qs,tag=tag_qs)
                                    city_village_qs.player_tag.add(pt)
                                    # cv_obj = CityVillage.objects.get(pk=city_village_qs.id)
                                    # print(pt)
                                    # print(city_village_qs)

                                    # cv_obj.save()

                                    # print('city_village_qs:',city_village_qs)
                                    # city_village_qs.player_tag.add('1')
                                    # city_village_qs.save()

                                    # city_village_qs.player_tag = pt
                                    # city_village_qs.save()

                                    # player_tag_qs, created = PlayerTag.objects.update_or_create(
                                    #     country=upload.country, player=player_qs,tag=tag_qs
                                    # )
                                    # print('player_tag_qs:',pt)

                    # user = Users.objects.get_or_create(name='test_user')
                    # user.tags.add(tag_1)

                    # if(upload.import_mode == Upload.APPEND or upload.import_mode == Upload.REFRESH ):

                    #     # In this case, if the Person already exists, its existing name is preserved
                    #     obj, created = Product.objects.get_or_create(
                    #         country=upload.country, code=product_code,
                    #         defaults=row
                    #     )
                    #     if(created): created_records+=1


                    # if(upload.import_mode == Upload.APPENDUPDATE ):
                    #     # In this case, if the Person already exists, its name is updated
                    #     obj, created = Product.objects.update_or_create(
                    #         country=upload.country, code=product_code,
                    #         defaults=row
                    #     )
                    #     if(created): created_records+=1
                    #     else: updated_records+=1


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
            print(('CSV file processing failed at %s Error Msg: %s')%(n,str(e)))
            log += 'CSV file processing failed. Error Msg:'+ str(e)
            upload.is_processing = Upload.ERROR
            upload.process_message = "CSV file processing failed. Error Msg:"+str(e)
            upload.log  = log
            upload.save()

