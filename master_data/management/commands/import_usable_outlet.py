from core.common_libs import *
from master_data.models import *
from master_setups.models import *


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('upload_id', type=int)

    def handle(self, *args, **options):
        start_time = time.time()
        upload_id = options['upload_id']
        upload = Upload.objects.get(pk=upload_id)
        country = Country.objects.get(pk=upload.country.id)
        log = ""

        updated_list = []
        # printr(Colors.BRIGHT_PURPLE,form_obj.file)
        try:
            with open(MEDIA_ROOT+'/'+str(upload.file), 'r',encoding='utf-8-sig') as read_obj:
                csv_reader = DictReader(read_obj)
                log += printr(".....CSV Read Successfully.....")
                log += printr("csv.DictReader took %s seconds" % (time.time() - start_time))

                n=0
                skiped_records = 0
                updated_records = 0
                created_records = 0
                for row in csv_reader:
                    # printr(n,end=' ',flush=True)
                    row = {replaceIndex(k): v.strip() for (k, v) in row.items()}

                    # month = row['month']
                    # year = row['year']
                    month_code = row['month_code']
                    index = row['index']
                    outlet_code = row['outlet_code']
                    row["upload"] = upload

                    # del row["month"]
                    # del row["year"]
                    del row["month_code"]
                    del row["index"]
                    del row["outlet_code"]



                    try:
                        month_obj = Month.objects.get(country=country, code=month_code)
                    except Month.DoesNotExist:
                        month_obj = None
                        log += ('month code not exist, csv row: '+ str(n))
                        skiped_records += 1
                        continue

                    row['month'] = month_obj


                    """ Select Inex or Skip  """
                    index_qs = None
                    if(index != ''):
                        try:
                            index_qs = IndexSetup.objects.filter(
                                                Q(country=upload.country) &
                                                Q(code__iexact = index)).get()
                        except IndexSetup.DoesNotExist:
                            log += printr('index code not exist: '+index)
                            skiped_records+=1
                            continue
                    else:
                        skiped_records+=1
                        log += printr('index code is empty: '+index)
                        continue

                    row['index'] = index_qs

                    """Get or Skip Outlet Object"""
                    try:
                        outlet_obj = Outlet.objects.get(country=upload.country, code=outlet_code)
                    except Outlet.DoesNotExist:
                        outlet_obj = None
                        log += printr('Outlet code not exist: '+outlet_code)
                        skiped_records+=1
                        continue

                    row['outlet'] = outlet_obj




                    if(upload.import_mode == Upload.APPEND or upload.import_mode == Upload.REFRESH ):

                        obj, created = UsableOutlet.objects.get_or_create(
                            country=upload.country, outlet=outlet_obj, month=month_obj,
                            defaults=row
                        )
                        if(created): created_records+=1


                    if(upload.import_mode == Upload.APPENDUPDATE ):

                        obj, created = UsableOutlet.objects.update_or_create(
                            country=upload.country, outlet=outlet_obj, month=month_obj,
                            defaults=row
                        )
                        if(created): created_records+=1
                        else: updated_records+=1

                    n+=1

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
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'CSV file processing failed. Error Msg:'+ str(e)+Colors.WHITE )

            log += 'CSV file processing failed. Error Msg:'+ str(e)
            upload.is_processing = Upload.ERROR
            upload.process_message = "CSV file processing failed. Error Msg:"+str(e)
            upload.log  = log
            upload.save()
