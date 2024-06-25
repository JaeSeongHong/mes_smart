from dal import autocomplete
from django import forms

from api.models import CodeMaster, CustomerMaster, GroupCodeMaster


class Search_Customer(forms.Form):

    # 거래처 autoComplete
    def __init__(self, *args, **kwargs):
        super(Search_Customer, self).__init__(*args, **kwargs)
        self.enterpriseName = args[1]

    enterpriseName = '서울소프트'
    qs_customer = CustomerMaster.objects.filter(enterprise__name=enterpriseName, enable=False)
    # 상호코드
    customerName = forms.ModelChoiceField(required=False,
                                          queryset=qs_customer,
                                          widget=autocomplete.ListSelect2(
                                              url='customer_autocomplete',
                                              attrs={
                                                  'class': 'form-control form-control-sm h-100',
                                                  'data-placeholder': '거래처를 입력해주세요',
                                              }),
                                          )  # 거래처

    # 거래구분 코드
    code_group = GroupCodeMaster.objects.get(enterprise__name=enterpriseName, code=108)
    qs_division = CodeMaster.objects.filter(enterprise__name=enterpriseName, group=code_group)
    # 그룹코드 - 거래구분
    division = forms.ModelChoiceField(required=False,
                                      queryset=qs_division,
                                      widget=autocomplete.ListSelect2(
                                          url='code_108_autocomplete',
                                          attrs={
                                              'class': 'form-control form-control-sm h-100',
                                              'data-placeholder': '거래구분',
                                          }),
                                      )  # 거래구분


class CustomerForm(forms.ModelForm):

    class Meta:
        model = CustomerMaster
        exclude = ['created_by', 'updated_by', 'created_at', 'updated_at', 'enterprise', 'enable']

    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.enterpriseName = args[1]
        code_group = GroupCodeMaster.objects.get(enterprise__name=self.enterpriseName, code=108)
        qs_division = CodeMaster.objects.filter(enterprise__name=self.enterpriseName, group=code_group)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            if visible.field.label == '거래처구분':
                visible.field.queryset = qs_division

            if visible.field.label == '거래처코드' or visible.field.label == '거래처명' or visible.field.label == '사업자번호':
                visible.field.required = True
            else:
                visible.field.required = False


class CustomerUpdateForm(forms.ModelForm):

    class Meta:
        model = CustomerMaster
        exclude = ['created_by', 'created_at', 'enterprise', 'enable']

    def __init__(self, *args, **kwargs):
        super(CustomerUpdateForm, self).__init__(*args, **kwargs)
        code_group = GroupCodeMaster.objects.get(enterprise=self.instance.enterprise, code=108)
        qs_division = CodeMaster.objects.filter(enterprise=self.instance.enterprise, group=code_group)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            if visible.field.label == '거래처구분':
                visible.field.queryset = qs_division

            if visible.field.label == '거래처코드' or visible.field.label == '거래처명' or visible.field.label == '사업자번호':
                visible.field.required = True
            else:
                visible.field.required = False
