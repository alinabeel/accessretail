from abc import abstractmethod
from datetime import date, datetime
import time, os, signal,logging,json
from time import strptime
from sys import stdout, stdin, stderr
from pprint import pprint
from var_dump import var_dump,var_export
from subprocess import Popen
from inspect import getmembers
from csv import DictReader

from urllib.parse import parse_qs,urlparse


from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

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



from core.helpers import getDictArray,getDicGroupList,getGroupFilter
from core.utils import prettyprint_queryset, trace, format_datetime,cdebug
from core.colors import Colors
from core.mixinsViews import PassRequestToFormViewMixin
from master_setups.models import User,Country,UserCountry,IndexSetup,UserIndex,Threshold,CountrySetting

from master_setups.forms import UserCreateModelForm,UserChangeModelForm,CountryModelForm,IndexSetupModelForm, \
                                IndexCategoryModelForm,UserCountryModelForm,ThresholdModelForm, \
                                RegionTypeModelForm,RegionModelForm,MonthModelForm,ColLabelModelForm, \
                                UserIndexModelForm

from master_data.models import Upload,RegionType,Region,Category,IndexCategory,OutletType,Outlet, \
                                CensusManager,Census,Month,UsableOutlet,PanelProfile,Product,ProductAudit, \
                                RBD,Cell,Province,District,Tehsil,CityVillage,ColLabel,OutletStatus

from master_data.forms import UploadCensusForm,CensusForm,UploadModalForm,UploadFormUpdate,CategoryListFormHelper, \
                                CategoryModelForm,OutletTypeModelForm,RBDModelForm,CellModelForm,UsableOutletModelForm, \
                                OutletStatusModelForm
from ajax_datatable.views import AjaxDatatableView


logger = logging.getLogger(__name__)

class IndexPageView(generic.TemplateView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        else:
            return redirect("login")

class HomeAjax(generic.View):
    def post(self, request):

        country_code = self.request.POST.get("country_code")
        country = Country.objects.get(code=country_code)
        user = self.request.user
        userindexs = UserIndex.objects.filter(country=country,user=user)

        if len(userindexs) >= 0:
            userindexs = userindexs[0].get_user_indexe_list()
            data = {'data':userindexs,'msg':'success'}
        else:
            data = {'data':'','msg':'failed'}

        return HttpResponse(
            json.dumps(
                data,
                cls=DjangoJSONEncoder
            ),
            content_type="application/json")

class HomeView(generic.TemplateView):
    template_name = "home.html"
    PAGE_TITLE = "Enter Into:"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def post(self, request):

        country = self.request.POST.get("country")
        index = self.request.POST.get("index")

        index = IndexSetup.objects.get(code=index)

        country = Country.objects.only('id','code','name').get(code=country)

        self.request.session['country_id'] =  country.id
        self.request.session['country_code'] =  country.code
        self.request.session['country_name'] =  country.name

        self.request.session['index_id'] =  index.id
        self.request.session['index_code'] =  index.code
        self.request.session['index_name'] =  index.name

        return HttpResponseRedirect(reverse("dashboard",kwargs={"country_code": country.code }))


    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        user = self.request.user

        usercountries = UserCountry.objects.filter(user=user)
        # userindexs = UserIndex.objects.filter(user=user)

        context.update({
            "usercountries": usercountries,
            # "userindexs": userindexs
        })

        return context


class DashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = "dashboard.html"
    PAGE_TITLE = "Dashboard"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        # country = Country.objects.only('id','code','name').get(code=self.kwargs['country_code'])

        # self.request.session['country_id'] =  country.id
        # self.request.session['country_code'] =  country.code
        # self.request.session['country_name'] =  country.name

        # context.update({

        # })

        return context



""" ------------------------- Country ------------------------- """

class CountryListView(LoginRequiredMixin, generic.ListView):
    template_name = "master_setups/country_list.html"
    # context_object_name = "objects_list"
    PAGE_TITLE = "Countries"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_queryset(self):
        user = self.request.user
        queryset = Country.objects.all()
        return queryset





class CountryCreateView(LoginRequiredMixin,  generic.CreateView):
    template_name = "master_setups/country_create.html"
    form_class = CountryModelForm
    PAGE_TITLE = "Create Country"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record created successfully.")
        return reverse("master-setups:country-list")

    def form_valid(self, form):
        country = form.save(commit=False)
        # lead.organisation = self.request.user.userprofile
        country.save()
        return super(self.__class__, self).form_valid(form)

class CountryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "master_setups/country_update.html"
    form_class = CountryModelForm
    PAGE_TITLE = "Update Country"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        return Country.objects.all()

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record updated successfully.")
        return reverse("master-setups:country-list")

    def form_valid(self, form):
        form.save()
        return super(self.__class__, self).form_valid(form)


class CountryDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "master_setups/country_delete.html"
    PAGE_TITLE = "Delete Country"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, "Record deleted successfully.")
        return reverse("master-setups:country-list")


    def get_queryset(self):
        queryset = Country.objects.filter(
            country__id=self.request.session['country_id'],
            pk=self.kwargs['pk']
        )
        return queryset

