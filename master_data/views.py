from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *
import base64


from termcolor import cprint
import traceback
import time, os,sys, signal,logging,json
from sys import stdout, stdin, stderr
from pprint import pprint
from var_dump import var_dump,var_export
from subprocess import Popen
from inspect import getmembers
from csv import DictReader
from urllib.parse import parse_qs,urlparse
from itertools import chain
from collections import OrderedDict

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import models
from django.db.models import Q, Avg, Count, Min,Max, Sum
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse,reverse_lazy
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.http import (HttpResponseRedirect,HttpResponse,JsonResponse)
from django.views import generic
from rest_framework.generics import ListAPIView

from core.utils import prettyprint_queryset, trace, format_datetime,cdebug

from core.pagination import StandardResultsSetPagination
from core.mixinsViews import PassRequestToFormViewMixin
from core.helpers import *
from core.colors import Colors
from master_setups.models import *
from master_data.models import *
from master_data.forms import *

from master_data.serializers import PanelProfileSerializers
from ajax_datatable.views import AjaxDatatableView
from django_datatables_view.base_datatable_view import BaseDatatableView

logger = logging.getLogger(__name__)

def census_list_ajax(request,*args, **kwargs):

    if request.method == 'GET':

        queryset = Census.objects.filter(
            country__id = self.request.session['country_id']
        ).values_list('censusdata',flat=True)
        data = []
        # queryset = Census.objects.values_list('censusdata',flat=True)[:10]
        for col in queryset:

            data.append(json.loads(col, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()}))

    return JsonResponse ({"data": data}, status = 200)

def census_list(request):
    return render(request, 'master_data/cencus_pivot.html')



class CensusUploadView(LoginRequiredMixin, generic.CreateView):
    template_name = "master_data/census_upload.html"
    form_class = UploadModalForm
    PAGE_TITLE = "Census Import"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, **kwargs):

        context = super(CensusUploadView, self).get_context_data(**kwargs)
        # queryset = Upload.objects.filter(country__id=self.request.session['country_id'])
        return context

    def form_valid(self, form):

        form_obj = form.save(commit=False)
        form_obj.is_processing = Upload.PROCESSING
        form_obj.process_message = Upload.PROCESSING_MSG
        form_obj.country_id = self.request.session['country_id']
        form_obj.index_id = self.request.session['index_id']
        form_obj.frommodel = "census"
        form_obj.save()

        print(Colors.BLUE,form_obj.pk)
        proc = Popen('python manage.py import_census '+str(form_obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, Upload.UPLOADING_MSG)
        return reverse("master-data:census-list", kwargs={"country_code": self.kwargs["country_code"]})


class CensusListView(LoginRequiredMixin, generic.TemplateView):
    model = Census
    template_name = "master_data/census_list.html"
    PAGE_TITLE = "Census List"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_queryset(self):
        queryset = Upload.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CensusListView, self).get_context_data(**kwargs)
        censusupload = Upload.objects.filter(
            country__id=self.request.session['country_id'], frommodel='census'
        ).last()

        uploadStatusMessage(self,self.request.session['country_id'],'census')

        context.update({
            "censusupload": censusupload,
        })
        return context


class CensusDetailView(LoginRequiredMixin,generic.DetailView):
    model = Census
    template_name = "master_data/census_detail.html"

class CensusUpdateView(LoginRequiredMixin,generic.UpdateView):
    model = Census
    form_class = CensusForm
    template_name = "master_data/census_detail.html"


class CensusDeleteView(LoginRequiredMixin,generic.DeleteView):
    model = Census
    template_name = "master_data/census_delete.html"
    success_url = reverse_lazy('master-data:census-list')


class CensusImportView(LoginRequiredMixin, generic.TemplateView):
    template_name = "master_data/census_import.html"


def handle_uploaded_file(f):
    with open(f.name, 'r') as read_obj:
        csv_reader = DictReader(read_obj)
        for row in csv_reader:
            print(row)
            exit()



# @login_required(login_url='/dashboard-login/')
def import_census(request):
    if request.method == 'POST':
        form = UploadCensusForm(request.POST, request.FILES)
        if form.is_valid():
            return redirect('master-data:census-import')
    else:
        form = UploadCensusForm()
    return render(request, 'master_data/census_import.html', {
        'form': form
    })
    return HttpResponseRedirect(reverse('master-data:census-import'))



""" ------------------------- Category ------------------------- """

