""" ------------------------- Outlet Census ------------------------- """

class OutletCensusListViewAjax(AjaxDatatableView):
    model = OutletCensus
    title = 'OutletCensus'
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

            {'name': 'Category Code', 'foreign_field': 'category__code', },
            {'name': 'Category Name', 'foreign_field': 'category__name','choices': True, 'autofilter': True, },
            {'name': 'Outlet Id', 'foreign_field': 'outlet__id', },
            {'name': 'Outlet Code', 'foreign_field': 'outlet__code', },

            {'name':'nra_tagging',},
            {'name':'ra_tagging',},
            {'name':'ret_tagging',},
            {'name':'audit_date',},
            {'name':'acv'},
            {'name':'over_all_sales_from',},
            {'name':'over_all_sales_to',},
            {'name':'over_all_sales_avg',},
            {'name':'category_sales_from',},
            {'name':'category_sales_to',},
            {'name':'category_sales_avg',},

        ]

        return self.column_defs

    def customize_row(self, row, obj):

            row['action'] = ('<a href="%s" title="Delete" class="btn btn-danger btn-xs dt-delete"><span class="mdi mdi-delete-circle-outline" aria-hidden="true"></span></a>') % (
                    reverse('master-data:outlet-census-delete', args=(self.kwargs['country_code'],obj.id)),
                )

    # model._meta.fields
    def get_initial_queryset(self, request=None):
        queryset = self.model.objects.filter(
            country__id=self.request.session['country_id']
        )
        return queryset

class OutletCensusListView(LoginRequiredMixin, generic.TemplateView):
    template_name = "master_data/outlet_census_list.html"
    PAGE_TITLE = "Outlet Census"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        uploadStatusMessage(self,self.request.session['country_id'],'outlet_census')

        return context

class OutletCensusUpdateView(LoginRequiredMixin, generic.CreateView):
    template_name = "generic_import.html"
    PAGE_TITLE = "Update Outlet Census"
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
        form_obj.frommodel = "outlet_census_update"
        form_obj.save()

        print(Colors.BLUE,form_obj.pk)
        proc = Popen('python manage.py import_outlet_census_update '+str(form_obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):

        messages.add_message(self.request, messages.INFO, Upload.UPLOADING_MSG)
        return reverse("master-data:outlet-census-list", kwargs={"country_code": self.kwargs["country_code"]})


class OutletCensusImportView(LoginRequiredMixin, generic.CreateView):
    template_name = "generic_import.html"
    PAGE_TITLE = "Import Outlet Census"
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
        form_obj.frommodel = "outlet_census"
        form_obj.save()

        print(Colors.BLUE,form_obj.pk)
        proc = Popen('python manage.py import_outlet_census '+str(form_obj.pk), shell=True, stdin=stdin, stdout=stdout, stderr=stderr)

        return super(self.__class__, self).form_valid(form)

    def get_success_url(self):

        messages.add_message(self.request, messages.INFO, Upload.UPLOADING_MSG)
        return reverse("master-data:outlet-census-list", kwargs={"country_code": self.kwargs["country_code"]})


class OutletCensusDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "generic_delete.html"
    PAGE_TITLE = "Delete OutletCensus and Related Data"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, "Record deleted successfully.")
        return reverse("master-data:outlet-census-list", kwargs={"country_code": self.kwargs["country_code"]})

    def get_queryset(self):
        country = Country.objects.get(code=self.kwargs["country_code"])
        pp =  OutletCensus.objects.get(id=self.kwargs['pk'])
        month_id = pp.month_id
        outlet_id = pp.outlet_id
        cdebug(outlet_id)
        AuditData.objects.filter(country=country,outlet__id = outlet_id, month__id = month_id).delete()

        queryset =  OutletCensus.objects.filter(
            country__id=self.request.session['country_id'],
            pk=self.kwargs['pk'],
        )
        return queryset

class OutletCensusListViewAjax2(AjaxDatatableView):
    model = OutletCensus
    title = 'OutletCensus'
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