""" ------------------------- IndexSetup ------------------------- """

class IndexSetupListView(LoginRequiredMixin, generic.ListView):
    template_name = "master_setups/indexsetup_list.html"
    # context_object_name = "object"
    PAGE_TITLE = "Index List"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_queryset(self):
        user = self.request.user
        queryset = IndexSetup.objects.filter(country__id=self.request.session['country_id'])
        return queryset


class IndexSetupCreateView(LoginRequiredMixin,  generic.CreateView):
    template_name = "master_setups/indexsetup_create.html"
    form_class = IndexSetupModelForm
    PAGE_TITLE = "Create Index"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        return reverse("master-setups:indexsetup-list", kwargs={"country_code": self.kwargs["country_code"]})

    def form_valid(self, form):
        form_obj = form.save(commit=False)
        form_obj.country_id = self.request.session['country_id']
        form_obj.save()
        messages.add_message(self.request, messages.SUCCESS, "Record created successfully.")
        return super(self.__class__, self).form_valid(form)

class IndexSetupUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "master_setups/indexsetup_update.html"
    form_class = IndexSetupModelForm
    PAGE_TITLE = "Update Index"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        queryset = IndexSetup.objects.filter(country__id=self.request.session['country_id'])
        return queryset

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record updated successfully.")
        return reverse("master-setups:indexsetup-list", kwargs={"country_code": self.kwargs["country_code"]})


class IndexSetupDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "master_setups/indexsetup_delete.html"
    PAGE_TITLE = "Delete IndexSetup"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, "Record deleted successfully.")
        return reverse("master-setups:indexsetup-list", kwargs={"country_code": self.kwargs["country_code"]})

    def get_queryset(self):
        queryset = IndexSetup.objects.filter(
            country__id=self.request.session['country_id'],
            pk=self.kwargs['pk']
        )
        return queryset



""" ------------------------- IndexCategory ------------------------- """


