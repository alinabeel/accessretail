from concurrent.futures import process
from logging import error

from django.db.models.expressions import Value
from core.common_libs import *
from master_data.models import *
from master_setups.models import *
import psycopg2

class Command(BaseCommand):

    start_time = time.time()
    last_time = timeSpent(start_time)
    log = ""
    is_first_month = current_month = previous_month = th = None
    avg_sd_sales_dict = dict()
    # def add_arguments(self, parser):
    #     parser.add_argument('upload_id', type=int)
    def getAvgSd(self, country_id, month_id, category_id, TH_SAMPLE):

            avg_sd_sales_purchase = AuditData.objects.all().filter(country_id = country_id,
                                category_id = category_id, month_id = month_id) \
                                .values('month_id','product_id') \
                                .annotate(avg_sales=Avg('sales'),sd_sales=StdDev('sales',TH_SAMPLE),
                                    avg_purchase=Avg('total_purchase'),sd_purchase=StdDev('total_purchase',TH_SAMPLE))

            avg_sd_sales_dict = dict()
            for obj in avg_sd_sales_purchase:
                avg_sd_sales_dict[obj['product_id']] = obj['avg_sales'], obj['sd_sales'],obj['avg_purchase'], obj['sd_purchase']

            return avg_sd_sales_dict

    def priceCleaning(self,panel,country_id,index_id,category_id):
        try:


            #Get current month  audit data with category
            curr_month_audit_data = AuditData.objects.filter(country_id = country_id,
                                                            category_id = category_id,
                                                            month_id = self.current_month.id,
                                                              outlet_id = panel.outlet.id)
            # prettyprint_queryset(curr_month_audit_data)

            cdebug(f"{panel.outlet.code},{country_id},{index_id},{category_id},{self.th},{self.current_month.id}")

            audit_data_list = []
            test = []
            outlet_status = UsableOutlet.QUARANTINE
            for cmad in curr_month_audit_data:
                # model_b = AuditDataChild()
                prev_month_price  = 0
                if(self.is_first_month):
                    pass
                else:
                    try:
                        prev_month_audit_data = AuditData.objects.get(country_id = country_id,
                                                                    product_id = cmad.product_id,
                                                                    month_id = self.previous_month.id,
                                                                    outlet_id = cmad.outlet_id)
                    except AuditData.DoesNotExist:
                        prev_month_audit_data  = None

                    if(prev_month_audit_data):
                        prev_month_price = prev_month_audit_data.price
                    else:
                        prev_month_price = 0



                # (Store + P_code Actual Sales) shall lie in between Avg (P_code Sales) + 3 SD

                avg_sales = self.avg_sd_sales_dict[cmad.product_id][0]
                sd_sales = self.avg_sd_sales_dict[cmad.product_id][1]
                avg_purchase = self.avg_sd_sales_dict[cmad.product_id][2]
                sd_purchase = self.avg_sd_sales_dict[cmad.product_id][3]


                avg_sales = avg_sales if avg_sales is not None else 0
                sd_sales = sd_sales if sd_sales is not None else 0
                avg_purchase = avg_purchase if avg_purchase is not None else 0
                sd_purchase = sd_purchase if sd_purchase is not None else 0

                # print(f"{type(avg_sales)}, {type(sd_sales)}")
                # print(f"{avg_sales}, {sd_sales}")

                valid_sales_min = (float(avg_sales)-float(self.th.audited_data_stddev)*float(sd_sales))
                valid_sales_max = (float(avg_sales)+float(self.th.audited_data_stddev)*float(sd_sales))

                valid_purchase_min = (float(avg_purchase)-float(self.th.audited_data_stddev)*float(sd_purchase))
                valid_purchase_max = (float(avg_purchase)+float(self.th.audited_data_stddev)*float(sd_purchase))


                # print(f"{avg_sales}, {sd_sales}, {sd_range_min}, {sd_range_max}")
                # # print((cmad.__dict__))
                # new_dict = dict()

                # skip_cols = ['id','pk','created','updated',]

                # for field in cmad._meta.get_fields():
                #     if(field.name in skip_cols): continue
                #     # if isinstance(field, models.ForeignKey): continue
                #     if isinstance(field, models.ManyToManyRel): continue
                #     if isinstance(field, models.ManyToOneRel): continue
                #     new_dict[field.name] = getattr(cmad, field.name)

                curr_sales = cmad.sales
                curr_purchase = cmad.total_purchase
                flag_outlier = False
                if curr_sales<valid_sales_min or curr_sales>valid_sales_max :
                    flag_outlier = True

                if curr_purchase<valid_purchase_min or curr_purchase>valid_purchase_max :
                    flag_outlier = True

                outlet_status = UsableOutlet.USABLE if flag_outlier else UsableOutlet.NOTUSABLE

                cmad.flag_outlier = flag_outlier
                cmad.price_variation = percentChange(cmad.price,prev_month_price)
                cmad.avg_sales = avg_sales
                cmad.sd_sales = sd_sales
                cmad.valid_sales_min = valid_sales_min
                cmad.valid_sales_max = valid_sales_max

                cmad.valid_purchase_min = valid_purchase_min
                cmad.valid_purchase_max = valid_purchase_max
                cmad.save()
                # audit_data_list.append(AuditDataChild(**new_dict)) #For bulk entry

                # obj, created = AuditDataChild.objects.update_or_create(
                #     country_id=cmad.country_id,outlet_id=cmad.outlet_id,product_id=cmad.product_id,month_id=cmad.month_id,
                #     defaults = new_dict
                # )

                obj, created = UsableOutlet.objects.update_or_create(
                    country_id=cmad.country_id,outlet_id=cmad.outlet_id,month_id=cmad.month_id,index_id=index_id,
                    defaults = {'status':outlet_status}
                )
                print('>>>')
                print(created)
                print(obj)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'Error Msg:'+ str(e)+Colors.WHITE )

    def commonOutets(panel,country_id,index_id,category_id):
        try:
            pass
            # # ABS (Store Actual Sales /  Store Last Month Sales - 1) <= c

            # prev_sales = AuditData.objects.all().filter(country_id = country_id,
            #                     category_id = category_id, month_id = self.previous_month.id) \
            #                     .values('month_id','product_id') \
            #                     .annotate(avg_sales=Avg('sales'),sd_sales=StdDev('sales',TH_SAMPLE),
            #                         avg_purchase=Avg('total_purchase'),sd_purchase=StdDev('total_purchase',TH_SAMPLE))

            # # common_outlet =




        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'Error Msg:'+ str(e)+Colors.WHITE )

    def processPanelProfile(self,panel,country_id,index_id,category_id):
        try:

            if(self.is_first_month):
                panel.flag_new_outlet = self.is_first_month
                panel.save()
            else:
                panel.flag_new_outlet = self.is_first_month
                panel.save()

            self.priceCleaning(panel,country_id,index_id,category_id)
            # slf.outlierDetection(panel,country_id,index_id,category_id)
            self.commonOutets(panel,country_id,index_id,category_id)

            # self.processAuditData(self,country_id,index_id,category_id)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'Error Msg:'+ str(e)+Colors.WHITE )

    def processThreshold(self, country_id,index_id,month_id):
        try:
            # month_date =  datetime.datetime(2021, 8, 1)

            month_qs = Month.objects.get(id=month_id)
            month_date = month_qs.date

            print(month_date)

            #Calculate Previous Month, Next Month
            self.is_first_month,self.current_month, self.previous_month = getTwoMonthFromDate(country_id,month_date)


            #Get Index categorries
            index_category = IndexCategory.objects.filter(country_id = country_id, index_id = index_id)
            index_category = index_category[0].get_index_category_ids()


            #Calculate category wise
            for category_id in index_category:

                #Get Threasholds
                try:
                    self.th = Threshold.objects.filter(country_id = country_id, index_id=index_id,category_id=category_id).first()
                except Threshold.DoesNotExist:
                    self.th = None
                    cdebug(f"Threshold not defined for category id {category_id}")
                    continue



                self.avg_sd_sales_dict = self.getAvgSd(country_id, month_id, category_id, self.th.stddev_sample)

                cdebug(self.current_month)
                #Get current month  audit data with category
                panel_profile_qs = PanelProfile.objects.filter(country_id = country_id,
                                                                index_id = index_id,
                                                                month_id = self.current_month.id)

                for panel in panel_profile_qs:
                    print(f"Processing Panel outlet code:{panel.outlet.code}")
                    self.processPanelProfile(panel,country_id,index_id,category_id)
                    # sys.exit(0)


                # self.processAuditData(country_id,index_id,category_id,th)





        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'Error Msg:'+ str(e)+Colors.WHITE )

    def handle(self, *args, **options):
        try:

            # upload_id = options['upload_id']
            # upload = Upload.objects.get(pk=upload_id)
            country = Country.objects.get(pk=1)
            country_id = country.id
            month_date =  datetime.datetime(2021, 8, 1)
            index_id = 3

            #Calculate Previous Month, Next Month
            month_qs = AuditData.objects.filter() \
                .filter(Q(country_id = country_id) ) \
                .values('month__id','month__date','month__code') \
                .annotate(current_month=Max("month__date")) \
                .order_by('month__date')

            for month in month_qs:
                self.processThreshold(country_id,index_id,month['month__id'])


        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'Error Msg:'+ str(e)+Colors.WHITE )

    # def processAuditData(self,country_id,index_id,category_id):

    #     try:
    #         # print(th.audited_data_stddev_max)
    #         #
    #         #
    #         # exit()
    #         TH_SAMPLE = th.stddev_sample
    #         TH_STDDEV = th.audited_data_stddev

    #         #Get current month  audit data with category
    #         curr_month_audit_data = AuditData.objects.filter(country_id = country_id,
    #                                                         category_id = category_id,
    #                                                         month_id = current_month.id)

    #         avg_sd_sales_purchase = AuditData.objects.all().filter(country_id = country_id,
    #                             category_id = category_id, month_id = current_month.id) \
    #                             .values('month_id','product_id') \
    #                             .annotate(avg_sales=Avg('sales'),sd_sales=StdDev('sales',TH_SAMPLE),
    #                                 avg_purchase=Avg('total_purchase'),sd_purchase=StdDev('total_purchase',TH_SAMPLE))

    #         avg_sd_sales_dict = dict()
    #         for obj in avg_sd_sales_purchase:
    #             avg_sd_sales_dict[obj['product_id']] = obj['avg_sales'], obj['sd_sales'],obj['avg_purchase'], obj['sd_purchase']

    #         # prettyprint_queryset(avg_sd_sales2)

    #         # cell_list = dict()
    #         # exit()
    #         # model_a = curr_month_audit_data
    #         skip_cols = ['id','pk','created','updated',]

    #         audit_data_list = []
    #         test = []
    #         for cmad in curr_month_audit_data:
    #             # model_b = AuditDataChild()
    #             try:
    #                 prev_month_audit_data = AuditData.objects.get(country_id = country_id,
    #                                                             product_id= cmad.product_id,
    #                                                             month_id = previous_month.id,
    #                                                             outlet_id=cmad.outlet_id)
    #             except AuditData.DoesNotExist:
    #                 prev_month_audit_data  = None

    #             if(prev_month_audit_data):
    #                 prev_month_price = prev_month_audit_data.price
    #             else:
    #                 prev_month_price = 0

    #             # prettyprint_queryset(prev_month_audit_data)

    #             # avg_sd_sales = AuditData.objects.all().filter(country_id = country_id,
    #             #                             product_id = cmad.product_id,
    #             #                             month_id = cmad.month_id) \
    #             #                             .aggregate(avg_sales=Avg('sales'),sd_sales=StdDev('sales',True))

    #             # avg_sales = avg_sd_sales['avg_sales']
    #             # sd_sales = avg_sd_sales['sd_sales'] if avg_sd_sales['sd_sales'] is not None else 0



    #             avg_sales = avg_sd_sales_dict[cmad.product_id][0]
    #             sd_sales = avg_sd_sales_dict[cmad.product_id][1]
    #             avg_purchase = avg_sd_sales_dict[cmad.product_id][2]
    #             sd_purchase = avg_sd_sales_dict[cmad.product_id][3]


    #             avg_sales = avg_sales if avg_sales is not None else 0
    #             sd_sales = sd_sales if sd_sales is not None else 0
    #             avg_purchase = avg_purchase if avg_purchase is not None else 0
    #             sd_purchase = sd_purchase if sd_purchase is not None else 0

    #             # print(f"{type(avg_sales)}, {type(sd_sales)}")
    #             # print(f"{avg_sales}, {sd_sales}")

    #             valid_sales_min = (float(avg_sales)-float(TH_STDDEV)*float(sd_sales))
    #             valid_sales_max = (float(avg_sales)+float(TH_STDDEV)*float(sd_sales))

    #             valid_purchase_min = (float(avg_purchase)-float(TH_STDDEV)*float(sd_purchase))
    #             valid_purchase_max = (float(avg_purchase)+float(TH_STDDEV)*float(sd_purchase))
    #             # print(f"{avg_sales}, {sd_sales}, {sd_range_min}, {sd_range_max}")
    #             # # print((cmad.__dict__))

    #             new_dict = dict()

    #             for field in cmad._meta.get_fields():
    #                 if(field.name in skip_cols): continue
    #                 # if isinstance(field, models.ForeignKey): continue
    #                 if isinstance(field, models.ManyToManyRel): continue
    #                 if isinstance(field, models.ManyToOneRel): continue
    #                 new_dict[field.name] = getattr(cmad, field.name)

    #             curr_sales = cmad.sales
    #             curr_purchase = cmad.total_purchase
    #             flag_outlier = False
    #             if curr_sales<valid_sales_min or curr_sales>valid_sales_max :
    #                 flag_outlier = True

    #             if curr_purchase<valid_purchase_min or curr_purchase>valid_purchase_max :
    #                 flag_outlier = True


    #             new_dict["flag_outlier"] = True
    #             new_dict["price_variation"] = percentChange(cmad.price,prev_month_price)
    #             new_dict["avg_sales"] = avg_sales
    #             new_dict["sd_sales"] = sd_sales
    #             new_dict["valid_sales_min"] = valid_sales_min
    #             new_dict["valid_sales_max"] = valid_sales_max

    #             new_dict["valid_purchase_min"] = valid_purchase_min
    #             new_dict["valid_purchase_max"] = valid_purchase_max

    #             # audit_data_list.append(AuditDataChild(**new_dict)) #For bulk entry

    #             obj, created = AuditDataChild.objects.update_or_create(
    #                 country_id=cmad.country_id,outlet_id=cmad.outlet_id,product_id=cmad.product_id,month_id=cmad.month_id,
    #                 defaults = new_dict
    #             )
    #             # print(f"{obj.id},")
    #             # break
    #         self.last_time = timeSpent(self.last_time)
    #         # created = AuditDataChild.objects.bulk_create(
    #         #     audit_data_list,
    #         #     ignore_conflicts=True
    #         # )
    #     except Exception as e:
    #         exc_type, exc_obj, exc_tb = sys.exc_info()
    #         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #         print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
    #         logger.error(Colors.BOLD_RED+'Error Msg:'+ str(e)+Colors.WHITE )
