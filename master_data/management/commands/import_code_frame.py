from core.common_libs import *
from master_setups.models import *
from master_data.models import *
from reports.models import *

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
            Province.objects.filter(country=upload.country).delete()
            District.objects.filter(country=upload.country).delete()
            Tehsil.objects.filter(country=upload.country).delete()
            CityVillage.objects.filter(country=upload.country).delete()

        # Get Valid Model Fields
        valid_fields = modelValidFields("CityVillage")

        try:
            with open(MEDIA_ROOT+'/'+str(upload.file), 'r',encoding='utf-8-sig') as read_obj:
                csv_reader = DictReader(read_obj)
                log += printr(".....CSV Read Successfully.....")
                n = 0
                row_count = 0
                log += printr("csv.DictReader took %s seconds" % (time.time() - start_time))

                for row in csv_reader:
                    n+=1
                    if n%500==0: print(n,end=' ',flush=True)
                    row = {csvHeadClean(k): v.strip() for (k, v) in row.items()}

                    city_village_row = dict()
                    province_code = row['province_code']
                    province_name = row['province_name']
                    district_code = row['district_code']
                    district_name = row['district_name']
                    tehsil_code = row['tehsil_code']
                    tehsil_name = row['tehsil_name']
                    urbanity = row['urbanity'] if row['urbanity'] else ''

                    city_village_row['code'] = row['city_village_code']
                    city_village_row['name'] = row['city_village_name']
                    city_village_row['upload'] = upload



                    # print(province_name,district_name,tehsil_name,rc_cut)
                    # row["upload"] = upload
                    if(province_code == '' or
                        province_name == '' or
                        district_code == '' or
                        district_name == '' or
                        tehsil_code == '' or
                        tehsil_name == '' or
                        city_village_row['code'] == '' or
                        city_village_row['name'] == ''):

                        log += ('mising information, ignore csv row: '+ str(n))
                        skiped_records+=1
                        print(log)
                        continue

                    # Handle Col head one time only

                    # player_count = 1
                    # max_player = 30
                    # for v in row:
                    #     if('player' in v and player_count <= max_player):
                    #         player  = v.replace('player_','')
                    #         player  = player.replace('_', ' ')
                    #         player  = player.title()
                    #         tag  = row[v]

                    #         col_name = 'extra_'+str(player_count)

                    #         city_village_row[col_name] = tag
                    #         if n==1:
                    #             col_label_qs, created = ColLabel.objects.update_or_create(
                    #                 country=upload.country, model_name=ColLabel.CityVillage,col_name=col_name,
                    #                 defaults={'col_label':player},
                    #             )

                    #         player_count += 1

                    # Get / Add Province
                    province_qs = None
                    # Get / Add Distric
                    district_qs = None



                    ## Handle APPEND and REFRESH
                    if(upload.import_mode == Upload.APPEND or upload.import_mode == Upload.REFRESH ):
                        province_qs, created = Province.objects.get_or_create(
                            country=upload.country, code__iexact=province_code,
                            defaults={'name':province_name},
                        )

                        district_qs, created = District.objects.get_or_create(
                            country=upload.country, code__iexact=district_code,
                            defaults={'name':district_name,'province':province_qs}
                        )

                        tehsil_qs, created = Tehsil.objects.get_or_create(
                            country=upload.country, code__iexact=tehsil_code,
                            defaults={'urbanity' : urbanity,
                                    'district' : district_qs,
                                    'name' : tehsil_name}
                        )

                        city_village_row['tehsil'] = tehsil_qs

                        # Row Of Valid Fields Only
                        new_row = { key:value for (key,value) in city_village_row.items() if key in valid_fields}
                        city_village_qs, created = CityVillage.objects.get_or_create(
                            country=upload.country, code = city_village_row['code'],
                            defaults = new_row
                        )

                    ## Handle APPENDUPDATE
                    if(upload.import_mode == Upload.APPENDUPDATE ):
                        province_qs, created = Province.objects.update_or_create(
                            country=upload.country, code__iexact=province_code,
                            defaults={'name':province_name},
                        )

                        # Get / Add District
                        district_qs, created = District.objects.update_or_create(
                            country=upload.country, code__iexact=district_code,
                            defaults={'name':district_name,'province':province_qs}
                        )

                        # Get / Add Tehsil
                        tehsil_qs, created = Tehsil.objects.update_or_create(
                            country=upload.country, code__iexact=tehsil_code,
                            defaults={'urbanity' : urbanity,
                                    'district' : district_qs,
                                    'name' : tehsil_name}
                        )
                        city_village_row['tehsil'] = tehsil_qs


                        # Row Of Valid Fields Only
                        new_row = { key:value for (key,value) in city_village_row.items() if key in valid_fields}

                        # Get / Add CityVillage
                        city_village_qs, created = CityVillage.objects.update_or_create(
                            country=upload.country, code__iexact = city_village_row['code'],
                            defaults = new_row
                        )


                    # for v in row:
                    #     if('player' in v):
                    #         player  = v.replace('player_','')
                    #         player  = player.replace('_', ' ')
                    #         player  = player.title()
                    #         tag  = row[v]


                    #         if(upload.import_mode == Upload.APPEND or upload.import_mode == Upload.REFRESH ):
                    #             if(player != ''):
                    #                 player_qs, created = Player.objects.get_or_create(
                    #                     country=upload.country, name=player,
                    #                 )
                    #             if(tag != ''):
                    #                 tag_qs, created = Tag.objects.get_or_create(
                    #                     country=upload.country, name=tag,
                    #                 )
                    #             if(tag != '' and player != ''):
                    #                 pt,created  = PlayerTag.objects.get_or_create(country = upload.country,player=player_qs,tag=tag_qs)
                    #                 city_village_qs.player_tag.add(pt)

                    #         if(upload.import_mode == Upload.APPENDUPDATE ):
                    #             if(player != ''):
                    #                 player_qs, created = Player.objects.update_or_create(
                    #                     country=upload.country, name=player,
                    #                 )
                    #                 # print('player:',player_qs, player_qs.id)
                    #             if(tag != ''):
                    #                 tag_qs, created = Tag.objects.update_or_create(
                    #                     country=upload.country, name=tag,
                    #                 )
                    #                 # print('tag:',tag_qs, tag_qs.id)
                    #             if(tag != '' and player != ''):
                    #                 pt,created  = PlayerTag.objects.update_or_create(country = upload.country,player=player_qs,tag=tag_qs)
                    #                 city_village_qs.player_tag.add(pt)


                    # user = Users.objects.get_or_create(name='test_user')
                    # user.tags.add(tag_1)

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