class IndexCategoryListViewAjax(AjaxDatatableView):
    model = IndexCategory
    title = 'IndexCategory'
    initial_order = [["index_setup", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'

    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id', 'visible': False, },
        {'name': 'index_setup',  },
        {'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
            row['action'] = ('<a href="%s" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'+
                             '<a href="%s" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                    reverse('master-setups:indexcategory-update', args=(self.kwargs['country_code'],obj.id,)),
                    reverse('master-setups:indexcategory-delete', args=(self.kwargs['country_code'],obj.id,)),
                )
                # <a href="{1}" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>


    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset




class IndexCategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = "master_setups/indexcategory_list.html"
    PAGE_TITLE = "Index Categories"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE,
    }

    def get_queryset(self):
        queryset = IndexCategory.objects.filter(country__id=self.request.session['country_id'])

        return queryset




class IndexCategoryCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "master_setups/indexcategory_create.html"
    form_class = IndexCategoryModelForm
    PAGE_TITLE = "Create Index Category"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record saved successfully.")
        return reverse("master-setups:indexcategory-list", kwargs={"country_code": self.kwargs["country_code"]})

    def form_valid(self, form):
        form_obj = form.save(commit=False)
        form_obj.country_id = self.request.session['country_id']
        form_obj.save()
        return super(self.__class__, self).form_valid(form)

class IndexCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "master_setups/indexcategory_update.html"
    form_class = IndexCategoryModelForm
    PAGE_TITLE = "Update Index Category"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_queryset(self):
        queryset = IndexCategory.objects.filter(country__id=self.request.session['country_id'])
        return queryset

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record updated successfully.")
        return reverse("master-setups:indexcategory-list", kwargs={"country_code": self.kwargs["country_code"]})

    def form_valid(self, form):
        form.save()
        return super(self.__class__, self).form_valid(form)

class IndexCategoryDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "generic_delete.html"
    PAGE_TITLE = "Delete Index Category"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, "Record deleted successfully.")
        return reverse("master-setups:indexcategory-list", kwargs={"country_code": self.kwargs["country_code"]})

    def get_queryset(self):
        queryset = IndexCategory.objects.filter(
            country__id=self.request.session['country_id'],
            pk=self.kwargs['pk']
        )
        return queryset

""" ------------------------- User ------------------------- """

class UserListViewAjax(AjaxDatatableView):
    model = User
    title = 'User'
    initial_order = [["first_name", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'

    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id', 'visible': False, },
        {'name': 'email',  },
        {'name': 'first_name',  },
        {'name': 'last_name',  },

        {'name': 'phone_no',  },
        {'name': 'city', 'choices': True, 'autofilter': True, },
        {'name': 'state', 'choices': True, 'autofilter': True, },
        {'name': 'zip', 'choices': True, 'autofilter': True, },
        {'name': 'country', 'choices': True, 'autofilter': True, },

        {'name': 'role',  'choices': True, 'autofilter': True,  },
        {'name': 'is_superuser',  'choices': True, 'autofilter': True,  },
        {'name': 'is_active',  'choices': True, 'autofilter': True,  },
        {'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
            row['action'] = ('<a href="%s" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'+
                             '<a href="%s" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                    reverse('master-setups:user-update', args=(self.kwargs['country_code'],obj.id,)),
                    reverse('master-setups:user-delete', args=(self.kwargs['country_code'],obj.id,)),
                )
                # <a href="{1}" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>


    # def get_initial_queryset(self, request=None):

    #     queryset = self.model.objects.filter(
    #         country__id=self.request.session['country_id']
    #     )
    #     return queryset


def change_password(request,country_code,pk):
    if request.method == 'POST':
        user_rs =  User.objects.get(id=pk)
        form = PasswordChangeForm(user_rs, request.POST)
        if form.is_valid():
            user = form.save()
            # update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('master-setups:user-list', country_code = country_code)
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        user =  User.objects.get(id=pk)
        form = PasswordChangeForm(user)
    return render(request, 'registration/change_password.html', {
        'form': form
    })

class UserListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "master_setups/user_list.html"
    PAGE_TITLE = "Users"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE,
    }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        return context


class UserCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "master_setups/user_create.html"
    form_class = UserCreateModelForm
    PAGE_TITLE = "Create User"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    # def get_form_kwargs(self):
    #     kwargs = super(self.__class__, self).get_form_kwargs()
    #     # kwargs['country_code'] = self.kwargs["country_code"]
    #     return kwargs


    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record saved successfully.")
        return reverse("master-setups:user-list", kwargs={"country_code": self.kwargs["country_code"]})

    def form_valid(self, form):
        form_obj = form.save(commit=False)
        form_obj.save()
        return super(self.__class__, self).form_valid(form)

class UserUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "master_setups/user_update.html"
    form_class = UserChangeModelForm
    PAGE_TITLE = "Update User"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }
    # def get_form_kwargs(self):
    #     kwargs = super(self.__class__, self).get_form_kwargs()
    #     # kwargs['request'] = self.request
    #     kwargs['country_code'] = self.kwargs["country_code"]
    #     return kwargs

    def get_queryset(self):
        queryset = User.objects.filter(
            # country__id=self.request.session['country_id']
        )
        return queryset

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record updated successfully.")
        return reverse("master-setups:user-list", kwargs={"country_code": self.kwargs["country_code"]})

    def form_valid(self, form):
        form.save()
        return super(self.__class__, self).form_valid(form)


class UserDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "generic_delete.html"
    PAGE_TITLE = "Delete User"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, "Record deleted successfully.")
        return reverse("master-setups:user-list", kwargs={"country_code": self.kwargs["country_code"]})

    def get_queryset(self):
        queryset = User.objects.filter(
            country__id=self.request.session['country_id'],
            pk=self.kwargs['pk']
        )
        return queryset




""" ------------------------- User Countries ------------------------- """

class UserCountryListView(LoginRequiredMixin, generic.ListView):
    template_name = "master_setups/usercountry_list.html"
    # context_object_name = "object"
    PAGE_TITLE = "User List in Country"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_queryset(self):
        user = self.request.user
        queryset = UserCountry.objects.filter(country__id=self.request.session['country_id'])

        return queryset


class UserCountryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "master_setups/usercountry_update.html"
    form_class = UserCountryModelForm
    PAGE_TITLE = "Update Country Users"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        queryset = UserCountry.objects.filter(country__id=self.request.session['country_id'])
        return queryset

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record updated successfully.")
        return reverse("master-setups:usercountry-list", kwargs={"country_code": self.kwargs["country_code"]})

""" ------------------------- UserIndex ------------------------- """


class UserIndexListViewAjax(AjaxDatatableView):
    model = UserIndex
    title = 'UserIndex'
    initial_order = [["user", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'

    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id', 'visible': False, },
        {'name': 'user',  },
        {'name': 'user_index',  },
        {'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
            row['action'] = ('<a href="%s" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'+
                             '<a href="%s" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                    reverse('master-setups:userindex-update', args=(self.kwargs['country_code'],obj.id,)),
                    reverse('master-setups:userindex-delete', args=(self.kwargs['country_code'],obj.id,)),
                )
                # <a href="{1}" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>


    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset


class UserIndexListView(LoginRequiredMixin, generic.ListView):
    template_name = "master_setups/userindex_list.html"
    PAGE_TITLE = "User Index"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE,
    }

    def get_queryset(self):
        queryset = UserIndex.objects.filter(country__id=self.request.session['country_id'])
        return queryset



class UserIndexCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "master_setups/userindex_create.html"
    form_class = UserIndexModelForm
    PAGE_TITLE = "Create User Index"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record saved successfully.")
        return reverse("master-setups:userindex-list", kwargs={"country_code": self.kwargs["country_code"]})

    def form_valid(self, form):
        form_obj = form.save(commit=False)
        form_obj.country_id = self.request.session['country_id']
        form_obj.save()
        return super(self.__class__, self).form_valid(form)

class UserIndexUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "master_setups/userindex_update.html"
    form_class = UserIndexModelForm
    PAGE_TITLE = "Update User Index"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_queryset(self):
        queryset = UserIndex.objects.filter(country__id=self.request.session['country_id'])
        return queryset

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record updated successfully.")
        return reverse("master-setups:userindex-list", kwargs={"country_code": self.kwargs["country_code"]})

    def form_valid(self, form):
        form.save()
        return super(self.__class__, self).form_valid(form)

class UserIndexDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "generic_delete.html"
    PAGE_TITLE = "Delete User Index"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, "Record deleted successfully.")
        return reverse("master-setups:userindex-list", kwargs={"country_code": self.kwargs["country_code"]})

    def get_queryset(self):
        queryset = UserIndex.objects.filter(
            country__id=self.request.session['country_id'],
            pk=self.kwargs['pk']
        )
        return queryset



""" ------------------------- Threshold ------------------------- """

class ThresholdListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "master_setups/threshold.html"
    PAGE_TITLE = "Threshold Settings"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, **kwargs):

        context = super(self.__class__, self).get_context_data(**kwargs)
        threshold = Threshold.objects.filter(
            country__id=self.request.session['country_id']
        )
        context.update({
            "threshold": threshold,
        })
        return context

    def get_queryset(self):
        queryset = Threshold.objects.filter(country__id=self.request.session['country_id'])


        # return redirect('master-setups:threshold-update', country_code = self.kwargs["country_code"])
        # return reverse("master-setups:thresholdZupdate", kwargs={"country_code": self.kwargs["country_code"]})
        return queryset

class ThresholdUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "master_setups/threshold_update.html"
    form_class = ThresholdModelForm
    model = Threshold
    PAGE_TITLE = "Update Threshold Settings"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }


    def form_valid(self, form):

        try:
            threshold = Threshold.objects.get(country__id = self.request.session['country_id'])
        except Threshold.DoesNotExist:
            threshold = None

        if  threshold is None:
            form_obj = form.save(commit=False)
            form_obj.country_id = self.request.session['country_id']
            form_obj.save()
        else:
            form_obj = form.save(commit=False)
            form_obj.created = datetime.now()
            form_obj.pk = threshold.id
            form_obj.country_id = self.request.session['country_id']
            form_obj.save()

        # management.call_command('import_census',self.kwargs["country_code"])
        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):
        # return reverse("leads:lead-detail", kwargs={"pk": self.kwargs["pk"]})
        return reverse("master-setups:threshold", kwargs={"country_code": self.kwargs["country_code"]})

    def get_object(self, queryset=None):
        return self.model.objects.filter(country__id=self.request.session['country_id']).first()

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        queryset = Threshold.objects.filter(country__id=self.request.session['country_id'])
        return queryset

    # def get_success_url(self):
    #     messages.add_message(self.request, messages.SUCCESS, "Record updated successfully.")
    #     return reverse("master-setups:threshold", kwargs={"country_code": self.kwargs["country_code"]})