class CategoryImportView(LoginRequiredMixin, generic.CreateView):
    template_name = "master_data/category_import.html"
    PAGE_TITLE = "Import Categories"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    form_class = UploadModalForm

    def get_context_data(self, **kwargs):
        context = super(CategoryImportView, self).get_context_data(**kwargs)
        # queryset = Upload.objects.filter(country__id=self.request.session['country_id'])
        return context

    def form_valid(self, form):

        form_obj = form.save(commit=False)
        form_obj.is_processing = Upload.PROCESSING
        form_obj.process_message = Upload.PROCESSING_MSG
        form_obj.country_id = self.request.session['country_id']
        form_obj.index_id = self.request.session['index_id']
        form_obj.frommodel = "category"
        form_obj.save()

        print(Colors.BLUE,form_obj.pk)
        proc = Popen('python manage.py import_category '+str(form_obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        # management.call_command('import_census',self.kwargs["country_code"])
        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):
        # return reverse("leads:lead-detail", kwargs={"pk": self.kwargs["pk"]})
        messages.add_message(self.request, messages.INFO, Upload.UPLOADING_MSG)
        return reverse("master-data:category-list", kwargs={"country_code": self.request.session['country_id']})

class CategoryListViewAjax(AjaxDatatableView):
    model = Category
    title = 'Categories'
    initial_order = [["code", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'


    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id','title':'ID', 'visible': True, },
        {'name': 'code',  },
        {'name': 'name',  },
        {'name': 'parent', 'foreign_field': 'parent__name',   'choices': True, 'autofilter': True,},
        {'name': 'is_active',  'choices': True, 'autofilter': True,},
        {'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
            row['action'] = ('<a href="%s" title="Edit" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'+
                             '<a href="%s" title="Delete" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                    reverse('master-data:category-update', args=(self.kwargs['country_code'],obj.id,)),
                    reverse('master-data:category-delete', args=(self.kwargs['country_code'],obj.id,)),
                )
                # <a href="{1}" title="Delete" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>


    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset

class CategoryListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "master_data/category_list.html"
    PAGE_TITLE = "Categories"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        uploadStatusMessage(self,self.request.session['country_id'],'category')
        return context

class CategoryCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "master_data/category_create.html"
    form_class = CategoryModelForm
    PAGE_TITLE = "Create Category"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record saved successfully.")
        return reverse("master-data:category-list", kwargs={"country_code": self.request.session['country_id']})

    def form_valid(self, form):

        form_obj = form.save(commit=False)
        form_obj.country_id = self.request.session['country_id']
        form_obj.save()
        return super(self.__class__, self).form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "master_data/category_update.html"
    form_class = CategoryModelForm
    PAGE_TITLE = "Update Category"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_queryset(self):
        queryset = Category.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record updated successfully.")
        return reverse("master-data:category-list", kwargs={"country_code": self.request.session['country_id']})

    def form_valid(self, form):
        form.save()
        return super(self.__class__, self).form_valid(form)

class CategoryDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "master_data/category_delete.html"
    PAGE_TITLE = "Delete Category"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, "Record deleted successfully.")
        return reverse("master-data:category-list", kwargs={"country_code": self.request.session['country_id']})

    def get_queryset(self):
        queryset = Category.objects.filter(
            country__id=self.request.session['country_id'],
            pk=self.kwargs['pk']
        )
        return queryset



""" ------------------------- Panel Profile ------------------------- """

class PanelProfileListViewAjax(AjaxDatatableView):
    model = PanelProfile
    title = 'PanelProfile'
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
            {'name':'audit_status','choices': True, 'autofilter': True,},
            {'name': 'month code', 'foreign_field': 'month__code', 'choices': True,'autofilter': True,},
            {'name': 'month', 'foreign_field': 'month__name', 'choices': True,'autofilter': True,},
            {'name': 'year', 'foreign_field': 'month__year', 'choices': True,'autofilter': True,},

            {'name': 'Index Code', 'foreign_field': 'index__code', },
            {'name': 'Index Name', 'foreign_field': 'index__name', 'choices': True, 'autofilter': True,},

            # {'name': 'Category Code', 'foreign_field': 'category__code', },
            # {'name': 'Category Name', 'foreign_field': 'category__name','choices': True, 'autofilter': True, },
            {'name': 'Outlet Id', 'foreign_field': 'outlet__id', },
            {'name': 'Outlet Code', 'foreign_field': 'outlet__code', },

            {'name': 'Outlet Type Code', 'foreign_field': 'outlet_type__code', },
            {'name': 'Outlet Type Name', 'foreign_field': 'outlet_type__name', 'choices': True, 'autofilter': True,},

            {'name': 'Outlet Status Code', 'foreign_field': 'outlet_status__code', },
            {'name': 'Outlet Status Name', 'foreign_field': 'outlet_status__name', 'choices': True, 'autofilter': True,},

            {'name': 'Province Code', 'foreign_field': 'city_village__tehsil__district__province__code', },
            {'name': 'Province Name', 'foreign_field': 'city_village__tehsil__district__province__name', 'choices': True, 'autofilter': True,},
            {'name': 'District Code', 'foreign_field': 'city_village__tehsil__district__code',},
            {'name': 'District Name', 'foreign_field': 'city_village__tehsil__district__name', 'choices': True, 'autofilter': True,},

            {'name': 'Tehsil Code', 'foreign_field': 'city_village__tehsil__code',},
            {'name': 'Tehsil Name', 'foreign_field': 'city_village__tehsil__name', 'choices': True, 'autofilter': True,},
            {'name': 'Tehsil Urbanity', 'foreign_field': 'city_village__tehsil__urbanity', 'choices': True, 'autofilter': True,},

            {'name': 'City Code', 'foreign_field': 'city_village__code', },
            {'name': 'City Name', 'foreign_field': 'city_village__name',},
            {'name':'lms', 'choices': True, 'autofilter': True,},
            {'name':'cell_description',},
            {'name':'nra_tagging',},
            {'name':'ra_tagging',},
            {'name':'ret_tagging',},
            {'name':'audit_date',},
            {'name':'acv'},

        ]

        # ('index', 'category', 'hand_nhand', 'region', 'city_village', 'outlet', 'outlet_type', 'outlet_status', , )
        skip_cols = ['id','pk','code','name','country','upload','created','updated',]
        for field in CityVillage._meta.get_fields():
            if isinstance(field, models.ForeignKey): continue
            if isinstance(field, models.ManyToManyRel): continue
            if isinstance(field, models.ManyToOneRel): continue

            if(field.name not in skip_cols):
                try:
                    col_label = ColLabel.objects.get(
                        country__code = self.kwargs['country_code'],
                        model_name = ColLabel.CityVillage,
                        col_name = field.name
                    )
                except ColLabel.DoesNotExist:
                    col_label = None

                title = col_label.col_label if col_label else field.name
                title = title if title != '' else field.name
                self.column_defs.append({'name': field.name,'title':title, 'foreign_field': 'city_village__'+field.name, 'choices': True, 'autofilter': True, })

        self.column_defs.append({'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, })
        return self.column_defs

    def customize_row(self, row, obj):

            row['action'] = ('<a href="%s" title="Delete" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                    reverse('master-data:panel-profile-delete', args=(self.kwargs['country_code'],obj.id)),
                )

    # model._meta.fields
    def get_initial_queryset(self, request=None):
        queryset = self.model.objects.filter(
            country__id=self.request.session['country_id'],
            index__id=self.request.session['index_id']
        )
        return queryset

class PanelProfileListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "master_data/panel_profile_list.html"
    PAGE_TITLE = "Panel Profile"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        uploadStatusMessage(self,self.request.session['country_id'],'panel_profile')

        return context

class PanelProfileUpdateView(LoginRequiredMixin, generic.CreateView):
    template_name = "generic_import.html"
    PAGE_TITLE = "Update Panel Profile"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }
    form_class = UploadFormUpdate

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):


        form_obj = form.save(commit=False)
        form_obj.is_processing = Upload.PROCESSING
        form_obj.process_message = Upload.PROCESSING_MSG
        form_obj.country_id = self.request.session['country_id']
        form_obj.index_id = self.request.session['index_id']
        form_obj.frommodel = "panel_profile_update"
        form_obj.save()

        print(Colors.BLUE,form_obj.pk)
        proc = Popen('python manage.py import_panel_profile_update '+str(form_obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):

        messages.add_message(self.request, messages.INFO, Upload.UPLOADING_MSG)
        return reverse("master-data:panel-profile-list", kwargs={"country_code": self.kwargs["country_code"]})


class PanelProfileImportView(LoginRequiredMixin, generic.CreateView):
    template_name = "generic_import.html"
    PAGE_TITLE = "Import Panel Profile"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    form_class = UploadModalForm

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):

        form_obj = form.save(commit=False)
        form_obj.is_processing = Upload.PROCESSING
        form_obj.process_message = Upload.PROCESSING_MSG
        form_obj.country_id = self.request.session['country_id']
        form_obj.index_id = self.request.session['index_id']
        form_obj.frommodel = "panel_profile"
        form_obj.save()

        print(Colors.BLUE,form_obj.pk)
        proc = Popen('python manage.py import_panel_profile '+str(form_obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):

        messages.add_message(self.request, messages.INFO, Upload.UPLOADING_MSG)
        return reverse("master-data:panel-profile-list", kwargs={"country_code": self.kwargs["country_code"]})


class PanelProfileDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "generic_delete.html"
    PAGE_TITLE = "Delete PanelProfile and Related Data"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, "Record deleted successfully.")
        return reverse("master-data:panel-profile-list", kwargs={"country_code": self.kwargs["country_code"]})

    def get_queryset(self):
        country = Country.objects.get(code=self.kwargs["country_code"])
        pp =  PanelProfile.objects.get(id=self.kwargs['pk'])
        month_id = pp.month_id
        outlet_id = pp.outlet_id
        cdebug(outlet_id)
        AuditData.objects.filter(country=country,outlet__id = outlet_id, month__id = month_id).delete()

        queryset =  PanelProfile.objects.filter(
            country__id=self.request.session['country_id'],
            pk=self.kwargs['pk'],
        )
        return queryset

class PanelProfileListViewAjax2(AjaxDatatableView):
    model = PanelProfile
    title = 'PanelProfile'
    initial_order = [["month", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'

    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id','title':'ID', 'visible': True, },
        {'name': 'month', 'foreign_field': 'month__code', 'choices': True,'autofilter': True,},
        {'name': 'outlet','title':'Outlet Code',  'foreign_field': 'outlet__code',},
        {'name': 'outlet_type',  'foreign_field': 'outlet_type__code', 'choices': True, 'autofilter': True,},
        {'name': 'outlet_status',  'choices': True,'autofilter': True,},
        {'name': 'index', 'foreign_field': 'index__name',  'choices': True, 'autofilter': True, 'width':'50',},
        {'name': 'hand_nhand',  'choices': True,'autofilter': True,},
        {'name': 'region',  'choices': True,'autofilter': True,},
        {'name': 'audit_date', },
        {'name': 'wtd_factor', },
        {'name': 'num_factor',  },

        ]
    for v in model._meta.get_fields():
        if('custom' in v.name):
            column_defs.append({'name':v.name})

    def post(self, request, *args, **kwargs):
        print(request)
        return self.get(request, *args, **kwargs)

    # model._meta.fields
    def get_initial_queryset(self, request=None):
        queryset = self.model.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset


""" ------------------------- Usable Outlet ------------------------- """

class UsableOutletImportView(LoginRequiredMixin, generic.CreateView):
    template_name = "generic_import.html"
    PAGE_TITLE = "Import Usable Outlet"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    form_class = UploadModalForm

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):

        form_obj = form.save(commit=False)
        form_obj.is_processing = Upload.PROCESSING
        form_obj.process_message = Upload.PROCESSING_MSG
        form_obj.country_id = self.request.session['country_id']
        form_obj.index_id = self.request.session['index_id']
        form_obj.frommodel = "usable_outlet"
        form_obj.save()

        print(Colors.BLUE,form_obj.pk)
        proc = Popen('python manage.py import_usable_outlet '+str(form_obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):

        messages.add_message(self.request, messages.SUCCESS, "File uploaded successfully, processing records.")
        return reverse("master-data:usable-outlet-list", kwargs={"country_code": self.kwargs["country_code"]})



class UsableOutletListViewAjax(AjaxDatatableView):
    model = UsableOutlet
    title = 'Usable Outlet'
    initial_order = [["id", "asc"]]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'


    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id','title':'ID', 'visible': True, },
        {'name': 'month','title':'Month Code', 'foreign_field': 'month__code', 'choices': True,'autofilter': True,},
        {'name': 'name','title':'Month', 'foreign_field': 'month__name', 'choices': True,'autofilter': True,},
        {'name': 'year','title':'Year', 'foreign_field': 'month__year', 'choices': True,'autofilter': True,},
        {'name': 'cell', 'foreign_field': 'cell__name', },
        {'name': 'outlet','title':'Outlet Code',  'foreign_field': 'outlet__code',},
        {'name': 'status',  'choices': True, 'autofilter': True,},

        {'name': UsableOutlet.USABLE, 'title': 'Usable', 'placeholder': True, 'searchable': False, 'orderable': False, },
        {'name': UsableOutlet.NOTUSABLE, 'title': 'Not Usable', 'placeholder': True, 'searchable': False, 'orderable': False, },
        {'name': UsableOutlet.DROP, 'title': 'Drop', 'placeholder': True, 'searchable': False, 'orderable': False, },
        {'name': UsableOutlet.QUARANTINE, 'title': 'Quarantine', 'placeholder': True, 'searchable': False, 'orderable': False, },
        {'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):

            row[UsableOutlet.USABLE] = '<input class="status" type="radio" name="'+str(obj.id)+'" value="'+UsableOutlet.USABLE+'" '+("checked" if obj.status==UsableOutlet.USABLE else "")+'  >'
            row[UsableOutlet.NOTUSABLE] = '<input class="status" type="radio" name="'+str(obj.id)+'" value="'+UsableOutlet.NOTUSABLE+'" '+("checked" if obj.status==UsableOutlet.NOTUSABLE else "")+'  >'
            row[UsableOutlet.DROP] = '<input class="status" type="radio" name="'+str(obj.id)+'" value="'+UsableOutlet.DROP+'" '+("checked" if obj.status==UsableOutlet.DROP else "")+'  >'
            row[UsableOutlet.QUARANTINE] = '<input class="status" type="radio" name="'+str(obj.id)+'" value="'+UsableOutlet.QUARANTINE+'" '+("checked" if obj.status==UsableOutlet.QUARANTINE else "")+'  >'

            row['action'] = ('<a href="%s" title="Edit" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'+
                             '<a href="%s" title="Delete" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                    reverse('master-data:usable-outlet-update', args=(self.kwargs['country_code'],obj.id,)),
                    reverse('master-data:usable-outlet-delete', args=(self.kwargs['country_code'],obj.id,)),
                )


    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__id=self.request.session['country_id'],
            index__id=self.request.session['index_id']
        )
        return queryset

class UsableOutletListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "master_data/usable_outlet_list.html"
    PAGE_TITLE = "Usable Outlet"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        uploadStatusMessage(self,self.request.session['country_id'],'usable_outlet')
        return context

class UsableOutletStatus(LoginRequiredMixin, generic.CreateView):
    def post(self, request, country_code):
        country = Country.objects.get(code=self.kwargs["country_code"])
        id = self.request.POST.get("id")
        value = self.request.POST.get("value")

        obj = UsableOutlet.objects.get(pk=id,country=country)
        obj.status  = value
        obj.save()

        return HttpResponse(
            json.dumps(
                {'data':'success'},
                cls=DjangoJSONEncoder
            ),
            content_type="application/json")


def usableoutletstatus(request):
    if request.method == 'POST':
        # post_id = request.GET['post_id']
        # likedpost = Post.objects.get(id = post_id )
        # m = Like( post=likedpost )
        # m.save()
        return HttpResponse('success')

class UsableOutletCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "generic_create.html"
    form_class = UsableOutletModelForm
    PAGE_TITLE = "Create Usable Outlet"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record saved successfully.")
        return reverse("master-data:usable-outlet-list", kwargs={"country_code": self.kwargs["country_code"]})

    def form_valid(self, form):

        form_obj = form.save(commit=False)
        form_obj.country_id = self.request.session['country_id']
        form_obj.save()
        return super(self.__class__, self).form_valid(form)

class UsableOutletUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "generic_update.html"
    form_class = UsableOutletModelForm
    PAGE_TITLE = "Update Usable Outlet"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_queryset(self):
        queryset = UsableOutlet.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record updated successfully.")
        return reverse("master-data:usable-outlet-list", kwargs={"country_code": self.kwargs["country_code"]})

    def form_valid(self, form):
        form.save()
        return super(self.__class__, self).form_valid(form)


class UsableOutletDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "generic_delete.html"
    PAGE_TITLE = "Delete UsableOutlet"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, "Record deleted successfully.")
        return reverse("master-data:usable-outlet-list", kwargs={"country_code": self.kwargs["country_code"]})

    def get_queryset(self):
        queryset = UsableOutlet.objects.filter(
            country__id=self.request.session['country_id'],
            pk=self.kwargs['pk']
        )
        return queryset

""" ------------------------- Outlets ------------------------- """


class OutletListViewAjax(AjaxDatatableView):
    model = Outlet
    initial_order = [["code", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'

    def get_column_defs(self, request):
        """
        Override to customize based of request
        """

        self.column_defs = [
            AjaxDatatableView.render_row_tools_column_def(),
            {'name': 'id','title':'ID', 'visible': True, },
            {'name': 'code',  },
            {'name': 'insert_date'},
        ]

        return self.column_defs

    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset

class OutletListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "master_data/outlet_list.html"
    PAGE_TITLE = "Outlets"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }
    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)

        return context

""" ------------------------- Product ------------------------- """

class ProductImportView(LoginRequiredMixin, generic.CreateView):
    template_name = "generic_import.html"
    PAGE_TITLE = "Import Product"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    form_class = UploadModalForm

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):

        form_obj = form.save(commit=False)
        form_obj.is_processing = Upload.PROCESSING
        form_obj.process_message = Upload.PROCESSING_MSG
        form_obj.country_id = self.request.session['country_id']
        form_obj.index_id = self.request.session['index_id']
        form_obj.frommodel = "product"
        form_obj.save()

        print(Colors.BLUE,form_obj.pk)
        proc = Popen('python manage.py import_product '+str(form_obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):

        messages.add_message(self.request, messages.SUCCESS, "File uploaded successfully, processing records.")
        return reverse("master-data:product-list", kwargs={"country_code": self.kwargs["country_code"]})

class ProductListViewAjax(AjaxDatatableView):
    model = Product
    initial_order = [["code", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'


    def get_column_defs(self, request):
        """
        Override to customize based of request
        """

        self.column_defs = [
            AjaxDatatableView.render_row_tools_column_def(),
            {'name': 'id','title':'ID', 'visible': True, },
            {'name': 'code','title':'Product Code'},
            {'name': 'Category Code','foreign_field': 'category__code', },
            {'name': 'Category Name','foreign_field': 'category__name', 'choices': True, 'autofilter': True,},
        ]
        # ('barcode', 'sku', 'brand', 'variant', 'size', 'packaging', 'weight', 'origin', 'country', 'manufacture', 'price_segment', 'super_manufacture', 'super_brand', 'weight', 'number_in_pack', 'price_per_unit', )

        skip_cols = ['id','pk','code','name','created','updated',]

        for field in Product._meta.get_fields():
            if(field.name in skip_cols): continue
            if isinstance(field, models.ForeignKey): continue
            if isinstance(field, models.ManyToManyRel): continue
            if isinstance(field, models.ManyToOneRel): continue
            try:
                col_label = ColLabel.objects.get(
                    country_id = self.request.session['country_id'],
                    model_name = ColLabel.Product,
                    col_name = field.name
                )
            except ColLabel.DoesNotExist:
                col_label = None

            title = col_label.col_label if col_label else field.name
            title = title if title != '' else field.name
            self.column_defs.append({'name': field.name,'title':title, })

        return self.column_defs

    def get_initial_queryset(self, request=None):
        country_id = self.request.session['country_id']
        index_id = self.request.session['index_id']

        index_category = IndexCategory.objects.filter(country__id = country_id, index__id = index_id)
        index_category = index_category[0].get_index_category_ids()

        queryset = self.model.objects.filter(
            country__id = country_id,
            category__id__in = index_category
        )

        return queryset

class ProductListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "master_data/product_list.html"
    PAGE_TITLE = "Product"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }
    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        uploadStatusMessage(self,self.request.session['country_id'],'product')
        return context

""" ------------------------- Audit Data ------------------------- """

class AuditDataImportView(LoginRequiredMixin, generic.CreateView):
    template_name = "generic_import.html"
    PAGE_TITLE = "Import Audit Data"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    form_class = UploadModalForm

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):

        form_obj = form.save(commit=False)
        form_obj.is_processing = Upload.PROCESSING
        form_obj.process_message = Upload.PROCESSING_MSG
        form_obj.country_id = self.request.session['country_id']
        form_obj.index_id = self.request.session['index_id']
        form_obj.frommodel = "audit_data"
        form_obj.save()

        print(Colors.BLUE,form_obj.pk)
        proc = Popen('python manage.py import_audit_data '+str(form_obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):

        messages.add_message(self.request, messages.SUCCESS, "File uploaded successfully, processing records.")
        return reverse("master-data:audit-data-list", kwargs={"country_code": self.kwargs["country_code"]})



class AuditDataListViewAjax(AjaxDatatableView):
    model = AuditData
    title = 'Audit Data'
    initial_order = [["month", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'

    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id','title':'ID', 'visible': True, },

        {'name': 'audit_status','choices': True, 'autofilter': True,},
        {'name': 'month code', 'foreign_field': 'month__code', 'choices': True,'autofilter': True,},
        {'name': 'month', 'foreign_field': 'month__name', 'choices': True,'autofilter': True,},
        {'name': 'year', 'foreign_field': 'month__year', 'choices': True,'autofilter': True,},

        {'name': 'Category Code', 'foreign_field': 'category__code', },
        {'name': 'Category Name', 'foreign_field': 'category__name','choices': True, 'autofilter': True, },
        {'name': 'Outlet Code', 'foreign_field': 'outlet__code', },

        # {'name': 'Outlet Type Code', 'foreign_field': 'outlet_type__code', },
        # {'name': 'Outlet Type Name', 'foreign_field': 'outlet_type__name', 'choices': True, 'autofilter': True,},

        # {'name': 'Outlet Status Code', 'foreign_field': 'outlet_status__code', },
        # {'name': 'Outlet Status Name', 'foreign_field': 'outlet_status__name', 'choices': True, 'autofilter': True,},


        # {'name': 'category', 'foreign_field': 'category__code', 'choices': True,'autofilter': True,},
        # {'name': 'outlet', 'foreign_field': 'outlet__code',},
        {'name': 'product','title':'Product Code', 'foreign_field': 'product__code',},

        ]

    skip_cols = ['id','pk','country','upload','created','updated',
                 'month', 'period', 'category', 'outlet', 'product','audit_status']

    for v in model._meta.get_fields():
        if(v.name not in skip_cols):
            column_defs.append({'name':v.name})


    def get_initial_queryset(self, request=None):

        country_id = self.request.session['country_id']
        index_id = self.request.session['index_id']

        index_category = IndexCategory.objects.filter(country__id = country_id, index__id = index_id)
        index_category = index_category[0].get_index_category_ids()

        queryset = self.model.objects.filter(
            country__id = country_id,
            category__id__in = index_category
        )

        return queryset


class AuditDataListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "master_data/audit_data_list.html"
    PAGE_TITLE = "Audit Data"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        uploadStatusMessage(self,self.request.session['country_id'],'audit_data')

        return context

""" ------------------------- RBD ------------------------- """


class RBDListViewAjax_backup(AjaxDatatableView):
    model = RBD
    title = 'RBD'
    initial_order = [["code", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'


    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id','title':'ID', 'visible': True, },
        {'name': 'code',  },
        {'name': 'name',  },
        {'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
            row['action'] = ('<a href="%s" title="Edit" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'+
                             '<a href="%s" title="Delete" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                    reverse('master-data:rbd-update', args=(self.kwargs['country_code'],obj.id,)),
                    reverse('master-data:rbd-delete', args=(self.kwargs['country_code'],obj.id,)),
                )
                # <a href="{1}" title="Delete" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>


    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset

#Used in RBD Create View
class PanelProfileRBDListing(ListAPIView):
    # set the pagination and serializer class
    pagination_class = StandardResultsSetPagination
    serializer_class = PanelProfileSerializers
    def get_queryset(self):
        try:
            country = Country.objects.get(code=self.kwargs["country_code"])
            try:
                pk = self.kwargs["pk"]
            except KeyError:
                pk = None


            audit_date_qs = PanelProfile.objects.all().filter(country = country).values('month__date').annotate(current_month=Max('audit_date')).order_by('-audit_date')[0:2]
            date_arr = []
            for instance in audit_date_qs:
                date_arr.append(instance['month__date'])
            current_month , previous_month = date_arr

            current_month_qs = Month.objects.get(date=current_month)
            previous_month_qs = Month.objects.get(date=previous_month)

            queryList = PanelProfile.objects.all().filter(country = country, month = current_month_qs)
            queryList = queryList.filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                    .filter(country = country, month = current_month_qs, status = UsableOutlet.USABLE))

            parent = self.request.query_params.get('parent')

            # cdebug(parent)

            field_group = self.request.query_params
            new_list = getDictArray(field_group,'field_group[group]')
            new_dic = getDicGroupList(new_list)
            group_filter = getGroupFilter(new_dic)
            # print('>>>>group_filter',group_filter,'<<<<')

            subrbd_group_filter = None
            if parent!='' and int(parent) >=0:

                subrbd = list(RBD.objects.filter(country = country, pk = parent) \
                              .get_descendants(include_self=True) \
                                .values_list('level','serialize_str','id'))
                # cdebug(subrbd)

                subrbd_group_filter = Q()
                for i in range(len(subrbd)):
                    subrbd_level = subrbd[i][0]
                    subrbd_serialize_str = subrbd[i][1]
                    row_id = subrbd[i][2]
                    if(pk is not None and pk == row_id):
                        continue


                    # cdebug(subrbd_level)

                    subrbd_params = parse_qs((subrbd_serialize_str))
                    # cdebug(subrbd_params)
                    subrbd_list = getDictArray(subrbd_params,'field_group[group]')
                    subrbd_dic = getDicGroupList(subrbd_list)
                    subrbd_group_filter_temp = getGroupFilter(subrbd_dic)

                    if(subrbd_group_filter is not None and subrbd_group_filter != ''):
                        if(subrbd_level==0):
                            subrbd_group_filter &= Q(subrbd_group_filter_temp)
                        else:
                            subrbd_group_filter &= ~Q(subrbd_group_filter_temp)

                        # queryList = queryList.filter(subrbd_group_filter)
                # cdebug(subrbd_group_filter)

            if(subrbd_group_filter is not None):
                queryList = queryList.filter(subrbd_group_filter)
            # prettyprint_queryset(queryList)

            rbd = self.request.query_params.get('rbd', None)
            # print('>>>>',rbd,'<<<<')
            if rbd != None and rbd != '':
                rbd = RBD.objects.get(pk=rbd)
                rbd_params = parse_qs((rbd.serialize_str))
                rbd_list = getDictArray(rbd_params,'field_group[group]')
                rbd_dic = getDicGroupList(rbd_list)
                rbd_group_filter = getGroupFilter(rbd_dic)
                # print('>>>>rbd_group_filter ',rbd_group_filter,'<<<<')



            if rbd != None and rbd != '' and rbd_group_filter != '':
                rbd_group_filter &= Q(group_filter)
                queryList = queryList.filter(rbd_group_filter)
            else:
                if(group_filter != ''):
                    queryList = queryList.filter(group_filter)


            prettyprint_queryset(queryList)
            # print(str(queryList.query))

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",str(e),', File: ',exc_type, fname,', Line: ',exc_tb.tb_lineno, Colors.WHITE)


        return queryList


class RBDListViewAjax_BACKUP(LoginRequiredMixin, generic.View):

    def get(self, request, *args, **kwargs):
        return_dic = {}
        response_dict = []
        temp_dic = dict()

        try:
            #Country Query List
            country = Country.objects.get(code=self.kwargs["country_code"])

            #RBD Query List
            queryList = RBD.objects.all().filter(country = country).order_by('tree_id','level')

            #Calculate Current Month
            audit_date_qs = PanelProfile.objects.all().filter(country = country).aggregate(current_month=Max('month__date'))

            current_month = audit_date_qs['current_month']
            current_month_qs = Month.objects.get(date=current_month)


            return_dic['count'] = len(queryList)
            return_dic['next'] = None
            return_dic['previous'] = None

            prettyprint_queryset(queryList)
            # queryList_json = serialize('json', queryList)
            for k in range(0,len(queryList)):

                pk = queryList[k].pk
                rbd_serialize_str = queryList[k].serialize_str
                level = queryList[k].level
                parent_id = queryList[k].parent_id

                print(Colors.BOLD_YELLOW,'Processing RBD: ', queryList[k].name,Colors.WHITE)

                #All Panel profile Records
                queryListPPAll = PanelProfile.objects.all() \
                                    .filter(country = country) \
                                        .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                            .filter(country = country, month = current_month_qs, status = UsableOutlet.USABLE))

                if rbd_serialize_str != '':
                    rbd_params = parse_qs((rbd_serialize_str))
                    rbd_list = getDictArray(rbd_params,'field_group[group]')
                    rbd_dic = getDicGroupList(rbd_list)
                    rbd_group_filter = getGroupFilter(rbd_dic)

                    rbd_group_filter_human = getGroupFilterHuman(rbd_dic)
                    filter_human = "RBD(\n{}) \n".format(rbd_group_filter_human)



                if parent_id is not None:

                    parentRBD = RBD.objects.get(country = country,pk=parent_id)
                    parent_rbd_serialize_str  = parentRBD.serialize_str

                    if parent_rbd_serialize_str != '':
                        parent_rbd_params = parse_qs((parent_rbd_serialize_str))
                        parent_rbd_list = getDictArray(parent_rbd_params,'field_group[group]')
                        parent_rbd_dic = getDicGroupList(parent_rbd_list)
                        parent_rbd_group_filter = getGroupFilter(parent_rbd_dic)

                        parent_rbd_group_filter_human = getGroupFilterHuman(parent_rbd_dic)
                        # filter_human = "RBD(\n{}) \n".format(parent_rbd_group_filter_human)
                        filter_human = "RBD(\n{}) \n AND \n SUB-RBD( \n {})".format(parent_rbd_group_filter_human, rbd_group_filter_human)
                        rbd_group_filter &= Q(parent_rbd_group_filter)
                else:
                    pass

                queryListPPAll = queryListPPAll.filter(rbd_group_filter)
                total_outlets_in_rbd = queryListPPAll.aggregate(count = Count('outlet__id',distinct=True))


                """ Store Cell information with cell conditions """
                # print(Colors.BLUE, queryList[k].rbd.serialize_str,Colors.WHITE)
                # data-node-id="1.1" data-node-pid="1

                data_node_id = ("%s.%s")%(parent_id,k) if parent_id is not None else pk
                data_node_pid = ("%s")%(parent_id) if parent_id is not None else ""

                temp_dic = {
                    'RBDName' : queryList[k].name,
                    'RBDCode' : queryList[k].code,
                    'RBDDescription' : queryList[k].description,
                    'Condition' : "<br />".join(filter_human.split("\n")),
                    'TotalOutlets' : total_outlets_in_rbd['count'],
                    'data-node-id' : data_node_id,
                    'data-node-pid' : data_node_pid,

                    'Actions' : ('<a href="%s" title="Edit" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'+
                                 '<a href="%s" title="Delete" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                                    reverse('master-data:rbd-update', args=(self.kwargs['country_code'],pk,)),
                                    reverse('master-data:rbd-delete', args=(self.kwargs['country_code'],pk,)),
                                )

                    }

                response_dict.append( temp_dic )

            return_dic['results'] = response_dict


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

class RBDListViewAjax(AjaxDatatableView):
    model = RBD
    title = 'RBD'
    initial_order = [["name", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'


    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id','title':'ID', 'visible': True, },
        {'name': 'name',  },
        {'name': 'cell','m2m_foreign_field':'cell__name'  },
        # {'name': 'rbdcode', 'title':'RBD Code', 'foreign_field': 'rbd__code', 'choices': True, 'autofilter': True,},
        {'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
            row['action'] = ('<a href="%s" title="Edit" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'+
                             '<a href="%s" title="Delete" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                    reverse('master-data:rbd-update', args=(self.kwargs['country_code'],obj.id,)),
                    reverse('master-data:rbd-delete', args=(self.kwargs['country_code'],obj.id,)),
                )
            row['cell'] = row['cell'].replace(',','<br>')

            # cdebug(obj.cell.__dict__,'M2')



    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__id=self.request.session['country_id'],
            index__id=self.request.session['index_id']
        )
        return queryset


class RBDListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "master_data/rbd_list.html"
    PAGE_TITLE = "Report Break Down"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

class RBDCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "master_data/rbd_create.html"
    PAGE_TITLE = "Create Report Break Down"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }
    model=RBD
    form_class=RBDModelForm
    #Forward Country Code in Forms
    def get_form_kwargs(self):
        kwargs = super(self.__class__, self).get_form_kwargs()
        # kwargs['request'] = self.request
        kwargs['country_code'] = self.kwargs["country_code"]
        # kwargs['parent'] = self.request.POST.get("parent")
        return kwargs

    def form_valid(self,form):

        try:
            form_obj = form.save(commit=False)
            form_obj.country_id = self.request.session['country_id']
            form_obj.index_id = self.request.session['index_id']
            form_obj.name = self.request.POST.get("name")
            form_obj.code = self.request.POST.get("code")
            form_obj.description = self.request.POST.get("description")
            form_obj.save()
            # cdebug(self.request.POST.get("checkbox"))
            # form_obj.cell.add(self.request.POST.get("checkbox"))
            # form_obj.save()

            return super(self.__class__, self).form_valid(form)

        except IntegrityError:
            messages.add_message(self.request, messages.ERROR, 'All of your Code must be unique.')
            return reverse("master-data:rbd-create",kwargs={"country_code": self.kwargs["country_code"]})

    def get_success_url(self):
            messages.add_message(self.request, messages.SUCCESS, "Record saved successfully.")
            return reverse("master-data:rbd-list", kwargs={"country_code": self.kwargs["country_code"]})


    def get_context_data(self, *args, **kwargs):
        try:
            context = super(self.__class__, self).get_context_data(**kwargs)

            country = Country.objects.get(code=self.kwargs["country_code"])
            objects = Cell.objects.only('id','name').filter(country = country).order_by('name')
            # objects = Cell.objects.only('id','name').get(country__id=self.request.session['country_id']).order_by('name')
            # data = [i[0] for i in list(data)]
            dictionaries = [ obj.as_dict() for obj in objects ]
            # return HttpResponse(), content_type='application/json')

            # row = {k: v for (k, v) in data.items()}
            # print(row)

            cells = {
                "data": json.dumps(dictionaries)
            }


        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",str(e),', File: ',exc_type, fname,', Line: ',exc_tb.tb_lineno, Colors.WHITE)

        context.update({
            "cells": cells,
        })
        return context

class RBDUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "master_data/rbd_update.html"
    PAGE_TITLE = "Update RBD"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }
    model=RBD
    form_class=RBDModelForm
    #Forward Country Code in Forms
    def get_form_kwargs(self):
        kwargs = super(self.__class__, self).get_form_kwargs()
        # kwargs['request'] = self.request
        kwargs['country_code'] = self.kwargs["country_code"]
        # kwargs['parent'] = self.request.POST.get("parent")
        return kwargs

    def form_valid(self,form):

        try:
            form_obj = form.save(commit=False)
            form_obj.country_id = self.request.session['country_id']
            form_obj.index_id = self.request.session['index_id']
            form_obj.name = self.request.POST.get("name")
            form_obj.code = self.request.POST.get("code")
            form_obj.description = self.request.POST.get("description")
            form_obj.save()
            # cdebug(self.request.POST.get("checkbox"))
            # form_obj.cell.add(self.request.POST.get("checkbox"))
            # form_obj.save()


            return super(self.__class__, self).form_valid(form)

        except IntegrityError:
            messages.add_message(self.request, messages.ERROR, 'All of your Code must be unique.')
            return reverse("master-data:rbd-create",kwargs={"country_code": self.kwargs["country_code"]})

    def get_queryset(self):
        queryset = RBD.objects.filter(
            country__id=self.request.session['country_id'],
            pk=self.kwargs['pk']
        )
        return queryset

    def get_success_url(self):
            messages.add_message(self.request, messages.SUCCESS, "Record saved successfully.")
            return reverse("master-data:rbd-list", kwargs={"country_code": self.kwargs["country_code"]})

    def get_context_data(self, *args, **kwargs):
        try:
            context = super(self.__class__, self).get_context_data(**kwargs)

            country = Country.objects.get(code=self.kwargs["country_code"])
            objects = Cell.objects.only('id','name').filter(country = country).order_by('name')
            # objects = Cell.objects.only('id','name').get(country__id=self.request.session['country_id']).order_by('name')
            # data = [i[0] for i in list(data)]
            dictionaries = [ obj.as_dict() for obj in objects ]
            # return HttpResponse(), content_type='application/json')

            # row = {k: v for (k, v) in data.items()}
            # print(row)

            cells = {
                "data": json.dumps(dictionaries)
            }


        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",str(e),', File: ',exc_type, fname,', Line: ',exc_tb.tb_lineno, Colors.WHITE)

        context.update({
            "cells": cells,
        })
        return context

class RBDDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "generic_delete.html"
    PAGE_TITLE = "Delete Report Break Down"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, "Record deleted successfully.")
        return reverse("master-data:rbd-list", kwargs={"country_code": self.kwargs["country_code"]})

    def get_queryset(self):
        queryset = RBD.objects.filter(
            country__id=self.request.session['country_id'],
            pk=self.kwargs['pk']

        )
        return queryset

""" ------------------------- Cell ------------------------- """

class CellImportView(LoginRequiredMixin, generic.CreateView):
    template_name = "generic_import.html"
    PAGE_TITLE = "Import Cell"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    form_class = UploadModalForm

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):

        form_obj = form.save(commit=False)
        form_obj.is_processing = Upload.PROCESSING
        form_obj.process_message = Upload.PROCESSING_MSG
        form_obj.country_id = self.request.session['country_id']
        form_obj.index_id = self.request.session['index_id']
        form_obj.frommodel = "cell"
        form_obj.save()

        print(Colors.BLUE,form_obj.pk)
        proc = Popen('python manage.py import_cell '+str(form_obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):

        messages.add_message(self.request, messages.SUCCESS, "File uploaded successfully, processing records.")
        return reverse("master-data:cell-list", kwargs={"country_code": self.kwargs["country_code"]})

#Used in Cell Create View - EXPRIMENT
class CellPanelProfileAJAX(AjaxDatatableView):
    model = PanelProfile
    title = 'Panel Profile'
    initial_order = [["Index Code", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'

    def get_column_defs(self, request):
        """
        Override to customize based of request
        """
        self.column_defs = [
            AjaxDatatableView.render_row_tools_column_def(),
            {'name': 'id','title':'ID', 'visible': True, },

            {'name': 'Index Code', 'foreign_field': 'index__code', },
            {'name': 'Index Name', 'foreign_field': 'index__name', 'choices': True, 'autofilter': True,},

            # {'name': 'Category Code', 'foreign_field': 'category__code', },
            # {'name': 'Category Name', 'foreign_field': 'category__name','choices': True, 'autofilter': True, },
            {'name': 'Outlet Code', 'foreign_field': 'outlet__code', },

            {'name': 'Outlet Type Code', 'foreign_field': 'outlet_type__code', },
            {'name': 'Outlet Type Name', 'foreign_field': 'outlet_type__name', 'choices': True, 'autofilter': True,},

            {'name': 'Outlet Status Code', 'foreign_field': 'outlet_status__code', },
            {'name': 'Outlet Status Name', 'foreign_field': 'outlet_status__name', 'choices': True, 'autofilter': True,},

            {'name': 'Province Code', 'foreign_field': 'city_village__tehsil__district__province__code', },
            {'name': 'Province Name', 'foreign_field': 'city_village__tehsil__district__province__name', 'choices': True, 'autofilter': True,},
            {'name': 'District Code', 'foreign_field': 'city_village__tehsil__district__code',},
            {'name': 'District Name', 'foreign_field': 'city_village__tehsil__district__name', 'choices': True, 'autofilter': True,},

            {'name': 'Tehsil Code', 'foreign_field': 'city_village__tehsil__code',},
            {'name': 'Tehsil Name', 'foreign_field': 'city_village__tehsil__name', 'choices': True, 'autofilter': True,},
            {'name': 'Tehsil Urbanity', 'foreign_field': 'city_village__tehsil__urbanity', 'choices': True, 'autofilter': True,},

            {'name': 'City Code', 'foreign_field': 'city_village__code', },
            {'name': 'City Name', 'foreign_field': 'city_village__name','choices': True, 'autofilter': True,},

            {'name': 'Rc Cut', 'foreign_field': 'city_village__rc_cut', 'choices': True, 'autofilter': True,},
            {'name':'lms', 'choices': True, 'autofilter': True,},
            {'name':'cell_description',},
            {'name':'nra_tagging',},
            {'name':'ra_tagging',},
            {'name':'ret_tagging',},
            {'name':'audit_date',},
            {'name':'acv'},
        ]

        # ('index', 'category', 'hand_nhand', 'region', 'city_village', 'outlet', 'outlet_type', 'outlet_status', , )
        for v in CityVillage._meta.get_fields():
            if('extra' in v.name):
                try:
                    col_label = ColLabel.objects.only("col_label").get(
                        country__code = self.kwargs['country_code'],
                        model_name = ColLabel.CityVillage,
                        col_name = v.name
                    )
                except ColLabel.DoesNotExist:
                    col_label = None

                title = col_label.col_label if col_label else v.name
                self.column_defs.append({'name': v.name,'title':title, 'foreign_field': 'city_village__'+v.name, 'choices': True, 'autofilter': True, })
        return self.column_defs

    def get_initial_queryset(self, request=None):

        queryList = super().get_initial_queryset(request=request)
        country_id=self.request.session['country_id']
        index_id=self.request.session['index_id']

        audit_date_qs = PanelProfile.objects.all().filter(country__id = country_id,index__id=index_id) \
                        .values('month__date').annotate(current_month=Max('audit_date')) \
                        .order_by('-month__date')[0:2]
        # temp_dic = dict()
        # temp_dic['values_list'] = {}
        # if(len(audit_date_qs) == 0):
        #     cdebug("TRUUE")
        #     return temp_dic


        date_arr = []
        for instance in audit_date_qs:
            date_arr.append(instance['month__date'])

        current_month , previous_month = date_arr
        # cdebug(date_arr)
        current_month_qs = Month.objects.get(date=current_month)
        previous_month_qs = Month.objects.get(date=previous_month)

        queryList = self.model.objects
        queryList = queryList.filter(country__id = country_id, index__id=index_id, month = current_month_qs)
        field_group = parse_qs(self.request.POST.get('data'))

        new_list = getDictArray(field_group,'field_group[group]')
        new_dic = getDicGroupList(new_list)
        group_filter = getGroupFilter(new_dic)

        # cdebug(field_group,'field_group')
        # cdebug(new_list,'new_list')
        # cdebug(group_filter,'group_filter')
        queryList = queryList.filter(group_filter)
        # prettyprint_queryset(queryList)


        # cdebug(self.request.POST.get('data'))
        # cdebug(queryset)
        return queryList

#Used in Cell Create View - X
class PanelProfileCellListing(ListAPIView):
    # set the pagination and serializer class
    pagination_class = StandardResultsSetPagination
    serializer_class = PanelProfileSerializers

    def get_queryset(self):
        try:
            country = Country.objects.get(code=self.kwargs["country_code"])
            try:
                pk = self.kwargs["pk"]
            except KeyError:
                pk = None

            audit_date_qs = PanelProfile.objects.all().filter(country = country).values('month__date').annotate(current_month=Max('audit_date')).order_by('-audit_date')[0:2]
            date_arr = []
            for instance in audit_date_qs:
                date_arr.append(instance['month__date'])
            current_month , previous_month = date_arr

            current_month_qs = Month.objects.get(date=current_month)
            previous_month_qs = Month.objects.get(date=previous_month)

            queryList = PanelProfile.objects.all().filter(country = country, month = current_month_qs)
            queryList = queryList.filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                    .filter(country = country, month = current_month_qs, status = UsableOutlet.USABLE))

            # Get condition filter
            field_group = self.request.query_params
            new_list = getDictArray(field_group,'field_group[group]')
            new_dic = getDicGroupList(new_list)
            group_filter = getGroupFilter(new_dic)

            # cdebug(field_group,'field_group')
            # cdebug(new_list,'new_list')
            # cdebug(group_filter,'group_filter')

            queryList = queryList.filter(group_filter)


            prettyprint_queryset(queryList)
            # print(str(queryList.query))

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",str(e),', File: ',exc_type, fname,', Line: ',exc_tb.tb_lineno, Colors.WHITE)


        return queryList

# class CellListViewAjax(LoginRequiredMixin, generic.View):

#     def get(self, request, *args, **kwargs):
#         return_dic = {}
#         response_dict = []
#         temp_dic = dict()

#         try:
#             #Country Query List
#             country = Country.objects.get(code=self.kwargs["country_code"])

#             #RBD Query List
#             queryList = Cell.objects.all().filter(country = country).order_by('name')
#             # prettyprint_queryset(queryList)
#             #Calculate Current Month
#             audit_date_qs = PanelProfile.objects.all().filter(country = country).aggregate(current_month=Max('month__date'))

#             current_month = audit_date_qs['current_month']
#             current_month_qs = Month.objects.get(date=current_month)


#             return_dic['count'] = len(queryList)
#             return_dic['next'] = None
#             return_dic['previous'] = None


#             #All Panel profile Records
#             queryListPPAll = PanelProfile.objects.all().filter(country = country)
#                                     # .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
#                                     #     .filter(country = country, month = current_month_qs, status = UsableOutlet.USABLE))


#             # queryList_json = serialize('json', queryList)
#             last_rbd_pk = ''
#             counter = 0
#             for k in range(0,len(queryList)):

#                 pk = queryList[k].pk
#                 cell_serialize_str = queryList[k].serialize_str

#                 # print(Colors.BOLD_YELLOW,'Processing Cell: ', queryList[k].name,Colors.WHITE)


#                 cell_group_filter_human = ""
#                 if cell_serialize_str != '':
#                     cell_params = parse_qs((cell_serialize_str))
#                     cell_list = getDictArray(cell_params,'field_group[group]')
#                     cell_dic = getDicGroupList(cell_list)
#                     # cdebug(cell_dic,'cell_dic')
#                     cell_group_filter = getGroupFilter(cell_dic)
#                     # cdebug(cell_group_filter,'cell_group_filter')
#                     cell_group_filter_human = getGroupFilterHuman(cell_dic)



#                 # rbd_cell_group_filter = Q(rbd_group_filter) & Q(cell_group_filter)

#                 filter_human = "Cell( \n {})".format(cell_group_filter_human)

#                 queryListPPAllCell = queryListPPAll.filter(cell_group_filter)

#                 # prettyprint_queryset(queryListPPAllRBDCell)

#                 total_outlets_in_cell = queryListPPAllCell.aggregate(count = Count('outlet__id',distinct=True))

#                 """ Store Cell information with cell conditions """

#                 temp_dic = {
#                     # 'CellCode' : queryList[k].code,
#                     'CellName' : queryList[k].name,
#                     'CellDescription' : queryList[k].description,
#                     'cell_acv' : queryList[k].cell_acv,
#                     'num_universe' : queryList[k].num_universe,
#                     'optimal_panel' : queryList[k].optimal_panel,
#                     'Condition' : "<br />".join(filter_human.split("\n")),

#                     'TotalOutlets' : total_outlets_in_cell['count'],


#                     'Actions' : ('<a href="%s" title="Edit" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'+
#                                 '<a href="%s" title="Duplicate" class="btn btn btn-warning btn-xs dt-duplicate"><span class="mdi mdi-content-duplicate" aria-hidden="true"></span></a>' +
#                                 '<a href="%s" title="Delete" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
#                                     reverse('master-data:cell-update', args=(self.kwargs['country_code'],pk,)),
#                                     reverse('master-data:cell-duplicate', args=(self.kwargs['country_code'],pk,)),
#                                     reverse('master-data:cell-delete', args=(self.kwargs['country_code'],pk,)),
#                                 )

#                     }

#                 response_dict.append( temp_dic )

#             return_dic['results'] = response_dict


#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#             print(Colors.RED, "Exception:",str(e),', File: ',exc_type, fname,', Line: ',exc_tb.tb_lineno, Colors.WHITE)


#         # Prepare response
#         return HttpResponse(
#             json.dumps(
#                 return_dic,
#                 cls=DjangoJSONEncoder
#             ),
#             content_type="application/json")

class CellListViewAjax(AjaxDatatableView):
    model = Cell
    initial_order = [["name", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'

    def get_column_defs(self, request):
        """
        Override to customize based of request
        """

        # ('name', 'description', 'cell_acv', 'num_universe', 'optimal_panel', 'condition_html', 'serialize_str', )
        self.column_defs = [
            AjaxDatatableView.render_row_tools_column_def(),
            {'name': 'id','title':'ID', 'visible': True, },
            {'name': 'name', },
            {'name': 'cell_acv', },
            {'name': 'num_universe', },
            {'name': 'optimal_panel', },
            {'name': 'condition', 'title': 'Condition', 'placeholder': True, 'searchable': False, 'orderable': False, },
            {'name': 'total_outlets', 'title': 'Total Outlets', 'placeholder': True, 'searchable': False, 'orderable': False, },
            {'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, },

        ]

        return self.column_defs

    def customize_row(self, row, obj):
            row['action'] = ('<a href="%s" title="Edit" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>' \
                                '<a href="%s" title="Duplicate" class="btn btn btn-warning btn-xs dt-duplicate"><span class="mdi mdi-content-duplicate" aria-hidden="true"></span></a>' \
                                '<a href="%s" title="Delete" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                                    reverse('master-data:cell-update', args=(self.kwargs['country_code'],obj.id,)),
                                    reverse('master-data:cell-duplicate', args=(self.kwargs['country_code'],obj.id,)),
                                    reverse('master-data:cell-delete', args=(self.kwargs['country_code'],obj.id,)),
                                )
            queryListPPAll = PanelProfile.objects.all().filter(country__id = obj.country_id)
            # cdebug(obj.country_id)
            cell_serialize_str = obj.serialize_str
            cell_group_filter_human = ""
            if cell_serialize_str != '':
                cell_params = parse_qs((cell_serialize_str))
                cell_list = getDictArray(cell_params,'field_group[group]')
                cell_dic = getDicGroupList(cell_list)
                cell_group_filter = getGroupFilter(cell_dic)

                cell_group_filter_human = getGroupFilterHuman(cell_dic)

            filter_human = "Cell( \n {})".format(cell_group_filter_human)

            queryListPPAllCell = queryListPPAll.filter(cell_group_filter)

            total_outlets_in_cell = queryListPPAllCell.aggregate(count = Count('outlet__id',distinct=True))



            row['condition'] = filter_human
            row['total_outlets'] = total_outlets_in_cell['count']

    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__id=self.request.session['country_id'],
            index__id=self.request.session['index_id']
        )
        return queryset


class CellListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "master_data/cell_list.html"
    PAGE_TITLE = "Cells"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

class CellCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "master_data/cell_create.html"
    PAGE_TITLE = "Create Cell"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }
    model=Cell
    form_class=CellModelForm

    def get_form_kwargs(self):
        kwargs = super(self.__class__, self).get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['country_code'] = self.kwargs["country_code"]
        return kwargs

    def form_valid(self,form):

        # rbd = RBD.objects.get(pk=self.request.POST.get("rbd"))
        try:
            form_obj = form.save(commit=False)
            form_obj.country_id = self.request.session['country_id']
            form_obj.index_id = self.request.session['index_id']
            form_obj.name = self.request.POST.get("name")
            form_obj.description = self.request.POST.get("description")
            form_obj.condition_html = self.request.POST.get("condition_html")
            # form_obj.condition_html =  base64.b64encode(condition_html.encode('ascii'))
            form_obj.serialize_str = self.request.POST.get("serialize_str")
            form_obj.condition_json = self.request.POST.get("condition_json")
            form_obj.save()

            month_qs = Month.objects.all().filter(country__id = self.request.session['country_id'])
            cell_acv = self.request.POST.get("cell_acv")

            for key in month_qs:
                CellMonthACV.objects.get_or_create(
                    country__id=self.request.session['country_id'], month=key,cell=form_obj,
                    defaults={'cell_acv':float(cell_acv)}
                )
            return super(self.__class__, self).form_valid(form)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",str(e),', File: ',exc_type, fname,', Line: ',exc_tb.tb_lineno, Colors.WHITE)

    def get_success_url(self):
            messages.add_message(self.request, messages.SUCCESS, "Record saved successfully.")
            return reverse("master-data:cell-list", kwargs={"country_code": self.kwargs["country_code"]})

    def get_context_data(self, *args, **kwargs):
        try:
            context = super(self.__class__, self).get_context_data(**kwargs)
            skip_cols = ['id','pk','month','outlet','outlet_type','country','upload','created','updated',]
            panel_profile_cols = {}
            for v in PanelProfile._meta.get_fields():
                if(v.name in skip_cols): continue
                if isinstance(v, models.ForeignKey):
                    pass
                    # panel_profile_cols[v.name+'__code'] = v.name.replace("_", " ").capitalize()
                else:
                    panel_profile_cols[v.name] = v.name.replace("_", " ").capitalize()


            skip_cols = ['id','pk','country','name','code','tehsil','upload','created','updated',]
            city_village_cols = {}
            for v in CityVillage._meta.get_fields():
                if(v.name in skip_cols): continue
                if('extra' in v.name):
                    try:
                        col_label = ColLabel.objects.only("col_label").get(
                            country__code = self.kwargs['country_code'],
                            model_name = ColLabel.CityVillage,
                            col_name = v.name
                        )
                    except ColLabel.DoesNotExist:
                        col_label = None
                    title = col_label.col_label if col_label else v.name
                    city_village_cols['city_village__'+v.name] = title.replace("_", " ").title()
                else:
                    city_village_cols['city_village__'+v.name] = v.name.replace("_", " ").title()



            cdebug(city_village_cols)
            country = Country.objects.only('id','code','name').get(code=self.kwargs['country_code'])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",str(e),', File: ',exc_type, fname,', Line: ',exc_tb.tb_lineno, Colors.WHITE)

        context.update({
            "panel_profile_cols": panel_profile_cols,
            "city_village_cols": city_village_cols
        })
        return context

class CellUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "master_data/cell_update.html"
    PAGE_TITLE = "Update Cell"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }
    model=Cell
    form_class=CellModelForm

    def get_form_kwargs(self):
        kwargs = super(self.__class__, self).get_form_kwargs()
        # print(Colors.BLUE,kwargs,Colors.WHITE)
        kwargs['request'] = self.request
        kwargs['country_code'] = self.kwargs["country_code"]
        return kwargs

    def form_valid(self,form):

        try:
            form_obj = form.save(commit=False)
            form_obj.country_id = self.request.session['country_id']
            form_obj.index_id = self.request.session['index_id']
            form_obj.name = self.request.POST.get("name")
            form_obj.code = self.request.POST.get("code")
            form_obj.description = self.request.POST.get("description")
            form_obj.condition_html = self.request.POST.get("condition_html")
            form_obj.serialize_str = self.request.POST.get("serialize_str")
            form_obj.condition_json = self.request.POST.get("condition_json")
            form_obj.save()

            return super(self.__class__, self).form_valid(form)
            # messages.add_message(self.request, messages.SUCCESS, "Record saved successfully.")
            # return HttpResponseRedirect(reverse("master-data:cell-update",kwargs={"country_code": self.kwargs["country_code"],"id":form_obj.id}))

        except IntegrityError:
            messages.add_message(self.request, messages.ERROR, 'All of your Code must be unique.')
            return reverse("master-data:cell-create",kwargs={"country_code": self.kwargs["country_code"]})

    def get_queryset(self):
        queryset = Cell.objects.filter(
            country__id=self.request.session['country_id'],
            pk=self.kwargs['pk']
        )
        return queryset

    def get_success_url(self):
            messages.add_message(self.request, messages.SUCCESS, "Record saved successfully.")
            return reverse("master-data:cell-list", kwargs={"country_code": self.kwargs["country_code"]})


    def get_context_data(self, *args, **kwargs):
        try:
            context = super(self.__class__, self).get_context_data(**kwargs)
            cell_qs = Cell.objects.get(
                country__id=self.request.session['country_id'],
                pk=self.kwargs['pk']
            )
            # base64_message = base64_bytes.decode('ascii')
            # print(cell_qs.condition_json)
            # condtion = json.loads(cell_qs.condition_json)
            # print(condtion)
            # for i in condtion:
            #     print(condtion[i])

            skip_cols = ['id','pk','month','outlet','outlet_type','country','upload','created','updated',]
            panel_profile_cols = {}
            for v in PanelProfile._meta.get_fields():
                if(v.name in skip_cols): continue
                panel_profile_cols[v.name] = v.name.replace("_", " ").capitalize()


            skip_cols = ['id','pk','country','name','code','tehsil','upload','created','updated',]
            city_village_cols = {}
            for v in CityVillage._meta.get_fields():
                if(v.name in skip_cols): continue
                if('extra' in v.name):
                    try:
                        col_label = ColLabel.objects.only("col_label").get(
                            country__code = self.kwargs['country_code'],
                            model_name = ColLabel.CityVillage,
                            col_name = v.name
                        )
                    except ColLabel.DoesNotExist:
                        col_label = None
                    title = col_label.col_label if col_label else v.name
                    city_village_cols['city_village__'+v.name] = title.replace("_", " ").title()
                else:
                    city_village_cols['city_village__'+v.name] = v.name.replace("_", " ").title()



            # cdebug(city_village_cols)
            country = Country.objects.only('id','code','name').get(code=self.kwargs['country_code'])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",str(e),', File: ',exc_type, fname,', Line: ',exc_tb.tb_lineno, Colors.WHITE)

        context.update({
            "panel_profile_cols": panel_profile_cols,
            "city_village_cols": city_village_cols,
            "cell_qs": cell_qs,
        })
        return context


class CellDuplicateView(LoginRequiredMixin, generic.ListView):
    template_name = "master_data/cell_update.html"
    PAGE_TITLE = "Duplicate Cell"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def dispatch(self, request, *args, **kwargs):
        # TODO: Duplicate month ACV
        pk = self.kwargs['pk']
        obj = Cell.objects.get(pk=pk)
        obj.pk = None
        obj.name  = obj.name+' - Copy'
        obj.save()

        month_qs = Month.objects.all().filter(country = obj.country)
        cell_acv = obj.cell_acv
        index = obj.index

        for key in month_qs:
            CellMonthACV.objects.get_or_create(
                country=obj.country, month=key,cell=obj,index=index,
                defaults={'cell_acv':float(cell_acv)}
            )


        return HttpResponseRedirect(reverse("master-data:cell-update",kwargs={"country_code": self.kwargs["country_code"],'pk':obj.pk}))

class CellDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "generic_delete.html"
    PAGE_TITLE = "Delete Cell"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, "Record deleted successfully.")
        return reverse("master-data:cell-list", kwargs={"country_code": self.kwargs["country_code"]})

    def get_queryset(self):
        queryset = Cell.objects.filter(
            country__id=self.request.session['country_id'],
            pk=self.kwargs['pk']

        )
        return queryset

""" ------------------------- CellMonthACV ------------------------- """

class CellMonthACVListViewAjax(AjaxDatatableView):
    model = CellMonthACV
    title = 'CellMonthACV'
    initial_order = [["month code", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'


    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id','title':'ID', 'visible': True, },
        {'name': 'month code', 'foreign_field': 'month__code', 'choices': True,'autofilter': True,},
        {'name': 'month', 'foreign_field': 'month__name', 'choices': True,'autofilter': True,},
        {'name': 'year', 'foreign_field': 'month__year', 'choices': True,'autofilter': True,},
        {'name': 'cell', 'foreign_field': 'cell__name','max_length': 100, },
        {'name': 'cell_acv',  },
        {'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
            row['action'] = ('<a href="%s" title="Edit" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'
                            ) % (
                                reverse('master-data:cell-month-acv-update', args=(self.kwargs['country_code'],obj.id,)),
                                )
                # <a href="{1}" title="Delete" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>


    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__id=self.request.session['country_id'],
            index__id=self.request.session['index_id']
        )
        return queryset

class CellMonthACVListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "master_data/cell_month_acv_list.html"
    PAGE_TITLE = "Cell Month ACV"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, **kwargs):

        # Just Temporary
        # objs = Cell.objects.all()
        # for obj in objs:
        #     month_qs = Month.objects.all().filter(country = obj.country)
        #     cell_acv = obj.cell_acv
        #     index = obj.index

        #     for key in month_qs:
        #         CellMonthACV.objects.get_or_create(
        #             country=obj.country, month=key,cell=obj,index=index,
        #             defaults={'cell_acv':float(cell_acv)}
        #         )


        context = super(CellMonthACVListView, self).get_context_data(**kwargs)
        return context


class CellMonthACVUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "master_data/cell_month_acv_update.html"
    form_class = CellMonthACVModelForm
    PAGE_TITLE = "Update CellMonthACV"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_queryset(self):
        queryset = CellMonthACV.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset



    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record updated successfully.")
        return reverse("master-data:cell-month-acv-list", kwargs={"country_code": self.kwargs["country_code"]})


    def form_valid(self,form):
        # country = Country.objects.get(code=self.kwargs["country_code"])

        form.save()

        cell_acv = self.request.POST.get("cell_acv")
        cell = self.request.POST.get("cell")
        cell_master = self.request.POST.get("cell_master")

        # Update master ACV
        if cell_master is not None:
            cell_qs = Cell.objects.get(pk=cell)
            cell_qs.cell_acv = cell_acv
            cell_qs.save()

        return super(self.__class__, self).form_valid(form)




""" ------------------------- OutletType ------------------------- """

class OutletTypeImportView(LoginRequiredMixin, generic.CreateView):
    template_name = "generic_import.html"
    PAGE_TITLE = "Import Outlet Types"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    form_class = UploadModalForm

    def get_context_data(self, **kwargs):
        context = super(OutletTypeImportView, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):

        form_obj = form.save(commit=False)
        form_obj.is_processing = Upload.PROCESSING
        form_obj.process_message = Upload.PROCESSING_MSG
        form_obj.country_id = self.request.session['country_id']
        form_obj.index_id = self.request.session['index_id']
        form_obj.frommodel = "outlet_type"
        form_obj.save()

        print(Colors.BLUE,form_obj.pk)
        proc = Popen('python manage.py import_outlet_type '+str(form_obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):
        # return reverse("leads:lead-detail", kwargs={"pk": self.kwargs["pk"]})
        messages.add_message(self.request, messages.SUCCESS, "File uploaded successfully, processing records.")
        return reverse("master-data:outlet-type-list", kwargs={"country_code": self.kwargs["country_code"]})

class OutletTypeListViewAjax(AjaxDatatableView):
    model = OutletType
    title = 'OutletType'
    initial_order = [["code", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'


    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id','title':'ID', 'visible': True, },
        {'name': 'code',  },
        {'name': 'name',  },
        {'name': 'urbanity',  'choices': True,'autofilter': True,},
        {'name': 'is_active',  'choices': True, 'autofilter': True,},
        {'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
            row['action'] = ('<a href="%s" title="Edit" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'+
                             '<a href="%s" title="Delete" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                    reverse('master-data:outlet-type-update', args=(self.kwargs['country_code'],obj.id,)),
                    reverse('master-data:outlet-type-delete', args=(self.kwargs['country_code'],obj.id,)),
                )
                # <a href="{1}" title="Delete" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>


    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset

class OutletTypeListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "master_data/outlet_type_list.html"
    PAGE_TITLE = "Outlet Types"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, **kwargs):
        context = super(OutletTypeListView, self).get_context_data(**kwargs)
        uploadStatusMessage(self,self.request.session['country_id'],'outlet_type')
        return context

class OutletTypeCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "generic_create.html"
    form_class = OutletTypeModelForm
    PAGE_TITLE = "Create OutletType"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record saved successfully.")
        return reverse("master-data:outlet-type-list", kwargs={"country_code": self.kwargs["country_code"]})

    def form_valid(self, form):
        form_obj = form.save(commit=False)
        form_obj.country_id = self.request.session['country_id']
        form_obj.save()
        return super(self.__class__, self).form_valid(form)
    # #Forward Country Code in Forms
    # def get_form_kwargs(self):
    #     kwargs = super(self.__class__, self).get_form_kwargs()
    #     kwargs['request'] = self.request
    #     kwargs['country_code'] = self.kwargs["country_code"]
    #     return kwargs

class OutletTypeUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "generic_update.html"
    form_class = OutletTypeModelForm
    PAGE_TITLE = "Update OutletType"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_queryset(self):
        queryset = OutletType.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record updated successfully.")
        return reverse("master-data:outlet-type-list", kwargs={"country_code": self.kwargs["country_code"]})

    def form_valid(self, form):
        form.save()
        return super(self.__class__, self).form_valid(form)

class OutletTypeDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "generic_delete.html"
    PAGE_TITLE = "Delete OutletType"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, "Record deleted successfully.")
        return reverse("master-data:outlet-type-list", kwargs={"country_code": self.kwargs["country_code"]})

    def get_queryset(self):
        queryset = OutletType.objects.filter(
            country__id=self.request.session['country_id'],
            pk=self.kwargs['pk']
        )
        return queryset

