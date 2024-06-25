from django.db import models
from api.models import UserMaster, EnterpriseMaster

# 제품
class LabelPrint_product(models.Model):

    name = models.CharField(max_length=20, null=True)  # 품명
    ingredient = models.CharField(max_length=500, null=True)  # 성분

    # 제조일 및 유통기한 필드는 기본값 역할을 하며 변경 가능
    # 제조일로부터로 표시하는 경우 60 언더인 경우 일, 이상인 경우 반올림 개월 수로 표시
    date_manufacture = models.DateField(null=True, blank=True)  # 제조일자

    expiration_type_list = (('제조일로부터', '제조일로부터'), ('특정일', '특정일'))
    expiration_type = models.CharField(choices=expiration_type_list, max_length=6, default='제조일로부터')  # 유통기한 작성방식
    date_expiration = models.DateField(null=True, blank=True)  # 유통기한
    date_expiration_days = models.IntegerField(null=True, blank=True)  # 유통기한 일자

    remarks = models.CharField(max_length=30, null=True, blank=True, verbose_name='비고')  # 비고

    enable = models.BooleanField(default=True, verbose_name='사용구분')

    # 기본 프로토콜
    created_by = models.ForeignKey(UserMaster, models.SET_NULL, null=True, blank=True,
                                   related_name='Label_product_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey(UserMaster, models.SET_NULL, null=True, blank=True,
                                   related_name='Label_product_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일', null=True, blank=True)  # 최종작성일
    enterprise = models.ForeignKey(EnterpriseMaster, models.PROTECT, related_name='Label_product_enterprise',
                                   verbose_name='업체')

    def __str__(self):
        return self.name

# 납품처
class LabelPrint_delivery(models.Model):

    delivery_to = models.CharField(max_length=20, null=True)  # 납품처

    # 하위 값은 마지막 항목을 저장
    unit_package = models.FloatField(null=True, default=0, blank=True)  # 포장 단위
    unit = models.FloatField(null=True, default=0, blank=True)  # 수량
    unit_total = models.FloatField(null=True, default=0, blank=True)  # 총량

    remarks = models.CharField(max_length=30, null=True, blank=True, verbose_name='비고')  # 비고

    enable = models.BooleanField(default=True, verbose_name='사용구분')

    # 기본 프로토콜
    created_by = models.ForeignKey(UserMaster, models.SET_NULL, null=True, blank=True,
                                   related_name='Label_delivery_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey(UserMaster, models.SET_NULL, null=True, blank=True,
                                   related_name='Label_delivery_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일', null=True, blank=True,)  # 최종작성일
    enterprise = models.ForeignKey(EnterpriseMaster, models.PROTECT, related_name='Label_delivery_enterprise',
                                   verbose_name='업체')

    def __str__(self):
        return self.delivery_to

# 출력내역
class LabelPrint_History(models.Model):

    date = models.DateField(null=True, blank=True)  # 발주 처리일
    delivery_date = models.DateField(null=True, blank=True)  # 납품 예정일

    product_name = models.CharField(max_length=20, null=True, blank=True)  # 품명
    # 조 중 석
    meal_type = models.CharField(max_length=4, null=True, blank=True)  # 품명

    customer_name = models.CharField(max_length=20, null=True, blank=True)  # 납품처

    ingredient = models.CharField(max_length=500, null=True)  # 성분

    standard = models.CharField(max_length=50, null=True, blank=True)   # 규격

    unit_package = models.FloatField(null=True, default=0, blank=True)  # 포장 단위
    unit = models.FloatField(null=True, default=0, blank=True)  # 수량

    # 작업자의 빠른 수정을 위해서 CharField 사용
    date_manufacture = models.CharField(max_length=20, null=True, blank=True)  # 제조일자

    date_expiration = models.CharField(max_length=30, null=True, blank=True)  # 유통기한 표기

    product_number = models.CharField(max_length=20, null=True, blank=True)  # 품목보고번호

    remarks = models.CharField(max_length=30, null=True, blank=True, verbose_name='비고')  # 비고

    # 기본 프로토콜
    created_by = models.ForeignKey(UserMaster, models.SET_NULL, null=True, blank=True,
                                   related_name='Label_history_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey(UserMaster, models.SET_NULL, null=True, blank=True,
                                   related_name='Label_history_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일', null=True, blank=True,)  # 최종작성일
    enterprise = models.ForeignKey(EnterpriseMaster, models.PROTECT, related_name='Label_history_enterprise',
                                   verbose_name='업체')