""" ------------------------- RegionType ------------------------- """

class RegionTypeImportView(LoginRequiredMixin, generic.CreateView):
    template_name = "generic_import.html"
    PAGE_TITLE = "Import RegionTypes"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    form_class = UploadModalForm

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        # queryset = Upload.objects.filter(country__id=self.request.session['country_id'])
        return context

    def form_valid(self, form):

        form_obj = form.save(commit=False)
        form_obj.is_processing = Upload.PROCESSING
        form_obj.process_message = "Records are processing in background, check back soon."
        form_obj.country_id = self.request.session['country_id']
        form_obj.frommodel = "region_type"
        form_obj.save()

        proc = Popen('python manage.py import_region_type '+str(form_obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        # management.call_command('import_census',self.kwargs["country_code"])
        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):
        # return reverse("leads:lead-detail", kwargs={"pk": self.kwargs["pk"]})
        messages.add_message(self.request, messages.SUCCESS, "File uploaded successfully, processing records.")

        return reverse("master-setups:region-type-list", kwargs={"country_code": self.kwargs["country_code"]})


class RegionTypeListViewAjax(AjaxDatatableView):
    model = RegionType
    title = 'RegionType'
    initial_order = [["name", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'

    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id', 'visible': False, },
        {'name': 'name', },
        {'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
            row['action'] = ('<a href="%s" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'+
                             '<a href="%s" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                    reverse('master-setups:region-type-update', args=(self.kwargs['country_code'],obj.id,)),
                    reverse('master-setups:region-type-delete', args=(self.kwargs['country_code'],obj.id,)),
                )
                # <a href="{1}" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>


    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset




class RegionTypeListView(LoginRequiredMixin, generic.TemplateView):
    # template_name = "master_setups/region_type_list.html"
    template_name = "master_setups/region_type_list.html"
    PAGE_TITLE = "RegionTypes"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE,
    }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        upload = Upload.objects.filter(
            country__id=self.request.session['country_id'], frommodel='region_type'
        ).last()
        if(upload is not None and  upload.is_processing != Upload.COMPLETED):
            messages.add_message(self.request, messages.SUCCESS, str(upload.is_processing +' : '+ upload.process_message))

        return context


class RegionTypeCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "generic_create.html"
    form_class = RegionTypeModelForm
    PAGE_TITLE = "Create RegionType"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record saved successfully.")
        return reverse("master-setups:region-type-list", kwargs={"country_code": self.kwargs["country_code"]})

    def form_valid(self, form):

        form_obj = form.save(commit=False)
        form_obj.country_id = self.request.session['country_id']
        form_obj.save()
        return super(self.__class__, self).form_valid(form)

class RegionTypeUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "generic_update.html"
    form_class = RegionTypeModelForm
    PAGE_TITLE = "Update RegionType"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }


    def get_queryset(self):
        queryset = RegionType.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record updated successfully.")
        return reverse("master-setups:region-type-list", kwargs={"country_code": self.kwargs["country_code"]})

    def form_valid(self, form):
        form.save()
        return super(self.__class__, self).form_valid(form)


class RegionTypeDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "generic_delete.html"
    PAGE_TITLE = "Delete RegionType"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, "Record deleted successfully.")
        return reverse("master-setups:region-type-list", kwargs={"country_code": self.kwargs["country_code"]})

    def get_queryset(self):
        queryset = RegionType.objects.filter(
            country__id=self.request.session['country_id'],
            pk=self.kwargs['pk']
        )
        return queryset


""" ------------------------- Region ------------------------- """

class RegionImportView(LoginRequiredMixin, generic.CreateView):
    template_name = "master_setups/region_import.html"
    PAGE_TITLE = "Import Regions"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    form_class = UploadModalForm

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        # queryset = Upload.objects.filter(country__id=self.request.session['country_id'])
        return context

    def form_valid(self, form):

        form_obj = form.save(commit=False)
        form_obj.is_processing = Upload.PROCESSING
        form_obj.process_message = "Records are processing in background, check back soon."
        form_obj.country_id = self.request.session['country_id']
        form_obj.frommodel = "region"
        form_obj.save()

        proc = Popen('python manage.py import_region '+str(form_obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        # management.call_command('import_census',self.kwargs["country_code"])
        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):
        # return reverse("leads:lead-detail", kwargs={"pk": self.kwargs["pk"]})
        messages.add_message(self.request, messages.SUCCESS, "File uploaded successfully, processing records.")

        return reverse("master-setups:region-list", kwargs={"country_code": self.kwargs["country_code"]})


class RegionListViewAjax(AjaxDatatableView):
    model = Region
    title = 'Region'
    initial_order = [["code", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'

    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id', 'visible': False, },
        {'name': 'code',  },
        {'name': 'name',  },
        {'name': 'region_type', 'foreign_field': 'region_type__name','choices': True, 'autofilter': True,},
        {'name': 'parent', 'foreign_field': 'parent__name',   'choices': True, 'autofilter': True,},
        {'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
            row['action'] = ('<a href="%s" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'+
                             '<a href="%s" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                    reverse('master-setups:region-update', args=(self.kwargs['country_code'],obj.id,)),
                    reverse('master-setups:region-delete', args=(self.kwargs['country_code'],obj.id,)),
                )
                # <a href="{1}" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>


    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset




class RegionListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "master_setups/region_list.html"
    PAGE_TITLE = "Regions"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE,
    }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        upload = Upload.objects.filter(
            country__id=self.request.session['country_id'], frommodel='region'
        ).last()
        if(upload is not None and  upload.is_processing != Upload.COMPLETED):
            messages.add_message(self.request, messages.SUCCESS, str(upload.is_processing +' : '+ upload.process_message))

        return context


class RegionCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "master_setups/region_create.html"
    form_class = RegionModelForm
    PAGE_TITLE = "Create Region"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_form_kwargs(self):
        kwargs = super(self.__class__, self).get_form_kwargs()
        # kwargs['request'] = self.request
        kwargs['country_code'] = self.kwargs["country_code"]
        return kwargs


    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record saved successfully.")
        return reverse("master-setups:region-list", kwargs={"country_code": self.kwargs["country_code"]})

    def form_valid(self, form):

        form_obj = form.save(commit=False)
        form_obj.country_id = self.request.session['country_id']
        form_obj.save()
        return super(self.__class__, self).form_valid(form)

class RegionUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "master_setups/region_update.html"
    form_class = RegionModelForm
    PAGE_TITLE = "Update Region"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }
    def get_form_kwargs(self):
        kwargs = super(self.__class__, self).get_form_kwargs()
        # kwargs['request'] = self.request
        kwargs['country_code'] = self.kwargs["country_code"]
        return kwargs

    def get_queryset(self):
        queryset = Region.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record updated successfully.")
        return reverse("master-setups:region-list", kwargs={"country_code": self.kwargs["country_code"]})

    def form_valid(self, form):
        form.save()
        return super(self.__class__, self).form_valid(form)


class RegionDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "generic_delete.html"
    PAGE_TITLE = "Delete Region"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, "Record deleted successfully.")
        return reverse("master-setups:region-list", kwargs={"country_code": self.kwargs["country_code"]})

    def get_queryset(self):
        queryset = Region.objects.filter(
            country__id=self.request.session['country_id'],
            pk=self.kwargs['pk']
        )
        return queryset


""" ------------------------- Month ------------------------- """

class MonthImportView(LoginRequiredMixin, generic.CreateView):
    template_name = "master_setups/month_import.html"
    PAGE_TITLE = "Import Months"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    form_class = UploadModalForm

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        # queryset = Upload.objects.filter(country__id=self.request.session['country_id'])
        return context

    def form_valid(self, form):

        form_obj = form.save(commit=False)
        form_obj.is_processing = Upload.PROCESSING
        form_obj.process_message = "Records are processing in background, check back soon."
        form_obj.country_id = self.request.session['country_id']
        form_obj.frommodel = "month"
        form_obj.save()

        proc = Popen('python manage.py import_month '+str(form_obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        # management.call_command('import_census',self.kwargs["country_code"])
        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):
        # return reverse("leads:lead-detail", kwargs={"pk": self.kwargs["pk"]})
        messages.add_message(self.request, messages.SUCCESS, "File uploaded successfully, processing records.")

        return reverse("master-setups:month-list", kwargs={"country_code": self.kwargs["country_code"]})

class MonthListViewAjax(AjaxDatatableView):
    model = Month
    title = 'Months'
    initial_order = [["month", "asc"],["year","asc"] ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'


    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id', 'visible': False, },
        {'name': 'code',  },
        {'name': 'name',  },
        {'name': 'month',  'choices': True, 'autofilter': True,  },
        {'name': 'year',  'choices': True, 'autofilter': True,  },
        {'name': 'is_locked',  'choices': True, 'autofilter': True,},

        {'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
            row['action'] = ('<a href="%s" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>'+
                             '<a href="%s" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                    reverse('master-setups:month-update', args=(self.kwargs['country_code'],obj.id,)),
                    reverse('master-setups:month-delete', args=(self.kwargs['country_code'],obj.id,)),
                )
                # <a href="{1}" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>


    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset

class MonthListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "master_setups/month_list.html"
    PAGE_TITLE = "Months"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        upload = Upload.objects.filter(
            country__id=self.request.session['country_id'], frommodel='month'
        ).last()
        if(upload is not None and  upload.is_processing != Upload.COMPLETED):
            messages.add_message(self.request, messages.SUCCESS, str(upload.is_processing +' : '+ upload.process_message))

        return context

class MonthCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "master_setups/month_create.html"
    form_class = MonthModelForm
    PAGE_TITLE = "Create Month"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record saved successfully.")
        return reverse("master-setups:month-list", kwargs={"country_code": self.kwargs["country_code"]})

    def get_form_kwargs(self):
        kwargs = super(self.__class__, self).get_form_kwargs()
        # kwargs['request'] = self.request
        kwargs['country_code'] = self.kwargs["country_code"]
        return kwargs

    def form_valid(self, form):
        print(self.request.POST.get("is_current_month"))
        month_name = self.request.POST.get("name")
        month_number = strptime(month_name,'%B').tm_mon

        form_obj = form.save(commit=False)
        form_obj.country_id = self.request.session['country_id']
        form_obj.month = month_number
        form_obj.save()
        return super(self.__class__, self).form_valid(form)

class MonthUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "master_setups/month_update.html"
    form_class = MonthModelForm
    PAGE_TITLE = "Update Month"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }
    def get_form_kwargs(self):
        kwargs = super(self.__class__, self).get_form_kwargs()
        # kwargs['request'] = self.request
        kwargs['country_code'] = self.kwargs["country_code"]
        return kwargs

    def form_valid(self, form):
        month_name = self.request.POST.get("name")
        month_number = strptime(month_name,'%B').tm_mon

        form_obj = form.save(commit=False)
        form_obj.country_id = self.request.session['country_id']
        form_obj.month = month_number
        form.save()
        return super(self.__class__, self).form_valid(form)

    def get_queryset(self):
        queryset = Month.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record updated successfully.")
        return reverse("master-setups:month-list", kwargs={"country_code": self.kwargs["country_code"]})


class MonthDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "master_setups/month_delete.html"
    PAGE_TITLE = "Delete Month"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, "Record deleted successfully.")
        return reverse("master-setups:month-list", kwargs={"country_code": self.kwargs["country_code"]})

    def get_queryset(self):
        queryset = Month.objects.filter(
            country__id=self.request.session['country_id'],
            pk=self.kwargs['pk']
        )
        return queryset


""" ------------------------- CodeFrame ------------------------- """

class CodeFrameImportView(LoginRequiredMixin, generic.CreateView):
    template_name = "generic_import.html"
    PAGE_TITLE = "Import CodeFrames"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    form_class = UploadModalForm

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        # queryset = Upload.objects.filter(country__id=self.request.session['country_id'])
        return context

    def form_valid(self, form):

        form_obj = form.save(commit=False)
        form_obj.is_processing = Upload.PROCESSING
        form_obj.process_message = "Records are processing in background, check back soon."
        form_obj.country_id = self.request.session['country_id']
        form_obj.frommodel = "code_frame"
        form_obj.save()

        cdebug(form_obj.pk)
        proc = Popen('python manage.py import_code_frame '+str(form_obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        # management.call_command('import_census',self.kwargs["country_code"])
        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):
        # return reverse("leads:lead-detail", kwargs={"pk": self.kwargs["pk"]})
        messages.add_message(self.request, messages.SUCCESS, "File uploaded successfully, processing records.")

        return reverse("master-setups:code-frame-list", kwargs={"country_code": self.kwargs["country_code"]})

class CodeFrameListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "master_setups/code_frame_list.html"
    PAGE_TITLE = "Code Frame"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE,
    }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        upload = Upload.objects.filter(
            country__id=self.request.session['country_id'], frommodel='code_frame'
        ).last()
        if(upload is not None and  upload.is_processing != Upload.COMPLETED):
            messages.add_message(self.request, messages.SUCCESS, str(upload.is_processing +' : '+ upload.process_message))

        return context

class CodeFrameListViewAjax(AjaxDatatableView):
    model = CityVillage
    title = 'Code Frame'
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

            {'name': 'Province Code', 'foreign_field': 'tehsil__district__province__code', },
            {'name': 'Province Name', 'foreign_field': 'tehsil__district__province__name', 'choices': True, 'autofilter': True,},
            {'name': 'District Code', 'foreign_field': 'tehsil__district__code',},
            {'name': 'District Name', 'foreign_field': 'tehsil__district__name', 'choices': True, 'autofilter': True,},

            {'name': 'Tehsil Code', 'foreign_field': 'tehsil__code',},
            {'name': 'Tehsil Name', 'foreign_field': 'tehsil__name', 'choices': True, 'autofilter': True,},
            {'name': 'Urbanity', 'foreign_field': 'tehsil__urbanity', 'choices': True, 'autofilter': True,},

            {'name': 'code', 'title':'City Code',},
            {'name': 'name', 'title':'City Name', },
            {'name': 'rc_cut', 'choices': True, 'autofilter': True,},
        ]

        for v in self.__class__.model._meta.get_fields():
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
                self.column_defs.append({'name': v.name,'title':title, 'choices': True, 'autofilter': True, })
        return self.column_defs

    def get_initial_queryset(self, request=None):
        queryset = self.model.objects.filter(
            country__id=self.request.session['country_id']
        )

        return queryset


""" ------------------------- OutletStatus ------------------------- """
class OutletStatusListViewAjax(AjaxDatatableView):
    model = OutletStatus
    title = 'Outlet Status'
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
                    reverse('master-setups:outlet-status-update', args=(self.kwargs['country_code'],obj.id,)),
                    reverse('master-setups:outlet-status-delete', args=(self.kwargs['country_code'],obj.id,)),
                )
                # <a href="{1}" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>


    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset



class OutletStatusListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "master_data/outlet_status_list.html"
    PAGE_TITLE = "Outlet Statuses"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        upload = Upload.objects.filter(
            country__id=self.request.session['country_id'], frommodel='outlet_status'
        ).last()
        if(upload is not None and  upload.is_processing != Upload.COMPLETED):
            messages.add_message(self.request, messages.SUCCESS, str(upload.is_processing +' : '+ upload.process_message))

        return context


class OutletStatusCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "generic_create.html"
    form_class = OutletStatusModelForm
    PAGE_TITLE = "Create Outlet Status"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record saved successfully.")
        return reverse("master-setups:outlet-status-list", kwargs={"country_code": self.kwargs["country_code"]})

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

class OutletStatusUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "generic_update.html"
    form_class = OutletStatusModelForm
    PAGE_TITLE = "Update Outlet Status"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_queryset(self):
        queryset = OutletStatus.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record updated successfully.")
        return reverse("master-setups:outlet-status-list", kwargs={"country_code": self.kwargs["country_code"]})

    def form_valid(self, form):
        form.save()
        return super(self.__class__, self).form_valid(form)


class OutletStatusDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "generic_delete.html"
    PAGE_TITLE = "Delete Outlet Status"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, "Record deleted successfully.")
        return reverse("master-setups:outlet-status-list", kwargs={"country_code": self.kwargs["country_code"]})

    def get_queryset(self):
        queryset = OutletStatus.objects.filter(
            country__id=self.request.session['country_id'],
            pk=self.kwargs['pk']
        )
        return queryset

