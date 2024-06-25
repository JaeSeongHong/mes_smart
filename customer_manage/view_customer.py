import datetime

from dal import autocomplete
from django.db import transaction
from django.db.models import Q
from django.urls import reverse
from django.views.generic import ListView, UpdateView, DeleteView
from django.shortcuts import render, redirect

from Pagenation import PaginatorManager
from api.models import CustomerMaster, GroupCodeMaster, CodeMaster, EnterpriseMaster, UserMaster
from customer_manage.form import Search_Customer, CustomerForm, CustomerUpdateForm


class CustomerAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = CustomerMaster.objects.filter(
            enterprise__name=self.request.COOKIES['enterprise_name'],
            enable=False
        )

        if self.q:
            qs = qs.filter(name__contains=self.q)
            a = 1


        return qs


class Code_108_AutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        code_group = GroupCodeMaster.objects.get(enterprise__name=self.request.COOKIES['enterprise_name'], code=108)
        qs_division = CodeMaster.objects.filter(enterprise__name=self.request.COOKIES['enterprise_name'], group=code_group)

        return qs_division


class CustomerList(ListView):

    def get(self, request, *args, **kwargs):
        context = {}

        context['searchForm'] = Search_Customer(request.GET, request.COOKIES['enterprise_name'])
        context['form'] = CustomerForm(request.GET, request.COOKIES['enterprise_name'])

        # 거래처 쿼리
        qs_customer = CustomerMaster.objects.filter(enterprise__name=self.request.COOKIES['enterprise_name'], enable=False).order_by('-id')
        customerName = request.GET.get('customerName', None)
        division = request.GET.get('division', None)
        if division:
            if division != '':
                qs_customer = qs_customer.filter(division__id=int(division))
        if customerName:
            if customerName != '':
                qs_customer = qs_customer.filter(pk=int(customerName))

        context['count'] = qs_customer.count()

        # 페이지 네이션
        context['page'] = request.GET.get('page', 1)
        context['paginate_by'] = request.GET.get('paginate_by', 10)
        context["page_range"], context["queryset"] = PaginatorManager(self.request, qs_customer, 10)

        context['method'] = '추가'

        return render(request, 'customer.html', context)

    def post(self, request):

        form = CustomerForm(request.POST, request.COOKIES['enterprise_name'])

        if form.is_valid():
            enterprise = EnterpriseMaster.objects.get(name=request.COOKIES['enterprise_name'])
            user = UserMaster.objects.get(username=request.COOKIES['username'])
            form.instance.enterprise = enterprise
            form.instance.enable = False
            today = datetime.date.today()
            form.instance.created_at = today
            form.instance.updated_at = today
            form.instance.created_by = user
            form.instance.updated_by = user
            form.save()
        else:
            print(form.errors)

        return redirect('customer_list')


class CustomerUpdate(UpdateView):
    model = CustomerMaster
    form_class = CustomerUpdateForm
    template_name = 'customer.html'

    def get_success_url(self):
        return reverse('customer_list')

    def get_context_data(self, **kwargs):
        context = super(CustomerUpdate, self).get_context_data(**kwargs)

        context['searchForm'] = Search_Customer(self.request.GET, self.request.COOKIES['enterprise_name'])

        # 거래처 쿼리
        qs_customer = CustomerMaster.objects.filter(enterprise__name=self.request.COOKIES['enterprise_name'],
                                                    enable=False).order_by('-id')
        context['customerId'] = self.kwargs['pk']
        context['count'] = qs_customer.count()

        # 페이지 네이션
        context['page'] = self.request.GET.get('page', 1)
        context['paginate_by'] = self.request.GET.get('paginate_by', 10)
        context["page_range"], context["queryset"] = PaginatorManager(self.request, qs_customer, 10)

        context['method'] = '수정'

        return context

    def form_valid(self, form):
        respons = super(CustomerUpdate, self).form_valid(form)
        with transaction.atomic():
            self.object = form.save()
            updated = form.save()
            updated.updated_at = datetime.date.today()

            user = UserMaster.objects.get(username=self.request.COOKIES['username'])
            updated.updated_by = user

            updated.save()

        return respons

    def form_invalid(self, form):
        response = super(CustomerUpdate, self).form_invalid(form)
        print(form.errors)
        return response


class CustomerDeleteView(DeleteView):
    model = CustomerMaster
    template_name = 'customer.html'

    def get(self, request, pk):
        customer = CustomerMaster.objects.get(pk=pk)
        customer.enable = True

        user = UserMaster.objects.get(username=request.COOKIES['username'])
        customer.updated_by = user

        customer.save()
        return redirect('customer_list')


