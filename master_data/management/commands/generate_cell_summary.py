from core.common_libs import *
from master_setups.models import *
from master_data.models import *
from reports.models import *

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('rbd_report_id', type=int)

    def handle(self, *args, **options):

        start_time = time.time()


        try:
            return_dic = {}
            response_dict = []
            temp_dic = {}
            month_data = dict()
            log = ""

            rbd_report_id = options['rbd_report_id']
            rbd_report_qs = RBDReport.objects.get(id=rbd_report_id)
            country_id = rbd_report_qs.country.id
            country_code = rbd_report_qs.country.code
            report_type = rbd_report_qs.report_type

            rbd_id = rbd_report_qs.rbd.id
            rbd_name = rbd_report_qs.rbd.name

            cat_id = rbd_report_qs.category.id
            cat_name = rbd_report_qs.category.name

            month_id = rbd_report_qs.month.id
            month_code = rbd_report_qs.month.code

            month_date = rbd_report_qs.month.date
            category = rbd_report_qs.category

            cdebug(rbd_id)
            cdebug(cat_id)
            cdebug(month_id)

            rbd_cells = RBD.objects.only('id').filter(country_id = country_id,pk=rbd_id).values('cell')
            # ,cell__name__iexact='National-Total Urban-Sp-Punjab-Multan-Roa-General-Medical Store-Handler-Ttl'
            # category = Category.objects.get(id=cat_id)

            #Cell Query List
            queryList = Cell.objects.all().filter(country_id = country_id, id__in=rbd_cells).order_by('name')

            #Product Audit Query List
            queryListPA = AuditData.objects.all().filter(country_id = country_id, category=category)
            # prettyprint_queryset(queryListPA)
            # exit()
            super_manufacture = Product.objects.filter(country_id = country_id, category=category).exclude(super_manufacture=None) \
                                .order_by('category').values_list('super_manufacture', flat=True).distinct()

            super_manufacture_products = dict()
            for sm in super_manufacture:
                smp = Product.objects \
                    .filter(country_id = country_id, category=category,super_manufacture__iexact=sm) \
                    .exclude(super_manufacture=None) \
                    .order_by('category').values_list('id', flat=True)
                super_manufacture_products[sm] = smp


            #Calculate Previous Month, Next Month
            audit_date_qs = PanelProfile.objects.all() \
                .filter(Q(country_id = country_id) & Q(month__date__lte = month_date) ) \
                .values('month__date') \
                .annotate(current_month=Max("month__date")) \
                .order_by('month__date')[0:3]

            # audit_date_qs = PanelProfile.objects.all().filter(country_id = country_id).values('month__date').annotate(current_month=Max('audit_date')).order_by('month__date')[0:3]


            date_arr = []
            date_arr_obj = []
            for instance in audit_date_qs:
                date_arr.append(instance['month__date'])

            if(len(date_arr)==3):
                month_1 , month_2, month_3 = date_arr
                month_1_qs = Month.objects.get(date=month_1)
                month_2_qs = Month.objects.get(date=month_2)
                month_3_qs = Month.objects.get(date=month_3)

                date_arr_obj.append(month_1_qs)
                date_arr_obj.append(month_2_qs)
                date_arr_obj.append(month_3_qs)

                cdebug('3-Month data')

            elif(len(date_arr)==2):
                month_1 , month_2 = date_arr
                month_1_qs = Month.objects.get(date=month_1)
                month_2_qs = Month.objects.get(date=month_2)
                date_arr_obj.append(month_1_qs)
                date_arr_obj.append(month_2_qs)
                cdebug('2-Month data')
            else:
                cdebug('1-Month data')
                # return HttpResponse(json.dumps({'msg','Please load minimum 2 month data.'},cls=DjangoJSONEncoder),content_type="application/json")

            # return_dic['previous_month'] = "{}, {}".format(previous_month_qs.name,previous_month_qs.year)
            # return_dic['current_month'] = "{}, {}".format(current_month_qs.name,current_month_qs.year)

            queryListPPAll = PanelProfile.objects.all().filter(country_id = country_id,category__id = cat_id)

            if len(queryListPPAll) == 0 :
                return_dic['count'] = 0
                return_dic['next'] = None
                return_dic['previous'] = None
                return_dic['results'] = []
                # return HttpResponse(json.dumps(return_dic,cls=DjangoJSONEncoder),content_type="application/json")

            return_dic['count'] = len(queryList)
            return_dic['next'] = None
            return_dic['previous'] = None

            # cdebug(len(queryList),'total:')
            # exit()
            # prettyprint_queryset(queryListPPAll)
            for k in range(0,len(queryList)):
                queryListPPCell = queryListPPAll
                cell_serialize_str = queryList[k].serialize_str
                print(Colors.BOLD_YELLOW,'Processing Cell: ', queryList[k].name,Colors.WHITE)

                """ Rbd and Cell Processing from previous saved serialize string """

                field_group = parse_qs((cell_serialize_str))
                new_list = getDictArray(field_group,'field_group[group]')
                new_dic = getDicGroupList(new_list)
                group_filter = getGroupFilter(new_dic)
                group_filter_human = getGroupFilterHuman(new_dic)


                filter_human = ''
                if(group_filter != ''):
                    # filter_human = group_filter_human
                    queryListPPCell = queryListPPCell.filter(group_filter)


                # prettyprint_queryset(queryListPPCell,'queryListPPCell')
                # N_Numeric_Universe = queryList[k].num_universe
                # W_Universe = queryList[k].cell_acv

                """-------------Month 1 Calculatuons-------------"""

                #"""CELL Panel Profile"""
                queryListPPCellMonth_1 = queryListPPCell.filter(month = date_arr_obj[-1]) \
                                            .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                    .filter(country_id = country_id, month = date_arr_obj[-1], status__iexact = UsableOutlet.USABLE))

                if len(queryListPPCellMonth_1) <= 0 :
                    log += f"\n Skip Cell: {queryList[k].name} \n"
                    continue

                # prettyprint_queryset(queryListPPCellMonth_1)
                temp_dic = {
                    'Category' : category.name,
                    'Cell Name' : queryList[k].name,
                    'Area': queryListPPCellMonth_1[0].city_village.name,
                    'Urbanity': queryListPPCellMonth_1[0].city_village.tehsil.urbanity,
                }


                for date_obj in date_arr_obj:
                    cell_month_acv = CellMonthACV.objects.get(country_id = country_id,month=date_obj,cell=queryList[k])
                    temp_dic['cell_acv_'+str(date_obj.code)] = cell_month_acv.cell_acv

                for date_obj in date_arr_obj:
                    temp_dic['num_universe_'+str(date_obj.code)] = queryList[k].num_universe


                for date_obj in date_arr_obj:
                    aggregate_val = queryListPPCell.filter(month = date_obj) \
                                                .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                        .filter(country_id = country_id, month = date_obj, status__iexact = UsableOutlet.USABLE)) \
                                                .aggregate(count = Count('id'))

                    temp_dic['store_'+str(date_obj.code)] = aggregate_val['count']

                for date_obj in date_arr_obj:
                    aggregate_val = queryListPPCell.filter(month = date_obj) \
                                                .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                        .filter(country_id = country_id, month = date_obj, status__iexact = UsableOutlet.USABLE)) \
                                                .aggregate(acv_sum = Sum('acv'))

                    temp_dic['panel_acv_'+str(date_obj.code)] = aggregate_val['acv_sum']


                temp_dic['optimal_panel'] = queryList[k].optimal_panel

                sales = []
                for date_obj in date_arr_obj:
                    aggregate_val = queryListPA.filter(month = date_obj) \
                                                .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                        .filter(country_id = country_id, month = date_obj, status__iexact = UsableOutlet.USABLE))  \
                                                .aggregate(sales = Sum('sales'))
                    temp_dic['sales_'+str(date_obj.code)] = aggregate_val['sales']
                    sales.append(aggregate_val['sales'])

                temp_dic['diff'] = sales[-1]  - sales[-2]




                prv_month = queryListPPCell.filter(month = date_arr_obj[-2]) \
                                            .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                    .filter(country_id = country_id, month = date_arr_obj[-2], status__iexact = UsableOutlet.USABLE)) \
                                            .values_list('outlet_id', flat=True)


                curr_month = queryListPPCell.filter(month = date_arr_obj[-1]) \
                                            .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                    .filter(country_id = country_id, month = date_arr_obj[-1], status__iexact = UsableOutlet.USABLE)) \
                                            .values_list('outlet_id', flat=True)

                new_outlets = queryListPPCell.filter(month = date_arr_obj[-1]).exclude(outlet_id__in = prv_month) \
                                            .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                    .filter(country_id = country_id, month = date_arr_obj[-1], status__iexact = UsableOutlet.USABLE)) \
                                            .values_list('outlet_id', flat=True)

                lost_outlets = queryListPPCell.filter(month = date_arr_obj[-2]).exclude(outlet_id__in = curr_month) \
                                            .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                    .filter(country_id = country_id, month = date_arr_obj[-2], status__iexact = UsableOutlet.USABLE)) \
                                            .values_list('outlet_id', flat=True)

                common_outlets = queryListPPCell.filter(month = date_arr_obj[-1]).filter(outlet_id__in = prv_month) \
                                            .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                    .filter(country_id = country_id, month = date_arr_obj[-1], status__iexact = UsableOutlet.USABLE)) \
                                            .values_list('outlet_id', flat=True)


                temp_dic['lost_outlets'] = len(lost_outlets)
                temp_dic['new_outlets'] = len(new_outlets)
                temp_dic['common_outlets'] = len(common_outlets)


                for date_obj in date_arr_obj:
                    panel_acv = temp_dic['panel_acv_'+str(date_obj.code)] if temp_dic['panel_acv_'+str(date_obj.code)] is not None else 1
                    temp_dic['acv_pf_'+str(date_obj.code)] = temp_dic['cell_acv_'+str(date_obj.code)] / panel_acv


                sales_vol = []
                for date_obj in date_arr_obj:
                    aggregate_val = queryListPA.filter(month = date_obj) \
                                                .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                        .filter(country_id = country_id, month = date_obj, status__iexact = UsableOutlet.USABLE))  \
                                                .aggregate(sales_vol = Sum('sales_vol'))
                    temp_dic['sales_vol_'+str(date_obj.code)] = aggregate_val['sales_vol']
                    sales_vol.append(aggregate_val['sales_vol'])

                temp_dic['weighted_change'] = sales_vol[-1]  - sales_vol[-2]

                sales_val = []
                for date_obj in date_arr_obj:
                    aggregate_val = queryListPA.filter(month = date_obj) \
                                                .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                        .filter(country_id = country_id, month = date_obj, status__iexact = UsableOutlet.USABLE))  \
                                                .aggregate(sales_val = Sum('sales_val'))
                    temp_dic['sales_val_'+str(date_obj.code)] = aggregate_val['sales_val']
                    sales_val.append(aggregate_val['sales_val'])

                temp_dic['val_change'] = sales_val[-1]  - sales_val[-2]

                for sm,smp in super_manufacture_products.items():



                    for date_obj in date_arr_obj:
                        # smpppp = queryListPA.filter(month = date_obj) \
                        #                             .filter(product_id__in = smp) \
                        #                             .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                        #                                     .filter(country_id = country_id, month = date_obj, status__iexact = UsableOutlet.USABLE))
                        # # prettyprint_queryset(smpppp)
                        aggregate_val = queryListPA.filter(month = date_obj) \
                                                    .filter(product_id__in = smp) \
                                                    .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                            .filter(country_id = country_id, month = date_obj, status__iexact = UsableOutlet.USABLE))  \
                                                    .aggregate(sales = Sum('sales'))
                        temp_dic[sm+'_'+str(date_obj.code)] = aggregate_val['sales']





                response_dict.append( temp_dic )



            return_dic['results'] = response_dict
            # print(return_dic)


            # response_dict['queryList_json'] = queryList_json

            logger.error('CSV file processed successfully.')
            log += ' Report Generated Successfully. '
            log += printr("Total time spent: %s seconds" % (convertSecond2Min(time.time() - start_time)))

            rbd_report_qs.report_json  = json.dumps(return_dic,cls=DjangoJSONEncoder)
            rbd_report_qs.is_generated = 1
            rbd_report_qs.log = log
            rbd_report_qs.save()

            # response['Content-Disposition'] = 'attachment; filename=cell_shop_inspection.csv'
            # csv_file = f"{rbd_report_qs.id}.csv"
            csv_file = f"{report_type}-{rbd_name}-{cat_name}-{month_code}-{rbd_report_qs.id}.csv"
            csv_file = csv_file.replace('/','-')
            report_path = f"{MEDIA_ROOT}/reports/{country_code}"
            Path(report_path).mkdir(parents=True, exist_ok=True)

            csv_writer = csv.writer(open(f"{report_path}/{csv_file}","w"))
            count = 0
            for d in return_dic['results']:
                if count == 0:
                    header = d.keys()
                    csv_writer.writerow(header)
                    count += 1
                csv_writer.writerow(d.values())
            rbd_report_qs.report_csv_source = f"{csv_file}"
            rbd_report_qs.save()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+' Report generation failed.. Error Msg:'+ str(e)+Colors.WHITE )

            log += f"Report generation failed. \n Error Msg: {e} \n " \
                    +"Exception: {exc_type} \n {fname} \n {exc_tb.tb_lineno}"
            rbd_report_qs.is_generated = 3
            rbd_report_qs.log = log
            rbd_report_qs.save()

