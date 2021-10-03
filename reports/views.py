from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *
from datetime import datetime,date,timedelta
from  decimal import Decimal

import csv
import re
import time, os,sys, signal,logging,json
from sys import stdout, stdin, stderr
from pprint import pprint
from var_dump import var_dump,var_export
from subprocess import Popen
from inspect import getmembers
from csv import DictReader
from urllib.parse import parse_qs,urlparse
from itertools import chain



from django.db import IntegrityError
from django.db.models import Q, Avg, Count, Min,Max, Sum
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse,reverse_lazy
from django.core.files.storage import FileSystemStorage
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (HttpResponseRedirect,HttpResponse,JsonResponse)
from django.http import StreamingHttpResponse
from django.db.models.functions import Concat


from django.views import generic
from rest_framework.generics import ListAPIView


from core.utils import cdebug, prettyprint_queryset, prettyprint_query ,trace, format_datetime

from core.pagination import StandardResultsSetPagination
from core.mixinsViews import PassRequestToFormViewMixin
from core.helpers import *
from core.colors import Colors
from master_data.serializers import *
from master_setups.models import *
from master_data.models import *


from ajax_datatable.views import AjaxDatatableView
from django_datatables_view.base_datatable_view import BaseDatatableView

from reports.models import RBDReport

logger = logging.getLogger(__name__)


""" ------------------------- Imports Logs ------------------------- """