""" ------------------------- ColLabel ------------------------- """
class ColLabelListViewAjax(AjaxDatatableView):
    model = ColLabel
    initial_order = [["model_name", "asc"],["col_name", "asc"], ]
    length_menu = [[10, 20, 50, 100, 500], [10, 20, 50, 100, 500]]
    search_values_separator = '+'


    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id', 'title':'ID', 'visible': True, },
        {'name': 'model_name', 'choices': True, 'autofilter': True,},
        {'name': 'col_name',  },
        {'name': 'col_label',  },

        {'name': 'action', 'title': 'Action', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
            row['action'] = ('<a href="%s" class="btn btn-primary btn-xs dt-edit" style="margin-right:16px;"><span class="mdi mdi-circle-edit-outline" aria-hidden="true"></span></a>') % (
                    reverse('master-setups:col-label-update', args=(self.kwargs['country_code'],obj.id,)),
                )
                # <a href="{1}" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>


    def get_initial_queryset(self, request=None):

        queryset = self.model.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset



class ColLabelListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "master_setups/col_label_list.html"
    PAGE_TITLE = "Col Labels"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        return context


class UpdateSyncFieldsAjax(LoginRequiredMixin, generic.CreateView):
    def post(self, request, country_code):
        country = Country.objects.get(code=self.kwargs["country_code"])
        action = self.request.POST.get("action")

        # for v in Product._meta.get_fields():
        #     if(v.name not in skip_cols):
        #         product_fields.append(v.name)

        skip_cols = ['id','pk','code','name','country','upload','created','updated',]
        for m,mm in ColLabel.MODEL_CHOICES:
            for field in eval(m)._meta.get_fields():
                if(field.name in skip_cols): continue
                if isinstance(field, models.ForeignKey): continue
                if isinstance(field, models.ManyToManyRel): continue
                if isinstance(field, models.ManyToOneRel): continue

                label = field.name
                label = label.replace('_',' ')
                label = label.title()
                col_label_qs, created = ColLabel.objects.get_or_create(
                    country=country, model_name=m,col_name=field.name,
                    defaults={'col_label':label}
                )

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
        # obj = ColLabel.objects.get(pk=id,country=country)
        # obj.status  = value
        # obj.save()

        return HttpResponse(
            json.dumps(
                {'data':'success'},
                cls=DjangoJSONEncoder
            ),
            content_type="application/json")

class ColLabelUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "generic_update.html"
    form_class = ColLabelModelForm
    PAGE_TITLE = "Update Col Labels"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_queryset(self):
        queryset = ColLabel.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Record updated successfully.")
        return reverse("master-setups:col-label-list", kwargs={"country_code": self.kwargs["country_code"]})

    def form_valid(self, form):
        form.save()
        return super(self.__class__, self).form_valid(form)

class ResetDBView(LoginRequiredMixin, generic.TemplateView):
    template_name = "resetdb.html"
    PAGE_TITLE = "Reset Datbase"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)

        mastert_data = ['RBD','Cell','Product','ProductAudit','PanelProfile','Outlet','UsableOutlet','Upload']
        # mastert_setups = ['Upload','Province','District','Tehsil','CityVillage','Category','IndexCategory','OutletType','Census','Month','OutletStatus','ColLabel',]

        context.update({
            "mastert_data": mastert_data
        })

        return context
    def post(self, request, country_code, *args, **kwargs):
        country_id = self.request.session['country_id']
        reset = self.request.POST
        # reset = self.request.POST
        cdebug(type(reset))
        cdebug(reset)
        for key, value in reset.items():
            if key in 'csrfmiddlewaretoken': continue
            eval(f"{key}").objects.filter(country__id=self.request.session['country_id']).delete()
            print(key, value)

        return HttpResponse(
            json.dumps(
                {'data':'success'},
                cls=DjangoJSONEncoder
            ),
            content_type="application/json")