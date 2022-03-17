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

        if(upload.import_mode == Upload.REFRESH):
            Cell.objects.filter(country=upload.country,index=upload.index).delete()

        # Get Valid Model Fields
        valid_fields = modelValidFields("Cell")

        try:
            with open(MEDIA_ROOT+'/'+str(upload.file), 'r',encoding='utf-8-sig') as read_obj:
                csv_reader = DictReader(read_obj)
                log += printr(".....CSV Read Successfully.....")
                n = 0
                row_count = 0
                log += printr("csv.DictReader took %s seconds" % (time.time() - start_time))

                for row in csv_reader:
                    n+=1

                    print(n,end=' ',flush=True)
                    row = {replaceIndex(k): v.strip() for (k, v) in row.items()}

                    row['upload'] = upload
                    row['cell_name'] = row['cell_name'].upper()
                    cell_name = row['cell_name']
                    cell_acv = row['cell_acv']

                    if(cell_name == ''):
                        log += ('mising information, ignore csv row: '+ str(n))
                        skiped_records+=1
                        continue

                    row['is_active'] = True
                    # if( row['is_active'].lower() in ['t','true','y','yes','',1,'1','']):
                    #     row['is_active'] = True


                    new_row = { key:value for (key,value) in row.items() if key in valid_fields}
                    cdebug(new_row)
                    month_qs = Month.objects.all().filter(country = upload.country)
                    if(upload.import_mode == Upload.APPEND or upload.import_mode == Upload.REFRESH ):

                        # In this case, if the Person already exists, its existing name is preserved
                        obj, created = Cell.objects.get_or_create(
                            country=upload.country, index=upload.index, name=cell_name,
                            defaults = new_row
                        )
                        if(created): created_records+=1

                        for key in month_qs:
                            CellMonthACV.objects.get_or_create(
                                country=upload.country, index=upload.index, month=key, cell=obj,
                                defaults={'cell_acv':float(cell_acv)}
                            )

                    if(upload.import_mode == Upload.APPENDUPDATE ):
                        # In this case, if the Person already exists, its name is updated
                        obj, created = Cell.objects.update_or_create(
                            country=upload.country, index=upload.index, name=cell_name,
                            defaults = new_row
                        )
                        if(created): created_records+=1
                        else: updated_records+=1

                        for key in month_qs:
                            CellMonthACV.objects.update_or_create(
                                country=upload.country, index=upload.index, month=key, cell=obj,
                                defaults={'cell_acv':float(cell_acv)}
                            )


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

