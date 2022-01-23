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
            PanelProfile.objects.filter(country=upload.country, index=upload.index).delete()

        # Get Valid Model Fields
        valid_fields = modelValidFields("PanelProfile")
        foreign_fields = modelForeignFields("PanelProfile")
        valid_fields_all = valid_fields + foreign_fields

        for ff in foreign_fields:
                valid_fields_all.append(f"{ff}_id")

        outlet_status_list = IdCodeModel(upload.country.id,'OutletStatus')
        outlet_type_list = IdCodeModel(upload.country.id,'OutletType')
        month_list = IdCodeModel(upload.country.id,'Month')
        month_islocked_list = chkMonthLocked(upload.country.id)
        city_village_list = IdCodeModel(upload.country.id,'CityVillage')


        try:
            with open(MEDIA_ROOT+'/'+str(upload.file), 'r',encoding='utf-8-sig') as read_obj:
                csv_reader = DictReader(read_obj)
                log += printr(".....Panel Profile Read Successfully.....")
                n=0
                log += printr("csv.DictReader took %s seconds" % (time.time() - start_time))

                for row in csv_reader:
                    n+=1
                    if n%500==0:
                        print(n,end=' ',flush=True)

                    row = {replaceIndex(k): v.strip() for (k, v) in row.items()}
                    row["upload"] = upload

                    # ['month', 'index', 'category', 'city_village', 'outlet', 'outlet_type', 'outlet_status']

                    # Conver Foreign fields into row
                    for ff in foreign_fields:
                        if f"{ff}_code" in row:
                            row[f"{ff}"] = row.pop(f"{ff}_code", None)


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



                    """ Audit Date """
                    if('audit_date' in row and row['audit_date'] != ''):
                        row['audit_date'] = parser.parse(row['audit_date'],dayfirst=True)


                    """ Select Outlet Type or Skip  """
                    if('outlet_type' in row):
                        if(row['outlet_type'] != ''):
                            try:
                                row['outlet_type_id'] = outlet_type_list[str(row['outlet_type']).lower()]
                            except KeyError:
                                log += printr(f'outlet_type not exist at: {n}')
                                skiped_records+=1
                                continue
                        else:
                            log += printr(f'outlet_type is empty at row at: {n}')
                            skiped_records+=1
                            continue
                        del row['outlet_type']


                    """ Select Outlet Status or Skip  """
                    if('outlet_status' in row):
                        if(row['outlet_status'] != ''):
                            try:
                                row['outlet_status_id'] = outlet_status_list[str(row['outlet_status']).lower()]
                            except KeyError:
                                log += printr(f'outlet_status not exist at: {n}')
                                skiped_records+=1
                                continue
                        else:
                            log += printr(f'outlet_status is empty at row at: {n}')
                            skiped_records+=1
                            continue
                        del row['outlet_status']

                    """ Select CityVillage or Skip  """
                    if('city_village' in row):
                        if(row['city_village'] != ''):
                            try:
                                row['city_village_id'] = city_village_list[str(row['city_village']).lower()]
                            except KeyError:
                                log += printr(f'city_village not exist at: {n}')
                                skiped_records+=1
                                continue
                        else:
                            log += printr(f'outlet status is empty at row at: {n}')
                            skiped_records+=1
                            continue
                        del row['city_village']

                    """Get Outlet Object"""
                    if('outlet' in row and row['outlet'] != ''):
                        try:
                            outlet_obj = Outlet.objects.get(
                                country=upload.country, code__iexact=str(row['outlet'])
                            )
                            row['outlet'] = outlet_obj
                        except Outlet.DoesNotExist:
                            outlet_obj = None
                            log += printr('Outlet code not exist: '+row["outlet"])
                            skiped_records+=1
                            continue
                    else:
                        log += printr(f'outlet is empty or not exist at row at: {n}')
                        skiped_records+=1
                        continue

                    new_row = { key:value for (key,value) in row.items() if key in valid_fields_all}
                    print(new_row)
                    cdebug(row)
                    # exit()

                    if(upload.import_mode == Upload.UPDATE ):


                        obj, created = PanelProfile.objects.update_or_create(
                            country=upload.country, outlet=outlet_obj, month_id=row['month_id'],index=upload.index,
                            defaults=new_row
                        )
                        if(created): created_records+=1
                    print(obj.id)
                    cdebug(created)
                    exit()


                    upload.skiped_records = skiped_records
                    upload.created_records = created_records
                    upload.updated_records = updated_records
                    upload.save()





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
            cdebug(row,'row')
            log += 'CSV file processing failed. Error Msg:'+ str(e)
            upload.is_processing = Upload.ERROR
            upload.process_message = "CSV file processing failed. Error Msg:"+str(e)
            upload.log  = log
            upload.save()

