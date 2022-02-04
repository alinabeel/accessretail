from core.common_libs_views import *


from master_data.models import AuditData, AuditDataChild,IndexCategory,PanelProfile,PanelProfileChild,CityVillage,ColLabel


""" ------------------------- Audit Data Child------------------------- """

class AuditDataListViewAjax(AjaxDatatableView):
    model = AuditDataChild
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

        {'name': 'product','title':'Product Code', 'foreign_field': 'product__code',},

        ]

    skip_cols = ['id','pk','country','upload','created','updated',
                 'month', 'period', 'category', 'outlet', 'product','audit_status']

    for field in model._meta.get_fields():
        # print(vars(v.model))
        if(field.name in skip_cols):
            continue
        # if field.name == 'flag_stock':
        #     # pprint(getmembers(field))
        #     cdebug(field)

        if f"{field.__class__}".find('BooleanField') != -1:
            # printr(f"BooleanField: {field.name}")
            column_defs.append({'name':field.name, 'choices': True, 'autofilter': True, })
        else:
            column_defs.append({'name':field.name})


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
    template_name = "correction/audit_data_list.html"
    PAGE_TITLE = "Audit Data - Correction"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        uploadStatusMessage(self,self.request.session['country_id'],'audit_data')

        return context

""" ------------------------- Panel Profile ------------------------- """

class PanelProfileListViewAjax(AjaxDatatableView):
    model = PanelProfileChild
    title = 'PanelProfileChild'
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
            # {'name':'lms', 'choices': True, 'autofilter': True,},
            # {'name':'cell_description',},
            # {'name':'nra_tagging',},
            # {'name':'ra_tagging',},
            # {'name':'ret_tagging',},
            # {'name':'audit_date',},
            # {'name':'acv'},

        ]

        skip_cols = ['id','pk','country','upload','created','updated','audit_status']


        for field in PanelProfileChild._meta.get_fields():
            if isinstance(field, models.ForeignKey): continue
            if isinstance(field, models.ManyToManyRel): continue
            if isinstance(field, models.ManyToOneRel): continue
            # if field.name is 'is_valid':
            #     # pprint(getmembers(field))
            #     cdebug(field)

            if(field.name not in skip_cols):
                # print(type(v)=="django.db.models.fields.BooleanField")
                if f"{field}".find('BooleanField') != -1:
                    self.column_defs.append({'name':field.name, 'choices': True, 'autofilter': True, })
                else:
                    self.column_defs.append({'name':field.name})
        # cdebug(self.column_defs[0])
        # cdebug(type(self.column_defs[0]))
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
                title = f'CityVillage - {title}'
                # if ('name',title) in self.column_defs:
                #     title = f'CityVillage {title}'

                self.column_defs.append({'name': title,'title':title, 'foreign_field': 'city_village__'+field.name, 'choices': True, 'autofilter': True, })

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
    template_name = "correction/panel_profile_list.html"
    PAGE_TITLE = "Correction - Panel Profile"
    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        uploadStatusMessage(self,self.request.session['country_id'],'panel_profile')

        return context

class InspectionSummeryView(LoginRequiredMixin, generic.TemplateView):
    template_name = "correction/inspection_summery.html"
    PAGE_TITLE = "Loading/Inspection Summery"

    extra_context = {
        'page_title': PAGE_TITLE,
        'header_title': PAGE_TITLE
    }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)

        # ad_child = AuditDataChild.objects.filter(user=user)
        # userindexs = UserIndex.objects.filter(user=user)

        context.update({
            # "usercountries": usercountries,
            # "userindexs": userindexs
        })

        return context

