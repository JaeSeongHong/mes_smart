import datetime

from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, UpdateView, DeleteView

from Pagenation import PaginatorManager
from order_manage.form import *
from order_manage.models import *

class LabelPrint_productList(ListView):

    def get(self, request, *args, **kwargs):
        context = {}

        context['searchForm'] = Search_labelprint_product(request.GET, request.COOKIES['enterprise_name'])
        context['form'] = LabelPrint_CreateForm(request.GET, request.COOKIES['enterprise_name'])

        context['search_name'] = request.GET.get('search_name', '')

        qs = LabelPrint_product.objects.filter(enterprise__name=self.request.COOKIES['enterprise_name'], enable=False)
        if context['search_name'] != '':
            qs = qs.filter(name__contains=context['search_name'])


        context['count'] = qs.count()

        # 페이지 네이션
        context['page'] = self.request.GET.get('page', 1)
        context['paginate_by'] = self.request.GET.get('paginate_by', 20)
        context["page_range"], context["queryset"] = PaginatorManager(self.request, qs, 20)

        context['method'] = '추가'

        return render(request, 'label_print_product.html', context)

    def post(self, request):

        form = LabelPrint_CreateForm(request.POST, request.COOKIES['enterprise_name'])

        if form.is_valid():
            enterprise = EnterpriseMaster.objects.get(name=request.COOKIES['enterprise_name'])
            user = UserMaster.objects.get(username=request.COOKIES['username'])
            form.instance.enterprise = enterprise
            form.instance.enable = False

            # 유통일자 계산
            try:
                form.instance.date_expiration_days = (form.instance.date_expiration - form.instance.date_manufacture).days
            except:
                pass

            today = datetime.date.today()
            form.instance.created_at = today
            form.instance.updated_at = today
            form.instance.created_by = user
            form.instance.updated_by = user
            form.save()
        else:
            print(form.errors)

        return redirect('labelprint_product_list')

# 제품 업데이트
class LabelPrint_productUpdate(UpdateView):
    model = LabelPrint_product
    form_class = LabelPrint_UpdateForm
    template_name = 'label_print_product.html'

    def get_success_url(self):
        return reverse('labelprint_product_list')

    def get_context_data(self, **kwargs):
        context = super(LabelPrint_productUpdate, self).get_context_data(**kwargs)

        context['searchForm'] = Search_labelprint_product(self.request.GET, self.request.COOKIES['enterprise_name'])

        # 거래처 쿼리
        qs = LabelPrint_product.objects.filter(enterprise__name=self.request.COOKIES['enterprise_name'], enable=False)
        if self.request.GET.get('name', '') != '':
            qs = qs.filter(name__contains=self.request.GET['name'])

        context['itemId'] = self.kwargs['pk']
        context['count'] = qs.count()

        # 페이지 네이션
        context['page'] = self.request.GET.get('page', 1)
        context['paginate_by'] = self.request.GET.get('paginate_by', 20)
        context["page_range"], context["queryset"] = PaginatorManager(self.request, qs, 20)

        context['method'] = '수정'

        return context

    def form_valid(self, form):
        respons = super(LabelPrint_productUpdate, self).form_valid(form)
        with transaction.atomic():
            self.object = form.save()
            updated = form.save()
            updated.updated_at = datetime.date.today()

            # 유통일자 계산
            try:
                form.instance.date_expiration_days = (
                            form.instance.date_expiration - form.instance.date_manufacture).days
            except:
                pass

            user = UserMaster.objects.get(username=self.request.COOKIES['username'])
            updated.updated_by = user

            updated.save()

        return respons

    def form_invalid(self, form):
        response = super(LabelPrint_productUpdate, self).form_invalid(form)
        print(form.errors)
        return response


class LabelPrint_productDeleteView(DeleteView):
    model = LabelPrint_product
    template_name = 'label_print_product.html'

    def get(self, request, pk):
        product = LabelPrint_product.objects.get(pk=pk)
        product.enable = True

        user = UserMaster.objects.get(username=request.COOKIES['username'])
        product.updated_by = user

        product.save()
        return redirect('labelprint_product_list')