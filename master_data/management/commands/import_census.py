from core.common_libs import *
from master_data.models import *
from master_setups.models import *

class Command(BaseCommand):

    def add_arguments(self, parser):
        # parser.add_argument('country_code', type=str)
        parser.add_argument('upload_id', type=int)

    def handle(self, *args, **options):

        upload_id = options['upload_id']
        upload = Upload.objects.get(pk=upload_id)
        country = Country.objects.get(pk=upload.country.id)

        if(upload.import_mode == Upload.REFRESH):
            Census.objects.filter(country=country).delete()


        # print(Colors.BRIGHT_PURPLE,form_obj.file)
        try:
            with open(MEDIA_ROOT+'/'+str(upload.file), 'r',encoding='utf-8-sig') as read_obj:
                csv_reader = DictReader(read_obj)
                print(".....I am in .....")
                n=0
                for row in csv_reader:
                    print(n,end=' ',flush=True)
                    # print(row)
                    # print(type(row))
                    data_head = list(row.keys())
                    od = OrderedDict()
                    for (k, v) in row.items():
                        k = re.sub('[^A-Za-z0-9]+', '_', k).lower().strip('_')
                        v = str(v.strip())
                        if(str(v.lower()) in ['true','t','y','yes']):
                            v = True
                        elif(str(v.lower()) in ['false','f','n','no']):
                            v = False
                        elif(str(v.lower()) in ['na','nill','','null']):
                            v = None
                        elif(v.replace('.','',1).isdigit()):
                            v = float(v)
                        else:
                            v = str(v)

                        od[k] = v

                    # row = {k.strip(): v.strip() for (k, v) in row.items()}
                    json_row = json.dumps(od)

                    # json_row = json_row.lstrip('\\ufeff')
                    # print(json_row)
                    if(upload.import_mode == Upload.APPENDUPDATE ):
                        census, created = Census.objects.update_or_create(
                            country=upload.country,censusdata=json_row,
                            defaults={
                                'upload' : upload,
                                'country' : country,
                                'censusdata' : json_row,
                                'heads' : data_head
                            },
                        )

                    if(upload.import_mode == Upload.APPEND ):
                        # In this case, if the Person already exists, its existing name is preserved
                        census, created = Census.objects.get_or_create(
                            country=upload.country,censusdata=json_row,
                            defaults={
                                'upload' : upload,
                                'country' : country,
                                'censusdata' : json_row,
                                'heads' : data_head
                            },

                        )

                    if(upload.import_mode == Upload.REFRESH ):
                        new = Census.objects.create(
                            upload = upload,
                            country = country,
                            censusdata = json_row,
                            heads = data_head,
                        )



                    n+=1
            logger.error('Census file processed successfully.')
            upload.is_processing = Upload.COMPLETED
            upload.process_message = "Census file processed successfully."
            upload.save()
        except Exception as e:
            logger.error('Census file processing failed. Error Msg:'+ str(e))
            upload.is_processing = Upload.ERROR
            upload.process_message = "Census file processing failed. Error Msg:"+str(e)
            upload.save()


        # # organisation = UserProfile.objects.get(user__email=organisor_email)
        # country = Country.objects.get(id=1)
        # with open(file_name, 'r',encoding='utf-8-sig') as read_obj:
        #     csv_reader = DictReader(read_obj)

        #     for row in csv_reader:
        #         row = {k.strip(): v.strip() for (k, v) in row.items()}
        #         data_head = list(row.keys())
        #         data_values = list(row.values())
        #         json_row = json.dumps(row)
        #         print((row))
        #         exit()

        #         # json_row = json_row.lstrip('\\ufeff')
        #         # print(json_row)
        #         new = Census.objects.create(
        #             country=country,
        #             censusdata=json_row,
        #             data_head = data_head,
        #             data_values = data_values,
        #         )



