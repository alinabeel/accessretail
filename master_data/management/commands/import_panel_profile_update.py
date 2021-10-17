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


        # valid_fields = []
        # skip_cols = ['id','pk','country','category','productaudit','upload','created','updated',]
        # for field in PanelProfile._meta.get_fields():
        #     if(field.name not in skip_cols):
        #         if(field.name in skip_cols): continue
        #         if isinstance(field, models.ForeignKey): continue
        #         if isinstance(field, models.ManyToManyRel): continue
        #         if isinstance(field, models.ManyToOneRel): continue
        #         valid_fields.append(field.name)


        # Get Valid Model Fields
        valid_fields = modelValidFields("PanelProfile")
        foreign_fields = modelForeignFields("PanelProfile")
        valid_fields_all = valid_fields + foreign_fields

        for ff in foreign_fields:
                valid_fields_all.append(f"{ff}_id")
        # cdebug(valid_fields_all)
        # print(valid_fields)
        # print(foreign_fields)
        # exit()
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


                    audit_date = row['audit_date']

                    # month_code = row['month_code']
                    # category = row['category']
                    # index = row['index']
                    # city_village_code = row['city_village_code']


                    # outlet_code = row['outlet_code']
                    # outlet_type_code = row['outlet_type_code']
                    # outlet_status_code = row['outlet_status_code']


                    # del row["month_code"]
                    # del row["index"]
                    # del row["category"]
                    # del row["outlet_code"]
                    # del row["outlet_type_code"]
                    # del row["outlet_status_code"]
                    # del row["city_village_code"]

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
                    else:
                        log += printr(f'audit_date is empty/not exist at row at: {n}')
                        skiped_records+=1
                        continue

                    """ Select Outlet Type or Skip  """
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
                    outlet_status_qs = None
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

                    # row.pop(row['outlet_status'])
                    # print(row['outlet_status_id'])
                    # exit()
                    # row['outlet_status'] = outlet_status_qs

                    # """ Select Inex or Skip  """
                    # index_qs = None
                    # if(row['index'] != ''):
                    #     try:
                    #         index_qs = IndexSetup.objects.filter(
                    #                             Q(country=upload.country) &
                    #                             Q(code__iexact = row['index'])).get()
                    #     except IndexSetup.DoesNotExist:
                    #         log += printr('index code not exist: '+row['index'])
                    #         skiped_records+=1
                    #         continue
                    # else:
                    #     skiped_records+=1
                    #     log += printr('index code is empty: '+row['index'])
                    #     continue

                    # row['index'] = index_qs

                    # """ Select Category or Skip  """
                    # category_qs = None
                    # if(row['category'] != ''):
                    #     try:
                    #         category_qs = Category.objects.filter(
                    #                             Q(country=upload.country) &
                    #                             Q(code__iexact=str(row['category']))).get()
                    #     except Category.DoesNotExist:
                    #         log += printr('category code not exist: '+row['category'])
                    #         skiped_records+=1
                    #         continue
                    # else:
                    #     skiped_records+=1
                    #     log += printr('category code is empty: '+row['category'])
                    #     continue

                    # row['category'] = category_qs




                    """ Select CityVillage or Skip  """
                    city_village_qs = None
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

                    """Get or Create Outlet Object"""
                    outlet_obj, created = Outlet.objects.get_or_create(
                        country=upload.country, code__iexact=str(row['outlet']),
                        defaults={'code':row['outlet'],}
                    )
                    row['outlet'] = outlet_obj

                    new_row = { key:value for (key,value) in row.items() if key in valid_fields_all}

                    if(upload.import_mode == Upload.APPEND or upload.import_mode == Upload.REFRESH ):

                        """In this case, if the Person already exists, its existing name is preserved"""
                        obj, created = PanelProfile.objects.get_or_create(
                            country=upload.country, outlet=outlet_obj, month_id=row['month_id'],index=upload.index,
                            defaults=new_row
                        )
                        if(created): created_records+=1


                    if(upload.import_mode == Upload.APPENDUPDATE ):
                        """In this case, if the Person already exists, its name is updated"""
                        obj, created = PanelProfile.objects.update_or_create(
                            country=upload.country, outlet=outlet_obj, month_id=row['month_id'],index=upload.index,
                            defaults=new_row
                        )
                        if(created): created_records+=1
                        else: updated_records+=1

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

