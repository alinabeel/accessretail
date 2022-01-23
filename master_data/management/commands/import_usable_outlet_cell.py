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

        # Get Valid Model Fields
        valid_fields = modelValidFields("UsableOutlet")
        foreign_fields = modelForeignFields("UsableOutlet")
        valid_fields_all = valid_fields + foreign_fields

        for ff in foreign_fields:
                valid_fields_all.append(f"{ff}_id")

        objs = Cell.objects.filter(country=upload.country,index=upload.index).values('id','name')
        cell_list = dict()
        for obj in objs:
            cell_list[str(obj['name']).lower()] = obj['id']

        month_list = getCode2AnyModelFieldList(upload.country.id,'Month','id')
        outlet_list = getCode2AnyModelFieldList(upload.country.id,'Outlet','id')
        month_islocked_list = getCode2AnyModelFieldList(upload.country.id,'Month','is_locked')

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

                    row["upload"] = upload

                    for ff in foreign_fields:
                        if ff=='cell':
                            row[f"{ff}"] = row.pop(f"{ff}_name", None)

                        if f"{ff}_code" in row:
                            row[f"{ff}"] = row.pop(f"{ff}_code", None)

                    # month_code = row['month_code']
                    # index = row['index']
                    # outlet_code = row['outlet_code']

                    # cdebug(row)
                    # exit()

                    # if row['cell_description'] != '' and len(row['cell_description'])>1:
                    #     cell_name = row['cell_description'].split("@")
                    #     cell_name = get_max_str(cell_name)
                    # else:
                    #     continue

                    # del row["month_code"]
                    # del row["index"]
                    # del row["outlet_code"]

                    """Get Month"""
                    if(row['month'] != ''):
                        try:
                            row['month_id'] = month_list[str(row['month']).lower()]
                        except KeyError:
                            log += printr(f'month not exist at: {n}')
                            skiped_records+=1
                            continue
                    else:
                        log += printr('month is empty at: '+str(row['month']))
                        skiped_records+=1
                        continue

                    #Check if month is locked
                    if(month_islocked_list[str(row['month']).lower()]==True):
                        log += 'Month Locked:, CSV ROW: '+ str(n)
                        skiped_records+=1
                        continue

                    del row['month']




                    """Get or Skip Cell Object"""
                    if(row['cell'] != ''):
                        try:
                            row['cell_id'] = cell_list[str(row['cell']).lower()]
                        except KeyError:
                            log += printr(f'cell not exist at: {n}')
                            skiped_records+=1
                            continue
                    else:
                        log += printr('cell is empty at: '+str(row['month']))
                        skiped_records+=1
                        continue

                    del row['cell']

                    # try:
                    #     cell_obj = Cell.objects.get(country=upload.country, name__iexact=cell_name)
                    # except Cell.DoesNotExist:
                    #     cell_obj = None
                    #     log += printr('Cell name not exist: '+cell_name)
                    #     skiped_records+=1
                    #     continue

                    # row['cell'] = cell_obj


                    # """Get or Skip Month Object"""
                    # try:
                    #     month_obj = Month.objects.get(country=country, code__iexact=month_code)
                    # except Month.DoesNotExist:
                    #     month_obj = None
                    #     log += ('month code not exist, csv row: '+ str(n))
                    #     skiped_records += 1
                    #     continue

                    # row['month'] = month_obj


                    """ Select Inex or Skip  """
                    # index_qs = None
                    # if(index != ''):
                    #     try:
                    #         index_qs = IndexSetup.objects.filter(
                    #                             Q(country=upload.country) &
                    #                             Q(code__iexact = index)).get()
                    #     except IndexSetup.DoesNotExist:
                    #         log += printr('index code not exist: '+index)
                    #         skiped_records+=1
                    #         continue
                    # else:
                    #     skiped_records+=1
                    #     log += printr('index code is empty: '+index)
                    #     continue

                    # row['index'] = index_qs

                    """Get or Skip Outlet Object"""

                    if(row['outlet'] != ''):
                        try:
                            row['outlet_id'] = outlet_list[str(row['outlet']).lower()]
                        except KeyError:
                            log += printr(f'outlet not exist at: {n}')
                            skiped_records+=1
                            continue
                    else:
                        log += printr('outlet is empty at: '+str(row['month']))
                        skiped_records+=1
                        continue

                    del row['outlet']


                    # try:
                    #     outlet_obj = Outlet.objects.get(country=upload.country, code__iexact=outlet_code)
                    # except Outlet.DoesNotExist:
                    #     outlet_obj = None
                    #     log += printr('Outlet code not exist: '+outlet_code)
                    #     skiped_records+=1
                    #     continue

                    # row['outlet'] = outlet_obj

                    new_row = { key:value for (key,value) in row.items() if key in valid_fields_all}

                    if(upload.import_mode == Upload.APPEND or upload.import_mode == Upload.REFRESH ):

                        obj, created = UsableOutlet.objects.get_or_create(
                            country=upload.country, outlet_id=row['outlet_id'], month_id=row['month_id'],
                            defaults=new_row
                        )
                        if(created): created_records+=1


                    if(upload.import_mode == Upload.APPENDUPDATE ):
                        """In this case, if the Person already exists, its name is updated"""
                        obj, created = UsableOutlet.objects.update_or_create(
                            country=upload.country,
                            cell_id=row['cell_id'],
                            outlet_id=row['outlet_id'],
                            month_id=row['month_id'],
                            index=upload.index,
                            defaults=new_row
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
