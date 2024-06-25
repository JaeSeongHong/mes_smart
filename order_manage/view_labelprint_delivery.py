import datetime

from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, UpdateView, DeleteView

from Pagenation import PaginatorManager
from order_manage.form import *
from order_manage.models import *

class LabelPrint_deliveryList(ListView):

    def get(self, request, *args, **kwargs):
        context = {}

        context['searchForm'] = Search_labelprint_product(request.GET, request.COOKIES['enterprise_name'])
        context['form'] = LabelPrint_delivery_CreateForm(request.GET, request.COOKIES['enterprise_name'])

        context['search_name'] = request.GET.get('search_name', '')

        qs = LabelPrint_delivery.objects.filter(enterprise__name=self.request.COOKIES['enterprise_name'], enable=False)
        if context['search_name'] != '':
            qs = qs.filter(delivery_to__contains=context['search_name'])

        context['count'] = qs.count()

        # 페이지 네이션
        context['page'] = self.request.GET.get('page', 1)
        context['paginate_by'] = self.request.GET.get('paginate_by', 20)
        context["page_range"], context["queryset"] = PaginatorManager(self.request, qs, 20)

        context['method'] = '추가'

        return render(request, 'label_print_delivery.html', context)

    def post(self, request):

        form = LabelPrint_delivery_CreateForm(request.POST, request.COOKIES['enterprise_name'])

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

        return redirect('labelprint_delivery_list')


class LabelPrint_deliveryUpdate(UpdateView):
    model = LabelPrint_delivery
    form_class = LabelPrint_delivery_UpdateForm
    template_name = 'label_print_delivery.html'

    def get_success_url(self):
        return reverse('labelprint_delivery_list')

    def get_context_data(self, **kwargs):
        context = super(LabelPrint_deliveryUpdate, self).get_context_data(**kwargs)

        context['searchForm'] = Search_labelprint_product(self.request.GET, self.request.COOKIES['enterprise_name'])

        qs = LabelPrint_delivery.objects.filter(enterprise__name=self.request.COOKIES['enterprise_name'], enable=False)
        if self.request.GET.get('name', '') != '':
            qs = qs.filter(delivery_to__contains=self.request.GET['name'])
        context['itemId'] = self.kwargs['pk']
        context['count'] = qs.count()

        # 페이지 네이션
        context['page'] = self.request.GET.get('page', 1)
        context['paginate_by'] = self.request.GET.get('paginate_by', 20)
        context["page_range"], context["queryset"] = PaginatorManager(self.request, qs, 20)

        context['method'] = '수정'

        return context

    def form_valid(self, form):
        respons = super(LabelPrint_deliveryUpdate, self).form_valid(form)
        with transaction.atomic():
            self.object = form.save()
            updated = form.save()
            updated.updated_at = datetime.date.today()

            user = UserMaster.objects.get(username=self.request.COOKIES['username'])
            updated.updated_by = user

            updated.save()

        return respons

    def form_invalid(self, form):
        response = super(LabelPrint_deliveryUpdate, self).form_invalid(form)
        print(form.errors)
        return response


class LabelPrint_deliveryDeleteView(DeleteView):
    model = LabelPrint_delivery
    template_name = 'label_print_delivery.html'

    def get(self, request, pk):
        product = LabelPrint_delivery.objects.get(pk=pk)
        product.enable = True

        user = UserMaster.objects.get(username=request.COOKIES['username'])
        product.updated_by = user

        product.save()
        return redirect('labelprint_delivery_list')