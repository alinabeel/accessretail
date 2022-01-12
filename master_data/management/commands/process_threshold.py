from logging import error

from django.db.models.expressions import Value
from core.common_libs import *
from master_data.models import *
from master_setups.models import *
import psycopg2

class Command(BaseCommand):

    # def add_arguments(self, parser):
    #     parser.add_argument('upload_id', type=int)

    def handle(self, *args, **options):
        start_time = time.time()
        last_time = timeSpent(start_time)

        # upload_id = options['upload_id']
        # upload = Upload.objects.get(pk=upload_id)
        country = Country.objects.get(pk=1)
        country_id = country.id
        month_date =  datetime.datetime(2021, 8, 1)
        index_id = 3
        log = ""

        #Get Threasholds
        #  audit_date_qs = AuditData.objects.all() \

        #Calculate Previous Month, Next Month
        audit_date_qs = AuditData.objects.all() \
            .filter(Q(country_id = country_id) & Q(month__date__lte = month_date) ) \
            .values('month__date','month__code') \
            .annotate(current_month=Max("month__date")) \
            .order_by('-month__date')[0:2]

        # audit_date_qs = PanelProfile.objects.all().filter(country_id = country_id).values('month__date').annotate(current_month=Max('audit_date')).order_by('month__date')[0:3]


        date_arr = []
        date_arr_obj = []
        for instance in audit_date_qs:
            date_arr.append(instance['month__date'])

        if(len(date_arr)==3):
            month_1 , month_2, month_3 = date_arr
            current_month = month_1_qs = Month.objects.get(date=month_1)
            previous_month = month_2_qs = Month.objects.get(date=month_2)
            previous_previous_month = month_3_qs = Month.objects.get(date=month_3)

            date_arr_obj.append(month_1_qs)
            date_arr_obj.append(month_2_qs)
            date_arr_obj.append(month_3_qs)

            cdebug('3-Month data')

        elif(len(date_arr)==2):
            month_1 , month_2 = date_arr
            # current_month , previous_month = date_arr
            current_month = month_1_qs = Month.objects.get(date=month_1)
            previous_month  = month_2_qs = Month.objects.get(date=month_2)
            date_arr_obj.append(month_1_qs)
            date_arr_obj.append(month_2_qs)
            cdebug('2-Month data')
        else:
            cdebug('1-Month data')


        #Get Inde   x categorries
        index_category = IndexCategory.objects.filter(country__id = country_id, index__id = index_id)
        index_category = index_category[0].get_index_category_ids()

        #Get current month  audit data with category
        curr_month_audit_data = AuditData.objects.filter(country_id = country_id,
                                                        category__id__in = index_category,
                                                        month_id = current_month.id)

        avg_sd_sales2 = AuditData.objects.all().filter(country_id = country_id,
                                                       category__id__in = index_category,
                                                month_id = current_month.id) \
                                                .values('month_id','product_id') \
                                                .annotate(avg_sales=Avg('sales'),sd_sales=StdDev('sales',True))
        avg_sd_sales_dict = dict()
        for obj in avg_sd_sales2:
            avg_sd_sales_dict[obj['product_id']] = obj['avg_sales'], obj['sd_sales']

        # prettyprint_queryset(avg_sd_sales2)
        # printr(index_category)
        # exit()
        # cell_list = dict()
        # exit()
        # model_a = curr_month_audit_data
        skip_cols = ['id','pk','created','updated',]

        audit_data_list = []
        test = []
        for cmad in curr_month_audit_data:
            # model_b = AuditDataChild()
            prev_month_audit_data = AuditData.objects.get(country_id = country_id,
                                                        product_id= cmad.product_id,
                                                        month_id = previous_month.id,
                                                        outlet_id=cmad.outlet_id).first()
            if(prev_month_audit_data):
                prev_month_price = prev_month_audit_data.price
            else:
                prev_month_price = 0

            # prettyprint_queryset(prev_month_audit_data)

            # avg_sd_sales = AuditData.objects.all().filter(country_id = country_id,
            #                             product_id = cmad.product_id,
            #                             month_id = cmad.month_id) \
            #                             .aggregate(avg_sales=Avg('sales'),sd_sales=StdDev('sales',True))

            # avg_sales = avg_sd_sales['avg_sales']
            # sd_sales = avg_sd_sales['sd_sales'] if avg_sd_sales['sd_sales'] is not None else 0

            avg_sales = avg_sd_sales_dict[cmad.product_id][0]
            sd_sales = avg_sd_sales_dict[cmad.product_id][1]


            avg_sales = avg_sales if avg_sales is not None else 0
            sd_sales = sd_sales if sd_sales is not None else 0

            # print(f"{type(avg_sales)}, {type(sd_sales)}")
            # print(f"{avg_sales}, {sd_sales}")

            sd_range_min = (float(avg_sales)-float(3)*float(sd_sales))
            sd_range_max = (float(avg_sales)+float(3)*float(sd_sales))
            # print(f"{avg_sales}, {sd_sales}, {sd_range_min}, {sd_range_max}")
            # # print((cmad.__dict__))

            new_dict = dict()

            for field in cmad._meta.get_fields():
                if(field.name in skip_cols): continue
                # if isinstance(field, models.ForeignKey): continue
                if isinstance(field, models.ManyToManyRel): continue
                if isinstance(field, models.ManyToOneRel): continue
                new_dict[field.name] = getattr(cmad, field.name)

                # print(field.name)
                # cdebug(getattr(cmad, field.name))
            #     # setattr(model_b, field.name, getattr(cmad, field.name))
            # model_b.pk = new_dict
            # model_b.save()
            # cdebug(new_dict)
            # new_dict["pk"] = None
            curr_sales = cmad.sales
            if curr_sales>sd_range_min or curr_sales<sd_range_max :
                new_dict["flag_outlier"] = True

            new_dict["price_variation"] = percentChange(cmad.price,prev_month_price)
            new_dict["avg_sales"] = avg_sales
            new_dict["sd_sales"] = sd_sales
            new_dict["sd_range_min"] = sd_range_min
            new_dict["sd_range_max"] = sd_range_max
            # print(new_dict)
            # print(new_dict["sd_range_min"])
            audit_data_list.append(AuditDataChild(**new_dict))
            # print(',',end=' ',flush=True)
            obj, created = AuditDataChild.objects.update_or_create(
                country_id=cmad.country_id,outlet_id=cmad.outlet_id,product_id=cmad.product_id,month_id=cmad.month_id,
                defaults = new_dict
            )
            # print(f"{obj.id},")
            # break
        last_time = timeSpent(last_time)
        # created = AuditDataChild.objects.bulk_create(
        #     audit_data_list,
        #     ignore_conflicts=True
        # )
        print(created)
        timeSpent(start_time)
        exit()

        # print(date_arr)
        # exit()
        # if(len(date_arr)==2):
        #     current_month , previous_month = date_arr
        # else:
        #     print('Please load minimum 2 month data.')
        #     exit()
        #     # return HttpResponse(json.dumps({'msg',''},cls=DjangoJSONEncoder),content_type="application/json")

        current_month_qs = Month.objects.get(date=current_month)
        previous_month_qs = Month.objects.get(date=previous_month)


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
            n=0
            skiped_records = 0
            updated_records = 0
            created_records = 0

            month_qs = Month.objects.filter(country = upload.country,is_locked=False).order_by('date')
            print(month_qs)
            for month in month_qs:
                total_month = len(month_qs)
                pp_qs = PanelProfile.objects.filter(country = upload.country,month_id = month.id ) \
                    .values_list('outlet__id', flat=True).distinct()
                total_outlet = len(pp_qs)
                total_cell = len(cell_list)
                total_rec = total_month*total_outlet*total_cell
                for cell in cell_list:
                    for outlet_id in pp_qs:
                        # print(month.id,cell_list[cell],outlet_id)
                        if n%1000==0:
                            print(n,end=' ',flush=True)
                            updateUploadStatus(
                                id=upload_id,
                                msg=f'Processing {n} of {total_rec}',
                                is_processing = Upload.PROCESSING )

                        obj, created = UsableOutlet.objects.update_or_create(
                            country=upload.country,
                            cell_id=cell_list[cell],
                            outlet_id=outlet_id,
                            month_id=month.id,
                            index=upload.index,
                        )

                        n+=1



        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'Sync failed. Error Msg:'+ str(e)+Colors.WHITE )
            log += 'CSV file processing failed. Error Msg:'+ str(e)
            upload.is_processing = Upload.ERROR
            upload.process_message = "Sync failed. Error Msg:"+str(e)
            upload.log  = log
            upload.save()
