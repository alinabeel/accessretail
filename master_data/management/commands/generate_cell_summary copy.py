from core.common_libs import *

from master_setups.models import *
from master_data.models import *
from reports.models import *



class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('rbd_report_id', type=int)

    def handle(self, *args, **options):
        start_time = time.time()

        rbd_report_id = options['rbd_report_id']
        rbd_report_qs = RBDReport.objects.get(pk=rbd_report_id)

        country = Country.objects.get(pk = rbd_report_qs.country.id)
        log = ""

        try:
            return_dic = {}
            response_dict = []
            temp_dic = {}

            month_data = dict()
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

            rbd_cells = RBD.objects.only('id').filter(country = country,pk=rbd_id).values('cell')
            # ,cell__name__iexact='National-Total Urban-Sp-Punjab-Multan-Roa-General-Medical Store-Handler-Ttl'
            # category = Category.objects.get(id=cat_id)

            #Cell Query List
            queryList = Cell.objects.all().filter(country = country, id__in=rbd_cells).order_by('name')

            #Product Audit Query List
            queryListPA = AuditData.objects.all().filter(country = country, category=category)
            cdebug(len(queryListPA),'total audit data')
            # prettyprint_queryset(queryListPA)
            # exit()

            ######-----------------------------######

            #Country Query List
            # country = Country.objects.get(code=self.kwargs["country_code"])

            #Cell Query List
            # queryList = Cell.objects.all().filter(country = country).order_by('rbd__name')

            #Product Audit Query List
            # queryListPA = AuditData.objects.all().filter(country = country)

            #Calculate Previous Month, Next Month
            # audit_date_qs = PanelProfile.objects.all().filter(country = country).values('month__date').annotate(current_month=Max('audit_date')).order_by('-audit_date')[0:2]
            # date_arr = []
            # for instance in audit_date_qs:
            #     date_arr.append(instance['month__date'])
            # if(len(date_arr)==2):
            #     current_month , previous_month = date_arr
            # else:
            #     log += "Report generation failed. \n Error Msg: Please load minimum 2 month data."
            #     rbd_report_qs.is_generated = 3
            #     rbd_report_qs.log = log
            #     rbd_report_qs.save()
            #     exit()

            audit_date_qs = PanelProfile.objects.all().filter(Q(country=country) & Q(month__date__lte = month_date) ).values('month__date').annotate(current_month=Max("month__date")).order_by('month__date')[0:2]

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
                current_month_qs = Month.objects.get(date=month_1)
                previous_month_qs = Month.objects.get(date=month_2)
                # date_arr_obj.append(current_month_qs)
                # date_arr_obj.append(previous_month_qs)
                cdebug('2-Month data')
            else:
                cdebug('1-Month data')


            # current_month_qs = Month.objects.get(date=current_month)
            # previous_month_qs = Month.objects.get(date=previous_month)

            return_dic['count'] = len(queryList)
            return_dic['next'] = None
            return_dic['previous'] = None

            return_dic['previous_month'] = "{}, {}".format(previous_month_qs.name,previous_month_qs.year)
            return_dic['current_month'] = "{}, {}".format(current_month_qs.name,current_month_qs.year)



            # queryList_json = serialize('json', queryList)
            for k in range(0,len(queryList)):
                # rbd_serialize_str = queryList[k].rbd.serialize_str
                cell_serialize_str = queryList[k].serialize_str

                print(Colors.BOLD_YELLOW,'Processing Cell: ', queryList[k].name,Colors.WHITE)

                """ Rbd and Cell Processing from previous saved serialize string """


                queryListPPAll = PanelProfile.objects.all().filter(country = country) #All Panel profile Records
                queryListPPCell = queryListPPAll


                # if rbd_serialize_str != '':
                #     rbd_params = parse_qs((rbd_serialize_str))
                #     rbd_list = getDictArray(rbd_params,'field_group[group]')
                #     rbd_dic = getDicGroupList(rbd_list)
                #     rbd_group_filter = getGroupFilter(rbd_dic)
                #     rbd_group_filter_human = getGroupFilterHuman(rbd_dic)


                field_group = parse_qs((cell_serialize_str))
                new_list = getDictArray(field_group,'field_group[group]')
                new_dic = getDicGroupList(new_list)
                group_filter = getGroupFilter(new_dic)
                group_filter_human = getGroupFilterHuman(new_dic)


                filter_human = ''
                # if rbd_serialize_str != '':
                #     rbd_group_filter &= Q(group_filter)
                #     filter_human = "RBD(\n{}) \n AND \n CELL( \n {})".format(rbd_group_filter_human, group_filter_human)
                #     queryListPPCell = queryListPPCell.filter(rbd_group_filter)
                # else:
                if(group_filter != ''):
                    filter_human = group_filter_human
                    queryListPPCell = queryListPPCell.filter(group_filter)


                # prettyprint_queryset(queryListPPCell)

                N_Numeric_Universe = queryList[k].num_universe
                W_Universe = queryList[k].cell_acv

                """-------------Previous Month Calculatuons-------------"""

                #"""CELL Panel Profile"""
                queryListPPCellPrevious = queryListPPCell.filter(month = previous_month_qs) \
                                            .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                    .filter(country = country, month = previous_month_qs, status__iexact = UsableOutlet.USABLE))
                agg_outlets_cell_previous = queryListPPCellPrevious.aggregate(count = Count('id'),
                                                                              num_factor_avg = Avg('num_factor'),
                                                                              turnover_sum = Sum('turnover'))
                total_outlets_in_cell_previous = agg_outlets_cell_previous['count'] #NPanel Numerator
                turnover_sum_cell_previous = agg_outlets_cell_previous['turnover_sum']

                #Audit Data
                queryListPAAllPrevious = queryListPA.filter(month = previous_month_qs) \
                                            .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                    .filter(country = country, month = previous_month_qs, status__iexact = UsableOutlet.USABLE))
                agg_outlets_audit_all_previous = queryListPAAllPrevious.aggregate(count = Count('outlet__id',distinct=True))
                total_outlets_in_audit_previous = agg_outlets_audit_all_previous['count']


                """ J K L M
                    Unprojected Sales (Volume)	Unprojected Sales (Value)	projected Sales (Volume)	projected Sales (Value)
                """

                #Get outlets from Product Audit
                agg_sum_sales_previous = queryListPAAllPrevious \
                                            .filter(outlet__id__in = queryListPPCellPrevious.values_list('outlet_id', flat=True) ) \
                                            .aggregate(
                                                sum_sales_unprojected_volume = Sum('sales_unprojected_volume'),
                                                sum_sales_unprojected_value = Sum('sales_unprojected_value'),
                                                sum_sales_projected_volume = Sum('sales_projected_volume'),
                                                sum_sales_projected_value = Sum('sales_projected_value'),
                                            )

                sum_sales_unprojected_volume_previous = agg_sum_sales_previous['sum_sales_unprojected_volume']
                sum_sales_unprojected_value_previous = agg_sum_sales_previous['sum_sales_unprojected_value']
                sum_sales_projected_volume_previous = agg_sum_sales_previous['sum_sales_projected_volume']
                sum_sales_projected_value_previous = agg_sum_sales_previous['sum_sales_projected_value']


                """Unprojected Contribution (Volume)	Projected Contribution (Volume)	Projected Contribution (Value)"""
                agg_sum_sales_all_previous = queryListPAAllPrevious.aggregate(
                                                sum_sales_unprojected_volume = Sum('sales_unprojected_volume'),
                                                sum_sales_projected_volume = Sum('sales_projected_volume'),
                                                sum_sales_projected_value = Sum('sales_projected_value'),
                                            )

                sum_sales_unprojected_volume_all_previous = agg_sum_sales_all_previous['sum_sales_unprojected_volume']
                sum_sales_projected_volume_all_previous = agg_sum_sales_all_previous['sum_sales_projected_volume']
                sum_sales_projected_value_all_previous = agg_sum_sales_all_previous['sum_sales_projected_value']



                unprojected_contribution_volume_previous = (sum_sales_unprojected_volume_previous / sum_sales_unprojected_volume_all_previous)*100
                projected_contribution_volume_previous = (sum_sales_projected_volume_previous / sum_sales_projected_volume_all_previous)*100
                projected_contribution_value_previous = (sum_sales_projected_value_previous / sum_sales_projected_value_all_previous)*100

                if(turnover_sum_cell_previous==0): turnover_sum_cell_previous = 1
                N_Factor_Previous = N_Numeric_Universe / total_outlets_in_cell_previous
                W_Factor_Previous = W_Universe / turnover_sum_cell_previous


                """-----------------------------------------Current Month Calculatuons-----------------------------------------"""

                #CELL Panel Profile
                #--Filter Useable Outlets
                queryListPPCellCurrent = queryListPPCell.filter(month = current_month_qs) \
                                            .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                    .filter(country = country, month = current_month_qs, status__iexact = UsableOutlet.USABLE))
                agg_outlets_cell_current = queryListPPCellCurrent.aggregate(count = Count('id'),
                                                                            num_factor_avg = Avg('num_factor'),
                                                                            turnover_sum = Sum('turnover'))
                total_outlets_in_cell_current = agg_outlets_cell_current['count']
                num_factor_avg_cell_current = agg_outlets_cell_current['num_factor_avg']
                turnover_sum_cell_current = agg_outlets_cell_current['turnover_sum']

                #Audit Data
                queryListPAAllCurrent = queryListPA.filter(month = current_month_qs) \
                                            .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                    .filter(country = country, month = current_month_qs, status__iexact = UsableOutlet.USABLE))
                agg_outlets_audit_all_current = queryListPAAllCurrent.aggregate(count = Count('outlet__id',distinct=True))
                total_outlets_in_audit_current = agg_outlets_audit_all_current['count']  #NPanel Denumerator


                """
                    Unprojected Sales (Volume)	Unprojected Sales (Value)	projected Sales (Volume)	projected Sales (Value)
                """

                #Get outlets from Product Audit
                agg_sum_sales_current = queryListPAAllCurrent \
                                                .filter(outlet__id__in = queryListPPCellCurrent.values_list('outlet_id', flat=True) ) \
                                                .aggregate(
                                                    sum_sales_unprojected_volume = Sum('sales_unprojected_volume'),
                                                    sum_sales_unprojected_value = Sum('sales_unprojected_value'),
                                                    sum_sales_projected_volume = Sum('sales_projected_volume'),
                                                    sum_sales_projected_value = Sum('sales_projected_value'),
                                                )

                sum_sales_unprojected_volume_current = agg_sum_sales_current['sum_sales_unprojected_volume']
                sum_sales_unprojected_value_current = agg_sum_sales_current['sum_sales_unprojected_value']
                sum_sales_projected_volume_current = agg_sum_sales_current['sum_sales_projected_volume']
                sum_sales_projected_value_current = agg_sum_sales_current['sum_sales_projected_value']


                """Unprojected Contribution (Volume)	Projected Contribution (Volume)	Projected Contribution (Value)"""
                agg_sum_sales_all_current = queryListPAAllCurrent.aggregate(
                                                sum_sales_unprojected_volume = Sum('sales_unprojected_volume'),
                                                sum_sales_projected_volume = Sum('sales_projected_volume'),
                                                sum_sales_projected_value = Sum('sales_projected_value'),
                                            )

                sum_sales_unprojected_volume_all_current = agg_sum_sales_all_current['sum_sales_unprojected_volume']
                sum_sales_projected_volume_all_current = agg_sum_sales_all_current['sum_sales_projected_volume']
                sum_sales_projected_value_all_current = agg_sum_sales_all_current['sum_sales_projected_value']


                unprojected_contribution_volume_current = (sum_sales_unprojected_volume_current / sum_sales_unprojected_volume_all_current)*100
                projected_contribution_volume_current = (sum_sales_projected_volume_current / sum_sales_projected_volume_all_current)*100
                projected_contribution_value_current = (sum_sales_projected_value_current / sum_sales_projected_value_all_current)*100


                if(turnover_sum_cell_current==0): turnover_sum_cell_current = 1
                N_Factor_Current = N_Numeric_Universe / total_outlets_in_cell_current
                W_Factor_Current = W_Universe / turnover_sum_cell_current


                temp_dic = {
                    'RBD Name' : rbd_report_qs.rbd.name,
                    'Cell Name' : queryList[k].name,
                    'Cell Description' : queryList[k].description,

                    'N Numeric Universe (Selected Projection Set-up)' : dropzeros(N_Numeric_Universe),
                    'W Universe (Selected Projection Setup)' : dropzeros(W_Universe),

                    'total_outlets_in_audit_previous' : dropzeros(total_outlets_in_audit_previous),
                    'w Panel Previous' : dropzeros(turnover_sum_cell_previous),
                    'n Panel Previous' : dropzeros(total_outlets_in_cell_previous),


                    'N Factor Previous' : "{:,.6f}".format(N_Factor_Previous),  # N-factor = N_Universe/nPanel (it must be 1 or greater then 1)
                    'W Factor Previous' : "{:,.6f}".format(W_Factor_Previous),  # W-factor = W_Universe/wPanel (it must be 1 or greater then 1)

                    'Unprojected Sales (Volume) in Millions' : "{:,.6f}".format(sum_sales_unprojected_volume_previous/1000000),
                    'Unprojected Sales (Value) in Millions' : "{:,.6f}".format(sum_sales_unprojected_value_previous/1000000),
                    'projected Sales (Volume) in Millions' : "{:,.6f}".format(sum_sales_projected_volume_previous/1000000),
                    'projected Sales (Value) in Millions' : "{:,.6f}".format(sum_sales_projected_value_previous/1000000),

                    'Unprojected Contribution (Volume)' : "{:,.4f}".format(unprojected_contribution_volume_previous),
                    'Projected Contribution (Volume)' : "{:,.4f}".format(projected_contribution_volume_previous),
                    'Projected Contribution (Value)' : "{:,.4f}".format(projected_contribution_value_previous),
                    #-----------------------------------------------------------------------------------------
                    'total_outlets_in_audit_current' : total_outlets_in_audit_current,

                    'w Panel Current' : dropzeros(turnover_sum_cell_current),
                    'n Panel Current' : dropzeros(total_outlets_in_cell_current),

                    'N Factor Current' : "{:,.6f}".format(N_Factor_Current),  # N-factor = N_Universe/nPanel (it must be 1 or greater then 1)
                    'W Factor Current' : "{:,.6f}".format(W_Factor_Current),  # W-factor = W_Universe/wPanel (it must be 1 or greater then 1)

                    'Unprojected Sales (Volume) Current in Millions' : "{:,.6f}".format(sum_sales_unprojected_volume_current/1000000),
                    'Unprojected Sales (Value) Current in Millions' : "{:,.6f}".format(sum_sales_unprojected_value_current/1000000),
                    'projected Sales (Volume) Current in Millions' : "{:,.6f}".format(sum_sales_projected_volume_current/1000000),
                    'projected Sales (Value) Current in Millions' :  "{:,.6f}".format(sum_sales_projected_value_current/1000000),

                    'Unprojected Contribution (Volume) Current' : "{:,.4f}".format(unprojected_contribution_volume_current),
                    'Projected Contribution (Volume) Current' : "{:,.4f}".format(projected_contribution_volume_current),
                    'Projected Contribution (Value) Current' : "{:,.4f}".format(projected_contribution_value_current),


                    }

                response_dict.append( temp_dic )

            # print(response_dict)
            return_dic['results'] = response_dict
            # response_dict['queryList_json'] = queryList_json

            logger.error('CSV file processed successfully.')
            log += ' Report Generated Successfully. '
            log += printr("Total time spent: %s seconds" % (convertSecond2Min(time.time() - start_time)))

            rbd_report_qs.report_json  = json.dumps(return_dic,cls=DjangoJSONEncoder)
            rbd_report_qs.is_generated = 1
            rbd_report_qs.log = log
            rbd_report_qs.save()

            # response['Content-Disposition'] = 'attachment; filename=cell_shop_inspection.csv'
            csv_file = f"CellSummary-{rbd_name}_{cat_name}_{month_code}_{rbd_report_qs.id}.csv"
            report_path = f"{MEDIA_ROOT}/reports/{rbd_report_qs.country.code}/"
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

