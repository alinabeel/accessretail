from core.common_libs import *
from master_data.models import *
from master_setups.models import *

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('upload_id', type=int)

    def handle(self, *args, **options):

        upload_id = options['upload_id']
        upload = Upload.objects.get(pk=upload_id)
        country = Country.objects.get(pk=upload.country.id)

        if(upload.import_mode == Upload.REFRESH):
            Category.objects.filter(country=upload.country).delete()



        # print(Colors.BRIGHT_PURPLE,form_obj.file)
        try:
            with open(MEDIA_ROOT+'/'+str(upload.file), 'r',encoding='utf-8-sig') as read_obj:
                csv_reader = DictReader(read_obj)
                print(".....I am in .....")
                n=0

                for row in csv_reader:
                    print(n,end=' ',flush=True)
                    row = {k.strip(): v.strip() for (k, v) in row.items()}

                    code = row['code']

                    if(row['is_active'].lower() in ['t','y','yes','',1,'1','']):
                        is_active = True
                    else:
                        is_active = False


                    parent = None
                    if(row['parent']!=''):
                        try:
                            parent = Category.objects.get(country=upload.country, code__iexact=row['parent'])
                        except Category.DoesNotExist:
                            parent = None


                    if(upload.import_mode == Upload.APPEND or upload.import_mode == Upload.REFRESH ):
                        # In this case, if the Person already exists, its existing name is preserved
                        category, created = Category.objects.get_or_create(

                            country=upload.country, code__iexact=row['code'],
                            defaults={
                                'upload': upload,
                                'name':row['name'],
                                'description':row['description'],
                                'is_active': is_active,
                                'parent': parent,
                            },

                        )


                    if(upload.import_mode == Upload.APPENDUPDATE ):
                        # In this case, if the Person already exists, its name is updated
                        category, created = Category.objects.update_or_create(
                            country=upload.country,code__iexact=row['code'],
                            defaults={
                                'upload': upload,
                                'name':row['name'],
                                'description':row['description'],
                                'is_active': is_active,
                                'parent': parent,
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