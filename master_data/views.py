from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *

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


from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q, Avg, Count, Min,Max, Sum
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse,reverse_lazy
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.mixins import LoginRequiredMixin
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
            country__code=kwargs['country_code']
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
        # queryset = Upload.objects.filter(country__code=self.kwargs['country_code'])
        return context

    def form_valid(self, form):

        country = Country.objects.get(code=self.kwargs["country_code"])

        form_obj = form.save(commit=False)
        form_obj.is_processing = Upload.PROCESSING
        form_obj.process_message = "Records are processing in background, check back soon."
        form_obj.country = country
        form_obj.frommodel = "census"
        form_obj.save()

        proc = Popen('python manage.py import_census '+str(form_obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "File uploaded successfully, processing records.")
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
            country__code=self.kwargs['country_code']
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CensusListView, self).get_context_data(**kwargs)
        censusupload = Upload.objects.filter(
            country__code=self.kwargs['country_code'], frommodel='census'
        ).last()
        if(censusupload is not None and  censusupload.is_processing != Upload.COMPLETED):
            messages.add_message(self.request, messages.SUCCESS, censusupload.is_processing +' : '+ censusupload.process_message)


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
        # queryset = Upload.objects.filter(country__code=self.kwargs['country_code'])
        return context

    def form_valid(self, form):

        country = Country.objects.get(code=self.kwargs["country_code"])

        # try:
        #     censusupload = Upload.objects.get(country=country,frommodel='category')
        # except Upload.DoesNotExist:
        #     censusupload = None

        # if  censusupload is None:
        form_obj = form.save(commit=False)
        form_obj.is_processing = Upload.PROCESSING
        form_obj.process_message = "Records are processing in background, check back soon."
        form_obj.country = country
        form_obj.frommodel = "category"
        form_obj.save()

        proc = Popen('python manage.py import_category '+str(form_obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        # management.call_command('import_census',self.kwargs["country_code"])
        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):
        # return reverse("leads:lead-detail", kwargs={"pk": self.kwargs["pk"]})
        messages.add_message(self.request, messages.SUCCESS, "File uploaded successfully, processing records.")

        return reverse("master-data:category-list", kwargs={"country_code": self.kwargs["country_code"]})

class CategoryListViewAjax(AjaxDatatableView):
    model = Category
    title = 'Categories'
    initial_order = [["code", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'


    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id', 'visible': False, },
        {'name': 'code',  },
        {'name': 'name',  },
        {'name': 'parent', 'foreign_field': 'parent__name',   'choices': True, 'autofilter': True,},
        {'name': 'is_active',  'choices': True, 'autofilter': True,},
        {'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
            row['action'] = ('<a href="%s" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'+
                             '<a href="%s" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                    reverse('master-data:category-update', args=(self.kwargs['country_code'],obj.id,)),
                    reverse('master-data:category-delete', args=(self.kwargs['country_code'],obj.id,)),
                )
                # <a href="{1}" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>


    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__code=self.kwargs['country_code']
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
        upload = Upload.objects.filter(
            country__code=self.kwargs['country_code'], frommodel='category'
        ).last()
        if(upload is not None and  upload.is_processing != Upload.COMPLETED):
            messages.add_message(self.request, messages.SUCCESS, str(upload.is_processing +' : '+ upload.process_message))

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
        return reverse("master-data:category-list", kwargs={"country_code": self.kwargs["country_code"]})

    def form_valid(self, form):
        country = Country.objects.get(code=self.kwargs["country_code"])
        form_obj = form.save(commit=False)
        form_obj.country = country
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
            country__code=self.kwargs['country_code']
        )
        return queryset

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record updated successfully.")
        return reverse("master-data:category-list", kwargs={"country_code": self.kwargs["country_code"]})

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
        return reverse("master-data:category-list", kwargs={"country_code": self.kwargs["country_code"]})

    def get_queryset(self):
        queryset = Category.objects.filter(
            country__code=self.kwargs['country_code'],
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

    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id', 'visible': False, },
        {'name': 'month', 'foreign_field': 'month__code', 'choices': True,'autofilter': True,},
        {'name': 'outlet','title':'Outlet Code',  'foreign_field': 'outlet__code',},
        {'title':'Outlet Type Code','name': 'outlet_type_code',  'foreign_field': 'outlet_type__code', 'choices': True, 'autofilter': True,},
        {'title':'Outlet Type Name','name': 'outlet_type_name',  'foreign_field': 'outlet_type__name', 'choices': True, 'autofilter': True,},


        {'title':'Outlet Status code','name': 'outlet_status_code',  'foreign_field': 'outlet_status__code', 'choices': True, 'autofilter': True,},
        {'title':'Outlet Status Name','name': 'outlet_status_name',  'foreign_field': 'outlet_status__name', 'choices': True, 'autofilter': True,},

        {'name': 'index', 'foreign_field': 'index__name',  'choices': True, 'autofilter': True, 'width':'50',},
        # {'name': 'hand_nhand',  'choices': True,'autofilter': True,},
        # {'name': 'region',  'choices': True,'autofilter': True,},
        {'name': 'audit_date', },
        {'name': 'acv', },
        # {'name': 'wtd_factor', },
        # {'name': 'num_factor',  },
        # {'name': 'turnover',  },

        ]
    # for v in model._meta.get_fields():
    #     if('custom' in v.name):
    #         column_defs.append({'name':v.name})



    # model._meta.fields
    def get_initial_queryset(self, request=None):
        queryset = self.model.objects.filter(
            country__code=self.kwargs['country_code']
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
        upload = Upload.objects.filter(
            country__code=self.kwargs['country_code'], frommodel='panel_profile'
        ).last()
        if(upload is not None and  upload.is_processing != Upload.COMPLETED):
            messages.add_message(self.request, messages.SUCCESS, str(upload.is_processing +' : '+ upload.process_message))

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
        country = Country.objects.get(code=self.kwargs["country_code"])

        form_obj = form.save(commit=False)
        form_obj.is_processing = Upload.PROCESSING
        form_obj.process_message = "Records are processing in background, check back soon."
        form_obj.country = country
        form_obj.frommodel = "panel_profile_update"
        form_obj.save()

        print(Colors.BLUE,form_obj.pk)
        proc = Popen('python manage.py import_panel_profile_update '+str(form_obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):

        messages.add_message(self.request, messages.SUCCESS, "File uploaded successfully, processing records.")
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
        country = Country.objects.get(code=self.kwargs["country_code"])

        form_obj = form.save(commit=False)
        form_obj.is_processing = Upload.PROCESSING
        form_obj.process_message = "Records are processing in background, check back soon."
        form_obj.country = country
        form_obj.frommodel = "panel_profile"
        form_obj.save()

        cdebug(form_obj.pk)
        proc = Popen('python manage.py import_panel_profile '+str(form_obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):

        messages.add_message(self.request, messages.SUCCESS, "File uploaded successfully, processing records.")
        return reverse("master-data:panel-profile-list", kwargs={"country_code": self.kwargs["country_code"]})




class PanelProfileListViewAjax2(AjaxDatatableView):
    model = PanelProfile
    title = 'PanelProfile'
    initial_order = [["month", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'

    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id', 'visible': False, },
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
            country__code=self.kwargs['country_code']
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
        country = Country.objects.get(code=self.kwargs["country_code"])

        form_obj = form.save(commit=False)
        form_obj.is_processing = Upload.PROCESSING
        form_obj.process_message = "Records are processing in background, check back soon."
        form_obj.country = country
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
    initial_order = [["month", "asc"],['index','asc'] ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'


    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id', 'visible': False, },
        {'name': 'month', 'foreign_field': 'month__code', 'choices': True,'autofilter': True,},
        {'name': 'index', 'foreign_field': 'index__name',  'choices': True, 'autofilter': True, 'width':'50',},
        {'name': 'outlet','title':'Outlet Code',  'foreign_field': 'outlet__code',},
        {'name': 'is_active',  'choices': True, 'autofilter': True,},
        {'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
            row['action'] = ('<a href="%s" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'+
                             '<a href="%s" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                    reverse('master-data:usable-outlet-update', args=(self.kwargs['country_code'],obj.id,)),
                    reverse('master-data:usable-outlet-delete', args=(self.kwargs['country_code'],obj.id,)),
                )


    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__code=self.kwargs['country_code']
        )
        return queryset

    # def get_foreign_queryset(self, request, field):
    #     print(Colors.BOLD_BLUE)
    #     pprint(self,indent=2)
    #     pprint(request,indent=2)
    #     pprint(field,indent=2)
    #     print(Colors.WHITE)
    #     queryset = field.model.objects.all()
    #     return queryset

class UsableOutletListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "master_data/usable_outlet_list.html"
    PAGE_TITLE = "Usable Outlet"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        upload = Upload.objects.filter(
            country__code=self.kwargs['country_code'], frommodel='usable_outlet'
        ).last()
        if(upload is not None and  upload.is_processing != Upload.COMPLETED):
            messages.add_message(self.request, messages.SUCCESS, str(upload.is_processing +' : '+ upload.process_message))

        return context


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
        country = Country.objects.get(code=self.kwargs["country_code"])
        form_obj = form.save(commit=False)
        form_obj.country = country
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
            country__code=self.kwargs['country_code']
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
            country__code=self.kwargs['country_code'],
            pk=self.kwargs['pk']
        )
        return queryset



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
        country = Country.objects.get(code=self.kwargs["country_code"])

        form_obj = form.save(commit=False)
        form_obj.is_processing = Upload.PROCESSING
        form_obj.process_message = "Records are processing in background, check back soon."
        form_obj.country = country
        form_obj.frommodel = "product"
        form_obj.save()

        proc = Popen('python manage.py import_product '+str(form_obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):

        messages.add_message(self.request, messages.SUCCESS, "File uploaded successfully, processing records.")
        return reverse("master-data:product-list", kwargs={"country_code": self.kwargs["country_code"]})



class ProductListViewAjax(AjaxDatatableView):
    model = Product
    title = 'Product'
    initial_order = [["code", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'


    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        # ('pack_type', 'aggregation_level', 'category_code', 'company', 'brand', 'family', 'flavour_type', 'weight', 'price_segment', 'length_range', 'number_in_pack', 'price_per_stick', )
        {'name': 'id', 'visible': False, },
        {'name': 'code',  },
        {'name': 'name',  },

        {'name': 'pack_type',  'choices': True, 'autofilter': True,},
        {'name': 'aggregation_level',  'choices': True, 'autofilter': True,},
        {'name': 'company',  'choices': True, 'autofilter': True,},
        {'name': 'brand',  'choices': True, 'autofilter': True,},
        {'name': 'family',  'choices': True, 'autofilter': True,},
        {'name': 'flavour_type',  'choices': True, 'autofilter': True,},
        {'name': 'weight',  },
        {'name': 'price_segment',  'choices': True, 'autofilter': True,},
        {'name': 'length_range',  'choices': True, 'autofilter': True,},
        {'name': 'number_in_pack',  },
        {'name': 'price_per_stick',  },
    ]

    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__code=self.kwargs['country_code']
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
        upload = Upload.objects.filter(
            country__code=self.kwargs['country_code'], frommodel='product'
        ).last()

        if(upload is not None and  upload.is_processing != Upload.COMPLETED):
            messages.add_message(self.request, messages.SUCCESS, str(upload.is_processing +' : '+ upload.process_message))

        return context

""" ------------------------- Audit Data ------------------------- """

class ProductAuditImportView(LoginRequiredMixin, generic.CreateView):
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
        country = Country.objects.get(code=self.kwargs["country_code"])

        form_obj = form.save(commit=False)
        form_obj.is_processing = Upload.PROCESSING
        form_obj.process_message = "Records are processing in background, check back soon."
        form_obj.country = country
        form_obj.frommodel = "product_audit"
        form_obj.save()

        print(Colors.BLUE,form_obj.pk)
        proc = Popen('python manage.py import_product_audit '+str(form_obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):

        messages.add_message(self.request, messages.SUCCESS, "File uploaded successfully, processing records.")
        return reverse("master-data:product-audit-list", kwargs={"country_code": self.kwargs["country_code"]})



class ProductAuditListViewAjax(AjaxDatatableView):
    model = ProductAudit
    title = 'Audit Data'
    initial_order = [["month", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'

    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id', 'visible': False, },
        {'name': 'period',  'choices': True,'autofilter': True,},
        {'name': 'month', 'foreign_field': 'month__code', 'choices': True,'autofilter': True,},
        {'name': 'category', 'foreign_field': 'category__code', 'choices': True,'autofilter': True,},
        {'name': 'outlet', 'foreign_field': 'outlet__code',},
        {'name': 'product','title':'Product Code', 'foreign_field': 'product__code',},
        {'name': 'avaibility', 'choices': True,'autofilter': True,},

        ]

    skip_cols = ['id','pk','country','upload','created','updated',
                 'month', 'period', 'category', 'outlet', 'product','avaibility',]

    for v in model._meta.get_fields():
        if(v.name not in skip_cols):
            column_defs.append({'name':v.name})


    # ['product_details', 'avaibility', 'facing_empty', 'facing_not_empty', 'forward', 'reserve', 'total_none_empty_facing_forward_reserve', 'purchaseother1', 'purchaseother2', 'purchasediary', 'purchaseinvoice', 'price_in_unit', 'price_in_pack', 'priceother', 'cash_discount', 'product_foc', 'gift_with_purchase', 'appreciation_award', 'other_trade_promotion', 'pack_without_graphic_health_warning', 'no_of_pack_without_graphic_health_warning_facing', 'no_of_pack_without_graphic_health_warning_total_stock', 'no_of_pack_without_none_tax_stamp', 'point_of_sales_signboard', 'point_of_sales_poster', 'point_of_sales_counter_shield', 'point_of_sales_price_sticker', 'point_of_sales_umbrella', 'point_of_sales_counter_top_display', 'point_of_sales_lighter', 'point_of_sales_others', 'point_of_sales_none', 'pack_type', 'aggregation_level', 'company', 'brand', 'family', 'flavour_type', 'weight', 'price_segment', 'length_range', 'number_in_pack', 'price_per_stick', ]

    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__code=self.kwargs['country_code']
        )
        return queryset


class ProductAuditListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "master_data/product_audit_list.html"
    PAGE_TITLE = "Audit Data"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        upload = Upload.objects.filter(
            country__code=self.kwargs['country_code'], frommodel='product_audit'
        ).last()
        if(upload is not None and  upload.is_processing != Upload.COMPLETED):
            messages.add_message(self.request, messages.SUCCESS, str(upload.is_processing +' : '+ upload.process_message))

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
        {'name': 'id', 'visible': False, },
        {'name': 'code',  },
        {'name': 'name',  },
        {'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
            row['action'] = ('<a href="%s" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'+
                             '<a href="%s" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                    reverse('master-data:rbd-update', args=(self.kwargs['country_code'],obj.id,)),
                    reverse('master-data:rbd-delete', args=(self.kwargs['country_code'],obj.id,)),
                )
                # <a href="{1}" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>


    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__code=self.kwargs['country_code']
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
                                    .filter(country = country, month = current_month_qs, is_active = True))

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
            # logger.error(Colors.BOLD_RED+'CSV file processing failed. Error Msg:'+ str(e)+Colors.WHITE )

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
                                            .filter(country = country, month = current_month_qs, is_active = True))

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

                    'Actions' : ('<a href="%s" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'+
                                 '<a href="%s" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
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
            # logger.error(Colors.BOLD_RED+'CSV file processing failed. Error Msg:'+ str(e)+Colors.WHITE )

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
    initial_order = [["code", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'


    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id', 'visible': False, },
        {'name': 'code',  },
        {'name': 'name',  },
        {'name': 'cell','m2m_foreign_field':'cell__code'  },
        # {'name': 'rbdcode', 'title':'RBD Code', 'foreign_field': 'rbd__code', 'choices': True, 'autofilter': True,},
        {'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
            row['action'] = ('<a href="%s" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'+
                             '<a href="%s" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                    reverse('master-data:rbd-update', args=(self.kwargs['country_code'],obj.id,)),
                    reverse('master-data:rbd-delete', args=(self.kwargs['country_code'],obj.id,)),
                )
                # <a href="{1}" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>


    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__code=self.kwargs['country_code']
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
        country = Country.objects.get(code=self.kwargs["country_code"])
        try:
            form_obj = form.save(commit=False)
            form_obj.country = country
            form_obj.name = self.request.POST.get("name")
            form_obj.code = self.request.POST.get("code")
            form_obj.description = self.request.POST.get("description")
            form_obj.save()
            return super(self.__class__, self).form_valid(form)

        except IntegrityError:
            messages.add_message(self.request, messages.ERROR, 'All of your Code must be unique.')
            return reverse("master-data:rbd-create",kwargs={"country_code": self.kwargs["country_code"]})

    def get_success_url(self):
            messages.add_message(self.request, messages.SUCCESS, "Record saved successfully.")
            return reverse("master-data:rbd-list", kwargs={"country_code": self.kwargs["country_code"]})


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
        country = Country.objects.get(code=self.kwargs["country_code"])

        try:
            form_obj = form.save(commit=False)
            form_obj.country = country
            form_obj.name = self.request.POST.get("name")
            form_obj.code = self.request.POST.get("code")
            form_obj.description = self.request.POST.get("description")
            form_obj.save()

            return super(self.__class__, self).form_valid(form)

        except IntegrityError:
            messages.add_message(self.request, messages.ERROR, 'All of your Code must be unique.')
            return reverse("master-data:rbd-create",kwargs={"country_code": self.kwargs["country_code"]})

    def get_queryset(self):
        queryset = RBD.objects.filter(
            country__code=self.kwargs['country_code'],
            pk=self.kwargs['pk']
        )
        return queryset

    def get_success_url(self):
            messages.add_message(self.request, messages.SUCCESS, "Record saved successfully.")
            return reverse("master-data:rbd-list", kwargs={"country_code": self.kwargs["country_code"]})

    def get_context_data(self, *args, **kwargs):

        context = super(self.__class__, self).get_context_data(**kwargs)
        rbd_qs = RBD.objects.get(
            country__code=self.kwargs['country_code'],
            pk=self.kwargs['pk']
        )
        skip_cols = ['id','pk','country','upload','created','updated',]

        panel_profile_cols = {}
        for v in PanelProfile._meta.get_fields():
            if(v.name not in skip_cols):
                if isinstance(v, models.ForeignKey):
                    panel_profile_cols[v.name+'__code'] = v.name.replace("_", " ").capitalize()
                else:
                    panel_profile_cols[v.name] = v.name.replace("_", " ").capitalize()

        country = Country.objects.only('id','code','name').get(code=self.kwargs['country_code'])

        context.update({
            "panel_profile_cols": panel_profile_cols,
            "rbd_qs": rbd_qs,
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
            country__code=self.kwargs['country_code'],
            pk=self.kwargs['pk']

        )
        return queryset

""" ------------------------- Cell ------------------------- """

class CellListViewAjax_backup(AjaxDatatableView):
    model = Cell
    title = 'Cell'
    initial_order = [["code", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'


    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id', 'visible': False, },
        {'name': 'name','title':'Cell Name' },
        {'name': 'code','title':'Cell Code'  },
        {'name': 'rbdcode', 'title':'RBD Code', 'foreign_field': 'rbd__code', 'choices': True, 'autofilter': True,},
        {'name': 'rbd','title':'RBD Name', 'foreign_field': 'rbd__name', 'choices': True, 'autofilter': True,},
        {'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
            row['action'] = ('<a href="%s" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'+
                             '<a href="%s" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                    reverse('master-data:cell-update', args=(self.kwargs['country_code'],obj.id,)),
                    reverse('master-data:cell-delete', args=(self.kwargs['country_code'],obj.id,)),
                )
                # <a href="{1}" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>


    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__code=self.kwargs['country_code']
        )
        return queryset


#Used in Cell Create View - EXPRIMENT
class CellPanelProfileAJAX(AjaxDatatableView):
    model = PanelProfile
    title = 'Panel Profile'
    initial_order = [["code", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'


    # abc = AjaxDatatableView.get_country
    # cdebug(abc)

    def get_column_defs(self, request):
        """
        Override to customize based of request
        """
        self.column_defs = [
            AjaxDatatableView.render_row_tools_column_def(),
            {'name': 'id', 'visible': False, },

            {'name': 'Province Code', 'foreign_field': 'city_village__tehsil__district__province__code', },
            {'name': 'Province Name', 'foreign_field': 'city_village__tehsil__district__province__name', 'choices': True, 'autofilter': True,},
            {'name': 'District Code', 'foreign_field': 'city_village__tehsil__district__code',},
            {'name': 'District Name', 'foreign_field': 'city_village__tehsil__district__name', 'choices': True, 'autofilter': True,},

            {'name': 'Tehsil Code', 'foreign_field': 'city_village__tehsil__code',},
            {'name': 'Tehsil Name', 'foreign_field': 'city_village__tehsil__name', 'choices': True, 'autofilter': True,},
            {'name': 'Urbanity', 'foreign_field': 'city_village__tehsil__urbanity', 'choices': True, 'autofilter': True,},

            {'name': 'code', 'title':'City Code', 'foreign_field': 'city_village__code', },
            {'name': 'name', 'title':'City Name',  'foreign_field': 'city_village__name',},
            {'name': 'rc_cut', 'foreign_field': 'city_village__rc_cut', 'choices': True, 'autofilter': True,},
        ]

        # ('index', 'category', 'hand_nhand', 'region', 'city_village', 'outlet', 'outlet_type', 'outlet_status', 'nra_tagging', 'ra_tagging', 'ret_tagging', 'audit_date', 'wtd_factor', 'num_factor', 'turnover', 'acv', )
        # for v in self.__class__.model._meta.get_fields():
        #     if('extra' in v.name):
        #         try:
        #             col_label = ColLabel.objects.only("col_label").get(
        #                 country__code = self.kwargs['country_code'],
        #                 model_name = 'CityVillage',
        #                 col_name = v.name
        #             )
        #         except ColLabel.DoesNotExist:
        #             col_label = None

        #         title = col_label.col_label if col_label else v.name
        #         self.column_defs.append({'name': v.name,'title':title, 'choices': True, 'autofilter': True, })
        return self.column_defs


    # def filter_queryset(self, params, queryList):

    #     # qs = self.model.objects.filter(
    #     #     code='10001'
    #     # )
    #     return queryList

    def get_initial_queryset(self, request=None):


        # queryset = self.model.objects.filter(
        #     country__code=self.kwargs['country_code']
        # )
        queryList = super().get_initial_queryset(request=request)

        country = Country.objects.get(code=self.kwargs["country_code"])

        audit_date_qs = PanelProfile.objects.all().filter(country = country).values('month__date').annotate(current_month=Max('audit_date')).order_by('-audit_date')[0:2]
        date_arr = []
        for instance in audit_date_qs:
            date_arr.append(instance['month__date'])
        current_month , previous_month = date_arr

        current_month_qs = Month.objects.get(date=current_month)
        previous_month_qs = Month.objects.get(date=previous_month)

        queryList = self.model.objects
        queryList = queryList.filter(country = country, month = current_month_qs)
        # queryList = queryList.filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
        #                         .filter(country = country, month = current_month_qs, is_active = True))
        field_group = parse_qs(self.request.POST.get('data'))

        new_list = getDictArray(field_group,'field_group[group]')
        new_dic = getDicGroupList(new_list)
        group_filter = getGroupFilter(new_dic)

        cdebug(field_group,'field_group')
        cdebug(new_list,'new_list')
        cdebug(group_filter,'group_filter')
        queryList = queryList.filter(group_filter)
        prettyprint_queryset(queryList)


        # cdebug(self.request.POST.get('data'))
        # cdebug(queryset)
        return queryList


#Used in Cell Create View
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
                                    .filter(country = country, month = current_month_qs, is_active = True))

            # Get condition filter
            field_group = self.request.query_params
            new_list = getDictArray(field_group,'field_group[group]')
            new_dic = getDicGroupList(new_list)
            group_filter = getGroupFilter(new_dic)

            cdebug(field_group,'field_group')
            cdebug(new_list,'new_list')
            cdebug(group_filter,'group_filter')

            queryList = queryList.filter(group_filter)


            prettyprint_queryset(queryList)
            # print(str(queryList.query))

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",str(e),', File: ',exc_type, fname,', Line: ',exc_tb.tb_lineno, Colors.WHITE)
            # logger.error(Colors.BOLD_RED+'CSV file processing failed. Error Msg:'+ str(e)+Colors.WHITE )

        return queryList

class CellListViewAjax(LoginRequiredMixin, generic.View):

    def get(self, request, *args, **kwargs):
        return_dic = {}
        response_dict = []
        temp_dic = dict()

        try:
            #Country Query List
            country = Country.objects.get(code=self.kwargs["country_code"])

            #RBD Query List
            queryList = Cell.objects.all().filter(country = country)
            # prettyprint_queryset(queryList)
            #Calculate Current Month
            audit_date_qs = PanelProfile.objects.all().filter(country = country).aggregate(current_month=Max('month__date'))

            current_month = audit_date_qs['current_month']
            current_month_qs = Month.objects.get(date=current_month)


            return_dic['count'] = len(queryList)
            return_dic['next'] = None
            return_dic['previous'] = None


            #All Panel profile Records
            queryListPPAll = PanelProfile.objects.all() \
                                .filter(country = country) \
                                    .filter(outlet_id__in = UsableOutlet.objects.values_list('outlet_id', flat=True) \
                                        .filter(country = country, month = current_month_qs, is_active = True))


            # queryList_json = serialize('json', queryList)
            last_rbd_pk = ''
            counter = 0
            for k in range(0,len(queryList)):

                pk = queryList[k].pk
                cell_serialize_str = queryList[k].serialize_str

                print(Colors.BOLD_YELLOW,'Processing Cell: ', queryList[k].name,Colors.WHITE)


                cell_group_filter_human = ""
                if cell_serialize_str != '':
                    cell_params = parse_qs((cell_serialize_str))
                    cell_list = getDictArray(cell_params,'field_group[group]')
                    cell_dic = getDicGroupList(cell_list)
                    cdebug(cell_dic,'cell_dic')
                    cell_group_filter = getGroupFilter(cell_dic)
                    cdebug(cell_group_filter,'cell_group_filter')
                    cell_group_filter_human = getGroupFilterHuman(cell_dic)



                # rbd_cell_group_filter = Q(rbd_group_filter) & Q(cell_group_filter)

                filter_human = "Cell( \n {})".format(cell_group_filter_human)

                # queryListPPAllCell = queryListPPAll.filter(cell_group_filter)

                # prettyprint_queryset(queryListPPAllRBDCell)

                # total_outlets_in_cell = queryListPPAllCell.aggregate(count = Count('outlet__id',distinct=True))

                """ Store Cell information with cell conditions """

                temp_dic = {
                    'CellCode' : queryList[k].code,
                    'CellName' : queryList[k].name,
                    'CellDescription' : queryList[k].description,
                    'cell_acv' : queryList[k].cell_acv,
                    'num_universe' : queryList[k].num_universe,
                    'optimal_panel' : queryList[k].optimal_panel,
                    'Condition' : "<br />".join(filter_human.split("\n")),
                    'TotalOutlets' : 0,
                    # 'TotalOutlets' : total_outlets_in_cell['count'],


                    'Actions' : ('<a href="%s" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'+
                                '<a href="%s" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                                    reverse('master-data:cell-update', args=(self.kwargs['country_code'],pk,)),
                                    reverse('master-data:cell-delete', args=(self.kwargs['country_code'],pk,)),
                                )

                    }

                response_dict.append( temp_dic )

            return_dic['results'] = response_dict


        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",str(e),', File: ',exc_type, fname,', Line: ',exc_tb.tb_lineno, Colors.WHITE)
            # logger.error(Colors.BOLD_RED+'CSV file processing failed. Error Msg:'+ str(e)+Colors.WHITE )

        # Prepare response
        return HttpResponse(
            json.dumps(
                return_dic,
                cls=DjangoJSONEncoder
            ),
            content_type="application/json")




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
        country = Country.objects.get(code=self.kwargs["country_code"])
        # rbd = RBD.objects.get(pk=self.request.POST.get("rbd"))
        try:
            form_obj = form.save(commit=False)
            form_obj.country = country
            form_obj.name = self.request.POST.get("name")
            form_obj.code = self.request.POST.get("code")
            form_obj.description = self.request.POST.get("description")
            form_obj.condition_html = self.request.POST.get("condition_html")
            form_obj.serialize_str = self.request.POST.get("serialize_str")
            form_obj.save()
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
                    panel_profile_cols['panel_profile__'+v.name] = v.name.replace("_", " ").capitalize()


            skip_cols = ['id','pk','country','name','code','tehsil','upload','created','updated',]
            city_village_cols = {}
            for v in CityVillage._meta.get_fields():
                if(v.name in skip_cols): continue
                if('extra' in v.name):
                    try:
                        col_label = ColLabel.objects.only("col_label").get(
                            country__code = self.kwargs['country_code'],
                            model_name = 'CityVillage',
                            col_name = v.name
                        )
                    except ColLabel.DoesNotExist:
                        col_label = None
                    title = col_label.col_label if col_label else v.name
                    city_village_cols[v.name] = title.replace("_", " ").title()
                else:
                    city_village_cols[v.name] = v.name.replace("_", " ").title()




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
        print(Colors.BLUE,kwargs,Colors.WHITE)
        kwargs['request'] = self.request
        kwargs['country_code'] = self.kwargs["country_code"]
        return kwargs

    def get_context_data(self, *args, **kwargs):

        context = super(self.__class__, self).get_context_data(**kwargs)
        cell_qs = Cell.objects.get(
            country__code=self.kwargs['country_code'],
            pk=self.kwargs['pk']
        )
        skip_cols = ['id','pk','country','upload','created','updated',]

        panel_profile_cols = {}
        for v in PanelProfile._meta.get_fields():
            if(v.name not in skip_cols):
                if isinstance(v, models.ForeignKey):
                    panel_profile_cols[v.name+'__code'] = v.name.replace("_", " ").capitalize()
                else:
                    panel_profile_cols[v.name] = v.name.replace("_", " ").capitalize()

        country = Country.objects.only('id','code','name').get(code=self.kwargs['country_code'])

        context.update({
            "panel_profile_cols": panel_profile_cols,
            "cell_qs": cell_qs,
        })
        return context

    def form_valid(self,form):
        country = Country.objects.get(code=self.kwargs["country_code"])

        try:
            form_obj = form.save(commit=False)
            form_obj.country = country
            form_obj.name = self.request.POST.get("name")
            form_obj.code = self.request.POST.get("code")
            form_obj.description = self.request.POST.get("description")
            form_obj.condition_html = self.request.POST.get("condition_html")
            form_obj.serialize_str = self.request.POST.get("serialize_str")
            form_obj.save()

            return super(self.__class__, self).form_valid(form)
            # messages.add_message(self.request, messages.SUCCESS, "Record saved successfully.")
            # return HttpResponseRedirect(reverse("master-data:cell-update",kwargs={"country_code": self.kwargs["country_code"],"id":form_obj.id}))

        except IntegrityError:
            messages.add_message(self.request, messages.ERROR, 'All of your Code must be unique.')
            return reverse("master-data:cell-create",kwargs={"country_code": self.kwargs["country_code"]})

    def get_queryset(self):
        queryset = Cell.objects.filter(
            country__code=self.kwargs['country_code'],
            pk=self.kwargs['pk']
        )
        return queryset

    def get_success_url(self):
            messages.add_message(self.request, messages.SUCCESS, "Record saved successfully.")
            return reverse("master-data:cell-list", kwargs={"country_code": self.kwargs["country_code"]})

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
            country__code=self.kwargs['country_code'],
            pk=self.kwargs['pk']

        )
        return queryset


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

        country = Country.objects.get(code=self.kwargs["country_code"])

        form_obj = form.save(commit=False)
        form_obj.is_processing = Upload.PROCESSING
        form_obj.process_message = "Records are processing in background, check back soon."
        form_obj.country = country
        form_obj.frommodel = "outlet_type"
        form_obj.save()

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
        {'name': 'id', 'visible': False, },
        {'name': 'code',  },
        {'name': 'name',  },
        {'name': 'urbanity',  'choices': True,'autofilter': True,},
        {'name': 'is_active',  'choices': True, 'autofilter': True,},
        {'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
            row['action'] = ('<a href="%s" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'+
                             '<a href="%s" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                    reverse('master-data:outlet-type-update', args=(self.kwargs['country_code'],obj.id,)),
                    reverse('master-data:outlet-type-delete', args=(self.kwargs['country_code'],obj.id,)),
                )
                # <a href="{1}" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>


    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__code=self.kwargs['country_code']
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
        upload = Upload.objects.filter(
            country__code=self.kwargs['country_code'], frommodel='outlet_type'
        ).last()
        if(upload is not None and  upload.is_processing != Upload.COMPLETED):
            messages.add_message(self.request, messages.SUCCESS, str(upload.is_processing +' : '+ upload.process_message))

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
        country = Country.objects.get(code=self.kwargs["country_code"])
        form_obj = form.save(commit=False)
        form_obj.country = country
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
            country__code=self.kwargs['country_code']
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
            country__code=self.kwargs['country_code'],
            pk=self.kwargs['pk']
        )
        return queryset

