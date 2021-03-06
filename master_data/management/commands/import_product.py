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

        index_category = IndexCategory.objects.filter(country = upload.country, index = upload.index)
        index_category = index_category[0].get_index_category_ids()

        log = ""

        if(upload.import_mode == Upload.REFRESH):
            Product.objects.filter(country = upload.country,
                            category__id__in = index_category) \
                            .delete()

        # Get Valid Model Fields
        valid_fields = modelValidFields("Product")
        foreign_fields = modelForeignFields("Product")
        valid_fields_all = valid_fields + foreign_fields

        for ff in foreign_fields:
                valid_fields_all.append(f"{ff}_id")

        category_list = IdCodeModel(upload.country.id,'Category')

        # printr(Colors.BRIGHT_PURPLE,form_obj.file)
        try:
            with open(MEDIA_ROOT+'/'+str(upload.file), 'r',encoding='utf-8-sig') as read_obj:
                csv_reader = DictReader(read_obj)
                log += printr(".....CSV Read Successfully.....")
                n=0
                log += printr("csv.DictReader took %s seconds" % (time.time() - start_time))

                for row in csv_reader:
                    n+=1
                    temp_row = dict()
                    # printr(n,end=' ',flush=True)
                    row = {replaceIndex(k): v.strip() for (k, v) in row.items()}
                    row["upload"] = upload

                    # Conver Foreign fields into row
                    for ff in foreign_fields:
                        if f"{ff}_code" in row:
                            row[f"{ff}"] = row.pop(f"{ff}_code", None)

                    # temp_row = row
                    # product_code	product	pack_type	aggregation_level	category_code	company	brand	family	flavour_type	weight	price_segment	length_range	number_in_pack	price_per_stick
                    # ('pack_type', 'aggregation_level', 'category_code', 'company', 'brand', 'family', 'flavour_type', 'weight', 'price_segment', 'length_range', 'number_in_pack', 'price_per_stick', )
                    # for (k, v) in row.items():
                    #     # k = re.sub('[^A-Za-z0-9]+', '_', k).lower().strip('_')
                    #     v = str(v.strip())
                    #     if(str(v.lower()) in ['-','na','nill','','null','n/a']):
                    #         v = None
                    #     else:
                    #         v = str(v)
                    #     row[k] = v
                    # # cdebug(row,'Line:70')
                    product_code = row['product_code']
                    product_name = row.pop("product_name", "")
                    # category_code = row['category_code']
                    # row['code'] = product_code
                    row['name'] = product_name
                    # row["upload"] = upload

                    # row.pop("product_code", None)
                    # row.pop("category_code", None)
                    # row.pop("category_name", None)

                    # #remove extra fields
                    # for v in product_fields:
                    #     if(v not in row.keys()):
                    #         row.pop(v, None)
                    # cdebug(row,'Line:86')
                    # cdebug(product_fields)

                    """ Select Outlet Type or Skip  """
                    if(row['category'] != ''):
                        try:
                            row['category_id'] = category_list[str(row['category']).lower()]
                        except KeyError:
                            log += printr(f'category not exist at: {n}')
                            skiped_records+=1
                            continue
                    else:
                        log += printr(f'category is empty at row: {n}')
                        skiped_records+=1
                        continue

                    del row['category']

                    if row['category_id'] not in index_category:
                        log += printr(f'category not assigned to index_category: ')
                        skiped_records+=1
                        continue
                    # extra_count = 1
                    # max_extra = 30
                    # for key, val in list(temp_row.items()):
                    #     if('extra' in key and extra_count <= max_extra):
                    #         # print(key,val)
                    #         extra  = key.replace('extra_','')
                    #         extra  = extra.replace('_', ' ')
                    #         extra  = extra.title()

                    #         col_name = 'extra_'+str(extra_count)

                    #         row[col_name] = val
                    #         cdebug(key,'row')
                    #         del row[key]
                    #         if n==1:
                    #             col_label_qs, created = ColLabel.objects.update_or_create(
                    #                 country=upload.country, model_name=ColLabel.Product,col_name=col_name,
                    #                 defaults={'col_label':extra},
                    #             )

                    #         extra_count += 1
                    new_row = { key:value for (key,value) in row.items() if key in valid_fields_all}

                    if(upload.import_mode == Upload.APPEND or upload.import_mode == Upload.REFRESH ):

                        # In this case, if the Person already exists, its existing name is preserved
                        obj, created = Product.objects.get_or_create(
                            country=upload.country, code=product_code,
                            defaults=new_row
                        )
                        if(created): created_records+=1


                    if(upload.import_mode == Upload.APPENDUPDATE ):
                        # In this case, if the Person already exists, its name is updated
                        obj, created = Product.objects.update_or_create(
                            country=upload.country, code=product_code,
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
            cdebug(row,'Exception:')
            log += 'CSV file processing failed. Error Msg:'+ str(e)
            upload.is_processing = Upload.ERROR
            upload.process_message = "CSV file processing failed. Error Msg:"+str(e)
            upload.log  = log
            upload.save()

