from core.common_libs import *
from master_data.models import *
from master_setups.models import *

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
        log = ""

        upload.is_processing = Upload.PROCESSING
        upload.process_message = Upload.PROCESSING_MSG
        upload.log  = log
        upload.save()

        if(upload.import_mode == Upload.REFRESH):
            Category.objects.filter(country=upload.country).delete()


        # Get Valid Model Fields
        valid_fields = modelValidFields("Category")
        foreign_fields = modelForeignFields("Category")
        valid_fields_all = valid_fields + foreign_fields


        for ff in foreign_fields:
            valid_fields_all.append(f"{ff}_id")

        # print(Colors.BRIGHT_PURPLE,form_obj.file)
        try:
            with open(MEDIA_ROOT+'/'+str(upload.file), 'r',encoding='utf-8-sig') as read_obj:
                csv_reader = DictReader(read_obj)
                print(".....I am in .....")
                n=0

                for row in csv_reader:
                    print(n,end=' ',flush=True)
                    row = {k.strip(): v.strip() for (k, v) in row.items()}

                    row['upload'] = upload
                    # Conver Foreign fields into row
                    for ff in foreign_fields:
                        if f"{ff}_code" in row:
                            row[f"{ff}"] = row.pop(f"{ff}_code", None)


                    row['code'] = row.pop("category_code", None)
                    row['name'] = row.pop("category_name", None)

                    if(row['is_active'].lower() in ['t','y','yes','',1,'1','']):
                        row['is_active'] = True
                    else:
                        row['is_active'] = False

                    new_row = { key:value for (key,value) in row.items() if key in valid_fields_all}
                    cdebug(new_row,'new_row')

                    parent = None
                    if 'parent' in new_row and new_row['parent'] != '':
                        try:
                            new_row['parent'] = Category.objects.get(country=upload.country, code__iexact=new_row['parent'])
                        except Category.DoesNotExist:
                            parent = None
                    else:
                        new_row.pop("parent",None)


                    if(upload.import_mode == Upload.APPEND or upload.import_mode == Upload.REFRESH ):
                        category, created = Category.objects.get_or_create(
                            country=upload.country, code__iexact=new_row['code'],
                            defaults=new_row

                        )

                        if(created): created_records+=1


                    if(upload.import_mode == Upload.APPENDUPDATE ):
                        category, created = Category.objects.update_or_create(
                            country=upload.country, code__iexact=new_row['code'],
                            defaults=new_row
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
            # cdebug(row,'row')
            log += 'CSV file processing failed. Error Msg:'+ str(e)
            upload.is_processing = Upload.ERROR
            upload.process_message = "CSV file processing failed. Error Msg:"+str(e)
            upload.log  = log
            upload.save()