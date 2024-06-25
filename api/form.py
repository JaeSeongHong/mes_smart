from dal import autocomplete
from django import forms

from api.models import CustomerMaster, ItemMaster



# 테스트
class Search_Customer1(forms.Form):

    # 거래처 autoComplete
    def __init__(self, *args, **kwargs):
        super(Search_Customer1, self).__init__(*args, **kwargs)
        self.enterpriseName = args[1]

    enterpriseName = '서울소프트'
    qs_customer = CustomerMaster.objects.filter(enterprise__name=enterpriseName, enable=False)
    # 상호코드
    customerName1 = forms.ModelChoiceField(required=False,
                                          queryset=qs_customer,
                                          widget=autocomplete.ListSelect2(
                                              url='customer_autocomplete',
                                              attrs={
                                                  'class': 'form-control form-control-sm h-100',
                                                  'data-placeholder': '거래처를 입력해주세요',
                                              }),
                                          )  # 거래처

class Search_Code(forms.Form):

    # 재고관리 TV autoComplete
    def __init__(self, *args, **kwargs):
        super(Search_Code, self).__init__(*args, **kwargs)
        self.enterpriseName = args[1]

    enterpriseName = '서울소프트'
    qs_item_master = ItemMaster.objects.filter(enterprise__name=enterpriseName).order_by('-id')

    # 품명
    codeName01 = forms.ModelChoiceField(required=False, queryset=qs_item_master, widget=autocomplete.ListSelect2(
        url='code_autocomplete', attrs={
            'class': 'form-control form-control-sm h-100',
            'data-placeholder': '품명을 선택해주세요',
        }), to_field_name="name")  # 품명

    codeName02 = forms.ModelChoiceField(required=False, queryset=qs_item_master, widget=autocomplete.ListSelect2(
        url='code_autocomplete', attrs={
            'class': 'form-control form-control-sm h-100',
            'data-placeholder': '품명을 선택해주세요',
        }), to_field_name="name")  # 품명

    codeName03 = forms.ModelChoiceField(required=False, queryset=qs_item_master, widget=autocomplete.ListSelect2(
        url='code_autocomplete', attrs={
            'class': 'form-control form-control-sm h-100',
            'data-placeholder': '품명을 선택해주세요',
        }), to_field_name="name")  # 품명

    codeName04 = forms.ModelChoiceField(required=False, queryset=qs_item_master, widget=autocomplete.ListSelect2(
        url='code_autocomplete', attrs={
            'class': 'form-control form-control-sm h-100',
            'data-placeholder': '품명을 선택해주세요',
        }), to_field_name="name")  # 품명

    codeName05 = forms.ModelChoiceField(required=False, queryset=qs_item_master, widget=autocomplete.ListSelect2(
        url='code_autocomplete', attrs={
            'class': 'form-control form-control-sm h-100',
            'data-placeholder': '품명을 선택해주세요',
        }), to_field_name="name")  # 품명

    codeName06 = forms.ModelChoiceField(required=False, queryset=qs_item_master, widget=autocomplete.ListSelect2(
        url='code_autocomplete', attrs={
            'class': 'form-control form-control-sm h-100',
            'data-placeholder': '품명을 선택해주세요',
        }), to_field_name="name")  # 품명

    codeName07 = forms.ModelChoiceField(required=False, queryset=qs_item_master, widget=autocomplete.ListSelect2(
        url='code_autocomplete', attrs={
            'class': 'form-control form-control-sm h-100',
            'data-placeholder': '품명을 선택해주세요',
        }), to_field_name="name")  # 품명

    codeName08 = forms.ModelChoiceField(required=False, queryset=qs_item_master, widget=autocomplete.ListSelect2(
        url='code_autocomplete', attrs={
            'class': 'form-control form-control-sm h-100',
            'data-placeholder': '품명을 선택해주세요',
        }), to_field_name="name")  # 품명

    codeName09 = forms.ModelChoiceField(required=False, queryset=qs_item_master, widget=autocomplete.ListSelect2(
        url='code_autocomplete', attrs={
            'class': 'form-control form-control-sm h-100',
            'data-placeholder': '품명을 선택해주세요',
        }), to_field_name="name")  # 품명

    codeName10 = forms.ModelChoiceField(required=False, queryset=qs_item_master, widget=autocomplete.ListSelect2(
        url='code_autocomplete', attrs={
            'class': 'form-control form-control-sm h-100',
            'data-placeholder': '품명을 선택해주세요',
        }), to_field_name="name")  # 품명

    codeName11 = forms.ModelChoiceField(required=False, queryset=qs_item_master, widget=autocomplete.ListSelect2(
        url='code_autocomplete', attrs={
            'class': 'form-control form-control-sm h-100',
            'data-placeholder': '품명을 선택해주세요',
        }), to_field_name="name")  # 품명

    codeName12 = forms.ModelChoiceField(required=False, queryset=qs_item_master, widget=autocomplete.ListSelect2(
        url='code_autocomplete', attrs={
            'class': 'form-control form-control-sm h-100',
            'data-placeholder': '품명을 선택해주세요',
        }), to_field_name="name")  # 품명
