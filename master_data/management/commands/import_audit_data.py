from unicodedata import category
from core.common_libs_views import *
from master_data.models import *
from master_setups.models import *


# Sales = Last month stock + current month purchase - current month stock => for 2 month sales
# sales = total_purchase => if first month

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

        index_category = IndexCategory.objects.filter(country_id = upload.country_id, index_id = upload.index_id)
        index_category = index_category[0].get_index_category_ids()

        log = ""

        if(upload.import_mode == Upload.REFRESH):
            AuditData.objects.filter(country_id=upload.country_id, category__id__in =  index_category).delete()
            AuditDataChild.objects.filter(country_id=upload.country_id, category__id__in =  index_category).delete()

        # Get Valid Model Fields
        valid_fields = modelValidFields("AuditData")
        foreign_fields = modelForeignFields("AuditData")
        valid_fields_all = valid_fields + foreign_fields

        for ff in foreign_fields:
                valid_fields_all.append(f"{ff}_id")

        category_list = getCode2AnyModelFieldList(upload.country.id,'Category','id')
        outlet_list = getCode2AnyModelFieldList(upload.country.id,'Outlet','id')
        product_list = getCode2AnyModelFieldList(upload.country.id,'Product','id')
        month_list = getCode2AnyModelFieldList(upload.country.id,'Month','id')

        month_islocked_list = getCode2AnyModelFieldList(upload.country.id,'Month','is_locked')
        product_weight_list = getCode2AnyModelFieldList(upload.country.id,'Product','weight')
        # print(valid_fields_all)
        # exit()
        try:
            with open(MEDIA_ROOT+'/'+str(upload.file), 'r',encoding='utf-8-sig') as read_obj:
                csv_reader = DictReader(read_obj)
                log += printr(".....CSV Read Successfully.....")
                n=0
                log += printr("csv.DictReader took %s seconds" % (time.time() - start_time))
                csv_indx = 0
                for row in csv_reader:
                    # loop_start_time = time.time()
                    n+=1
                    if n%500==0:
                        print(n,end=' ',flush=True)
                    csv_indx += 1
                    row = {replaceIndex(k): v.strip() for (k, v) in row.items()}

                    # Conver Foreign fields into row
                    for ff in foreign_fields:
                        if f"{ff}_code" in row:
                            row[f"{ff}"] = row.pop(f"{ff}_code", None)

                    product_code = row['product']

                    row['purchase_1'] = int(row['purchase_1']) if row['purchase_1']!='' else 0
                    row['purchase_2'] = int(row['purchase_2']) if row['purchase_2']!='' else 0
                    row['purchase_3'] = int(row['purchase_3']) if row['purchase_3']!='' else 0
                    row['purchase_4'] = int(row['purchase_4']) if row['purchase_4']!='' else 0
                    row['purchase_5'] = int(row['purchase_5']) if row['purchase_5']!='' else 0


                    row['opening_stock'] = int(row['opening_stock']) if row['opening_stock']!='' else 0
                    row['stock_1'] = int(row['stock_1']) if row['stock_1']!='' else 0
                    row['stock_2'] = int(row['stock_2']) if row['stock_2']!='' else 0
                    row['stock_3'] = int(row['stock_3']) if row['stock_3']!='' else 0
                    row['total_stock'] = int(row['total_stock']) if row['total_stock']!='' else 0
                    row['price'] = float(row['price']) if row['price']!='' else 0


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
                    del row['audit_date']
                    # if('audit_date' in row and row['audit_date'] != ''):
                    #     row['audit_date'] = parser.parse(row['audit_date'],dayfirst=True)
                    # else:
                    #     log += printr(f'audit_date is empty/not exist at row at: {n}')
                    #     skiped_records+=1
                    #     continue


                    """ Select Outlet Code """
                    if(row['outlet'] != ''):
                        try:
                            row['outlet_id'] = outlet_list[str(row['outlet']).lower()]
                        except KeyError:
                            log += printr(f'outlet not exist at: {n}')
                            skiped_records+=1
                            continue
                    else:
                        log += printr(f'outlet is empty at row at: {n}')
                        skiped_records+=1
                        continue

                    del row['outlet']


                    """ Select Product Code """
                    if(row['product'] != ''):
                        try:
                            row['product_id'] = product_list[str(row['product']).lower()]
                        except KeyError:
                            log += printr(f'product not exist at: {n}')
                            skiped_records+=1
                            continue
                    else:
                        log += printr(f'product is empty at row at: {n}')
                        skiped_records+=1
                        continue
                    del row['product']

                    """ Select Category Code """
                    if(row['category'] != ''):
                        try:
                            row['category_id'] = category_list[str(row['category']).lower()]
                        except KeyError:
                            log += printr(f'category not exist at: {n}')
                            skiped_records+=1
                            continue
                    else:
                        log += printr(f'category is empty at row at: {n}')
                        skiped_records+=1
                        continue
                    del row['category']

                    """--------------- Calculate Total Purchase ---------------"""

                    purchase_1 = row['purchase_1']
                    purchase_2 = row['purchase_2']
                    purchase_3 = row['purchase_3']
                    purchase_4 = row['purchase_4']
                    purchase_5 = row['purchase_5']



                    total_purchase = purchase_1 + purchase_2 + purchase_3 + purchase_4 + purchase_5


                    """--------------- Calculate Total Stock ---------------"""
                    opening_stock = row['opening_stock']
                    stock1 = row['stock_1']
                    stock2 = row['stock_2']
                    stock3 = row['stock_3']

                    total_stock = stock1 + stock2 + stock3

                    price = row['price']

                    # =IF((T6+AN6-U6-V6)>0, AN6, -1*(T6+AN6-U6-V6)+AN6)

                    try:
                        panel_profile_qs = PanelProfile.objects.get(
                            country=upload.country,outlet_id=row['outlet_id'] ,month_id=row['month_id']
                        )
                    except PanelProfile.DoesNotExist:
                        panel_profile_qs = None
                        log += printr(f"Panel Profile for month {row['month_id']} not exist: {n}")
                        skiped_records+=1
                        continue

                    current_month_audit_date = panel_profile_qs.audit_date

                    current_month = current_month_audit_date.replace(day=1)
                    previous_month = current_month + relativedelta(months=-1)

                    try:
                        previous_month_qs = Month.objects.get(country=upload.country, date=previous_month)
                    except Month.DoesNotExist:
                        previous_month_qs = None


                    if previous_month_qs is not None:
                        try:
                            panel_profile_qs = PanelProfile.objects.get(
                                country=upload.country,outlet_id=row['outlet_id'] ,month_id=previous_month_qs.id
                            )
                            previous_month_audit_date = panel_profile_qs.audit_date

                            delta = current_month_audit_date - previous_month_audit_date
                            vd_factor= delta.days/30.5

                        except PanelProfile.DoesNotExist:
                            vd_factor = 1
                    else:
                        vd_factor = 1




                    purchase,rev_purchase,sales = calculateSales(total_purchase,opening_stock,total_stock,vd_factor)

                    product_weight = product_weight_list[str(product_code).lower()]
                    product_weight = 0 if product_weight == None or product_weight < 0 else float(product_weight)




                    # multiply sales with weight(from Product table) * Q6
                    sales_vol = sales * float(product_weight)
                    # Multiply Sales Vol with price (column P) *Q6
                    sales_val = sales * price

                    row['vd_factor'] = vd_factor
                    row['total_stock'] = total_stock
                    row['total_purchase'] = total_purchase
                    row['purchase'] = purchase
                    row['rev_purchase'] = rev_purchase

                    row['sales'] = sales
                    row['sales_vol'] = sales_vol
                    row['sales_val'] = sales_val

                    new_row = { key:value for (key,value) in row.items() if key in valid_fields_all}

                    # if sales<0:
                    #     cdebug(new_row)
                    #     exit()

                    if(upload.import_mode == Upload.APPEND or upload.import_mode == Upload.REFRESH ):
                        # print(csv_indx,outlet_code)
                        # In this case, if the Person already exists, its existing name is preserved
                        obj, created = AuditData.objects.get_or_create(
                            country=upload.country, product_id=row['product_id'],outlet_id=row['outlet_id'] ,month_id=row['month_id'],
                            defaults=new_row
                        )
                        obj, created = AuditDataChild.objects.get_or_create(
                            country=upload.country, product_id=row['product_id'],outlet_id=row['outlet_id'] ,month_id=row['month_id'],
                            defaults=new_row
                        )

                        if(created): created_records+=1


                    if(upload.import_mode == Upload.APPENDUPDATE ):
                        # In this case, if the Person already exists, its name is updated
                        obj, created = AuditData.objects.update_or_create(
                            country=upload.country, product_id=row['product_id'],outlet_id=row['outlet_id'],month_id=row['month_id'],
                            defaults=new_row
                        )

                        obj, created = AuditDataChild.objects.update_or_create(
                            country=upload.country, product_id=row['product_id'],outlet_id=row['outlet_id'],month_id=row['month_id'],
                            defaults=new_row
                        )

                        if(created): created_records+=1
                        else: updated_records+=1
                    # print("Loop  took %s seconds" % (time.time() - loop_start_time))

                    upload.skiped_records = skiped_records
                    upload.created_records = created_records
                    upload.updated_records = updated_records
                    upload.save()
                    print('|',end=' ',flush=True)


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