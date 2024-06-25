from dal import autocomplete
from django import forms

from api.models import CustomerMaster, CodeMaster, ItemMaster


# 매입관리
class item_form(forms.Form):

    def __init__(self, *args, **kwargs):
        super(item_form, self).__init__(*args, **kwargs)
        self.enterpriseName = args[1]

    enterpriseName = '서울소프트'
    qs_it = ItemMaster.objects.none()
    qs_cm = CodeMaster.objects.none()
    qs_cs = CustomerMaster.objects.none()

    cs_name_sch = forms.ModelChoiceField(required=False,
                                         queryset=qs_cs,
                                         widget=autocomplete.ListSelect2(
                                             url='customer_name_ac',
                                             attrs={
                                                 'class': 'form-control form-control-sm',
                                                 'style': 'width:100%; height:100%',
                                                 'data-placeholder': '거래처명',
                                             }),
                                         )


    # 품번
    it_code_name = forms.ModelChoiceField(required=False,
                                              queryset=qs_it,
                                              widget=autocomplete.ListSelect2(
                                                  url='item_code_name_ac',
                                                  attrs={
                                                      'class': 'form-control form-control-sm',
                                                      'style': 'width:100%; height:100%',
                                                      'data-placeholder': '품번:품명',
                                                  }),
                                              )

    # 품명
    it_name_sch = forms.ModelChoiceField(required=False,
                                         queryset=qs_it,
                                         widget=autocomplete.ListSelect2(
                                             url='item_name_ac',
                                             attrs={
                                                 'class': 'form-control form-control-sm',
                                                 'style': 'width:100%; height:100%',
                                                 'data-placeholder': '선택 및 검색',
                                             }),
                                         )
