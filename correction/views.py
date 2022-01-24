from core.common_libs_views import *


from master_data.models import AuditData, AuditDataChild,IndexCategory


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

    for v in model._meta.get_fields():
        # print(vars(v.model))

        if(v.name not in skip_cols):
            # print(type(v)=="django.db.models.fields.BooleanField")
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