class ImportsLogsListViewAjax(AjaxDatatableView):
    model = Upload
    title = 'Imports Logs'
    initial_order = [["created", "desc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'


    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id', 'visible': True, 'title':'ID' },
        {'name': 'import_mode',  'choices': True,'autofilter': True,},
        {'name': 'frommodel','title':'Module',  'choices': True,'autofilter': True,},
        {'name': 'is_processing','title':'Process',  'choices': True,'autofilter': True,'className': 'is_processing',},
        {'name': 'process_message','width':'200px'},
        {'name': 'skiped_records', 'title':'Skipped'},
        {'name': 'updated_records','title':'Updated'},
        {'name': 'created_records','title':'Created'},

        {'name': 'created','title':'Created at'},
        {'name': 'updated','title':'Updated at'},

        ]

    def get_initial_queryset(self, request=None):
        queryset = self.model.objects.filter(
            country__code=self.kwargs['country_code']
        )
        return queryset

class ImportsLogsListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "reports/import_logs.html"
    PAGE_TITLE = "Imports Logs"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        return context

""" ------------------------- CellSummaryGenerateReport  ------------------------- """

#Generate Report AJAX Action
class CellSummaryGenerateReportAjax(LoginRequiredMixin, generic.CreateView):

    def post(self, request, country_code):
        country = Country.objects.get(code=self.kwargs["country_code"])
        rbd = RBD.objects.get(id=self.request.POST.get("rbd"))
        category = Category.objects.get(id=self.request.POST.get("category"))
        month = Month.objects.get(id=self.request.POST.get("month"))

        user = self.request.user
        # rbd = self.request.POST.get("rbd")
        # category = self.request.POST.get("category")
        # month = self.request.POST.get("month")
        cdebug(self.request.POST)
        # ('country', 'name', 'rbd', 'category', 'month', 'report_html', 'report_json', 'is_confirmed', 'confirmed_on', 'confirmed_by', 'is_generated', 'generated_on', 'generated_by', )
        obj, created = RBDReport.objects.get_or_create(
            country = country, rbd=rbd, category=category, month=month,
            defaults={
                'generated_by': user,
                'generated_on': date.today(),
                'is_generated': 2
            },

        )
        # obj = UsableOutlet.objects.get(pk=id,country=country)
        # obj.status  = value
        # obj.save()
        proc = Popen('python manage.py generate_cell_report '+str(obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        return HttpResponse(
            json.dumps(
                {'data':'success'},
                cls=DjangoJSONEncoder
            ),
            content_type="application/json")

#Grid view of generated reports
class CellSummaryReportViewAjax(AjaxDatatableView):
    model = RBDReport
    initial_order = [["category", "asc"],["rbd", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'

    # ('country', 'name', 'rbd', 'category', 'month', 'report_html', 'report_json', 'is_confirmed', 'confirmed_on', 'confirmed_by', 'is_generated', 'generated_on', 'generated_by', )
    column_defs = [
        AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id','title':'ID', 'visible': True, },
        {'name': 'category', 'title':'Category', 'foreign_field': 'category__name', 'choices': True,'autofilter': True,},
        {'name': 'rbd', 'title':'RBD', 'foreign_field': 'rbd__name', },
        {'name': 'month code','title':'Month Code', 'foreign_field': 'month__code', },
        {'name': 'month', 'title':'Month','foreign_field': 'month__name', 'choices': True,'autofilter': True,},
        {'name': 'year', 'title':'Year','foreign_field': 'month__year', 'choices': True,'autofilter': True,},
        {'name': 'status', 'title': 'Status', 'placeholder': True, 'searchable': False, 'orderable': False, },
        {'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):

            is_generated = obj.is_generated
            if  is_generated==1:
                row['status'] = ('<div class="alert alert-success" role="alert">%s</div>') % ('Generated')
                row['action'] = ('<a href="%s" class="btn btn-info">View Summary</a>') % (
                                reverse('reports:cell-summary', args=(self.kwargs['country_code'],obj.id,)),
                                )
            elif is_generated==2:
                row['status'] = ('<div class="alert alert-warning" role="alert">%s</div>') % ('Generating...')
                row['action'] = ''

            elif is_generated==3:
                row['status'] = ('<div class="alert alert-danger" role="alert">%s</div>') % ('Failed / Retry.')
                row['action'] = ''


    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__code=self.kwargs['country_code']
        )
        return queryset

#Generate Cell Summary View
class CellSummaryReportView(LoginRequiredMixin, generic.TemplateView):
    template_name = "reports/cell_summary_report.html"
    PAGE_TITLE = "Generate Cell Summary Report"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, *args, **kwargs):
        try:
            context = super(self.__class__, self).get_context_data(**kwargs)

            rbd_qs = RBD.objects.filter(country__code=self.kwargs['country_code']).order_by('name')
            category_qs = Category.objects.filter(country__code=self.kwargs['country_code']).order_by('name')
            month_qs = Month.objects.filter(country__code=self.kwargs['country_code']).order_by('date')

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",str(e),', File: ',exc_type, fname,', Line: ',exc_tb.tb_lineno, Colors.WHITE)

        context.update({
            "rbd_qs": rbd_qs,
            "category_qs": category_qs,
            "month_qs": month_qs,
        })
        return context

""" ------------------------- Cell Summary ------------------------- """

#Logic shifted to command generate_cell_report
class CellSummaryAJAX_Backup(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        return_dic = {}
        response_dict = []
        temp_dic = {}
        month_data = dict()
        rbd_id = self.kwargs["pk"]
        cat_id = self.kwargs["cat"]
        cdebug(rbd_id)
        cdebug(cat_id)
        export = False
        if 'export' in request.GET:
            export = request.GET['export']

        try:
            #Country Query List
            country = Country.objects.get(code=self.kwargs["country_code"])

            rbd_cells = RBD.objects.only('id').filter(country = country,pk=rbd_id).values('cell')

            category = Category.objects.get(id=cat_id)

            #Cell Query List
            queryList = Cell.objects.all().filter(country = country, id__in=rbd_cells).order_by('name')

            #Product Audit Query List
            queryListPA = ProductAudit.objects.all().filter(country = country, category=category)

            super_manufacture = Product.objects.filter(country = country, category=category).exclude(super_manufacture=None) \
                                .order_by('category').values_list('super_manufacture', flat=True).distinct()
            super_manufacture_products = dict()
            for sm in super_manufacture:
                smp = Product.objects \
                    .filter(country = country, category=category,super_manufacture__iexact=sm) \
                    .exclude(super_manufacture=None) \
                    .order_by('category').values_list('id', flat=True)
                super_manufacture_products[sm] = smp


            #Calculate Previous Month, Next Month
            audit_date_qs = PanelProfile.objects.all().filter(country = country).values('month__date').annotate(current_month=Max('audit_date')).order_by('month__date')[0:3]

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
                return HttpResponse(json.dumps({'msg','Please load minimum 2 month data.'},cls=DjangoJSONEncoder),content_type="application/json")




            # return_dic['previous_month'] = "{}, {}".format(previous_month_qs.name,previous_month_qs.year)
            # return_dic['current_month'] = "{}, {}".format(current_month_qs.name,current_month_qs.year)

            queryListPPAll = PanelProfile.objects.all().filter(country = country,category__id = cat_id)

            if len(queryListPPAll) == 0 :
                return_dic['count'] = 0
                return_dic['next'] = None
                return_dic['previous'] = None
                return_dic['results'] = []
                return HttpResponse(json.dumps(return_dic,cls=DjangoJSONEncoder),content_type="application/json")

            return_dic['count'] = len(queryList)
            return_dic['next'] = None
            return_dic['previous'] = None

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
                queryListPPCellMonth_1 = queryListPPCell.filter(month = month_1_qs) \
                                            .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                    .filter(country = country, month = month_1_qs, status__iexact = UsableOutlet.USABLE))


                # prettyprint_queryset(queryListPPCellMonth_1)
                temp_dic = {
                    'Category' : category.name,
                    'Cell Name' : queryList[k].name,
                    'Area': queryListPPCellMonth_1[0].city_village.name,
                    'Urbanity': queryListPPCellMonth_1[0].city_village.tehsil.urbanity,
                }


                for date_obj in date_arr_obj:
                    cell_month_acv = CellMonthACV.objects.get(country = country,month=date_obj,cell=queryList[k])
                    temp_dic['cell_acv_'+str(date_obj.code)] = cell_month_acv.cell_acv

                for date_obj in date_arr_obj:
                    temp_dic['num_universe_'+str(date_obj.code)] = queryList[k].num_universe


                for date_obj in date_arr_obj:
                    aggregate_val = queryListPPCell.filter(month = date_obj) \
                                                .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                        .filter(country = country, month = date_obj, status__iexact = UsableOutlet.USABLE)) \
                                                .aggregate(count = Count('id'))

                    temp_dic['store_'+str(date_obj.code)] = aggregate_val['count']

                for date_obj in date_arr_obj:
                    aggregate_val = queryListPPCell.filter(month = date_obj) \
                                                .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                        .filter(country = country, month = date_obj, status__iexact = UsableOutlet.USABLE)) \
                                                .aggregate(acv_sum = Sum('acv'))

                    temp_dic['panel_acv_'+str(date_obj.code)] = aggregate_val['acv_sum']


                temp_dic['optimal_panel'] = queryList[k].optimal_panel

                sales = []
                for date_obj in date_arr_obj:
                    aggregate_val = queryListPA.filter(month = date_obj) \
                                                .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                        .filter(country = country, month = date_obj, status__iexact = UsableOutlet.USABLE))  \
                                                .aggregate(sales = Sum('sales'))
                    temp_dic['sales_'+str(date_obj.code)] = aggregate_val['sales']
                    sales.append(aggregate_val['sales'])

                temp_dic['diff'] = sales[-1]  - sales[-2]




                prv_month = queryListPPCell.filter(month = date_arr_obj[-2]) \
                                            .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                    .filter(country = country, month = date_arr_obj[-2], status__iexact = UsableOutlet.USABLE)) \
                                            .values_list('outlet_id', flat=True)


                curr_month = queryListPPCell.filter(month = date_arr_obj[-1]) \
                                            .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                    .filter(country = country, month = date_arr_obj[-1], status__iexact = UsableOutlet.USABLE)) \
                                            .values_list('outlet_id', flat=True)
                print(prv_month)
                cdebug(curr_month)
                new_outlets = queryListPPCell.filter(month = date_arr_obj[-1]).exclude(outlet_id__in = prv_month) \
                                            .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                    .filter(country = country, month = date_arr_obj[-1], status__iexact = UsableOutlet.USABLE)) \
                                            .values_list('outlet_id', flat=True)

                lost_outlets = queryListPPCell.filter(month = date_arr_obj[-2]).exclude(outlet_id__in = curr_month) \
                                            .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                    .filter(country = country, month = date_arr_obj[-2], status__iexact = UsableOutlet.USABLE)) \
                                            .values_list('outlet_id', flat=True)

                common_outlets = queryListPPCell.filter(month = date_arr_obj[-1]).filter(outlet_id__in = prv_month) \
                                            .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                    .filter(country = country, month = date_arr_obj[-1], status__iexact = UsableOutlet.USABLE)) \
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
                                                        .filter(country = country, month = date_obj, status__iexact = UsableOutlet.USABLE))  \
                                                .aggregate(sales_vol = Sum('sales_vol'))
                    temp_dic['sales_vol_'+str(date_obj.code)] = aggregate_val['sales_vol']
                    sales_vol.append(aggregate_val['sales_vol'])

                temp_dic['weighted_change'] = sales_vol[-1]  - sales_vol[-2]

                sales_val = []
                for date_obj in date_arr_obj:
                    aggregate_val = queryListPA.filter(month = date_obj) \
                                                .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                        .filter(country = country, month = date_obj, status__iexact = UsableOutlet.USABLE))  \
                                                .aggregate(sales_val = Sum('sales_val'))
                    temp_dic['sales_val_'+str(date_obj.code)] = aggregate_val['sales_val']
                    sales_val.append(aggregate_val['sales_val'])

                temp_dic['val_change'] = sales_val[-1]  - sales_val[-2]

                for sm,smp in super_manufacture_products.items():



                    for date_obj in date_arr_obj:
                        # smpppp = queryListPA.filter(month = date_obj) \
                        #                             .filter(product_id__in = smp) \
                        #                             .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                        #                                     .filter(country = country, month = date_obj, status__iexact = UsableOutlet.USABLE))
                        # # prettyprint_queryset(smpppp)
                        aggregate_val = queryListPA.filter(month = date_obj) \
                                                    .filter(product_id__in = smp) \
                                                    .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                            .filter(country = country, month = date_obj, status__iexact = UsableOutlet.USABLE))  \
                                                    .aggregate(sales = Sum('sales'))
                        temp_dic[sm+'_'+str(date_obj.code)] = aggregate_val['sales']





                response_dict.append( temp_dic )

            return_dic['results'] = response_dict
            # response_dict['queryList_json'] = queryList_json

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",str(e),', File: ',exc_type, fname,', Line: ',exc_tb.tb_lineno, Colors.WHITE)


        # Prepare response

        if export is not False:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=cell_summary.csv'
            csv_writer = csv.writer(response)
            count = 0
            for d in return_dic['results']:
                if count == 0:
                    header = d.keys()
                    csv_writer.writerow(header)
                    count += 1
                csv_writer.writerow(d.values())

            return response
        else:
            return HttpResponse(
                json.dumps(
                    return_dic,
                    cls=DjangoJSONEncoder
                ),
                content_type="application/json")


class CellSummaryListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "reports/cell_summary.html"
    PAGE_TITLE = "Cell Summary"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }


""" ------------------------- Cell Summary Overview ------------------------- """

class CellSummaryOverviewAJAX(LoginRequiredMixin, generic.View):

    def get(self, request, *args, **kwargs):
        return_dic = {}
        response_dict = []
        temp_dic = dict()

        export = False
        if 'export' in request.GET:
            export = request.GET['export']

        sum_total_outlets_in_rbd_previous = 0
        sum_total_outlets_in_cell_previous = 0

        sum_total_outlets_in_rbd_current = 0
        sum_total_outlets_in_cell_current = 0




        try:
            #Country Query List
            country = Country.objects.get(code=self.kwargs["country_code"])

            #RBD Query List
            queryRBDList = RBD.objects.all().filter(country = country,parent=None).order_by('name')

            #Calculate Previous Month, Next Month
            audit_date_qs = PanelProfile.objects.all().filter(country = country).values('month__date').annotate(current_month=Max('audit_date')).order_by('-audit_date')[0:2]
            date_arr = []
            for instance in audit_date_qs:
                date_arr.append(instance['month__date'])
            if(len(date_arr)==2):
                current_month , previous_month = date_arr
            else:
                return HttpResponse(json.dumps({'msg','Please load minimum 2 month data.'},cls=DjangoJSONEncoder),content_type="application/json")

            current_month_qs = Month.objects.get(date=current_month)
            previous_month_qs = Month.objects.get(date=previous_month)

            return_dic['count'] = len(queryRBDList)
            return_dic['next'] = None
            return_dic['previous'] = None

            #All Panel profile Records with in Usableoutlets
            queryListPPAll = PanelProfile.objects.all().filter(country = country)

            agg_total_outlets_in_pp_previous = queryListPPAll.filter(month = previous_month_qs) \
                                    .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                            .filter(country = country, month = previous_month_qs, status__iexact = UsableOutlet.USABLE)) \
                                    .aggregate(count = Count('outlet__id'))
            total_outlets_in_pp_previous = agg_total_outlets_in_pp_previous['count']

            agg_total_outlets_in_pp_current = queryListPPAll.filter(month = current_month_qs) \
                                    .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                            .filter(country = country, month = current_month_qs, status__iexact = UsableOutlet.USABLE)) \
                                    .aggregate(count = Count('outlet__id'))
            total_outlets_in_pp_current = agg_total_outlets_in_pp_current['count']



            # queryList_json = serialize('json', queryList)

            for k in range(0,len(queryRBDList)):
                sub_total_cell_outlts_previous = 0
                sub_total_cell_outlts_current = 0

                rbd_serialize_str = queryRBDList[k].serialize_str
                rbd_name = queryRBDList[k].name
                rbd_code = queryRBDList[k].code

                """ Rbd Processing from previous saved serialize string """

                if rbd_serialize_str != '':
                    rbd_params = parse_qs((rbd_serialize_str))
                    rbd_list = getDictArray(rbd_params,'field_group[group]')
                    rbd_dic = getDicGroupList(rbd_list)
                    rbd_group_filter = getGroupFilter(rbd_dic)

                    rbd_group_filter_temp = rbd_group_filter

                    rbd_group_filter_human = getGroupFilterHuman(rbd_dic)
                    rbd_filter_human = "RBD(\n{}) \n".format(rbd_group_filter_human)


                    queryListPPRBDAll = queryListPPAll.filter(rbd_group_filter)



                    """-------------Previous Month Calculatuons-------------"""

                    queryListPPRBDAllPrevious = queryListPPRBDAll.filter(month = previous_month_qs) \
                                            .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                    .filter(country = country, month = previous_month_qs, status__iexact = UsableOutlet.USABLE))



                    agg_total_outlets_in_rbd_previous = queryListPPRBDAllPrevious.aggregate(count = Count('outlet__id'))
                    total_outlets_in_rbd_previous = agg_total_outlets_in_rbd_previous['count']


                    """-------------Current Month Calculatuons-------------"""

                    queryListPPRBDAllCurrent = queryListPPRBDAll.filter(month = current_month_qs) \
                                            .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                    .filter(country = country, month = current_month_qs, status__iexact = UsableOutlet.USABLE))



                    agg_total_outlets_in_rbd_current = queryListPPRBDAllCurrent.aggregate(count = Count('outlet__id'))
                    total_outlets_in_rbd_current = agg_total_outlets_in_rbd_current['count']

                """--------------------------------------------------------"""


                return_dic['previous_month'] = "{}, {}".format(previous_month_qs.name,previous_month_qs.year)
                return_dic['current_month'] = "{}, {}".format(current_month_qs.name,current_month_qs.year)

                rbd_dic = {
                    'RBD_Name' : ("%s(%s)")%(rbd_name,rbd_code),
                    'Condition' : "".join(rbd_filter_human.split("\n")),
                    'Total_Outlets_in_RBD_Previous' : total_outlets_in_rbd_previous,
                    'Total_Outlets_in_RBD_Current' : total_outlets_in_rbd_current,
                    'Cell':[],
                    }

                sum_total_outlets_in_rbd_previous += total_outlets_in_rbd_previous
                sum_total_outlets_in_rbd_current += total_outlets_in_rbd_current

                cell_dic = {}
                queryCellList = Cell.objects.all().filter(country = country,rbd=queryRBDList[k])
                for i in range(0,len(queryCellList)):
                    cell_serialize_str = queryCellList[i].serialize_str
                    cell_name = queryCellList[i].name
                    cell_code = queryCellList[i].code
                    rbd_group_filter = rbd_group_filter_temp

                    if cell_serialize_str != '':
                        field_group = parse_qs((cell_serialize_str))
                        new_list = getDictArray(field_group,'field_group[group]')
                        new_dic = getDicGroupList(new_list)

                        group_filter = getGroupFilter(new_dic)
                        group_filter_human = getGroupFilterHuman(new_dic)

                        filter_human = ''
                        if rbd_serialize_str != '':
                            rbd_group_filter &= Q(group_filter)
                            filter_human = "RBD(\n{}) \n AND \n CELL( \n {})".format(rbd_group_filter_human, group_filter_human)
                            queryListPPCellAll = queryListPPAll.filter(rbd_group_filter)
                        else:
                            if(group_filter != ''):
                                filter_human = group_filter_human
                                queryListPPCellAll = queryListPPAll.filter(group_filter)


                        """-------------Cell Previous Month Calculatuons-------------"""

                        queryListPPCellAllPrevious = queryListPPCellAll.filter(month = previous_month_qs) \
                                                .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                        .filter(country = country, month = previous_month_qs, status__iexact = UsableOutlet.USABLE))



                        agg_total_outlets_in_cell_previous = queryListPPCellAllPrevious.aggregate(count = Count('outlet__id'))
                        total_outlets_in_cell_previous = agg_total_outlets_in_cell_previous['count']

                        sub_total_cell_outlts_previous  += total_outlets_in_cell_previous
                        sum_total_outlets_in_cell_previous += total_outlets_in_cell_previous

                        """-------------Cell Current Month Calculatuons-------------"""

                        queryListPPCellAllCurrent = queryListPPCellAll.filter(month = current_month_qs) \
                                                .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                        .filter(country = country, month = current_month_qs, status__iexact = UsableOutlet.USABLE))



                        agg_total_outlets_in_cell_current = queryListPPCellAllCurrent.aggregate(count = Count('outlet__id'))
                        total_outlets_in_cell_current = agg_total_outlets_in_cell_current['count']

                        sub_total_cell_outlts_current  += total_outlets_in_cell_current
                        sum_total_outlets_in_cell_current += total_outlets_in_cell_current


                        cell_dic = {
                                'Cell_Name' : ("%s(%s)")%(cell_name,cell_code),
                                'Condition' : "".join(filter_human.split("\n")),
                                'Total_Outlets_in_Cell_Previous' : total_outlets_in_cell_previous,
                                'Total_Outlets_in_Cell_Current' : total_outlets_in_cell_current,
                            }

                        rbd_dic['Cell'].append(cell_dic)

                #End Cell For
                rbd_dic['Cell_Sub_Total_Previous'] = sub_total_cell_outlts_previous
                rbd_dic['Cell_Sub_Total_Current'] = sub_total_cell_outlts_current
                response_dict.append( rbd_dic )

            #End RBD For


            # return_dic['sum_total_outlets_in_rbd_previous'] = sum_total_outlets_in_rbd_previous
            # return_dic['sum_total_outlets_in_rbd_current'] = sum_total_outlets_in_rbd_current

            # return_dic['sum_total_outlets_in_cell_previous'] = sum_total_outlets_in_cell_previous
            # return_dic['sum_total_outlets_in_cell_current'] = sum_total_outlets_in_cell_current

            return_dic['total_outlets_in_pp_previous'] = total_outlets_in_pp_previous
            return_dic['total_outlets_in_pp_current'] = total_outlets_in_pp_current



            return_dic['results'] = response_dict

            # response_dict['queryList_json'] = queryList_json

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",str(e),', File: ',exc_type, fname,', Line: ',exc_tb.tb_lineno, Colors.WHITE)


        # Prepare response
        return HttpResponse(
            json.dumps(
                return_dic,
                cls=DjangoJSONEncoder
            ),
            content_type="application/json")

class CellSummaryOverviewListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "reports/cell_summary_overview.html"
    PAGE_TITLE = "Cell Summary Overview"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }


""" ------------------------- Cell and Shop Inspection ------------------------- """

class CellShopInspectionAJAX(LoginRequiredMixin, generic.View):

    def get(self, request, *args, **kwargs):
        return_dic = {}
        response_dict = []
        temp_dic = dict()

        export = False
        if 'export' in request.GET:
            export = request.GET['export']

        try:
            #Country Query List
            country = Country.objects.get(code=self.kwargs["country_code"])

            #Cell Query List
            queryList = Cell.objects.all().filter(country = country).order_by('rbd__name')
            if export is False:
                queryList = queryList[0:1]

            #Product Audit Query List
            queryListPA = ProductAudit.objects.all().filter(country = country)

            #Calculate Previous Month, Next Month
            audit_date_qs = PanelProfile.objects.all().filter(country = country).values('month__date').annotate(current_month=Max('audit_date')).order_by('-audit_date')[0:2]
            date_arr = []
            for instance in audit_date_qs:
                date_arr.append(instance['month__date'])
            if(len(date_arr)==2):
                current_month , previous_month = date_arr
            else:
                return HttpResponse(json.dumps({'msg','Please load minimum 2 month data.'},cls=DjangoJSONEncoder),content_type="application/json")

            current_month_qs = Month.objects.get(date=current_month)
            previous_month_qs = Month.objects.get(date=previous_month)
            cdebug(len(queryList),'total cells')
            return_dic['count'] = len(queryList)
            return_dic['next'] = None
            return_dic['previous'] = None

            return_dic['previous_month'] = "{}, {}".format(previous_month_qs.name,previous_month_qs.year)
            return_dic['current_month'] = "{}, {}".format(current_month_qs.name,current_month_qs.year)



            # queryList_json = serialize('json', queryList)
            for k in range(0,len(queryList)):
                rbd_serialize_str = queryList[k].rbd.serialize_str
                cell_serialize_str = queryList[k].serialize_str

                print(Colors.BOLD_YELLOW,'Processing Cell: ', queryList[k].name,Colors.WHITE)

                """ Rbd and Cell Processing from previous saved serialize string """


                queryListPPAll = PanelProfile.objects.all().filter(country = country) #All Panel profile Records
                queryListPPCell = queryListPPAll


                if rbd_serialize_str != '':
                    rbd_params = parse_qs((rbd_serialize_str))
                    rbd_list = getDictArray(rbd_params,'field_group[group]')
                    rbd_dic = getDicGroupList(rbd_list)
                    rbd_group_filter = getGroupFilter(rbd_dic)
                    rbd_group_filter_human = getGroupFilterHuman(rbd_dic)


                field_group = parse_qs((cell_serialize_str))
                new_list = getDictArray(field_group,'field_group[group]')
                new_dic = getDicGroupList(new_list)
                group_filter = getGroupFilter(new_dic)
                group_filter_human = getGroupFilterHuman(new_dic)


                filter_human = ''
                if rbd_serialize_str != '':
                    rbd_group_filter &= Q(group_filter)
                    filter_human = "RBD(\n{}) \n AND \n CELL( \n {})".format(rbd_group_filter_human, group_filter_human)
                    queryListPPCell = queryListPPCell.filter(rbd_group_filter)
                else:
                    if(group_filter != ''):
                        filter_human = group_filter_human
                        queryListPPCell = queryListPPCell.filter(group_filter)


                # prettyprint_queryset(queryListPPCell)

                N_Numeric_Universe = queryList[k].num_universe
                W_Universe = queryList[k].cell_acv


                temp_dic_previous = []
                temp_dic_current = []
                shops = dict()

                queryListPPCellCurrentPrevious = queryListPPCell.filter(Q(month = previous_month_qs)| Q(month = current_month_qs)) \
                                            .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                    .filter(Q(country = country) & Q(status__iexact = UsableOutlet.USABLE) & Q(Q(month = previous_month_qs)| Q(month = current_month_qs)))) \
                                            .values('outlet__code','outlet__id').annotate(outlet_id_count=Count('outlet__code'))
                # prettyprint_queryset(queryListPPCellCurrentPrevious)
                outlets  = list(queryListPPCellCurrentPrevious)

                for o in range(0,len(outlets)):
                    total_outlets_in_audit_previous = 0
                    turnover_sum_cell_previous = 0
                    total_outlets_in_cell_previous = 0
                    N_Factor_Previous = 0
                    W_Factor_Previous = 0
                    sum_sales_unprojected_volume_previous = 0
                    sum_sales_unprojected_value_previous = 0
                    sum_sales_projected_volume_previous = 0
                    sum_sales_projected_value_previous = 0
                    unprojected_contribution_volume_previous = 0
                    projected_contribution_volume_previous = 0
                    projected_contribution_value_previous = 0

                    total_outlets_in_audit_current = 0
                    turnover_sum_cell_current = 0
                    total_outlets_in_cell_current = 0
                    N_Factor_Current = 0
                    W_Factor_Current = 0
                    sum_sales_unprojected_volume_current = 0
                    sum_sales_unprojected_value_current = 0
                    sum_sales_projected_volume_current = 0
                    sum_sales_projected_value_current = 0
                    unprojected_contribution_volume_current = 0
                    projected_contribution_volume_current = 0
                    projected_contribution_value_current = 0

                    outlet_id = outlets[o]['outlet__id']
                    outlet_code = outlets[o]['outlet__code']
                    cdebug(outlet_code,'Processing')
                    """-----------------------------------------Previous Month Calculatuons-----------------------------------------"""

                    #"""CELL Panel Profile"""
                    is_usable_previous  = list(UsableOutlet.objects.values_list('outlet__code',flat=True) \
                                                        .filter(country = country, month = previous_month_qs, status__iexact = UsableOutlet.USABLE,outlet_id=outlet_id))

                    if(is_usable_previous):
                        queryListPPCellPrevious = queryListPPCell.filter(month = previous_month_qs) \
                                                    .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                            .filter(country = country, month = previous_month_qs, status__iexact = UsableOutlet.USABLE))


                        # for i in range(0,len(queryListPPCellPrevious)):
                        agg_outlets_cell_previous = queryListPPCellPrevious.aggregate(count = Count('id'),
                                                                                    num_factor_avg = Avg('num_factor'),
                                                                                    turnover_sum = Sum('turnover'))
                        total_outlets_in_cell_previous = agg_outlets_cell_previous['count']
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
                        #--- Only This Changed to individulal outlet rest remains same ---
                        # outlet_id = queryListPPCellPrevious[i].outlet.id
                        # outlet_code = queryListPPCellPrevious[i].outlet.code

                        agg_sum_sales_previous = queryListPAAllPrevious \
                                                    .filter(outlet__id = outlet_id ) \
                                                    .aggregate(
                                                        sum_sales_unprojected_volume = Sum('sales_unprojected_volume'),
                                                        sum_sales_unprojected_value = Sum('sales_unprojected_value'),
                                                        sum_sales_projected_volume = Sum('sales_projected_volume'),
                                                        sum_sales_projected_value = Sum('sales_projected_value'),
                                                    )
                        #Numinators value
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
                        #De-Numinators Values
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

                    is_usable_current  = list(UsableOutlet.objects.values_list('outlet__code',flat=True) \
                                                        .filter(country = country, month = current_month_qs, status__iexact = UsableOutlet.USABLE,outlet_id=outlet_id))

                    if(is_usable_current):

                        #CELL Panel Profile
                        #--Filter Useable Outlets
                        queryListPPCellCurrent = queryListPPCell.filter(month = current_month_qs) \
                                                    .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                                            .filter(country = country, month = current_month_qs, status__iexact = UsableOutlet.USABLE))

                        # for i in range(0,len(queryListPPCellCurrent)):

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
                        #--- Only This Changed to individulal outlet rest remains same ---
                        # outlet_id = queryListPPCellCurrent[i].outlet.id
                        # outlet_code = queryListPPCellCurrent[i].outlet.code
                        agg_sum_sales_current = queryListPAAllCurrent \
                                                        .filter(outlet__id = outlet_id ) \
                                                        .aggregate(
                                                            sum_sales_unprojected_volume = Sum('sales_unprojected_volume'),
                                                            sum_sales_unprojected_value = Sum('sales_unprojected_value'),
                                                            sum_sales_projected_volume = Sum('sales_projected_volume'),
                                                            sum_sales_projected_value = Sum('sales_projected_value'),
                                                        )
                        #Numinators Values
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
                        #De-Numinators Values
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
                        'RBD_Name' : queryList[k].rbd.name,
                        'Cell_Name' : queryList[k].name,
                        'Cell_Code' : queryList[k].code,
                        'Cell_Description' : queryList[k].description,
                        'Active' : queryList[k].is_active,
                        'Condition' : re.sub(r'\n', '', filter_human),

                        'N_Numeric_Universe' : dropzeros(N_Numeric_Universe),
                        'W_Universe' : dropzeros(W_Universe),

                        'outlet_code':outlet_code,
                        'total_outlets_in_audit_previous' : dropzeros(total_outlets_in_audit_previous),
                        'w_Panel_Previous' : dropzeros(turnover_sum_cell_previous),
                        'n_Panel_Previous' : dropzeros(total_outlets_in_cell_previous),

                        'N_Factor_Previous' : "{:,.6f}".format(N_Factor_Previous),  # N-factor = N_Universe/nPanel (it must be 1 or greater then 1)
                        'W_Factor_Previous' : "{:,.6f}".format(W_Factor_Previous),  # W-factor = W_Universe/wPanel (it must be 1 or greater then 1)

                        'Unprojected_Sales_Volume' : "{:,.6f}".format(sum_sales_unprojected_volume_previous/1000000),
                        'Unprojected_Sales_Value' : "{:,.6f}".format(sum_sales_unprojected_value_previous/1000000),
                        'projected_Sales_Volume' : "{:,.6f}".format(sum_sales_projected_volume_previous/1000000),
                        'projected_Sales_Value' : "{:,.6f}".format(sum_sales_projected_value_previous/1000000),

                        'Unprojected_Contribution_Volume' : "{:,.4f}".format(unprojected_contribution_volume_previous),
                        'Projected_Contribution_Volume' : "{:,.4f}".format(projected_contribution_volume_previous),
                        'Projected_Contribution_Value' : "{:,.4f}".format(projected_contribution_value_previous),

                        # -------------------------------------------

                        'total_outlets_in_audit_current' : total_outlets_in_audit_current,

                        'w_Panel_Current' : dropzeros(turnover_sum_cell_current),
                        'n_Panel_Current' : dropzeros(total_outlets_in_cell_current),

                        'N_Factor_Current' : "{:,.6f}".format(N_Factor_Current),  # N-factor = N_Universe/nPanel (it must be 1 or greater then 1)
                        'W_Factor_Current' : "{:,.6f}".format(W_Factor_Current),  # W-factor = W_Universe/wPanel (it must be 1 or greater then 1)

                        'Unprojected_Sales_Volume_Current' : "{:,.6f}".format(sum_sales_unprojected_volume_current/1000000),
                        'Unprojected_Sales_Value_Current' : "{:,.6f}".format(sum_sales_unprojected_value_current/1000000),
                        'projected_Sales_Current' : "{:,.6f}".format(sum_sales_projected_volume_current/1000000),
                        'projected_Sales_Value_Current' :  "{:,.6f}".format(sum_sales_projected_value_current/1000000),

                        'Unprojected_Contribution_Volume_Current' : "{:,.4f}".format(unprojected_contribution_volume_current),
                        'Projected_Contribution_Volume_Current' : "{:,.4f}".format(projected_contribution_volume_current),
                        'Projected_Contribution_Value_Current' : "{:,.4f}".format(projected_contribution_value_current),

                    }

                    # cdebug(temp_dic)
                    response_dict.append( temp_dic )

            sourceFile = open('debug.txt', 'w')
            print(temp_dic, file = sourceFile)
            sourceFile.close()

            return_dic['results'] = response_dict
            # response_dict['queryList_json'] = queryList_json

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",str(e),', File: ',exc_type, fname,', Line: ',exc_tb.tb_lineno, Colors.WHITE)

        # Prepare response

        if export is not False:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=cell_shop_inspection.csv'
            csv_writer = csv.writer(response)
            count = 0
            for d in return_dic['results']:
                if count == 0:
                    header = d.keys()
                    csv_writer.writerow(header)
                    count += 1
                csv_writer.writerow(d.values())

            return response
        else:
            return HttpResponse(
                json.dumps(
                    return_dic,
                    cls=DjangoJSONEncoder
                ),
                content_type="application/json")

class CellShopInspectionListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "reports/cell_shop_inspection.html"
    PAGE_TITLE = "Cell and Shop Inspection"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }


""" ------------------------- Client Reporting ------------------------- """

class ClientReportingView(LoginRequiredMixin, generic.TemplateView):
    model = Census
    template_name = "reports/client_reporting.html"
    PAGE_TITLE = "Client Reporting"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_queryset(self):
        queryset = Upload.objects.filter(
            country__code=self.kwargs['country_code']
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ClientReportingView, self).get_context_data(**kwargs)
        censusupload = ''
        # censusupload = Upload.objects.filter(
        #     country__code=self.kwargs['country_code'], frommodel='census'
        # ).last()
        # if(censusupload is not None and  censusupload.is_processing != Upload.COMPLETED):
        #     messages.add_message(self.request, messages.SUCCESS, censusupload.is_processing +' : '+ censusupload.process_message)


        context.update({
            "censusupload": censusupload,
        })
        return context


class SampleMaintenanceViewAjax(AjaxDatatableView):
    model = PanelProfile
    initial_order = [["month", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'

    def get_column_defs(self, request):
        """
        Override to customize based of request
        """
        self.column_defs = [
            AjaxDatatableView.render_row_tools_column_def(),
            {'name': 'id','title':'ID', 'visible': True, },

            {'name': 'month_code', 'foreign_field': 'month__code', 'choices': True,'autofilter': True,},
            {'name': 'month', 'foreign_field': 'month__name', 'choices': True,'autofilter': True,},
            {'name': 'year', 'foreign_field': 'month__year', 'choices': True,'autofilter': True,},
            {'name': 'copy', 'title': 'Copy From', 'placeholder': True, 'searchable': False, 'orderable': False, },
            {'name': 'outlet_code','title': 'Copy To - Missing Outlet', 'foreign_field': 'outlet__code','width':'50', },
            {'name': 'outlet_id', 'foreign_field': 'outlet__id','visible': True, },
            {'name': 'estimate', 'title': 'Estimate', 'placeholder': True, 'searchable': False, 'orderable': False, },



        ]

        # self.column_defs.append({'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, })
        return self.column_defs

    def customize_row(self, row, obj):
            country = Country.objects.get(code=self.kwargs["country_code"])
            audit_date_qs = PanelProfile.objects.all().filter(country = country).values('month__date').annotate(current_month=Max('audit_date')).order_by('-month__date')[0:2]

            date_arr = []
            date_arr_obj = []
            for instance in audit_date_qs:
                date_arr.append(instance['month__date'])

            if(len(date_arr)==2):
                month_1 , month_2 = date_arr
                month_1_qs = Month.objects.get(date=month_1)
                month_2_qs = Month.objects.get(date=month_2)
                date_arr_obj.append(month_1_qs)
                date_arr_obj.append(month_2_qs)
            else:
                cdebug('1-Month data')
                return HttpResponse(json.dumps({'msg','Please load minimum 2 month data.'},cls=DjangoJSONEncoder),content_type="application/json")


            # curr_month = PanelProfile.objects.all().filter(country = country,month = date_arr_obj[0]) \
            #     .values_list('outlet__code', flat=True)

            prv_month = PanelProfile.objects.all().filter(country = country,month = date_arr_obj[1]) \
                .values_list('outlet__id','outlet__code')

            outlet_to = row['outlet_id']
            data_row = obj.id

            # cdebug(prv_month)
            prv_select_html = ''
            for p in prv_month:
                prv_select_html += '<option value="'+str(p[0])+'">'+str(p[1])+'</option>'

            row['copy'] = ('<select class="select2" id="outlet_from_'+str(data_row)+'">%s</select>') % (
                    prv_select_html,
                )
            row['estimate'] = '<a href="javascript:void(0);" title="Estimate" class="btn btn-info estimate_from" data_row="'+str(data_row)+'" month_from="'+str(row['month_code'])+'" outlet_to="'+str(outlet_to)+'">Estimate</a>'
            row['outlet_code'] = row['outlet_code']+'&nbsp;'+'<a href="javascript:void(0);" title="Copy" class="btn btn-info copy_to" data_row="'+str(data_row)+'" month_from="'+str(row['month_code'])+'" outlet_to="'+str(outlet_to)+'">Copy</a>'


    # model._meta.fields
    def get_initial_queryset(self, request=None):
        # queryset = self.model.objects.filter(
        #     country__code=self.kwargs['country_code']
        # )
        # return queryset
        queryList = super().get_initial_queryset(request=request)

        country = Country.objects.get(code=self.kwargs["country_code"])


        audit_date_qs = PanelProfile.objects.all().filter(country = country).values('month__date').annotate(current_month=Max('audit_date')).order_by('-month__date')[0:2]
        # prettyprint_queryset(audit_date_qs)

        date_arr = []
        date_arr_obj = []
        for instance in audit_date_qs:
            date_arr.append(instance['month__date'])

        if(len(date_arr)==2):
            month_1 , month_2 = date_arr
            month_1_qs = Month.objects.get(date=month_1)
            month_2_qs = Month.objects.get(date=month_2)
            date_arr_obj.append(month_1_qs)
            date_arr_obj.append(month_2_qs)
            # cdebug('2-Month data')
        else:
            cdebug('1-Month data')
            return HttpResponse(json.dumps({'msg','Please load minimum 2 month data.'},cls=DjangoJSONEncoder),content_type="application/json")
        # cdebug(date_arr_obj)

        curr_month = queryList.filter(month = date_arr_obj[0]).values_list('outlet_id', flat=True)
        # prv_month = queryList.filter(month = date_arr_obj[1]).values_list('outlet_id', flat=True)

        queryList = queryList.filter(month = date_arr_obj[1]).exclude(outlet_id__in = curr_month)


        # print(lost_outlets)


        return queryList

class SampleMaintenanceView(LoginRequiredMixin, generic.TemplateView):
    template_name = "reports/sample_maintenance.html"
    PAGE_TITLE = "Sample Maintenance"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        return context


class SampleMaintenanceCopyViewAjax(LoginRequiredMixin, generic.CreateView):
    def post(self, request, country_code):
        country = Country.objects.get(code=self.kwargs["country_code"])
        outlet_from = self.request.POST.get("outlet_from")
        outlet_to = self.request.POST.get("outlet_to")
        month_from = self.request.POST.get("month_from")

        audit_date_qs = PanelProfile.objects.all().filter(country = country).values('month__date').annotate(current_month=Max('audit_date')).order_by('-month__date')[0:2]

        date_arr = []
        date_arr_obj = []
        for instance in audit_date_qs:
            date_arr.append(instance['month__date'])

        if(len(date_arr)==2):
            month_1 , month_2 = date_arr
            month_1_qs = Month.objects.get(date=month_1)
            month_2_qs = Month.objects.get(date=month_2)
            date_arr_obj.append(month_1_qs)
            date_arr_obj.append(month_2_qs)
        else:
            cdebug('1-Month data')
            return HttpResponse(json.dumps({'msg','Please load minimum 2 month data.'},cls=DjangoJSONEncoder),content_type="application/json")


        cdebug(outlet_from)
        cdebug(outlet_to)
        cdebug(month_from)


        # cdebug(obj.audit_date)
        # cdebug(obj.audit_date+timedelta(days=30))

        obj = PanelProfile.objects.get(outlet__id=outlet_from,month__code=month_from)
        obj.pk = None # New Copy
        obj.outlet_id  = outlet_to
        obj.audit_status  = PanelProfile.COPIED
        obj.audit_date = obj.audit_date+timedelta(days=30)
        obj.month = date_arr_obj[0]
        obj.save()

        objs = ProductAudit.objects.filter(outlet__id=outlet_from, month__code=month_from)
        for obj in objs:
            obj.pk = None # New Copy
            obj.outlet_id  = outlet_to
            obj.audit_status  = ProductAudit.COPIED
            obj.audit_date = obj.audit_date+timedelta(days=30)
            obj.month = date_arr_obj[0]
            obj.save()

        # obj = UsableOutlet.objects.get(pk=id,country=country)
        # obj.status  = value
        # obj.save()


        # pp = PanelProfile.objects.filter(month__code='30')
        # for r in pp:
        #     r.audit_date = datetime(2021, 6, 1)
        #     r.save()
        # pp = PanelProfile.objects.filter(month__code='31')
        # for r in pp:
        #     r.audit_date = datetime(2021, 7, 1)
        #     r.save()
        # pp = PanelProfile.objects.filter(month__code='32')
        # for r in pp:
        #     r.audit_date = datetime(2021, 8, 1)
        #     r.save()

        # pp = ProductAudit.objects.filter(month__code='30')
        # for r in pp:
        #     r.audit_date = datetime(2021, 6, 1)
        #     r.save()
        # pp = ProductAudit.objects.filter(month__code='31')
        # for r in pp:
        #     r.audit_date = datetime(2021, 7, 1)
        #     r.save()
        # pp = ProductAudit.objects.filter(month__code='32')
        # for r in pp:
        #     r.audit_date = datetime(2021, 8, 1)
        #     r.save()

        # cdebug(obj.id,'new_id')

        return HttpResponse(
            json.dumps(
                {'data':'success'},
                cls=DjangoJSONEncoder
            ),
            content_type="application/json")

class SampleMaintenanceEstimateViewAjax(LoginRequiredMixin, generic.CreateView):
    def post(self, request, country_code):
        country = Country.objects.get(code=self.kwargs["country_code"])
        outlet_from = self.request.POST.get("outlet_from")
        outlet_to = self.request.POST.get("outlet_to")
        month_from = self.request.POST.get("month_from")

        audit_date_qs = PanelProfile.objects.all().filter(country = country).values('month__date').annotate(current_month=Max('audit_date')).order_by('-month__date')[0:2]

        date_arr = []
        date_arr_obj = []
        for instance in audit_date_qs:
            date_arr.append(instance['month__date'])

        if(len(date_arr)==2):
            month_1 , month_2 = date_arr
            month_1_qs = Month.objects.get(date=month_1)
            month_2_qs = Month.objects.get(date=month_2)
            date_arr_obj.append(month_1_qs)
            date_arr_obj.append(month_2_qs)
        else:
            cdebug('1-Month data')
            return HttpResponse(json.dumps({'msg','Please load minimum 2 month data.'},cls=DjangoJSONEncoder),content_type="application/json")


        cdebug(outlet_from)
        cdebug(outlet_to)
        cdebug(month_from)


        obj = PanelProfile.objects.get(outlet__id=outlet_from,month__code=month_from)
        obj.pk = None # New Copy
        obj.outlet_id  = outlet_to
        obj.audit_status  = PanelProfile.ESTIMATED
        obj.audit_date = obj.audit_date+timedelta(days=30)
        obj.month = date_arr_obj[0]
        obj.save()

        objs = ProductAudit.objects.filter(outlet__id=outlet_from, month__code=month_from)
        for obj in objs:
            obj.pk = None # New Copy
            obj.outlet_id  = outlet_to
            obj.audit_status  = ProductAudit.ESTIMATED
            obj.audit_date = obj.audit_date+timedelta(days=30)
            obj.month = date_arr_obj[0]
            obj.save()

        return HttpResponse(
            json.dumps(
                {'data':'success'},
                cls=DjangoJSONEncoder
            ),
            content_type="application/json")


def getRBDs(request):
    # get all the countreis from the database excluding
    # null and blank values
    # from django.db.models import get_model
    # model = get_model('myapp', 'modelA')
    # model.objects.filter(**kwargs)

    if request.method == "GET" and request.is_ajax():
        objects = RBD.objects.order_by('name').values_list('name','code').distinct()
        objects = [i[0] for i in list(objects)]
        data = {
            "objects": objects,
        }
        return JsonResponse(data, status = 200)

