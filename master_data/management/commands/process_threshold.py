from concurrent.futures import process
from logging import error
from tkinter.messagebox import NO

from django.db.models.expressions import Value
from core.common_libs_views import *
from master_data.models import *
from master_setups.models import *
import psycopg2

class Command(BaseCommand):

    start_time = time.time()
    last_time = timeSpent(start_time)
    log = ""
    is_first_month = False
    is_second_month = False
    is_morethantwo = False
    total_months = 0
    curr_month = None
    prev_month = None
    third_month = None

    product_weight_list = None
    TH = None
    avg_sd_sales_dict = dict()
    # def add_arguments(self, parser):
    #     parser.add_argument('upload_id', type=int)
    def getAvgSd(self, country_id, month_id, category_id, TH_SAMPLE,audit_data_child=False):


            MODEL = "AuditData" if audit_data_child is False else "AuditDataChild"

            avg_sd_sales_purchase = eval(f"{MODEL}").objects.all().filter(country_id = country_id,
                                category_id = category_id, month_id = month_id) \
                                .values('month_id','product_id') \
                                .annotate(avg_sales=Avg('sales'),sd_sales=StdDev('sales',TH_SAMPLE),
                                    avg_purchase=Avg('total_purchase'),sd_purchase=StdDev('total_purchase',TH_SAMPLE))

            avg_sd_sales_dict = dict()
            for obj in avg_sd_sales_purchase:
                # avg_sd_sales_dict[obj['product_id']] = obj['avg_sales'], obj['sd_sales'],obj['avg_purchase'], obj['sd_purchase']
                avg_sd_sales_dict[obj['product_id']] = obj

            return avg_sd_sales_dict

    def getCellOutletsAvgSales(self,panel,country_id,index_id,category_id,cell_obj, panel_profile_child=False):

            cell_serialize_str = cell_obj.serialize_str
            cell_group_filter_human = ''
            cell_group_filter = ''
            if cell_serialize_str != '':
                cell_params = parse_qs((cell_serialize_str))
                cell_list = getDictArray(cell_params,'field_group[group]')
                cell_dic = getDicGroupList(cell_list)
                cell_group_filter = getGroupFilter(cell_dic)

                # cell_group_filter_human = getGroupFilterHuman(cell_dic)

            # filter_human = "Cell( \n {})".format(cell_group_filter_human)
            MODEL = "PanelProfile" if panel_profile_child is False else "PanelProfileChild"
            queryListPPAllCell = eval(f"{MODEL}").objects.all() \
                            .filter(country_id = country_id,
                                    month_id = self.curr_month.id,
                                    index_id = index_id
                            ) \
                            .filter(cell_group_filter) \
                            .values_list('outlet_id', flat=True)



            curr_audit_data = dict()
            curr_audit_data['sum_sales'] = 0
            curr_audit_data['avg_sales'] = 0

            MODEL = "AuditData" if panel_profile_child is False else "AuditDataChild"
            try:
                curr_audit_data = eval(f"{MODEL}").objects \
                                .filter(country_id = country_id,
                                        category_id = category_id,
                                        month_id = self.curr_month.id,
                                        outlet_id__in = queryListPPAllCell) \
                                .aggregate(sum_sales=Sum('sales'),avg_sales=Avg('sales'))
            except AuditDataChild.DoesNotExist:
                pass


            return curr_audit_data

    def updateCreateUsableOutlet(self,panel,country_id,index_id,cell_id,status):
        try:
            obj, created = UsableOutlet.objects.update_or_create(
                country_id=country_id,
                cell_id=cell_id,
                outlet_id=panel.outlet.id,
                month_id=self.curr_month.id,
                index_id=index_id,
                defaults={'status':status}
            )
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'Error Msg:'+ str(e)+Colors.WHITE )

    def recalculateSales(self,panel,country_id,index_id,category_id):
        try:
            outlet_id = panel.outlet.id
            curr_month_id = self.curr_month.id
            prev_month_id = self.prev_month.id

            curr_audit_data = AuditDataChild.objects.filter(country_id = country_id,
                                                            category_id = category_id,
                                                            month_id = curr_month_id,
                                                            outlet_id = outlet_id)

            prev_audit_data = AuditDataChild.objects.filter(country_id = country_id,
                                                            category_id = category_id,
                                                            month_id = prev_month_id,
                                                            outlet_id = outlet_id)

            for row in curr_audit_data:

                product_id = row.product.id
                product_code = row.product.code

                purchase_1 = row.purchase_1
                purchase_2 = row.purchase_2
                purchase_3 = row.purchase_3
                purchase_4 = row.purchase_4
                purchase_5 = row.purchase_5

                total_purchase = purchase_1 + purchase_2 + purchase_3 + purchase_4 + purchase_5

                """--------------- Calculate Total Stock ---------------"""
                opening_stock = row.opening_stock
                stock1 = row.stock_1
                stock2 = row.stock_2
                stock3 = row.stock_3

                total_stock = stock1 + stock2 + stock3

                price = row.price

                # =IF((T6+AN6-U6-V6)>0, AN6, -1*(T6+AN6-U6-V6)+AN6)

                try:
                    panel_profile_qs = PanelProfileChild.objects.get(
                        country_id=country_id,outlet_id=panel.outlet.id ,month_id=self.curr_month.id
                    )
                    current_month_audit_date = panel_profile_qs.audit_date
                except PanelProfileChild.DoesNotExist:
                    panel_profile_qs = None
                    printr(f"Panel Profile for month {row.month_id} not exist:")
                    continue


                try:
                    panel_profile_qs = PanelProfileChild.objects.get(
                        country=country_id,outlet_id=panel.outlet.id ,month_id=self.prev_month.id
                    )
                    previous_month_audit_date = panel_profile_qs.audit_date

                except PanelProfileChild.DoesNotExist:
                    vd_factor = 1
                    panel_profile_qs = None
                    printr(f"Panel Profile for month {row.month_id} not exist:")
                    continue


                delta = current_month_audit_date - previous_month_audit_date
                vd_factor= delta.days/30.5


                purchase,rev_purchase,sales = calculateSales(total_purchase,opening_stock,total_stock,vd_factor)

                product_weight = self.product_weight_list[str(product_code).lower()]
                product_weight = 0 if product_weight == None or product_weight < 0 else float(product_weight)




                # multiply sales with weight(from Product table) * Q6
                sales_vol = float(sales) * float(product_weight)
                # Multiply Sales Vol with price (column P) *Q6
                sales_val = float(sales) * float(price)


                new_dict = dict()

                new_dict['vd_factor'] = vd_factor
                new_dict['total_stock'] = total_stock
                new_dict['total_purchase'] = total_purchase
                new_dict['purchase'] = purchase
                new_dict['rev_purchase'] = rev_purchase

                new_dict['sales'] = sales
                new_dict['sales_vol'] = sales_vol
                new_dict['sales_val'] = sales_val

                obj, created = AuditDataChild.objects.update_or_create(
                    country_id=country_id, product_id=product_id,outlet_id=outlet_id,month_id=curr_month_id,
                    defaults=new_dict
                )

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'Error Msg:'+ str(e)+Colors.WHITE )

    def updateAuditData(self,cmad):
        try:
            # model_b = AuditDataChild()
            curr_price = cmad.price
            curr_sales = cmad.sales
            curr_purchase = cmad.purchase
            curr_stock = cmad.total_stock

            prev_price  = 0
            prev_sales = 0
            prev_purchase = 0
            prev_stock = 0

            if self.is_first_month:
                prev_price = curr_price
                prev_sales = curr_sales
                prev_purchase = curr_purchase
                prev_stock = curr_stock

            if self.prev_month != None :
                try:
                    prev_audit_data = AuditData.objects.get(country_id = cmad.country_id,
                                                                product_id = cmad.product_id,
                                                                month_id = self.prev_month.id,
                                                                outlet_id = cmad.outlet_id)
                    prev_price = prev_audit_data.price
                    prev_sales = prev_audit_data.sales
                    prev_purchase = prev_audit_data.purchase
                except AuditData.DoesNotExist:
                    prev_audit_data  = None
            else:
                prev_audit_data = None


            price_variation = percentChange(curr_price,prev_price)
            sales_variation = percentChange(curr_sales,prev_sales)
            purchase_variation = percentChange(curr_purchase,prev_purchase)
            stock_variation = percentChange(curr_stock,prev_stock)

            cmad.price_variation = price_variation

            if price_variation < self.TH.audited_data_price_min or \
                price_variation > self.TH.audited_data_price_max:
                cmad.flag_price = True
                cmad.is_valid = False

            if sales_variation < self.TH.audited_data_sales_min or \
                sales_variation > self.TH.audited_data_sales_max:
                cmad.flag_sales = True
                cmad.is_valid = False

            if purchase_variation < self.TH.audited_data_purchase_min or \
                purchase_variation > self.TH.audited_data_purchase_max:
                cmad.flag_purchse = True
                cmad.is_valid = False

            if stock_variation < self.TH.audited_data_stock_min or \
                stock_variation > self.TH.audited_data_stock_max:
                cmad.flag_stock = True
                cmad.is_valid = False

            cmad.save()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'Error Msg:'+ str(e)+Colors.WHITE )

    def updateAuditDataChild(self,cmad):
        try:


            new_dict = dict()
            skip_cols = ['id','pk','created','updated',]

            for field in cmad._meta.get_fields():
                if(field.name in skip_cols): continue
                if isinstance(field, models.ForeignKey): continue
                if isinstance(field, models.ManyToManyRel): continue
                if isinstance(field, models.ManyToOneRel): continue
                new_dict[field.name] = getattr(cmad, field.name)


            # created = AuditDataChild.objects.bulk_update(
            #     audit_data_list,
            #     ignore_conflicts=True
            # )

            obj, created = AuditDataChild.objects.update_or_create(
                country_id=cmad.country_id,
                product_id=cmad.product_id,
                outlet_id=cmad.outlet_id,
                month_id=cmad.month_id,
                category_id=cmad.category_id,
                defaults=new_dict
            )
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'Error Msg:'+ str(e)+Colors.WHITE )

    def outlierDetection(self,cmad):
        try:

            curr_sales = cmad.sales
            curr_purchase = cmad.purchase


            # (Store + P_code Actual Sales) shall lie in between Avg (P_code Sales) + 3 SD

            avg_sales = self.avg_sd_sales_dict[cmad.product_id]['avg_sales']
            sd_sales = self.avg_sd_sales_dict[cmad.product_id]['sd_sales']
            avg_purchase = self.avg_sd_sales_dict[cmad.product_id]['avg_purchase']
            sd_purchase = self.avg_sd_sales_dict[cmad.product_id]['sd_purchase']


            avg_sales = avg_sales if avg_sales is not None else 0
            sd_sales = sd_sales if sd_sales is not None else 0
            avg_purchase = avg_purchase if avg_purchase is not None else 0
            sd_purchase = sd_purchase if sd_purchase is not None else 0

            # print(f"{type(avg_sales)}, {type(sd_sales)}")
            # print(f"{avg_sales}, {sd_sales}")

            valid_sales_min = (float(avg_sales)-float(self.TH.audited_data_stddev)*float(sd_sales))
            valid_sales_max = (float(avg_sales)+float(self.TH.audited_data_stddev)*float(sd_sales))

            valid_purchase_min = (float(avg_purchase)-float(self.TH.audited_data_stddev)*float(sd_purchase))
            valid_purchase_max = (float(avg_purchase)+float(self.TH.audited_data_stddev)*float(sd_purchase))


            if curr_sales<valid_sales_min or curr_sales>valid_sales_max or curr_sales == 0:
                cmad.flag_outlier = True
                cmad.is_valid = False

            if curr_purchase<valid_purchase_min or curr_purchase>valid_purchase_max or curr_purchase == 0:
                cmad.flag_outlier = True
                cmad.is_valid = False

            # outlet_status = UsableOutlet.USABLE if cmad.is_valid else UsableOutlet.NOTUSABLE

            # cmad.price_variation = percentChangeAbs(curr_price,prev_price)
            # cmad.purchase_variation = percentChangeAbs(curr_price,prev_price)
            # cmad.price_variation = percentChangeAbs(curr_price,prev_price)
            cmad.avg_sales = avg_sales
            cmad.sd_sales = sd_sales
            cmad.valid_sales_min = valid_sales_min
            cmad.valid_sales_max = valid_sales_max

            cmad.valid_purchase_min = valid_purchase_min
            cmad.valid_purchase_max = valid_purchase_max
            cmad.save()



        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'Error Msg:'+ str(e)+Colors.WHITE )

    def outlierDetectionDecsion(self,panel,country_id,index_id,category_id):
        try:

            #Apply Last Month Price Cleaning on the Stores + P_Codes
            #Get current month  audit data with category


            curr_audit_data = AuditDataChild.objects.filter(country_id = country_id,
                                                    category_id = category_id,
                                                    month_id = self.curr_month.id,
                                                    outlet_id = panel.outlet.id,
                                                    flag_outlier =  True
                                                    )

            curr_audit_data_has_outlier = curr_audit_data.filter(flag_outlier =  True)



            if len(curr_audit_data_has_outlier) >= 1:
                # Delete al audit data and copy from prevous month
                curr_audit_data.delete()
                # try:

                # cdebug(self.prev_month)
                # sys.exit(0)
                try:
                    prev_audit_data = AuditDataChild.objects.filter(
                                                            country_id = country_id,
                                                            category_id = category_id,
                                                            month_id = self.prev_month.id,
                                                            outlet_id = panel.outlet.id
                                                            )
                except AuditDataChild.DoesNotExist:
                    return

                try:
                    prev_pp_qs = PanelProfileChild.objects.get(
                                                    country_id = country_id,
                                                    index_id = index_id,
                                                    month_id = self.prev_month.id,
                                                    outlet_id = panel.outlet.id
                                                    )
                except PanelProfileChild.DoesNotExist:
                    return

                # cdebug(prev_pp_qs)
                # prettyprint_queryset(prev_pp_qs)
                # exit()
                prev_audit_date = prev_pp_qs.audit_date


                panel.audit_status = PanelProfile.COPIED
                panel.save()
                # obj.pk = None # New Copy
                # # obj.outlet_id  = outlet_to
                # obj.audit_status  = PanelProfile.COPIED
                # obj.audit_date = obj.audit_date+timedelta(days=30)
                # obj.month = date_arr_obj[0]
                # obj.save()


                for obj in prev_audit_data:

                    # obj.pk = None # New Copy
                    # obj.outlet_id  = panel.outlet.id
                    # obj.audit_status  = AuditDataChild.COPIED
                    # obj.audit_date = prev_audit_date+timedelta(days=30.5)
                    # obj.month_id = self.curr_month.id
                    # obj.save()

                    new_dict = dict()
                    skip_cols = ['id','pk','created','updated',]

                    for field in obj._meta.get_fields():
                        if(field.name in skip_cols): continue
                        if isinstance(field, models.ForeignKey): continue
                        if isinstance(field, models.ManyToManyRel): continue
                        if isinstance(field, models.ManyToOneRel): continue
                        new_dict[field.name] = getattr(obj, field.name)


                    new_dict['audit_status'] = AuditData.COPIED
                    new_dict['audit_date'] = prev_audit_date+timedelta(days=30.5)
                    obj, created = AuditDataChild.objects.update_or_create(
                        country_id=obj.country_id,
                        product_id=obj.product_id,
                        outlet_id=obj.outlet_id,
                        month_id=obj.month_id,
                        category_id=obj.category_id,
                        defaults=new_dict
                    )

                    # prev_price = prev_audit_data.price
                    # prev_sales = prev_audit_data.sales
                    # prev_purchase = prev_audit_data.purchase
                # except AuditDataChild.DoesNotExist:
                #     prev_audit_data  = None

            # prettyprint_queryset(curr_audit_data)
            # cdebug(f"{panel.outlet.code},{country_id},{index_id},{category_id},{self.TH},{self.curr_month.id}")

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'Error Msg:'+ str(e)+Colors.WHITE )
            sys.exit(0)


    def priceCleaning(self,panel,country_id,index_id,category_id):
        try:

            #Apply Last Month Price Cleaning on the Stores + P_Codes
            #Get current month  audit data with category
            curr_audit_data = AuditData.objects.filter(country_id = country_id,
                                                            category_id = category_id,
                                                            month_id = self.curr_month.id,
                                                              outlet_id = panel.outlet.id)
            # prettyprint_queryset(curr_audit_data)

            # cdebug(f"{panel.outlet.code},{country_id},{index_id},{category_id},{self.TH},{self.curr_month.id}")

            audit_data_list = []
            test = []
            outlet_status = UsableOutlet.QUARANTINE

            for cmad in curr_audit_data:
                self.updateAuditData(cmad)

                ## STEP: 2 ##
                self.outlierDetection(cmad)

                ## STEP: 3 ##
                self.updateAuditDataChild(cmad)


                # if cmad.product.code == '150' and cmad.outlet.code == '114635':
                #     print(cmad.product.code)
                #     print(cmad.outlet.code)
                #     sys.exit(0)
                # else:
                #     continue

                # sys.exit(0)
                # audit_data_list.append(AuditDataChild(**new_dict)) #For bulk entry

                # obj, created = AuditDataChild.objects.update_or_create(
                #     country_id=cmad.country_id,outlet_id=cmad.outlet_id,product_id=cmad.product_id,month_id=cmad.month_id,
                #     defaults = new_dict
                # )

                # obj, created = UsableOutlet.objects.update_or_create(
                #     country_id=cmad.country_id,
                #     outlet_id=cmad.outlet_id,
                #     month_id=cmad.month_id,
                #     index_id=index_id,
                #     defaults = {'status':outlet_status}
                # )


        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'Error Msg:'+ str(e)+Colors.WHITE )



    def commonOutlets(self,panel,country_id,index_id,category_id,cell_obj):
        # cdebug(self)
        try:

            # Accept the store if	ABS (Store Actual Sales /  Store Last Month Sales - 1) <= c
            # "it is  after correction of data,
            # c = criteria
            # c is sales in percentage and is by category
            # a = criteria
            # a is acceptance of store based on category/index"

            flag_common_outlet = False
            is_valid = False
            outlet_id = panel.outlet.id
            curr_month_id = self.curr_month.id
            prev_month_id = self.prev_month.id

            try:
                curr_audit_data = AuditDataChild.objects \
                                .filter(country_id = country_id,
                                        category_id = category_id,
                                        month_id = curr_month_id,
                                        outlet_id = outlet_id) \
                                .aggregate(sum_sales=Sum('sales'))
            except AuditDataChild.DoesNotExist:
                curr_audit_data = None


            try:
                prev_audit_data = AuditDataChild.objects \
                                .filter(country_id = country_id,
                                        category_id = category_id,
                                        month_id = prev_month_id,
                                        outlet_id = outlet_id) \
                                .aggregate(sum_sales=Sum('sales'))
            except AuditDataChild.DoesNotExist:
                prev_audit_data = None


            if curr_audit_data['sum_sales'] is not None and prev_audit_data['sum_sales'] is not None:

                curr_sales = curr_audit_data['sum_sales']
                prev_sales = prev_audit_data['sum_sales']

                prev_sales = 1 if prev_sales==0 else prev_sales

                printr(f"c , p = {curr_sales},{prev_sales}")
                cp_formula = abs((float(curr_sales) / float(prev_sales) -1)*100 )
                if cp_formula <= self.TH.common_outlet_accept:
                    flag_common_outlet = True
                    is_valid = True
                    self.updateCreateUsableOutlet(panel,country_id,index_id,cell_obj.id,UsableOutlet.USABLE)

            panel.is_valid = is_valid
            panel.flag_common_outlet = flag_common_outlet
            panel.save()




            # audit_data_list = []
            # test = []
            # outlet_status = UsableOutlet.QUARANTINE

            # for cmad in curr_audit_data:
            #     self.updateAuditData(cmad)


        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'Error Msg:'+ str(e)+Colors.WHITE )
            exit()

    def processPanelProfile(self,panel,country_id,index_id,category_id):
        try:

            if(self.is_first_month):
                panel.flag_new_outlet = True
                panel.save()
            else:
                panel.flag_new_outlet = False
                panel.save()
            ## STEP: 1 ##
            self.priceCleaning(panel,country_id,index_id,category_id)

            # self.processAuditData(self,country_id,index_id,category_id)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'Error Msg:'+ str(e)+Colors.WHITE )

    def newOutlets(self,panel,country_id,index_id,category_id,cell_obj):
        try:

            curr_sales = 0
            try:
                curr_audit_data = AuditDataChild.objects \
                                .filter(country_id = country_id,
                                        category_id = category_id,
                                        month_id = self.curr_month.id,
                                        outlet_id = panel.outlet_id) \
                                .aggregate(sum_sales=Sum('sales'),avg_sales=Avg('sales'))
            except AuditDataChild.DoesNotExist:
                curr_audit_data = None


            curr_sales = curr_audit_data['sum_sales']


            try:
                oc_qs = OutletCensus.objects.filter(country_id=country_id,
                                                    index_id=index_id,
                                                    category_id=category_id,
                                                    outlet_id=panel.outlet.id) \
                                            .values('category_sales_avg')

                census_category_sales_avg = oc_qs[0]['category_sales_avg']
            except OutletCensus.DoesNotExist:
                oc_qs = None
                census_category_sales_avg = 0
            except KeyError:
                oc_qs = None
                census_category_sales_avg = 0

            # New Stores
            #     2	Accept the store if	ABS (Store Actual Sales /  Store Census Sales - 1) <= a
            flag_accepted_a = False
            flag_droped_a = False
            flag_accepted_b = False
            flag_droped_b = False

            is_valid = False
            if census_category_sales_avg > 0:
                if abs((float(curr_sales) / float(census_category_sales_avg) -1)*100 ) <= self.TH.new_outlet_accept_a:
                    flag_accepted_a = True
                    is_valid = True
                    self.updateCreateUsableOutlet(panel,country_id,index_id,cell_obj.id,UsableOutlet.USABLE)

            #       Drop the store if	ABS (Store Actual Sales /  Store Census Sales - 1) > a
                if abs((float(curr_sales) / float(census_category_sales_avg) -1)*100 ) > self.TH.new_outlet_drop_a:
                    flag_droped_a = True
                    is_valid = False
                    self.updateCreateUsableOutlet(panel,country_id,index_id,cell_obj.id,UsableOutlet.DROP)


            cell_outlet_avg_sales = self.getCellOutletsAvgSales(panel,country_id,index_id,category_id,cell_obj,True)
            avg_sales = cell_outlet_avg_sales['avg_sales']

            #     3	Accept the store if	ABS (Store Actual Sales /  Avg Cell Sales - 1) <= b
            if avg_sales > 0:
                if abs((float(curr_sales) / float(avg_sales) -1)*100 ) <= self.TH.new_outlet_accept_b:
                    flag_accepted_b = True
                    is_valid = True
                    self.updateCreateUsableOutlet(panel,country_id,index_id,cell_obj.id,UsableOutlet.USABLE)

            #       Drop the store if	ABS (Store Actual Sales /  Avg Cell Sales - 1) > b
                if abs((float(curr_sales) / float(avg_sales) -1)*100 ) > self.TH.new_outlet_drop_b:
                    flag_droped_b = True
                    is_valid = False
                    self.updateCreateUsableOutlet(panel,country_id,index_id,cell_obj.id,UsableOutlet.DROP)


            panel.is_valid = is_valid
            panel.flag_accepted_a = flag_accepted_a
            panel.flag_droped_a = flag_droped_a
            panel.flag_accepted_b = flag_accepted_b
            panel.flag_droped_b = flag_droped_b
            panel.save()

            # ('common_outlet_accept',
            # 'new_outlet_accept_a',
            # 'new_outlet_accept_b',
            # 'drop_outlet_copied',
            # 'drop_outlet_copied_once',
            # 'weighted_store',
            # 'weighted_cell', )


        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'Error Msg:'+ str(e)+Colors.WHITE )

    def dropedOutlets(self,panel,country_id,index_id,category_id,cell_obj):

        try:
            pass

        #     curr_sales = panel.sales

        #     try:
        #         oc_qs = OutletCensus.objects.get(country_id=country_id,
        #                                             index_id=index_id,
        #                                             category_id=category_id,
        #                                             outlet_id=panel.outlet.id) \
        #                                     .values('category_sales_avg')
        #         census_category_sales_avg = oc_qs.category_sales_avg
        #     except OutletCensus.DoesNotExist:
        #         oc_qs = None
        #         census_category_sales_avg = 0

        #     # New Stores
        #     #     2	Accept the store if	ABS (Store Actual Sales /  Store Census Sales - 1) <= a
        #     flag_accepted_a = False
        #     flag_droped_a = False
        #     flag_accepted_b = False
        #     flag_droped_b = False

        #     is_valid = False
        #     if census_category_sales_avg > 0:
        #         if abs((float(curr_sales) / float(census_category_sales_avg) -1)*100 ) <= self.TH.new_outlet_accept_a:
        #             flag_accepted_a = True
        #             is_valid = True
        #             self.updateCreateUsableOutlet(panel,country_id,index_id,cell_obj.id,UsableOutlet.USABLE)

        #     #       Drop the store if	ABS (Store Actual Sales /  Store Census Sales - 1) > a
        #         if abs((float(curr_sales) / float(census_category_sales_avg) -1)*100 ) > self.TH.new_outlet_drop_a:
        #             flag_droped_a = True
        #             is_valid = False
        #             self.updateCreateUsableOutlet(panel,country_id,index_id,cell_obj.id,UsableOutlet.DROP)


        #     cell_outlet_avg_sales = self.getCellOutletsAvgSales(panel,country_id,self.curr_month.id,index_id,cell_obj,True)
        #     avg_sales = cell_outlet_avg_sales['avg_sales']

        #     #     3	Accept the store if	ABS (Store Actual Sales /  Avg Cell Sales - 1) <= b
        #     if avg_sales > 0:
        #         if abs((float(curr_sales) / float(avg_sales) -1)*100 ) <= self.TH.new_outlet_accept_b:
        #             flag_accepted_b = True
        #             is_valid = True
        #             self.updateCreateUsableOutlet(panel,country_id,index_id,cell_obj.id,UsableOutlet.USABLE)

        #     #       Drop the store if	ABS (Store Actual Sales /  Avg Cell Sales - 1) > b
        #         if abs((float(curr_sales) / float(avg_sales) -1)*100 ) > self.TH.new_outlet_drop_b:
        #             flag_droped_b = True
        #             is_valid = False
        #             self.updateCreateUsableOutlet(panel,country_id,index_id,cell_obj.id,UsableOutlet.DROP)


        #     panel.is_valid = is_valid
        #     panel.flag_accepted_a = flag_accepted_a
        #     panel.flag_droped_a = flag_droped_a
        #     panel.flag_accepted_b = flag_accepted_b
        #     panel.flag_droped_b = flag_droped_b
        #     panel.save()



        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'Error Msg:'+ str(e)+Colors.WHITE )


    def processThreshold(self, country_id,index_id,category_id,month_id):
        try:
            # month_date =  datetime(2021, 8, 1)


            month_qs = Month.objects.get(id=month_id)
            self.curr_month = month_qs
            month_date = month_qs.date

            cdebug(f"month: {month_date}")


            audit_date_qs = PanelProfile.objects.all() \
                .filter(country_id = country_id, index_id = index_id) \
                .values('month__code','month__id') \
                .annotate(monts_count=Count('month__date')) \
                .order_by('month__date')

            audit_dates = list(audit_date_qs)

            first_month_id = audit_dates[0]['month__id']
            current_month_id = month_id
            previous_month_id = None



            if first_month_id != current_month_id:
                current_month_index = next((index for (index, d) in enumerate(audit_dates) if d["month__id"] == month_id), None)
                if current_month_index is not None:
                    previous_month_id = audit_dates[current_month_index-1]['month__id']
                    self.prev_month = Month.objects.get(id=previous_month_id)
            #Calculate Previous Month, Next Month
            # self.curr_month, self.prev_month, self.third_month = getThreeMonthFromDate(country_id,month_date)






            #Get Index categorries
            # index_category = IndexCategory.objects.filter(country_id = country_id, index_id = index_id)
            # index_category = index_category[0].get_index_category_ids()


            #Calculate category wise
            # for category_id in index_category:

            #Get Threasholds
            try:
                self.TH = Threshold.objects.filter(country_id = country_id, index_id=index_id,category_id=category_id).first()
            except Threshold.DoesNotExist:
                self.TH = None
                cdebug(f"Threshold not defined for category id {category_id}")
                return



            self.avg_sd_sales_dict = self.getAvgSd(country_id, month_id, category_id, self.TH.stddev_sample)

            # cdebug(self.curr_month)
            #Get current month  audit data with category
            panel_profile_qs = PanelProfileChild.objects.filter(country_id = country_id,
                                                            index_id = index_id,
                                                            month_id = self.curr_month.id
                                                        )


            for panel in panel_profile_qs:
                print(f"Processing Panel outlet id,code:{panel.outlet.id},{panel.outlet.code}")

                self.total_months = getOutletTotalMonthFromDate(country_id, month_date, panel.outlet_id)
                printr(f"total_months: {self.total_months}, curr_month:{self.curr_month}")

                # self.is_first_month = True if self.total_months == 1 else False
                # self.is_second_month = True if self.total_months == 2 else False
                # self.is_morethantwo = True if self.total_months >= 3 else False


                self.is_first_month = True if self.curr_month is not None and self.prev_month is None and self.third_month is None else False
                self.is_second_month = True if self.curr_month is not None and self.prev_month is not None and self.third_month is None else False
                # self.is_morethantwo = True if self.curr_month is not None and self.prev_month is not None and self.third_month is not None else False


                self.processPanelProfile(panel,country_id,index_id,category_id)

                if self.total_months > 1 and self.is_first_month == False:
                    ## STEP: 4 ##
                    self.outlierDetectionDecsion(panel,country_id,index_id,category_id)
                    ## STEP: 5 ##
                    self.recalculateSales(panel,country_id,index_id,category_id)

            #Process on cleaned outlets
            panel_profile_clean_qs = PanelProfileChild.objects.filter(country_id = country_id,
                                                            index_id = index_id,
                                                            month_id = self.curr_month.id,
                                                            is_valid = True
                                                        )



            ## STEP: 6 ##

            for panel in panel_profile_clean_qs:

                try:
                    cell_obj = Cell.objects.filter(
                        country_id=country_id,
                        index_id=index_id,
                        name__iexact=panel.cell_description,
                    ).get()
                    # prettyprint_queryset(cell_obj)
                except Cell.DoesNotExist:
                    cell_obj = None

                if cell_obj is not None and self.total_months > 1:
                    self.commonOutlets(panel,country_id,index_id,category_id,cell_obj)


                #New Store:
                # 1	In 1st month store will be kept in Qurantine,
                if cell_obj is not None and self.is_first_month is True:
                    cdebug(cell_obj.id)
                    self.updateCreateUsableOutlet(panel,country_id,index_id,cell_obj.id,UsableOutlet.QUARANTINE)

                #New Store:
                # 2nd Month Store will appeasr as new store tag
                if self.is_second_month is True:
                    panel.flag_new_outlet = True
                    panel.save()

                # if cell_obj is not None and self.is_second_month is True:
                #     self.updateCreateUsableOutlet(panel,country_id,index_id,cell_obj.id,UsableOutlet.N)

                if cell_obj is not None and self.total_months == 2:
                    self.newOutlets(panel,country_id,index_id,category_id,cell_obj)
                    self.dropedOutlets(panel,country_id,index_id,category_id,cell_obj)

                # sys.exit(0)


            # self.processAuditData(country_id,index_id,category_id,TH)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'Error Msg:'+ str(e)+Colors.WHITE )
    def add_arguments(self, parser):
        parser.add_argument('index_id', type=int)
        parser.add_argument('category_id', type=int)

    def handle(self, *args, **options):
        try:

            # upload_id = options['upload_id']
            # upload = Upload.objects.get(pk=upload_id)
            country = Country.objects.get(pk=1)
            country_id = country.id
            # month_date =  datetime(2021, 8, 1)
            # index_id = 1
            # category_id = 8

            # index_id = 3 #Tobaco
            # category_id = 20  #Cig
            index_id = options['index_id']
            category_id = options['category_id']


            self.product_weight_list = getCode2AnyModelFieldList(country_id,'Product','weight')

            #Calculate Previous Month, Next Month
            month_qs = AuditData.objects.filter() \
                .filter(Q(country_id = country_id) ) \
                .values('month__id','month__date','month__code') \
                .annotate(curr_month=Max("month__date")) \
                .order_by('month__date')
            # prettyprint_queryset(month_qs)
            # exit()
            c = 0
            for month in month_qs:
                # if c==0:
                #     c += 1
                #     continue
                self.processThreshold(country_id,index_id,category_id,month['month__id'])



        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'Error Msg:'+ str(e)+Colors.WHITE )


