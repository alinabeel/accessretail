from core.common_libs_views import *
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
            PanelProfile.objects.filter(country=upload.country, index_id=upload.index_id).delete()
            PanelProfileChild.objects.filter(country=upload.country, index_id=upload.index_id).delete()


        # valid_fields = []
        # skip_cols = ['id','pk','country','category','AuditData','upload','created','updated',]
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
                log += printr(".....CSV Read Successfully.....")
                n=0
                printr("csv.DictReader took %s seconds" % (time.time() - start_time))
                batch_data_list = []
                objs = []
                batch_start_time = time.time()
                for row in csv_reader:

                    n+=1
                    if n%5000==0:
                        print(convertSecond2Min(time.time() - start_time))
                        print(n,end=' ',flush=True)

                    row = {replaceIndex(k): v.strip() for (k, v) in row.items()}
                    row["upload"] = upload

                    # Conver Foreign fields into row
                    for ff in foreign_fields:
                        if f"{ff}_code" in row:
                            row[f"{ff}"] = row.pop(f"{ff}_code", None)

                    try:
                        if row['index']:
                            del(row['index'])
                    except KeyError:
                        pass


                    """Get Month"""
                    if(row['month'] != ''):
                        try:
                            row['month_id'] = month_list[str(row['month']).lower()]
                        except KeyError:
                            # log += printr(f'month not exist at: {n}')
                            updateUploadStatus(upload.id,"Pleas initilize month first.",Upload.FAILED,log)
                            # skiped_records+=1
                            # continue
                    else:
                        # log += printr('month is empty at: '+str(row['month']))
                        skiped_records+=1
                        continue

                    #Check if month is locked
                    if(month_islocked_list[str(row['month']).lower()]==True):
                        # log += 'Month Locked:, CSV ROW: '+ str(n)
                        skiped_records+=1
                        continue

                    del row['month']


                    """ Audit Date """
                    if('audit_date' in row and row['audit_date'] != ''):
                        # row['audit_date'] = parse(row['audit_date'],dayfirst=True)
                        row['audit_date'] = parse(row['audit_date'], dayfirst=False)
                    else:
                        # log += printr(f'audit_date is empty/not exist at row at: {n}')
                        skiped_records+=1
                        continue

                    """ Select Outlet Type or Skip  """
                    if(row['outlet_type'] != ''):
                        try:
                            row['outlet_type_id'] = outlet_type_list[str(row['outlet_type']).lower()]
                        except KeyError:
                            # log += printr(f'outlet_type not exist at: {n}')
                            skiped_records+=1
                            continue
                    else:
                        # log += printr(f'outlet_type is empty at row at: {n}')
                        skiped_records+=1
                        continue
                    del row['outlet_type']


                    """ Select Outlet Status or Skip  """
                    outlet_status_qs = None
                    if(row['outlet_status'] != ''):
                        try:
                            row['outlet_status_id'] = outlet_status_list[str(row['outlet_status']).lower()]
                        except KeyError:
                            # log += printr(f'outlet_status not exist at: {n}')
                            skiped_records+=1
                            continue
                    else:
                        # log += printr(f'outlet_status is empty at row at: {n}')
                        skiped_records+=1
                        continue
                    del row['outlet_status']

                    """ Select CityVillage or Skip  """
                    city_village_qs = None
                    if(row['city_village'] != ''):
                        try:
                            row['city_village_id'] = city_village_list[str(row['city_village']).lower()]
                        except KeyError:
                            # log += printr(f'city_village not exist at: {n}')
                            skiped_records+=1
                            continue
                    else:
                        # log += printr(f'outlet status is empty at row at: {n}')
                        skiped_records+=1
                        continue
                    del row['city_village']


                    # cdebug(row)
                    """Get or Create Outlet Object"""
                    if('outlet' in row and row['outlet'] != ''):
                        try:
                            outlet_obj = Outlet.objects.get(
                                    country_id=upload.country_id, code=str(row['outlet'])
                            )
                        except Outlet.DoesNotExist:
                            outlet_obj = Outlet.objects.create(
                                country_id=upload.country_id,code=row['outlet']
                            )
                        del(row['outlet'])
                        row['outlet_id'] = outlet_obj.id
                    else:
                        # log += printr(f'outlet is empty at row at: {n}')
                        skiped_records+=1
                        continue

                    # if('outlet' in row and row['outlet'] != ''):
                    #     outlet_obj, created = Outlet.objects.get_or_create(
                    #         country=upload.country, code__iexact=str(row['outlet']),
                    #         defaults={'code':row['outlet'],}
                    #     )
                    #     row['outlet'] = outlet_obj
                    # else:
                    #     log += printr(f'outlet is empty at row at: {n}')
                    #     skiped_records+=1
                    #     continue


                    try:
                        if row['cell_description'] != '' and len(row['cell_description'])>1:

                            cell_name = row['cell_description'].split("@")
                            cell_name = get_max_str(cell_name)
                            cell_name = cell_name.upper()
                            serialize_str = (f"field_group[group][0][row][0][cols]=cell_description&field_group[group][0][row][0][operator]=icontains&field_group[group][0][row][0][value]={cell_name}")
                            try:
                                cell_obj = Cell.objects.get(
                                    country_id=upload.country_id, index_id=upload.index_id, name=cell_name,
                                )
                            except Cell.DoesNotExist:
                                cell_obj = Cell.objects.create(
                                    country_id=upload.country_id, index_id=upload.index_id, name=cell_name,
                                    ipp=True,serialize_str=serialize_str
                                )

                            # cell_obj, cell_created = Cell.objects.update_or_create(
                            #     country=upload.country, index_id=upload.index_id, name=cell_name,
                            #     defaults = {'ipp':True,'serialize_str':serialize_str}
                            # )

                            # TODO: Comment out temporarly
                            # obj, created = UsableOutlet.objects.update_or_create(
                            #     country=upload.country,
                            #     cell_id=cell_obj.id,
                            #     outlet_id=outlet_obj.id,
                            #     month_id=row['month_id'],
                            #     index_id=upload.index_id,
                            #     defaults={'status':UsableOutlet.NOTUSABLE}
                            # )

                    except KeyError:
                        pass


                    new_row = { key:value for (key,value) in row.items() if key in valid_fields_all}
                    new_row['country_id'] = upload.country_id
                    new_row['index_id'] = upload.index_id

                    if(upload.import_mode == Upload.APPEND or upload.import_mode == Upload.REFRESH ):
                        batch_data_list.append(PanelProfile(**new_row)) #For bulk entry

                        if len(batch_data_list) > 5000:
                            print('Batch took:',convertSecond2Min(time.time() - batch_start_time))
                            PanelProfile.objects.bulk_create(
                                    batch_data_list,
                                    ignore_conflicts=True
                            )
                            PanelProfileChild.objects.bulk_create(
                                    batch_data_list,
                                    ignore_conflicts=True
                            )
                            batch_data_list = []
                            batch_start_time = time.time()

                    update_col = list()
                    if(upload.import_mode == Upload.APPENDUPDATE or upload.import_mode == Upload.UPDATE ):

                        try:
                            obj = PanelProfile.objects.get(
                                country_id=upload.country_id,
                                outlet_id=outlet_obj.id,
                                month_id=row['month_id'],
                                index_id=upload.index_id,
                            )

                            for k,v in new_row.items():
                                setattr(obj,k,v)
                                update_col.append(k)

                            batch_data_list.append(obj)
                        except PanelProfile.DoesNotExist:
                            pass

                        if len(batch_data_list) > 5000:
                            print('Batch took:',convertSecond2Min(time.time() - batch_start_time))
                            PanelProfile.objects.bulk_update(batch_data_list,update_col,batch_size=5000)
                            PanelProfileChild.objects.bulk_update(batch_data_list,update_col,batch_size=5000)

                            batch_data_list = []
                            batch_start_time = time.time()

                            # for person in p:
                            #     obj = People.objects.get(email=person['email'])
                            #     obj.birthday = person['birthday']
                            #     objs.append(obj)
                            # People.objects.bulk_update(objs, ['birthday'], batch_size=1000)

                if batch_data_list :
                    if(upload.import_mode == Upload.APPEND or upload.import_mode == Upload.REFRESH ):
                        PanelProfile.objects.bulk_create(batch_data_list,ignore_conflicts=True)
                        PanelProfileChild.objects.bulk_create(batch_data_list,ignore_conflicts=True)


                    if(upload.import_mode == Upload.APPENDUPDATE or upload.import_mode == Upload.UPDATE ):
                        PanelProfile.objects.bulk_update(batch_data_list,update_col,batch_size=5000)
                        PanelProfileChild.objects.bulk_update(batch_data_list,update_col,batch_size=5000)

                    # cdebug(new_row)
                    # # if(upload.import_mode == Upload.APPEND or upload.import_mode == Upload.REFRESH ):

                    # try:
                    #     panelprofile_obj = PanelProfile.objects.get(
                    #         country_id=upload.country_id, outlet_id=outlet_obj.id, month_id=row['month_id'],index_id=upload.index_id
                    #     )
                    # except PanelProfile.DoesNotExist:
                    #     panelprofile_obj = PanelProfile.objects.create(
                    #         country_id=upload.country_id, outlet_id=outlet_obj.id, month_id=row['month_id'],index_id=upload.index_id
                    #     )

                        # panelprofilechild_obj = PanelProfileChild.objects.get(
                        #     country_id=upload.country_id, outlet=outlet_obj, month_id=row['month_id'],index_id=upload.index_id,
                        # )
                        # obj, created = PanelProfile.objects.get_or_create(
                        #     country=upload.country, outlet=outlet_obj, month_id=row['month_id'],index_id=upload.index_id,
                        #     defaults=new_row
                        # )
                        # obj, created = PanelProfileChild.objects.get_or_create(
                        #     country=upload.country, outlet=outlet_obj, month_id=row['month_id'],index_id=upload.index_id,
                        #     defaults=new_row
                        # )
                        # if(created): created_records+=1


                    # if(upload.import_mode == Upload.APPENDUPDATE or upload.import_mode == Upload.UPDATE ):

                    #     batch_data_list.append(PanelProfile(**new_row)) #For bulk entry

                    #     if len(batch_data_list) > 5000:
                    #         created = PanelProfile.objects.bulk_create(
                    #                 batch_data_list,
                    #                 ignore_conflicts=True
                    #         )
                    #         batch_data_list = []


                        # obj, created = PanelProfile.objects.update_or_create(
                        #     country=upload.country,
                        #     outlet=outlet_obj,
                        #     month_id=row['month_id'],
                        #     index_id=upload.index_id,
                        #     defaults=new_row
                        # )
                        # obj, created = PanelProfileChild.objects.update_or_create(
                        #     country=upload.country,
                        #     outlet=outlet_obj,
                        #     month_id=row['month_id'],
                        #     index_id=upload.index_id,
                        #     defaults=new_row
                        # )
                        # if(created): created_records+=1
                        # else: updated_records+=1

                    # upload.skiped_records = skiped_records
                    # upload.created_records = created_records
                    # upload.updated_records = updated_records
                    # upload.save()


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
            # cdebug(row,'Exception at Row')
            log += 'CSV file processing failed. Error Msg:'+ str(e)
            upload.is_processing = Upload.ERROR
            upload.process_message = "CSV file processing failed. Error Msg:"+str(e)
            upload.log  = log
            upload.save()

