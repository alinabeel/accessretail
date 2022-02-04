from unicodedata import category
from core.common_libs import *
from master_data.models import *
from master_setups.models import *
def convertRangeSale(cat_sales):
    cat_sales = cat_sales.split('-')
    if len(cat_sales)==2:
        cat_sales_from = int(cat_sales[0].replace(',',''))
        cat_sales_to = int(cat_sales[1].replace(',',''))
        cat_sales_avg = (cat_sales_from+cat_sales_to)/2
        return cat_sales_from,cat_sales_to,cat_sales_avg
    else:
        return 0,0,0


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('upload_id', type=int)

    def handle(self, *args, **options):

        skiped_records = 0
        updated_records = 0
        created_records = 0
        start_time = time.time()
        timespent = timeSpent(start_time)

        upload_id = options['upload_id']
        upload = Upload.objects.get(pk=upload_id)
        country_id = upload.country_id
        index_id = upload.index_id
        log = ""

        upload.is_processing = Upload.PROCESSING
        upload.process_message = Upload.PROCESSING_MSG
        upload.log  = log
        upload.save()

        if(upload.import_mode == Upload.REFRESH):
            OutletCensus.objects.filter(country=upload.country, index=upload.index).delete()



        # Get Valid Model Fields
        valid_fields = modelValidFields("OutletCensus")
        foreign_fields = modelForeignFields("OutletCensus")
        valid_fields_all = valid_fields + foreign_fields


        for ff in foreign_fields:
            valid_fields_all.append(f"{ff}_id")

        index_category = IndexCategory.objects.filter(country_id = country_id, index_id = index_id)
        index_category = index_category[0].get_index_category_code()
        index_category = [s.lower() for s in index_category]

        # outlet_status_list = IdCodeModel(upload.country.id,'OutletStatus')
        # outlet_type_list = IdCodeModel(upload.country.id,'OutletType')

        try:
            with open(MEDIA_ROOT+'/'+str(upload.file), 'r',encoding='utf-8-sig') as read_obj:
                csv_reader = DictReader(read_obj)
                log += printr(".....CSV Read Successfully.....")
                n=0
                timespent = timeSpent(timespent)
                # log += printr("csv.DictReader took %s seconds" % (time.time() - start_time))

                for row in csv_reader:
                    n+=1
                    if n%500==0:
                        print(n,end=' ',flush=True)

                    row = {replaceIndex(k): v.strip() for (k, v) in row.items()}
                    row["upload"] = upload

                    # Conver Foreign fields into row
                    for ff in foreign_fields:
                        if f"{ff}_code" in row:
                            row[f"{ff}"] = row.pop(f"{ff}_code", None)


                    try:
                        outlet_qs = Outlet.objects.get(
                            country=upload.country, code__iexact=str(row['outlet'])
                        )
                        row['outlet'] = outlet_qs
                    except Outlet.DoesNotExist:
                        outlet_qs = None
                        log += printr(f"Outlet {row['outlet']} not exist: {n}")
                        skiped_records+=1
                        continue



                    for cat in index_category:

                        cat_sales_from,cat_sales_to,cat_sales_avg = 0,0,0
                        over_all_sales_from,over_all_sales_to,over_all_sales_avg = 0,0,0


                        exclude = ['Refused','Do Not Handle']
                        if f"{cat}_sales" in row:
                            if row[f"{cat}_sales"] not in exclude:
                                cat_sales_from,cat_sales_to,cat_sales_avg = convertRangeSale(row[f"{cat}_sales"])
                        if "overall_shop_sales" in row:
                            if row['overall_shop_sales'] not in exclude:
                                over_all_sales_from,over_all_sales_to,over_all_sales_avg = convertRangeSale(row['overall_shop_sales'])

                        category_qs = Category.objects.get(
                            country=upload.country, code__iexact=str(cat)
                        )
                        row['category'] = category_qs

                        row['over_all_sales_from'] = over_all_sales_from
                        row['over_all_sales_to'] = over_all_sales_to
                        row['over_all_sales_avg'] = over_all_sales_avg
                        row['category_sales_from'] = cat_sales_from
                        row['category_sales_to'] = cat_sales_to
                        row['category_sales_avg'] = cat_sales_avg
                        new_row = { key:value for (key,value) in row.items() if key in valid_fields_all}

                        if(upload.import_mode == Upload.APPEND or upload.import_mode == Upload.REFRESH ):

                            obj, created = OutletCensus.objects.get_or_create(
                                country_id=country_id,index_id=index_id, outlet_id=outlet_qs.id, category__code__iexact=cat,
                                defaults=new_row
                            )
                            if(created): created_records+=1

                        if(upload.import_mode == Upload.APPENDUPDATE ):

                            obj, created = OutletCensus.objects.update_or_create(
                                country_id=country_id,index_id=upload.index_id ,outlet_id=outlet_qs.id, category__code__iexact=cat,
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
            cdebug(row,'Exception at row')
            log += 'CSV file processing failed. Error Msg:'+ str(e)
            upload.is_processing = Upload.ERROR
            upload.process_message = "CSV file processing failed. Error Msg:"+str(e)
            upload.log  = log
            upload.save()

