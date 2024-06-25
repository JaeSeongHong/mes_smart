import datetime

from dal import autocomplete
from django import forms

from api.models import GroupCodeMaster
from order_manage.models import *


class Search_labelprint_product(forms.Form):

    search_name = forms.CharField(max_length=20, required=False, widget=forms.TextInput(
        attrs={'class': "form-control", 'autocomplete': 'off', 'placeholder': ''}))


class LabelPrint_CreateForm(forms.ModelForm):

    class Meta:
        model = LabelPrint_product
        exclude = ['created_by', 'updated_by', 'created_at', 'updated_at', 'enterprise', 'enable', 'date_expiration_days']

    ingredient = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'class': 'form-control', 'maxlength': '500', 'rows': 2, 'style': 'resize: none'}))  # 비고

    def __init__(self, *args, **kwargs):
        super(LabelPrint_CreateForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            # print(visible.field.label)
            if visible.field.label == 'Date expiration' or visible.field.label == 'Date manufacture':
                visible.field.widget.attrs['class'] = 'form-control datepicker'
            else:
                visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['autocomplete'] = 'off'


class LabelPrint_UpdateForm(forms.ModelForm):

    class Meta:
        model = LabelPrint_product
        exclude = ['created_by', 'created_at', 'enterprise', 'enable', 'date_expiration_days']

    ingredient = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'class': 'form-control', 'maxlength': '500', 'rows': 2, 'style': 'resize: none'}))  # 비고

    def __init__(self, *args, **kwargs):
        super(LabelPrint_UpdateForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            # print(visible.field.label)
            if visible.field.label == 'Date expiration' or visible.field.label == 'Date manufacture':
                visible.field.widget.attrs['class'] = 'form-control datepicker'
            else:
                visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['autocomplete'] = 'off'


class LabelPrint_delivery_CreateForm(forms.ModelForm):

    class Meta:
        model = LabelPrint_delivery
        exclude = ['created_by', 'updated_by', 'created_at', 'updated_at', 'enterprise', 'enable']

    def __init__(self, *args, **kwargs):
        super(LabelPrint_delivery_CreateForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['autocomplete'] = 'off'


class LabelPrint_delivery_UpdateForm(forms.ModelForm):

    class Meta:
        model = LabelPrint_delivery
        exclude = ['created_by', 'created_at', 'enterprise', 'enable']

    def __init__(self, *args, **kwargs):
        super(LabelPrint_delivery_UpdateForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['autocomplete'] = 'off'


class Search_labelprint(forms.Form):

    def __init__(self, *args, **kwargs):
        super(Search_labelprint, self).__init__(*args, **kwargs)
        self.enterpriseName = args[1]

    search_date = forms.CharField(widget=forms.TextInput(
        attrs={'class': "form-control datepicker", 'autocomplete': 'off'}), required=True)

    enterpriseName = '서울소프트'
    search_product = forms.CharField(max_length=20, required=False, widget=forms.TextInput(
        attrs={'class': "form-control", 'autocomplete': 'off', 'placeholder': ''}))

    qs_delivery = LabelPrint_delivery.objects.filter(enterprise__name=enterpriseName, enable=False)
    search_customer = forms.ModelChoiceField(required=True,
                                          queryset=qs_delivery,
                                          widget=autocomplete.ListSelect2(
                                              url='label_print_delivery_autocomplete',
                                              attrs={
                                                  'class': 'form-control form-control-sm h-100',
                                                  'data-placeholder': '납품처를 선택해주세요',
                                              }),
                                          )


class LabelPrint_History_CreateForm(forms.ModelForm):

    class Meta:
        model = LabelPrint_History
        exclude = ['created_by', 'updated_by', 'created_at', 'updated_at', 'enterprise', 'enable']

    ingredient = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'class': 'form-control', 'maxlength': '500', 'rows': 2, 'style': 'resize: none'}))  # 비고

    def __init__(self, *args, **kwargs):
        super(LabelPrint_History_CreateForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            # print(visible.field.label)
            if visible.field.label == 'Date' or visible.field.label == 'Delivery date':
                visible.field.widget.attrs['class'] = 'form-control datepicker'
            else:
                visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['autocomplete'] = 'off'