# FLow
# 	method handle
#       method processThreshold
# 	        method processPanelProfile
# 	            method priceCleaning
# 	                method updateAuditData
#                	method outlierDetection
# 	                method updateAuditDataChild
# 	        method outlierDetectionDecsion
#           method recalculateSales
#           *Process on cleaned outlets*
# 	        method commonOutlets
#           method newOutlets






    # def processAuditData(self,country_id,index_id,category_id):

    #     try:
    #         # print(TH.audited_data_stddev_max)
    #         #
    #         #
    #         # exit()
    #         TH_SAMPLE = TH.stddev_sample
    #         TH_STDDEV = TH.audited_data_stddev

    #         #Get current month  audit data with category
    #         curr_audit_data = AuditData.objects.filter(country_id = country_id,
    #                                                         category_id = category_id,
    #                                                         month_id = curr_month.id)

    #         avg_sd_sales_purchase = AuditData.objects.all().filter(country_id = country_id,
    #                             category_id = category_id, month_id = curr_month.id) \
    #                             .values('month_id','product_id') \
    #                             .annotate(avg_sales=Avg('sales'),sd_sales=StdDev('sales',TH_SAMPLE),
    #                                 avg_purchase=Avg('total_purchase'),sd_purchase=StdDev('total_purchase',TH_SAMPLE))

    #         avg_sd_sales_dict = dict()
    #         for obj in avg_sd_sales_purchase:
    #             avg_sd_sales_dict[obj['product_id']] = obj['avg_sales'], obj['sd_sales'],obj['avg_purchase'], obj['sd_purchase']

    #         # prettyprint_queryset(avg_sd_sales2)

    #         # cell_list = dict()
    #         # exit()
    #         # model_a = curr_audit_data
    #         skip_cols = ['id','pk','created','updated',]

    #         audit_data_list = []
    #         test = []
    #         for cmad in curr_audit_data:
    #             # model_b = AuditDataChild()
    #             try:
    #                 prev_audit_data = AuditData.objects.get(country_id = country_id,
    #                                                             product_id= cmad.product_id,
    #                                                             month_id = prev_month.id,
    #                                                             outlet_id=cmad.outlet_id)
    #             except AuditData.DoesNotExist:
    #                 prev_audit_data  = None

    #             if(prev_audit_data):
    #                 prev_price = prev_audit_data.price
    #             else:
    #                 prev_price = 0

    #             # prettyprint_queryset(prev_audit_data)

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
    #             new_dict["price_variation"] = percentChangeAbs(curr_price,prev_price)
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
