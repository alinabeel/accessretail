from django import forms
from django.forms import fields,ModelForm, Textarea
from django.core.exceptions import ValidationError
from django_json_widget.widgets import JSONEditorWidget
from django.contrib.auth import get_user_model


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django_select2 import forms as s2forms
from django.contrib.sessions.models import Session

from master_data.models import *
from pprintpp import pprint as pp


User = get_user_model()

class UploadCensusForm(forms.Form):
 file = forms.FileField()



class CensusForm(forms.ModelForm):

    class Meta:
        model = Census
        fields = ('country', "censusdata",)
        widgets = {
            'censusdata': JSONEditorWidget
        }

class UploadModalForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = (
            'import_mode',
            'file'
        )

class UploadFormUpdate(forms.ModelForm):
    import_mode = forms.ChoiceField(choices = Upload.CHOICES_UPDATE)
    class Meta:
        model = Upload
        fields = (
            'import_mode',
            'file'
        )


class CategoryListFormHelper(FormHelper):
    model = Category
    form_tag = False
    form_method = 'GET'
    layout = Layout(
        'name',
        Submit('submit', 'Filter'),
    )
class CategoryModelForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name','code', 'parent', 'description', 'is_active', )

class OutletTypeModelForm(forms.ModelForm):
    #
    # def __init__(self, category = None, *args, **kwargs):
    #     self.request = kwargs.pop("request")
    #     super(OutletTypeModelForm, self).__init__(*args, **kwargs)
    #     country_code = self.request.session.get('country_code')
    #     # category = forms.ModelChoiceField(queryset=)
    #     qs_category = Category.objects.filter(country__code=country_code)
    #     self.fields['category'].queryset = qs_category
    class Meta:
        model = OutletType
        fields = ('name','code', 'parent','urbanity' ,'description', 'is_active', )
        # self.fields['category'].queryset = Category.objects.filter(country__code = request.session['country_code'])

        # print(args,self)
    # def __init__(self, *args, **kwargs):
        # country_code = kwargs.pop('country_code')

        # self.category = forms.ModelChoiceField(queryset=Category.objects.filter(country__code=country_code))

        # widgets ={
        #     "category": CategoryWidget,
        #     "parent" : OutletTypeWidget,
        # }

    # def __init__(self, user, *args, **kwargs):
    #     print(self.data,args,kwargs,user)
    #     # super(OutletTypeModelForm, self).__init__(*args, **kwargs)
    #     self.fields['category'].queryset = Category.objects.filter(
    #         country__code='PK'
    #     )

class RBDModelForm(forms.ModelForm):
    MAX_TREE_DEPTH = 1

    def __init__(self,*args,**kwargs):
        self.country_code = kwargs.pop('country_code')
        self.parent = kwargs.pop('parent')
        super (self.__class__,self ).__init__(*args,**kwargs) # populates the post

    def clean(self):
        data = self.cleaned_data
        code = data.get('code')
        name = data.get('name')

        if (code == '' or name == ''):
            raise forms.ValidationError('This field cannot be left blank')

        if self.parent != '' and int(self.parent) >= 0:
            level = list(RBD.objects.filter(country__code = self.country_code, pk = self.parent).values_list('level', flat=True))

            if level[0] >= self.MAX_TREE_DEPTH:
                raise ValidationError({'parent': 'RBD can only be nested '+str(self.MAX_TREE_DEPTH)+' levels deep'})

        #TODO: Fix  Later
        # level = list(RBD.objects.filter(country__code = self.country_code, pk = self.parent).values_list('level', flat=True))
        # if level[0] == 0:
        #     raise ValidationError({'parent': 'A node may not be made a child of itself.'})


        if self.instance.pk is None:  # add
            for instance in RBD.objects.filter(country__code = self.country_code):
                if instance.code == code:
                    raise forms.ValidationError({'code': code + ' is already exist.'})
                if instance.name == name:
                    raise forms.ValidationError({'name': name + ' is already exist.'})
        else:
            for instance in RBD.objects.filter(country__code = self.country_code).exclude(pk = self.instance.pk):
                if instance.code == code:
                    raise forms.ValidationError({'code': code + ' is already exist.'})
                if instance.name == name:
                    raise forms.ValidationError({'name': name + ' is already exist.'})

        return data

    class Meta:
        model = RBD
        fields = ('name','code', 'parent','description','cell_acv','num_universe','optimal_panel')


class CellModelForm(forms.ModelForm):

    def __init__(self,*args,**kwargs):
        self.request = kwargs.pop('request')
        self.country_code = kwargs.pop('country_code')
        super (self.__class__,self ).__init__(*args,**kwargs) # populates the post
        qs_rbd = RBD.objects.filter(country__code = self.country_code, parent_id=None)
        self.fields['rbd'].queryset = qs_rbd



    def clean(self):
        data = self.cleaned_data
        code = data.get('code')
        name = data.get('name')

        if (code == '' or name == ''):
            raise forms.ValidationError('This field cannot be left blank')

        if self.instance.pk is None:  # add
            for instance in Cell.objects.filter(country__code = self.country_code):
                if instance.code == code:
                    raise forms.ValidationError({'code': code + ' is already exist.'})
                if instance.name == name:
                    raise forms.ValidationError({'name': name + ' is already exist.'})
        else:
            for instance in Cell.objects.filter(country__code = self.country_code).exclude(pk = self.instance.pk):
                if instance.code == code:
                    raise forms.ValidationError({'code': code + ' is already exist.'})
                if instance.name == name:
                    raise forms.ValidationError({'name': name + ' is already exist.'})

        return data

    class Meta:
        model = Cell
        fields = ('rbd','name','code', 'description','cell_acv', 'num_universe', 'optimal_panel',)

class UsableOutletModelForm(forms.ModelForm):
    class Meta:
        model = UsableOutlet
        fields = ('month', 'outlet', 'index', 'is_active', )
