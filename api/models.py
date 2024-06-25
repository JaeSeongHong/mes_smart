import datetime
import os

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models import Model, Sum, F
from django.db.models.signals import pre_save
from django.dispatch import receiver

"""
This models.py is initially written based on '데이터베이스설계서(유니로보틱스).hwp' of which version 1.0
For the explicit models, I did neither add class nor inherits any custom-made class and used naive models.Model.   
"""


class EnterpriseMaster(models.Model):
    class Meta:
        unique_together = ('code', 'name')

    code = models.CharField(max_length=4, unique=True, verbose_name='업체코드')
    name = models.CharField(max_length=128, unique=True, verbose_name='업체명')
    manage = models.CharField(max_length=128, null=True, verbose_name='관리명')
    com_type = models.CharField(max_length=1, null=True,
                                verbose_name='회사유형')  # 운영기관(I), 고객사(C), 운영사(O), 공급사(S), 소상인(M), 서울소프트(A)


class GroupCodeMaster(models.Model):
    class Meta:
        unique_together = ('enterprise', 'code')

    # code = models.IntegerField(verbose_name='그룹코드')
    code = models.CharField(max_length=10, verbose_name='그룹코드')
    name = models.CharField(max_length=16, verbose_name='그룹코드 이름')
    enable = models.BooleanField(default=True, verbose_name='사용구분')

    created_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='group_code_master_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='group_code_master_updated_by',
                                   verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='group_code_master_enterprise',
                                   verbose_name='업체')


class CodeMaster(models.Model):
    class Meta:
        unique_together = ('enterprise', 'group', 'code')

    group = models.ForeignKey('GroupCodeMaster', models.PROTECT, related_name='codemaster_group',
                              verbose_name='그룹 코드')
    # code = models.IntegerField(verbose_name='상세 코드')  # 상세 코드
    code = models.CharField(max_length=10, verbose_name='상세 코드')  # 상세 코드
    name = models.CharField(max_length=16, verbose_name='상세 코드명')  # 상세 코드명
    ref_code = models.ForeignKey('CodeMaster',
                                 models.PROTECT,
                                 null=True,
                                 related_name='codemaster_ref_detail_code',
                                 verbose_name='참조 상세코드')
    explain = models.CharField(max_length=32, null=True, verbose_name='코드설명')  # 코드설명
    enable = models.BooleanField(default=True, verbose_name='사용구분')  # 사용 구분
    etc = models.CharField(max_length=64, null=True, verbose_name='기타')  # 기 타

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='code_master_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='code_master_updated_by',
                                   verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='code_master_enterprise',
                                   verbose_name='업체')

    def __str__(self):
        return self.name


class CustomerMaster(models.Model):
    class Meta:
        unique_together = ('enterprise', 'code')

    code = models.CharField(max_length=16, verbose_name='거래처코드')  # 거래처코드
    name = models.CharField(max_length=64, verbose_name='거래처명')  # 거래처명
    division = models.ForeignKey('CodeMaster',
                                 models.PROTECT,
                                 null=True,
                                 verbose_name='거래처구분')
    licensee_number = models.CharField(max_length=32, verbose_name='사업자번호',
                                       null=True)  # 사업자번호, it will cause bad occasions..
    owner_name = models.CharField(max_length=20, null=True,
                                  verbose_name='대표자명')  # 대표자명
    business_conditions = models.CharField(max_length=48, null=True, verbose_name='업태')  # 업태
    business_event = models.CharField(max_length=24, null=True, verbose_name='종목')  # 종목
    postal_code = models.CharField(max_length=12, null=True, verbose_name='우편번호')  # 우편번호
    address = models.CharField(max_length=128, null=True, verbose_name='주소')  # 주소
    office_phone = models.CharField(max_length=32, null=True,
                                    verbose_name='회사전화번호')  # 회사전화번호, it will cause bad occasions..
    office_fax = models.CharField(max_length=32, null=True,
                                  verbose_name='회사팩스번호')  # 회사팩스번호, it will cause bad occasions..
    charge_name = models.CharField(max_length=20, null=True, verbose_name='담당자')  # 담당자, it will cause bad occasions..
    charge_phone = models.CharField(max_length=32, null=True,
                                    verbose_name='담당자연락처')  # 담당자연락처, it will cause bad occasions..
    charge_level = models.CharField(max_length=20, null=True, verbose_name='직급')  # 직급
    email = models.CharField(max_length=64, null=True, verbose_name='이메일')  # 6/5 설계서 email
    enable = models.BooleanField(default=True, verbose_name='사용구분')  # 사용구분
    etc = models.CharField(max_length=128, null=True, verbose_name='비고')  # 비고

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='customer_master_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, blank=True,
                                   related_name='customer_master_updated_by',
                                   verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일', null=True, blank=True)  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='customer_master_enterprise',
                                   verbose_name='업체')

    def __str__(self):
        return self.name


class UserMaster(AbstractBaseUser, PermissionsMixin):
    class UserMasterManager(BaseUserManager):

        def usermodel(self, user_id, password, username):
            # Do not add user using this usermodel()
            # This is for bootstrapping function

            user = self.model(user_id=user_id,
                              code="00000000",
                              username=username, )

            user.set_password(password)
            return user

        def create_user(self, user_id, password, username=""):
            user = self.usermodel(user_id, password, username)
            user.save(using=self._db)
            return user

        def create_superuser(self, user_id, password, username=""):
            user = self.usermodel(user_id, password, username)
            user.is_superuser = True
            user.save(using=self._db)

            return user

    class Meta:
        unique_together = ('enterprise', 'code')

    objects = UserMasterManager()
    USERNAME_FIELD = 'user_id'

    user_id = models.CharField(max_length=32, unique=True, verbose_name='유저 ID')
    code = models.CharField(max_length=8, null=True, verbose_name='사번')  # 사번
    username = models.CharField(max_length=26, null=True, verbose_name='유저 이름')
    factory_classification = models.ForeignKey('CodeMaster', models.PROTECT,
                                               null=True,
                                               related_name='factory_classification',
                                               verbose_name='공장구분')  # 공장구분,
    employment_division = models.ForeignKey('CodeMaster', models.PROTECT,
                                            null=True,
                                            related_name='employment_division',
                                            verbose_name='고용구분')  # 고용구분,
    employment_date = models.DateField(null=True, verbose_name='입사일자')  # 입사일자
    job_position = models.ForeignKey('CodeMaster', models.PROTECT,
                                     null=True,
                                     related_name='job_position',
                                     verbose_name='직위')
    department_position = models.ForeignKey('CodeMaster', models.PROTECT,
                                            null=True,
                                            related_name='department_position',
                                            verbose_name='부서구분')
    postal_code = models.CharField(max_length=12, null=True, verbose_name='우편번호')  # 우편번호
    address = models.CharField(max_length=64, null=True, verbose_name='주소')  # 주소
    # enable = models.BooleanField(default=True, verbose_name='사용구분')  # 사용구분
    etc = models.CharField(max_length=36, null=True, verbose_name='기타')  # 기타

    email = models.CharField(max_length=36, null=True, verbose_name='이메일')  #
    tel = models.CharField(max_length=36, null=True, verbose_name='전화번호')  #

    is_master = models.BooleanField(default=False, verbose_name='마스터 아이디')

    # permissions = models.BigIntegerField(default=0, verbose_name='권한')
    permissions = models.CharField(default='0', max_length=100, verbose_name='권한')

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='user_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='user_master_enterprise',
                                   verbose_name='업체', null=True)
    order_company = models.ForeignKey('OrderCompany', models.SET_NULL, null=True, related_name='order_company',
                                      verbose_name='납품기업')  # 납품기업

    snd_auth = models.CharField(default='00', max_length=128, verbose_name='2차인증')  # 스마트름뱅이 요청


class ItemLed(models.Model):
    font_size = models.IntegerField(default=30, verbose_name='폰트크기')
    code01 = models.ForeignKey('ItemMaster', models.SET_NULL, null=True, related_name='item_led_01')
    code02 = models.ForeignKey('ItemMaster', models.SET_NULL, null=True, related_name='item_led_02')
    code03 = models.ForeignKey('ItemMaster', models.SET_NULL, null=True, related_name='item_led_03')
    code04 = models.ForeignKey('ItemMaster', models.SET_NULL, null=True, related_name='item_led_04')
    code05 = models.ForeignKey('ItemMaster', models.SET_NULL, null=True, related_name='item_led_05')
    code06 = models.ForeignKey('ItemMaster', models.SET_NULL, null=True, related_name='item_led_06')
    code07 = models.ForeignKey('ItemMaster', models.SET_NULL, null=True, related_name='item_led_07')
    code08 = models.ForeignKey('ItemMaster', models.SET_NULL, null=True, related_name='item_led_08')
    code09 = models.ForeignKey('ItemMaster', models.SET_NULL, null=True, related_name='item_led_09')
    code10 = models.ForeignKey('ItemMaster', models.SET_NULL, null=True, related_name='item_led_10')
    code11 = models.ForeignKey('ItemMaster', models.SET_NULL, null=True, related_name='item_led_11')
    code12 = models.ForeignKey('ItemMaster', models.SET_NULL, null=True, related_name='item_led_12')

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='item_led_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='item_led_updated_by',
                                   verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='item_led_enterprise',
                                   verbose_name='업체')


class ItemMaster(models.Model):
    class Meta:
        unique_together = ('enterprise', 'code')

    code = models.CharField(max_length=256, verbose_name='품번')  # 품번  (BOM 코드)
    name = models.CharField(max_length=256, verbose_name='품명')  # 품명  (생산제품명)
    type = models.ForeignKey('CodeMaster', models.PROTECT,
                             null=True,
                             related_name='type',
                             verbose_name='품종')  # 품종
    # brand = models.CharField(max_length=20, null=True, verbose_name='브랜드')  # 브랜드
    # family = models.CharField(max_length=20, null=True, verbose_name='제품군')  # 제품군
    # nice = models.CharField(max_length=20, null=True, verbose_name='나이스번호')  # 나이스번호
    # shape = models.CharField(max_length=20, null=True, verbose_name='형태')  # 형태
    detail = models.CharField(max_length=128, null=True, verbose_name='품명상세')  # 품명상세
    model = models.ForeignKey('CodeMaster', models.PROTECT,
                              null=True,
                              related_name='model',
                              verbose_name='모델')  # 모델
    standard_price = models.FloatField(default=0, verbose_name="표준단가")  # 마지막에 입고된 단가
    item_division = models.ForeignKey('CodeMaster', models.PROTECT,
                                      null=True,
                                      related_name='item_division',
                                      verbose_name='자재구분')  # 재고분류
    # factory_division = models.ForeignKey('CodeMaster', models.PROTECT,
    #                                      null=True,
    #                                      related_name='factory_division',
    #                                      verbose_name='공장구분')  # 공장구분

    color = models.ForeignKey('CodeMaster', models.PROTECT,
                              null=True,
                              related_name='color_division',
                              verbose_name='칼라구분')  # 칼라구분

    # LR_division = models.CharField(max_length=1, null=True, verbose_name='LH/RH')  # LH/RH
    # TD_division = models.CharField(max_length=1, null=True, verbose_name='TOP/DOWN')  # TOP/DOWN

    # alc_code = models.CharField(max_length=16, null=True, verbose_name='ALC 코드')  # ALC코드
    # source = models.CharField(max_length=16, null=True, verbose_name='사용원료')  # 사용원료
    purchase_from = models.ForeignKey('CustomerMaster', models.PROTECT, null=True, related_name='purchase_from',
                                      verbose_name='구매처')  # 구매처
    # purchase_from2 = models.ForeignKey('CustomerMaster', models.PROTECT, null=True, related_name='purchase_from2',
    #                                   verbose_name='구매처')  # 구매처
    # purchase_from3 = models.ForeignKey('CustomerMaster', models.PROTECT, null=True, related_name='purchase_from3',
    #                                   verbose_name='구매처')  # 구매처
    # sales_to = models.ForeignKey('CustomerMaster', models.PROTECT, null=True, related_name='sales_to',
    #                              verbose_name='판매처')  # 판매처
    unit = models.ForeignKey('CodeMaster', models.PROTECT,
                             null=True,
                             related_name='unit',
                             verbose_name='단위')  # 단위
    container = models.ForeignKey('CodeMaster', models.PROTECT,
                                  null=True,
                                  related_name='container_type',
                                  verbose_name='용기타입')  # 용기타입

    # box_size = models.FloatField(null=True, verbose_name='BOX SIZE')  # BOX_SIZE
    # box_quantity = models.FloatField(null=True, verbose_name='BOX 수량')  # BOX_수량
    # warehouse_keep_location = models.ForeignKey('CodeMaster', models.PROTECT,
    #                                             null=True,
    #                                             related_name='warehouse_keep_location',
    #                                             verbose_name='창고보관위치')  # 단위
    # check_type = models.FloatField(null=True, verbose_name="검사타입")
    # check_method = models.FloatField(null=True, verbose_name="검사방법")
    # enable = models.BooleanField(default=True, verbose_name='사용구분')  # 사용구분
    etc = models.CharField(max_length=36, null=True, verbose_name='기타')  # 기타
    moq = models.FloatField(default=0, verbose_name="moq")  # MOQ

    bom_division = models.ForeignKey('BomMaster', models.PROTECT,
                                     null=True,
                                     related_name='bom_division',
                                     verbose_name='BOM구분')  # BOM구분

    # 지원상사 추가본
    g1_standard = models.CharField(max_length=64, null=True, verbose_name='규격')
    g1_standard_type = models.CharField(max_length=64, null=True, verbose_name='규격구분')
    g1_item_type = models.CharField(max_length=64, null=True, verbose_name='품목구분')
    g1_set = models.CharField(max_length=64, null=True, verbose_name='세트여부')
    g1_stock = models.CharField(max_length=64, null=True, verbose_name='재고수량관리')
    g1_process = models.ForeignKey('CodeMaster', models.PROTECT,
                                   null=True,
                                   related_name='g1_process',
                                   verbose_name='생산공정')

    # 동원엔텍 추가본
    dwe_image = models.ImageField(upload_to='uploads', default=None, null=True, verbose_name='이미지')

    # 유성산업
    brand = models.ForeignKey('CodeMaster', models.PROTECT,
                              null=True,
                              related_name='bom_brand',
                              verbose_name='브랜드')  # 단위
    item_group = models.ForeignKey('CodeMaster', models.PROTECT,
                                   null=True,
                                   related_name='bom_item_group',
                                   verbose_name='제품군')  # 단위
    # brand = models.CharField(max_length=32, null=True, verbose_name='브랜드')
    # item_group = models.CharField(max_length=32, null=True, verbose_name='제품군')
    nice_number = models.CharField(max_length=32, null=True, verbose_name='나이스번호')
    shape = models.CharField(max_length=32, null=True, verbose_name='형태')
    safe_amount = models.IntegerField(default=0, verbose_name='안전재고수량')  # 안전재고수량
    create_type = models.CharField(max_length=32, null=True, verbose_name='TYPE(일반/BOM)')

    stock = models.FloatField(default=0, verbose_name='현 재고')

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='item_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='item_updated_by',
                                   verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='item_master_enterprise',
                                   verbose_name='업체')
    qr_path = models.CharField(max_length=50, default='', null=True, verbose_name='QR경로')  # QR 경로

    # 스마트름뱅이
    fee_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='수수료율')

    def __str__(self):
        return self.name


class FacilitiesMaster(models.Model):
    class Meta:
        unique_together = ('code',)

    code = models.CharField(max_length=20, verbose_name='설비코드')
    name = models.CharField(max_length=32, verbose_name='설비명')
    detail = models.CharField(max_length=64, default="", verbose_name='설비상세')
    factory = models.ForeignKey('CodeMaster', models.PROTECT, related_name='facilities_factory', verbose_name="공장구분")
    process = models.ForeignKey('CodeMaster', models.PROTECT, null=True, related_name='facilities_process',
                                verbose_name="세부공정명")
    workshop = models.ForeignKey('CodeMaster', models.PROTECT, null=True, related_name='facilities_workshop',
                                 verbose_name="작업장")
    made_by = models.CharField(max_length=32, verbose_name='제작업체')
    type = models.ForeignKey('CodeMaster', models.PROTECT, null=True, related_name='facilities_type',
                             verbose_name="설비구분 (설비타입)")
    order = models.CharField(max_length=32, null=True, verbose_name='설비순번')
    group = models.CharField(max_length=32, null=True, verbose_name='설비그룹')
    buy_at = models.DateField(auto_now_add=True, verbose_name='구입일자')
    op_at = models.DateField(null=True, verbose_name='가동일자')
    kill_at = models.DateField(null=True, verbose_name='폐기일자')
    enable = models.BooleanField(null=True, verbose_name='사용유무')
    etc = models.CharField(max_length=64, null=True, verbose_name='비고')

    # 동원엔텍 요청사항
    dwe_admin_master = models.CharField(max_length=64, null=True, verbose_name='관리자')
    dwe_admin_vice = models.CharField(max_length=64, null=True, verbose_name='부관리자')
    dwe_image = models.ImageField(upload_to='uploads', default=None, null=True, verbose_name='이미지')
    dwe_rating = models.CharField(max_length=16, null=True, verbose_name='등급')
    dwe_making_country = models.CharField(max_length=64, null=True, verbose_name='제조국')
    dwe_making_number = models.CharField(max_length=64, null=True, verbose_name='제조번호')
    dwe_price = models.CharField(max_length=64, null=True, verbose_name='구입가격')
    dwe_kill_reason = models.CharField(max_length=64, null=True, verbose_name='폐기사유')

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='facilities_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='facilities_updated_by',
                                   verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='facilities_enterprise',
                                   verbose_name='업체')


class FacilitiesFiles(models.Model):
    """설비 파일 업로드"""
    facility = models.ForeignKey('FacilitiesMaster', models.PROTECT, verbose_name='설비')
    title = models.CharField(max_length=64, null=True, verbose_name='파일 설명')
    file = models.FileField(upload_to='uploads', default=None, null=True, verbose_name='파일')


class BomMaster(models.Model):
    class Meta:
        unique_together = ('enterprise', 'bom_number', 'product_name')

    # bom_number = models.IntegerField(default=20061400, verbose_name='BOM 코드번호')  # BOM 코드번호
    # bom_number = models.CharField(default='20061400', max_length=9, verbose_name='BOM 코드번호')  # BOM 코드번호
    bom_number = models.CharField(default='20061400', max_length=320, verbose_name='BOM 코드번호')  # BOM 코드번호

    bom_name = models.CharField(max_length=20, default='', verbose_name='BOM 명')  # BOM 명
    brand = models.ForeignKey('CodeMaster', models.PROTECT,
                              null=True,
                              related_name='BomMaster_brand',
                              verbose_name='브랜드')  # 단위
    item_group = models.ForeignKey('CodeMaster', models.PROTECT,
                                   null=True,
                                   related_name='BomMaster_item_group',
                                   verbose_name='제품군')  # 단위
    nice_number = models.CharField(max_length=20, default='', verbose_name='나이스번호')  # 나이스번호
    shape = models.CharField(max_length=20, default='', null=True, verbose_name='형태')  # 형태
    # amount = models.IntegerField(default=0 , verbose_name="안전재고수량")
    # price = models.IntegerField(default = 0, verbose_name="단가")
    product_name = models.CharField(max_length=320, verbose_name='생산제품명')  # 생산제품명

    detail = models.CharField(max_length=320, null=True, verbose_name='품명상세')  # 품명상세
    item_division = models.ForeignKey('CodeMaster', models.PROTECT, null=True, verbose_name='재고분류')  # 재고분류
    model_name = models.ForeignKey('CodeMaster', models.PROTECT, null=True, related_name='model_name',
                                   verbose_name='모델')  # 모델

    model_name = models.ForeignKey('CodeMaster', models.PROTECT, null=True, related_name='BomMaster_model_name',
                                   verbose_name='모델')  # 모델

    container = models.ForeignKey('CodeMaster', models.PROTECT, null=True, related_name='BomMaster_container_type',
                                  verbose_name='용기타입')  # 용기타입

    color = models.ForeignKey('CodeMaster', models.PROTECT, null=True, related_name='BomMaster_color_division',
                              verbose_name='칼라구분')  # 칼라구분

    type = models.ForeignKey('CodeMaster', models.PROTECT, null=True, related_name='BomMaster_type',
                             verbose_name='품종')  # 품종

    version = models.CharField(max_length=8, null=True, verbose_name='버전')  # 버전
    master_customer = models.ForeignKey('CustomerMaster', models.PROTECT, null=True,
                                        related_name='bom_master_customer',
                                        verbose_name='고객사')  # 고객사, NULL 이여도 가능하도록 수정
    amount = models.IntegerField(default=0, verbose_name='안전 수량')  # 레벨
    price = models.IntegerField(default=0, verbose_name='단가')  # 레벨

    level = models.IntegerField(default=-1, verbose_name='레벨 위치')  # 레벨
    item = models.IntegerField(default=-1, verbose_name='Item 코드 위치')  # Item 코드, TODO:
    part = models.IntegerField(default=-1, verbose_name='part 위치')  # part
    part_num = models.IntegerField(default=-1, verbose_name='part number 위치')  # part_number
    capacity = models.IntegerField(default=-1, verbose_name='용량 위치')  # 용량
    size = models.IntegerField(default=-1, verbose_name='사이즈 위치')
    voltage = models.IntegerField(default=-1, verbose_name='전압 위치')  # 전압
    band = models.IntegerField(default=-1, verbose_name='허용범위 위치')  # 허용범위
    unit = models.IntegerField(default=-1, verbose_name='단위 위치')  # 단위
    tnb = models.IntegerField(default=-1, verbose_name='Top/Bottom 위치')  # Top/Bottom
    lnr = models.IntegerField(default=-1, verbose_name='Left/Right 위치')  # Left/Right
    required_amount = models.IntegerField(default=-1, verbose_name='소요량 위치')  # 소요량
    manufacturer = models.IntegerField(default=-1, verbose_name='제조사 위치')  # 제조사
    customer = models.IntegerField(default=-1, verbose_name='고객사 위치')  # 고객사
    etc = models.IntegerField(default=-1, verbose_name='비고 위치')  # 비고
    weight = models.IntegerField(default=-1, verbose_name='중량 위치')  # 중량
    standard = models.IntegerField(default=-1, verbose_name='사양 위치', null=True, blank=True)  # 사양
    package = models.IntegerField(default=-1, verbose_name='Package 위치')  # package

    item_name = models.IntegerField(default=-1, verbose_name='품명 위치')  # 품명
    location = models.IntegerField(default=-1, verbose_name='생산공정(창고) 위치')  # 창고

    enable = models.BooleanField(default=True, verbose_name='사용구분')  # 사용구분

    file = models.FileField(upload_to='uploads', default=None, null=True, verbose_name='파일')

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='bom_master_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='bom_master_updated_by',
                                   verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='bom_master_enterprise',
                                   verbose_name='업체')


class Bom(models.Model):
    master = models.ForeignKey('BomMaster', models.PROTECT, default='20061400', verbose_name='BOM 번호')

    level = models.IntegerField(null=True, verbose_name='레벨')  # 레벨
    item = models.ForeignKey('ItemMaster', models.SET_NULL, null=True, verbose_name='ITEM 코드')
    part = models.CharField(max_length=30, null=True, verbose_name='PART')  # PART
    part_num = models.CharField(max_length=40, null=True, verbose_name='PART No')  # PART_No
    capacity = models.CharField(max_length=10, null=True, verbose_name='용량')  # 용량
    size = models.CharField(max_length=10, null=True, verbose_name='사이즈')  # 사이즈
    voltage = models.CharField(max_length=10, null=True, verbose_name='전압')  # 전압
    band = models.CharField(max_length=10, null=True, verbose_name='허용범위')  # 허용범위
    unit = models.CharField(max_length=3, null=True, verbose_name='단위')  # 단위
    tnb = models.CharField(max_length=1, null=True, verbose_name='Top/Bottom')  # T/B
    lnr = models.CharField(max_length=1, null=True, verbose_name='Left/Right')  # L/R
    package = models.CharField(max_length=16, null=True, verbose_name='Package')  # package
    required_amount = models.FloatField(verbose_name='소요량')  # 소요량
    # location = models.IntegerField(default=-1, verbose_name='자재 위치의 위치')  # 자재 위치

    manufacturer = models.ForeignKey('CustomerMaster', models.PROTECT,
                                     null=True,
                                     related_name='bom_manufacturer',
                                     verbose_name='제조사')
    customer = models.ForeignKey('CustomerMaster', models.PROTECT,
                                 null=True,
                                 related_name='bom_customer', verbose_name='고객사')  # 고객사
    etc = models.CharField(max_length=20, null=True, verbose_name='비고')  # 비고
    weight = models.CharField(max_length=16, null=True, verbose_name='중량')  # 중량
    standard = models.CharField(max_length=64, verbose_name='사양', null=True, blank=True)  # 사양
    # cost = models.IntegerField(verbose_name='단가', null=True)  # 사양

    item_name = models.CharField(max_length=100, null=True, verbose_name='품명')  # 품명
    location = models.ForeignKey('CodeMaster', models.SET_NULL, null=True, related_name='bom_location', verbose_name='생산공정(창고)')  # 창고

    enable = models.BooleanField(default=True, verbose_name='사용구분')  # 사용구분

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='bom_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='bom_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일

    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='bom_enterprise',
                                   verbose_name='업체')


class BomLog(models.Model):
    master = models.ForeignKey('BomMaster', models.PROTECT, verbose_name='BOM')

    work_date = models.DateField(verbose_name='작업날짜')
    amount = models.FloatField(verbose_name='작업수량')
    faulty_amount = models.FloatField(verbose_name='불량수량')

    file = models.FileField(upload_to='uploads', default=None, null=True, verbose_name='파일')

    etc = models.CharField(max_length=20, null=True, verbose_name='비고')  # 비고

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='bom_log_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='bom_log_updated_by',
                                   verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='bom_log_enterprise',
                                   verbose_name='업체')


class ItemIn(models.Model):
    class Meta:
        unique_together = ('enterprise', 'num')

    # 자재입고

    num = models.CharField(max_length=17, verbose_name='입하번호')  # 입/출하번호
    item = models.ForeignKey('ItemMaster', models.PROTECT, verbose_name='품번 (품목관리 마스터)')  # 품번,,, 이 곧
    item_created_at = models.DateField(null=True, verbose_name='자재생산일자')  # 자재생산일자 (자재입고)
    check_at = models.DateField(null=True, verbose_name='검사일자')  # 검사일자 (자재입고)
    in_at = models.DateField(verbose_name='입하일자')  # 입하 /출고 일자

    customer = models.ForeignKey('CustomerMaster', models.PROTECT, null=True, related_name='item_in_customer',
                                 verbose_name='구매처')  # 구매처

    package_amount = models.FloatField(null=True, verbose_name='포장수량')  # 포장수량 (자재입고)

    current_amount = models.FloatField(default=0, verbose_name='현재재고')  # 현재 재고
    receive_amount = models.FloatField(verbose_name='입하수량')  # 입하 수량
    in_faulty_amount = models.FloatField(verbose_name='불량수량')  # 불량 수량 = 입하 수량 - 입고 수량
    in_price = models.FloatField(default=0, null=True, verbose_name="입고단가")

    location = models.ForeignKey('CodeMaster', models.SET_NULL, null=True, verbose_name="입고창고")  # 입고창고
    etc = models.CharField(max_length=64, null=True, verbose_name='비고')  # 비고

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='item_in_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='item_in_updated_by',
                                   verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='item_in_master_enterprise',
                                   verbose_name='업체')

    qr_path = models.CharField(max_length=50, default='', null=True, verbose_name='QR경로')  # QR 경로
    #file = models.FileField(upload_to='uploads/itemin/%Y/%m/%d/', default=None, null=True, verbose_name='파일')  # 첨부파일

    #fee_rate = models.DecimalField(max_digits=9, decimal_places=3, default=0.00, verbose_name='수수료율')

    @property
    def in_amount(self):
        # 입고 수량
        return self.receive_amount - self.in_faulty_amount


class ItemInPay(models.Model):
    # 자재입고
    item_in = models.ForeignKey('ItemIn', models.PROTECT)  # 입고 ID
    pay_at = models.DateField(null=True, verbose_name='지급일자')  # 지급일자
    pay_amount = models.FloatField(verbose_name='지급액')  # 지급액

    etc = models.CharField(max_length=20, null=True, verbose_name='비고')  # 비고
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='ItemInPay',
                                   verbose_name='업체')


class ItemOut(models.Model):
    class Meta:
        unique_together = ('enterprise', 'num')

    # 자재출고
    num = models.CharField(max_length=12, verbose_name='출하번호')  # 입/출하번호
    item = models.ForeignKey('ItemMaster', models.PROTECT, related_name='item_out_item_code',
                             verbose_name='품목관리 마스터')  # 품번,,, 이 곧
    out_at = models.DateField(verbose_name='출고일자')  # 입하 /출고 일자
    current_amount = models.FloatField(default=0, verbose_name='현재재고')  # 현재 재고
    out_amount = models.FloatField(default=0, verbose_name='출고수량')  # 출고 수량
    purpose = models.CharField(max_length=64, verbose_name='출고목적', null=True)  # 출고 목적 수량
    out_price = models.FloatField(default=0, null=True, verbose_name="출고단가")
    surtax_chk = models.BooleanField(default=False, verbose_name='부가세포함')  # 부가세포함
    etc = models.CharField(max_length=20, null=True, verbose_name='비고')  # 비고
    location = models.ForeignKey('CodeMaster', models.SET_NULL, null=True, verbose_name="출고창고")  # 출고창고

    purchase_from = models.ForeignKey('CustomerMaster', models.PROTECT, null=True,
                                      related_name='item_out_purchase_from',
                                      verbose_name='출고_거래처')  # 출고거래처

    # 창고관리 필드들. 추후에 더 추가된다면 정규화 할 것.
    wh_bom = models.ForeignKey('BomMaster', models.PROTECT, null=True,
                               related_name='item_out_wh_bom', verbose_name='창고관리-생산제품(BOM)')  # 창고관리-생산제품 (BOM)
    wh_to = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                              related_name='item_out_wh_to', verbose_name='창고관리-반출처')  # 창고관리 - 반출처
    wh_is_auto = models.BooleanField(default=False, verbose_name='창고관리-출고방식자동여부')  # 창고관리 - 출고방식 자동여부

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='item_out_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='item_out_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='item_out_master_enterprise',
                                   verbose_name='업체')
    item = models.ForeignKey(ItemMaster, on_delete=models.CASCADE, related_name='itemout_related')


class ItemOutPay(models.Model):
    # 자재출고
    item_out = models.ForeignKey('ItemOut', models.PROTECT)  # 출고 ID
    pay_at = models.DateField(null=True, verbose_name='수금일자')  # 수금일자
    pay_amount = models.FloatField(verbose_name='수금액')  # 수금액

    etc = models.CharField(max_length=20, null=True, verbose_name='비고')  # 비고
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='ItemOutPay',
                                   verbose_name='업체')


class ItemOutOrder(models.Model):
    class Meta:
        unique_together = ('enterprise', 'num')

    # 출고지시서
    num = models.CharField(max_length=12, verbose_name='출고지시번호')  # 입/출하번호
    item = models.ForeignKey('ItemMaster', models.PROTECT, related_name='item_out_order_item_code',
                             verbose_name='품목관리 마스터')  # 품번

    out_at = models.DateField(verbose_name='출고예정일자')  # 출고 예정 일자
    out_amount = models.FloatField(default=0, verbose_name='출고예정수량')  # 출고 예정 수량
    purpose = models.CharField(max_length=64, verbose_name='출고목적')  # 출고 목적 수량
    etc = models.CharField(max_length=20, null=True, verbose_name='비고')  # 비고

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='item_out_order_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='item_out_order_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='item_out_order_master_enterprise',
                                   verbose_name='업체')


class ItemRein(models.Model):
    item = models.ForeignKey('ItemMaster', models.PROTECT, related_name='item_rein_item_code',
                             verbose_name='품목관리 마스터')
    rein_at = models.DateField(verbose_name='반입일자', null=True)  # 반입 일자

    # 반입
    current_amount = models.FloatField(default=0, verbose_name='기준재고현황')  # 불량 수량
    rein_amount = models.FloatField(default=0, verbose_name='반입수량')  # 반입 수량
    rein_price = models.FloatField(default=0, null=True, verbose_name="반입단가")
    out_faulty_amount = models.FloatField(default=0, verbose_name='불량수량')  # 불량 수량
    etc = models.CharField(max_length=20, null=True, verbose_name='비고')  # 비고

    customer = models.ForeignKey('CustomerMaster', models.SET_NULL, null=True, related_name='item_rein_customer',
                                 verbose_name='반입_거래처')  # 반입거래처
    location = models.ForeignKey('CodeMaster', models.SET_NULL, null=True, verbose_name="반입창고")  # 반입창고

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='item_rein_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='item_rein_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='item_rein_master_enterprise',
                                   verbose_name='업체')

    item = models.ForeignKey(ItemMaster, on_delete=models.CASCADE, related_name='itemrein_related')

    @property
    def after_rein_amount(self):
        return self.current_amount + self.rein_amount - self.out_faulty_amount


class ItemAdjust(models.Model):
    # 재고실사
    item = models.ForeignKey('ItemMaster', models.PROTECT, related_name='item_adjust_item')  # 품번,,, 이 곧

    previous_amount = models.FloatField(verbose_name='기존 전산재고')
    current_amount = models.FloatField(verbose_name='실재고')
    reason = models.TextField(null=True, verbose_name='재고조정사유')  # 재고조정사유

    location = models.ForeignKey('CodeMaster', models.SET_NULL, null=True, verbose_name="반입창고")  # 반입창고

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='item_adjust_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='item_adjust_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='item_adjust_master_enterprise',
                                   verbose_name='업체')


class Process(models.Model):
    class Meta:
        unique_together = ('enterprise', 'code')

    code = models.CharField(max_length=20, verbose_name="공정등록코드")
    name = models.CharField(max_length=64, verbose_name="생산공정명")
    customer = models.ForeignKey('CustomerMaster',
                                 models.PROTECT, null=True,
                                 related_name='process_customer',
                                 verbose_name="고객사")
    bom_master = models.ForeignKey('BomMaster',
                                   models.SET_NULL, null=True,
                                   related_name='process_bom',
                                   verbose_name="Bom - 생산제품명, 모델명, 버전")
    factory_classification = models.ForeignKey('CodeMaster',
                                               models.PROTECT, null=True,
                                               related_name='process_factory_classification',
                                               verbose_name="공장구분")
    amount = models.FloatField(verbose_name="생산수량")

    fr_date = models.DateField(null=True, verbose_name='From_Date')
    to_date = models.DateField(null=True, verbose_name='From_Date')

    avg_fault_rate = models.FloatField(default=0, verbose_name="평균불량률")

    actual_fr_date = models.DateField(null=True, verbose_name='Actual_From_Date')  # 실 생산 시작 날짜
    actual_to_date = models.DateField(null=True, verbose_name='Actual_From_Date')  # 실 생산 완료 날짜

    complete = models.BooleanField(default=False)
    has_fault_reason = models.BooleanField(default=False)

    is_connection = models.BooleanField(default=False, verbose_name='연돋중')

    created_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='process_created_by',
                                   verbose_name="최초작성자")
    updated_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='process_updated_by',
                                   verbose_name="최종작성자")
    created_at = models.DateField(auto_now_add=True, verbose_name="최초작성일")
    updated_at = models.DateField(auto_now=True, verbose_name="최종작성일")
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='process_master_enterprise',
                                   verbose_name='업체')


class SubprocessTemplet(models.Model):
    master = models.ForeignKey('BomMaster', models.PROTECT, default='20061400', verbose_name='BOM 번호')

    type = models.ForeignKey('CodeMaster',
                             models.PROTECT,
                             related_name='subprocesstemp_type',
                             verbose_name="세부공정명")
    workshop = models.ForeignKey('CodeMaster',
                                 models.PROTECT,
                                 related_name='subprocesstemp_workshop',
                                 verbose_name="작업장",
                                 null=True)
    charge = models.ForeignKey('UserMaster', models.SET_NULL, null=True)

    # unit = models.ForeignKey('CodeMaster',
    #                          models.PROTECT,
    #                          related_name='subprocesstemp_unit',
    #                          verbose_name="단위")
    # amount = models.IntegerField(verbose_name='생산수량')
    # by = models.DateField(verbose_name='일정')

    etc = models.CharField(max_length=64, blank=True, verbose_name='기타')

    created_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='subprocesstemp_created_by',
                                   verbose_name="최초작성자")
    updated_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='subprocesstemp_updated_by',
                                   verbose_name="최종작성자")
    created_at = models.DateField(auto_now_add=True, verbose_name="최초작성일")
    updated_at = models.DateField(auto_now=True, verbose_name="최종작성일")
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='subprocesstemp_master_enterprise',
                                   verbose_name='업체')


class Subprocess(models.Model):
    process = models.ForeignKey('Process',
                                models.PROTECT,
                                related_name='subprocess_process',
                                verbose_name='공정',
                                null=True)
    type = models.ForeignKey('CodeMaster',
                             models.PROTECT,
                             related_name='subprocess_type',
                             verbose_name="세부공정명",
                             null=True)
    workshop = models.ForeignKey('CodeMaster',
                                 models.PROTECT,
                                 related_name='subprocess_workshop',
                                 verbose_name="작업장",
                                 null=True)
    charge = models.ForeignKey('UserMaster', models.SET_NULL, null=True)

    # unit = models.ForeignKey('CodeMaster',
    #                          models.PROTECT,
    #                          related_name='subprocess_unit',
    #                          verbose_name="단위")

    by = models.DateField(verbose_name='일정', null=True)
    etc = models.CharField(max_length=64, blank=True, verbose_name='기타')

    fr_date = models.DateField(null=True, verbose_name='From_Date')
    to_date = models.DateField(null=True, verbose_name='From_Date')

    actual_fr_date = models.DateField(null=True, verbose_name='Actual_From_Date')  # 실 생산 시작 날짜
    actual_to_date = models.DateField(null=True, verbose_name='Actual_From_Date')  # 실 생산 완료 날짜

    amount = models.FloatField(default=0, verbose_name='계획수량')
    complete_amount = models.FloatField(default=0, verbose_name='완료수량')
    complete_check = models.IntegerField(default=0, verbose_name='완료체크')
    remain_amount = models.FloatField(default=0, verbose_name='잔여수량')
    faulty_amount = models.FloatField(default=0, verbose_name='불량수량')
    # status = models.ForeignKey('CodeMaster', models.PROTECT, null=True, verbose_name="작업진행현황")
    status = models.CharField(default='대기', max_length=64, blank=True, verbose_name='작업진행현황')  # 대기, 진행, 완료

    finished_at = models.DateField(null=True, verbose_name='완료 예정일')
    reason = models.CharField(max_length=64, blank=True, verbose_name='지연사유')
    is_connection = models.BooleanField(default=False, verbose_name='장비연동여부')

    fault_reason = models.ForeignKey('SubprocessFaultReason',
                                     models.PROTECT, null=True,
                                     related_name='subprocess_fault_reason',
                                     verbose_name='불량 사유')
    created_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='subprocess_created_by',
                                   verbose_name="최초작성자")
    updated_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='subprocess_updated_by',
                                   verbose_name="최종작성자")
    created_at = models.DateField(auto_now_add=True, verbose_name="최초작성일")
    updated_at = models.DateField(auto_now=True, verbose_name="최종작성일")
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='subprocess_master_enterprise',
                                   verbose_name='업체')


class SubprocessLog(models.Model):
    subprocess = models.ForeignKey('Subprocess',
                                   models.PROTECT,
                                   related_name='subprocess_log_subprocess',
                                   verbose_name='세부공정')

    itemIn = models.ForeignKey('ItemIn',
                               models.SET_NULL,
                               related_name='subprocess_log_itemIn',
                               verbose_name='재고입고',
                               null=True)

    itemOut = models.ForeignKey('ItemOut',
                                models.SET_NULL,
                                related_name='subprocess_log_itemOut',
                                verbose_name='재고출고',
                                null=True)


class SubprocessProgress(models.Model):
    subprocess = models.ForeignKey('Subprocess',
                                   models.PROTECT,
                                   related_name='subprocess_progress_subprocess',
                                   verbose_name='Subprocess - 세부공정명, 작업자명, 생산지시수량, 담당자명, 작업일정')
    amount = models.FloatField(verbose_name='생산진행수량')
    faulty_amount = models.FloatField(verbose_name='불량수량')
    status = models.ForeignKey('CodeMaster',
                               models.PROTECT,
                               related_name='subprocess_progress_status',
                               verbose_name="작업진행현황")
    finished_at = models.DateField(verbose_name='완료 예정일')
    reason = models.CharField(max_length=64, blank=True, verbose_name='지연사유')

    created_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='subprocess_progress_created_by',
                                   verbose_name="최초작성자")
    updated_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='subprocess_progress_updated_by',
                                   verbose_name="최종작성자")
    created_at = models.DateField(auto_now_add=True, verbose_name="최초작성일")
    updated_at = models.DateField(auto_now=True, verbose_name="최종작성일")
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT,
                                   related_name='subprocess_progress_master_enterprise',
                                   verbose_name='업체')


class SubprocessFaultReason(models.Model):
    R01_upper = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 대분류01', related_name='upper_classification_01')
    R01_lower = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 소분류01', related_name='lower_classification_01')
    R01_amount = models.FloatField(default=0, verbose_name='불량수량01')

    R02_upper = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 대분류02', related_name='upper_classification_02')
    R02_lower = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 소분류02', related_name='lower_classification_02')
    R02_amount = models.FloatField(default=0, verbose_name='불량수량02')

    R03_upper = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 대분류03', related_name='upper_classification_03')
    R03_lower = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 소분류03', related_name='lower_classification_03')
    R03_amount = models.FloatField(default=0, verbose_name='불량수량03')

    R04_upper = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 대분류04', related_name='upper_classification_04')
    R04_lower = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 소분류04', related_name='lower_classification_04')
    R04_amount = models.FloatField(default=0, verbose_name='불량수량04')

    R05_upper = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 대분류05', related_name='upper_classification_05')
    R05_lower = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 소분류05', related_name='lower_classification_05')
    R05_amount = models.FloatField(default=0, verbose_name='불량수량05')

    R06_upper = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 대분류06', related_name='upper_classification_06')
    R06_lower = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 소분류06', related_name='lower_classification_06')
    R06_amount = models.FloatField(default=0, verbose_name='불량수량06')

    R07_upper = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 대분류07', related_name='upper_classification_07')
    R07_lower = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 소분류07', related_name='lower_classification_07')
    R07_amount = models.FloatField(default=0, verbose_name='불량수량07')

    R08_upper = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 대분류08', related_name='upper_classification_08')
    R08_lower = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 소분류08', related_name='lower_classification_08')
    R08_amount = models.FloatField(default=0, verbose_name='불량수량08')

    R09_upper = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 대분류09', related_name='upper_classification_09')
    R09_lower = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 소분류09', related_name='lower_classification_09')
    R09_amount = models.FloatField(default=0, verbose_name='불량수량09')

    R10_upper = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 대분류10', related_name='upper_classification_10')
    R10_lower = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 소분류10', related_name='lower_classification_10')
    R10_amount = models.FloatField(default=0, verbose_name='불량수량10')

    R11_upper = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 대분류11', related_name='upper_classification_11')
    R11_lower = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 소분류11', related_name='lower_classification_11')
    R11_amount = models.FloatField(default=0, verbose_name='불량수량11')

    R12_upper = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 대분류12', related_name='upper_classification_12')
    R12_lower = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 소분류12', related_name='lower_classification_12')
    R12_amount = models.FloatField(default=0, verbose_name='불량수량12')

    R13_upper = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 대분류13', related_name='upper_classification_13')
    R13_lower = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 소분류13', related_name='lower_classification_13')
    R13_amount = models.FloatField(default=0, verbose_name='불량수량13')

    R14_upper = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 대분류14', related_name='upper_classification_14')
    R14_lower = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 소분류14', related_name='lower_classification_14')
    R14_amount = models.FloatField(default=0, verbose_name='불량수량14')

    R15_upper = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 대분류15', related_name='upper_classification_15')
    R15_lower = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                  verbose_name='사유 소분류15', related_name='lower_classification_15')
    R15_amount = models.FloatField(default=0, verbose_name='불량수량15')

    amount_sum = models.FloatField(default=0, verbose_name='불량수량 총합')
    col_cnt = models.IntegerField(default=5, verbose_name='열 수')
    row_cnt = models.IntegerField(default=5, verbose_name='행 수')

    created_at = models.DateField(auto_now_add=True, verbose_name="최초작성일")
    updated_at = models.DateField(auto_now=True, verbose_name="최종작성일")

    master = models.ForeignKey('Subprocess', models.PROTECT,
                               related_name='master_subprocess',
                               verbose_name="서브프로세스")

    created_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='subprocess_fault_created_by',
                                   verbose_name="최초작성자")
    updated_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='subprocess_fault_updated_by',
                                   verbose_name="최종작성자")
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='subprocess_enterprise',
                                   verbose_name='업체')


class RentalMaster(models.Model):
    class Meta:
        unique_together = ('enterprise', 'code')

    code = models.CharField(max_length=20, verbose_name="대여품목코드")
    item = models.ForeignKey('ItemMaster', models.SET_NULL, null=True)  # 대여품목

    rental_class = models.ForeignKey('CodeMaster', models.PROTECT,
                                     related_name='rental_master_rental_class',
                                     verbose_name='대여품구분')

    factory_class = models.ForeignKey('CodeMaster', models.PROTECT,
                                      related_name='rental_master_factory_class',
                                      verbose_name='공장구분')

    serial = models.CharField(max_length=16, verbose_name='시리얼 No')
    caution = models.CharField(max_length=64, verbose_name='대여시 주의사항')
    days = models.IntegerField(verbose_name='평균대여기간')

    created_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='rental_master_created_by',
                                   verbose_name="최초작성자")
    updated_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='rental_master_updated_by',
                                   verbose_name="최종작성자")
    created_at = models.DateField(auto_now_add=True, verbose_name="최초작성일")
    updated_at = models.DateField(auto_now=True, verbose_name="최종작성일")
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='rental_master_enterprise',
                                   verbose_name='업체')


class Rental(models.Model):
    master = models.ForeignKey('RentalMaster', models.PROTECT, verbose_name="대여품목코드")
    exp_date = models.DateField(verbose_name='반납 예정일')
    condition = models.CharField(max_length=16, verbose_name='대여품 상태')
    customer = models.ForeignKey('CustomerMaster',
                                 models.SET_NULL, null=True,
                                 related_name='rental_customer',
                                 verbose_name='대여업체')  # 고객사
    customer_name = models.CharField(max_length=16, verbose_name='대여자명')
    customer_phone = models.CharField(max_length=16, verbose_name='대여자 연락처')

    is_returned = models.BooleanField(default=False, verbose_name='회수여부')
    return_date = models.DateField(null=True, verbose_name='반납일')
    return_condition = models.CharField(max_length=16, null=True, verbose_name='회수품이상유무')
    return_name = models.CharField(max_length=16, null=True, verbose_name='반납자명')
    return_phone = models.CharField(max_length=16, null=True, verbose_name='반납자 연락처')

    etc = models.CharField(max_length=64, verbose_name='특이사항')

    created_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='rental_created_by',
                                   verbose_name="최초작성자")
    updated_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='rental_updated_by',
                                   verbose_name="최종작성자")
    created_at = models.DateField(auto_now_add=True, verbose_name="최초작성일")
    updated_at = models.DateField(auto_now=True, verbose_name="최종작성일")
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='rental_enterprise',
                                   verbose_name='업체')


class Sensor(models.Model):
    factory = models.ForeignKey('CodeMaster', models.PROTECT,
                                related_name='sensor_factory', verbose_name='공장명')
    facilities = models.ForeignKey('FacilitiesMaster', models.SET_NULL, null=True,
                                   related_name='sensor_facilities',
                                   verbose_name='설비명')
    model = models.CharField(null=True, max_length=32, verbose_name='온습도계 모델')
    serial = models.CharField(null=True, max_length=32, verbose_name='시리얼 No')
    type = models.ForeignKey('CodeMaster', models.PROTECT,
                             related_name='sensor_type', verbose_name='관리구분')
    threshold_low = models.FloatField(null=True, verbose_name='허용범위 최저치')
    threshold_high = models.FloatField(null=True, verbose_name='허용범위 최대치')
    api_url = models.TextField(verbose_name='API URL')
    etc = models.CharField(null=True, max_length=64, verbose_name='기타')

    created_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='sensor_created_by',
                                   verbose_name="최초작성자")
    updated_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='sensor_updated_by',
                                   verbose_name="최종작성자")
    created_at = models.DateField(auto_now_add=True, verbose_name="최초작성일")
    updated_at = models.DateField(auto_now=True, verbose_name="최종작성일")
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='sensor_enterprise',
                                   verbose_name='업체')


class SensorValue(models.Model):
    master = models.ForeignKey('Sensor', models.CASCADE,
                               related_name='sensor_value_master', verbose_name='센서')
    temp = models.FloatField(verbose_name='[임시] 현재온도')
    hue = models.FloatField(verbose_name='[임시] 현재습도')
    fetch_datetime = models.DateTimeField(verbose_name="통신시간")
    created_at = models.DateField(auto_now_add=True, verbose_name="최초작성일")


# H2_PS, TK_EX 온습도 모듈
class SensorH2(models.Model):
    device = models.CharField(null=False, max_length=32, verbose_name='장비명')
    mac = models.CharField(null=False, max_length=32, verbose_name='MAC')

    factory = models.ForeignKey('CodeMaster', models.PROTECT,
                                related_name='h2_sensor_factory', null=True, verbose_name='공장명')

    workshop = models.ForeignKey('CodeMaster', models.PROTECT,
                                 related_name='h2_sensor_workshop', null=True, verbose_name='작업장')

    model = models.CharField(null=True, max_length=32, verbose_name='모델명')

    etc = models.CharField(null=True, max_length=64, verbose_name='기타')

    created_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='h2_sensor_created_by',
                                   verbose_name="최초작성자")
    updated_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='h2_sensor_updated_by',
                                   verbose_name="최종작성자")
    created_at = models.DateField(auto_now_add=True, verbose_name="최초작성일")
    updated_at = models.DateField(auto_now=True, verbose_name="최종작성일")
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='h2_sensor_enterprise',
                                   verbose_name='업체')


class Device(models.Model):
    device = models.CharField(null=False, max_length=32, verbose_name='장비명')
    mac = models.CharField(null=False, max_length=32, verbose_name='MAC')

    factory = models.ForeignKey('CodeMaster', models.PROTECT,
                                related_name='Device_factory', null=True, verbose_name='공장명')

    workshop = models.ForeignKey('CodeMaster', models.PROTECT,
                                 related_name='Device_workshop', null=True, verbose_name='작업장')

    model = models.CharField(null=True, max_length=32, verbose_name='모델명')

    etc = models.CharField(null=True, max_length=64, verbose_name='기타')

    created_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='Device_created_by',
                                   verbose_name="최초작성자")
    updated_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='Device_updated_by',
                                   verbose_name="최종작성자")
    created_at = models.DateField(auto_now_add=True, verbose_name="최초작성일")
    updated_at = models.DateField(auto_now=True, verbose_name="최종작성일")
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='Device_enterprise',
                                   verbose_name='업체')


class SensorH2Value(models.Model):
    # master = models.ForeignKey('SensorH2', models.CASCADE,related_name='h2_sensor_value_master', verbose_name='센서')
    mac = models.CharField(default='', max_length=32, verbose_name='mac address')
    temp = models.FloatField(verbose_name='[임시] 현재온도')
    hue = models.FloatField(verbose_name='[임시] 현재습도')
    fetch_datetime = models.DateTimeField(verbose_name="통신시간")
    created_at = models.DateField(auto_now_add=True, verbose_name="최초작성일")


# 창고관리를 위한 자재 확장. 품목관리의 창고와는 다른 개념임.

class ItemWarehouseStock(models.Model):
    """창고관리의 창고별 자재 수량을 기록하기 위함."""

    class Meta:
        unique_together = ('item', 'warehouse')

    item = models.ForeignKey('ItemMaster', models.CASCADE, related_name='item_warehouse_stock_item',
                             verbose_name='품목')
    warehouse = models.ForeignKey('CodeMaster', models.PROTECT,
                                  related_name='item_warehouse_stock_warehouse', verbose_name='창고')  # 창고
    stock = models.FloatField(default=0, verbose_name='현 재고')

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='item_warehouse_stock_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='item_warehouse_stock_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일

    def update_stock(self, value):  # stock 값 저장
        self.stock = value
        self.save()


class ItemWarehouseIn(models.Model):
    """창고관리의 입고을 위한 모델. 기존 자재입고를 확장함."""

    item_in = models.OneToOneField('ItemIn', models.CASCADE, related_name='item_warehouse_in_item_in',
                                   verbose_name='자재입고')  # 자재입고
    warehouse = models.ForeignKey('CodeMaster', models.PROTECT,
                                  related_name='item_warehouse_in_warehouse', verbose_name='창고')  # 창고

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='item_warehouse_in_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='item_warehouse_in_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일


class ItemWarehouseOut(models.Model):
    """창고관리의 반출을 위한 모델. 기존 자재출고를 확장함."""

    item_out = models.OneToOneField('ItemOut', models.CASCADE, related_name='item_warehouse_out_item_out',
                                    verbose_name='자재출고')  # 자재출고
    warehouse = models.ForeignKey('CodeMaster', models.PROTECT,
                                  related_name='item_warehouse_out_warehouse', verbose_name='창고')  # 창고

    bom = models.ForeignKey('BomMaster', models.PROTECT, null=True,
                            related_name='item_warehouse_out_bom', verbose_name='생산제품(BOM)')  # 창고관리-생산제품 (BOM)
    warehouse_to = models.ForeignKey('CodeMaster', models.PROTECT, null=True,
                                     related_name='item_warehouse_out_warehouse_to', verbose_name='반출처')  # 반출처
    customer_to = models.ForeignKey('CustomerMaster', models.PROTECT, null=True,
                                    related_name='item_warehouse_out_customer_to', verbose_name='거래')  # 반출처
    is_auto = models.BooleanField(default=False, verbose_name='출고방식자동여부')  # 창고관리 - 출고방식 자동여부
    related_itemwarehousein = models.OneToOneField('ItemWarehouseIn', models.PROTECT, null=True,
                                                   related_name='item_warehouse_out_related_itemwarehousein',
                                                   verbose_name='관련 창고입고')

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='item_warehouse_out_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='item_warehouse_out_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일


class ItemWarehouseRein(models.Model):
    """창고관리의 반입을 위한 모델. 기존 자재반입을 확장함."""

    item_rein = models.OneToOneField('ItemRein', models.CASCADE, related_name='item_warehouse_rein_item_rein',
                                     verbose_name='자재반입')  # 자재반입
    warehouse = models.ForeignKey('CodeMaster', models.PROTECT,
                                  related_name='item_warehouse_rein_warehouse', verbose_name='창고')  # 창고

    warehouse_from = models.ForeignKey('CodeMaster', models.PROTECT,
                                       related_name='item_warehouse_rein_warehouse_from', verbose_name='반입처')  # 반입처

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='item_warehouse_rein_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='item_warehouse_rein_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일


class ItemWarehouseAdjust(models.Model):
    """창고관리의 조정을 위한 모델. 기존 자재조정을 확장함."""

    item_adjust = models.OneToOneField('ItemAdjust', models.CASCADE, related_name='item_warehouse_adjust_item_adjust',
                                       verbose_name='자재조정')
    warehouse = models.ForeignKey('CodeMaster', models.PROTECT,
                                  related_name='item_warehouse_adjust_warehouse', verbose_name='창고')  # 창고

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='item_warehouse_adjust_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='item_warehouse_adjust_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일


class SensorPC(models.Model):
    """온도전압관리"""
    factory = models.ForeignKey('CodeMaster', models.PROTECT,
                                related_name='sensorpc_factory', verbose_name='공장명')
    name = models.CharField(null=True, max_length=64, verbose_name='PC명')
    model = models.CharField(null=True, max_length=64, verbose_name='PC 모델')
    serial = models.CharField(null=True, max_length=64, verbose_name='시리얼 No')
    mac = models.CharField(null=True, max_length=64, verbose_name='맥 주소')
    temp_threshold_low = models.FloatField(null=True, verbose_name='온도 허용범위 최저치')
    temp_threshold_high = models.FloatField(null=True, verbose_name='온도 허용범위 최대치')
    voltage_threshold_low = models.FloatField(null=True, verbose_name='전압 허용범위 최저치')
    voltage_threshold_high = models.FloatField(null=True, verbose_name='전압 허용범위 최대치')
    voltage_3v_threshold_low = models.FloatField(null=True, verbose_name='3.3V 허용범위 최저치')
    voltage_3v_threshold_high = models.FloatField(null=True, verbose_name='3.3V 허용범위 최대치')
    voltage_5v_threshold_low = models.FloatField(null=True, verbose_name='5V 허용범위 최저치')
    voltage_5v_threshold_high = models.FloatField(null=True, verbose_name='5V 허용범위 최대치')
    voltage_12v_threshold_low = models.FloatField(null=True, verbose_name='12V 허용범위 최저치')
    voltage_12v_threshold_high = models.FloatField(null=True, verbose_name='12V 허용범위 최대치')

    admin_email_1 = models.CharField(null=True, max_length=128, verbose_name='관리자 메일 1')
    admin_email_2 = models.CharField(null=True, max_length=128, verbose_name='관리자 메일 2')

    etc = models.CharField(null=True, max_length=64, verbose_name='기타')
    alert = models.CharField(null=True, max_length=64, verbose_name='위험경보관리')  # ?? 수정 필요

    # 기업. 사용자 기준으로 등록되어야 함.
    company = models.ForeignKey('UserMaster',
                                models.SET_NULL, null=True,
                                related_name='sensorpc_company',
                                verbose_name="최초작성자")

    created_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='sensorpc_created_by',
                                   verbose_name="최초작성자")
    updated_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='sensorpc_updated_by',
                                   verbose_name="최종작성자")
    created_at = models.DateField(auto_now_add=True, verbose_name="최초작성일")
    updated_at = models.DateField(auto_now=True, verbose_name="최종작성일")
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='sensorpc_enterprise',
                                   verbose_name='업체')
    order_company = models.ForeignKey('OrderCompany', models.PROTECT, null=True, related_name='sensorpc_order_company',
                                      verbose_name='납품기업')  # 납품기업


class SensorPCValue(models.Model):
    master = models.ForeignKey('SensorPC', models.CASCADE,
                               related_name='sensorpc_value_master', verbose_name='센서')
    temp = models.FloatField(verbose_name='현재온도')
    voltage = models.FloatField(verbose_name='현재전압')
    voltage3 = models.FloatField(verbose_name='현재3.3V', null=True)
    voltage5 = models.FloatField(verbose_name='현재5V', null=True)
    voltage12 = models.FloatField(verbose_name='현재12V', null=True)
    fetch_datetime = models.DateTimeField(verbose_name="통신시간")
    created_at = models.DateField(auto_now_add=True, verbose_name="최초작성일")


class Order(models.Model):
    """발주"""

    class Meta:
        unique_together = ('enterprise', 'po')

    po = models.CharField(max_length=32, verbose_name='발주코드')  # 품번
    cpo = models.CharField(max_length=24, verbose_name='내부발주코드')  # 품번

    item = models.ForeignKey('ItemMaster', models.PROTECT, related_name='order_item', verbose_name='품목')
    price = models.FloatField(default=0, null=True, verbose_name="단가")
    amount = models.FloatField(default=0, null=True, verbose_name="수량")
    total = models.FloatField(default=0, null=True, verbose_name="총금액")
    customer = models.ForeignKey('CustomerMaster', models.PROTECT, related_name='order_customer', verbose_name='거래처')
    etc = models.TextField(null=True, verbose_name="기타")
    purchase_condition = models.CharField(null=True, max_length=128, verbose_name="결제조건")
    date = models.DateField(null=True, verbose_name="납기일")
    package = models.CharField(null=True, max_length=128, verbose_name="포장")
    quality_guarantee = models.CharField(null=True, max_length=128, verbose_name="품질보증기간")
    place = models.CharField(null=True, max_length=128, verbose_name="납품장소")

    mail_sent_at = models.DateField(null=True, verbose_name="메일발신")
    is_excel_printed = models.BooleanField(default=False, verbose_name="발주서출력여부")

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='order_created_by',
                                   verbose_name="최초작성자")
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='order_updated_by',
                                   verbose_name="최종작성자")
    created_at = models.DateField(auto_now_add=True, verbose_name="최초작성일")
    updated_at = models.DateField(auto_now=True, verbose_name="최종작성일")
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='order_enterprise',
                                   verbose_name='업체')


class OrderIn(models.Model):
    master = models.ForeignKey('Order', models.PROTECT, verbose_name="발주")
    in_at = models.DateField(verbose_name='입하일자')  # 입하 /출고 일자

    receive_amount = models.FloatField(verbose_name='입하수량')  # 입하 수량
    in_faulty_amount = models.FloatField(verbose_name='불량수량')  # 불량 수량 = 입고 수량 - 입하 수량

    check_at = models.DateField(null=True, verbose_name='검사일자')  # 검사일자 (자재입고)
    item_created_at = models.DateField(null=True, verbose_name='자재생산일자')  # 자재생산일자 (자재입고)
    location = models.ForeignKey('CodeMaster', models.SET_NULL, null=True, related_name="OrderIn_location",
                                 verbose_name="자재위치")  # 자재위치

    package_amount = models.FloatField(null=True, verbose_name='포장수량')  # 포장수량 (자재입고)
    is_in = models.ForeignKey('CodeMaster', models.PROTECT, verbose_name='입고상태')  # 포장수량 (자재입고)

    etc = models.CharField(max_length=64, null=True, verbose_name='기타')  # 기 타

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='order_in_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='order_in_updated_by',
                                   verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='order_in_master_enterprise',
                                   verbose_name='업체')

    @property
    def in_amount(self):
        # 입고 수량
        return self.receive_amount - self.in_faulty_amount


class Orders(models.Model):
    # code = models.ForeignKey('CustomerMaster', models.PROTECT, null=True, verbose_name='거래처코드', related_name='Orders_code')  # 거래처코드
    customer = models.ForeignKey('CustomerMaster', models.PROTECT, null=True, verbose_name='거래처코드',
                                 related_name='Orders_customer')  # 거래처코드

    # division = models.ForeignKey('CodeMaster', models.PROTECT, null=True, verbose_name='거래처구분')  # 거래처구분

    # enable = models.BooleanField(default=True, verbose_name='사용구분')  # 사용구분
    etc = models.CharField(max_length=64, null=True, verbose_name='비고')  # 비고

    # orders_code = models.CharField(max_length=32, null=True, verbose_name='발주번호')
    po_no = models.CharField(max_length=32, null=True, verbose_name='발주번호')
    in_status = models.CharField(default='U', max_length=16, verbose_name='입고현황')  # U(미입고),P(일부입고),Finish(입고완료)
    provide_sum = models.FloatField(default=0, verbose_name='공급가')
    provide_surtax = models.BooleanField(default=True, verbose_name='부가세포함')

    due_date = models.DateField(null=True, verbose_name='납기일')  # 납기일
    pay_option = models.CharField(max_length=32, null=True, verbose_name='결제조건')  # 결제조건
    guarantee_date = models.DateField(null=True, verbose_name='품질보증기한')  # 품질보증기한
    deliver_place = models.CharField(max_length=32, null=True, verbose_name='납품장소')  # 납품장소
    note = models.CharField(max_length=128, null=True, verbose_name='NOTE 내용고정')  # NOTE

    send_date = models.DateField(null=True, verbose_name='발송일자')  # 발송일자
    send_chk = models.BooleanField(default=False, verbose_name='발송여부')  # 발송여부

    finish_date = models.DateTimeField(null=True, verbose_name='마감일자')  # 마감일자
    finish_chk = models.BooleanField(default=0, verbose_name='마감여부')  # 마감여부  0(미완료), 1(마감완료)

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='orders_master_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='orders_master_updated_by',
                                   verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateTimeField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='orders_master_enterprise',
                                   verbose_name='업체')


class OrdersItems(models.Model):
    orders = models.ForeignKey('Orders', models.PROTECT, null=True, verbose_name='발주서')
    item = models.ForeignKey('ItemMaster', models.PROTECT, verbose_name='품목')

    item_detail = models.CharField(max_length=32, null=True, verbose_name='품명상세')  # 품명상세
    item_unit = models.CharField(max_length=32, null=True, verbose_name='단위')  # 단위

    quantity = models.FloatField(default=0, verbose_name='발주수량')  # 발주수량
    item_price = models.FloatField(default=0, verbose_name='단가', null=True)  # 단가
    # supply_price = models.FloatField(default=0, verbose_name='공급가', null=True)  # 공급가
    # surtax = models.FloatField(default=0, verbose_name='부가세', null=True)  # 부가세
    # item_supply_total = models.FloatField(default=0, verbose_name='합계', null=True)  # 합계
    file = models.FileField(upload_to='uploads/orders/%Y/%m/%d/', default=None, null=True, verbose_name='파일')  # 첨부파일
    remarks = models.CharField(max_length=128, null=True, verbose_name='비고')  # 비고

    stock = models.FloatField(null=True, verbose_name='현재재고')  # 현재재고
    in_ed_quantity = models.FloatField(default=0, verbose_name='입고된수량')  # 입고된 수량
    in_will_quantity = models.FloatField(default=0, verbose_name='입고할수량')  # 입고할 수량

    in_ed_faulty = models.FloatField(default=0, verbose_name='입고된 불량수량')  # 입고된 불량 수량  // 입하수량 = 입고수량 - 불량수량
    in_will_faulty = models.FloatField(default=0, verbose_name='입고할 불량수량')  # 입고할 불량 수량

    in_date = models.DateField(null=True, verbose_name='입고일자')  # 입고일자
    item_created_at = models.DateField(null=True, verbose_name='자재생산일자')  # 자재생산일자 (자재입고)
    location = models.ForeignKey('CodeMaster', models.SET_NULL, null=True, verbose_name="자재위치")  # 자재위치
    etc = models.CharField(max_length=20, null=True, verbose_name='비고')  # 비고

    in_status = models.CharField(default='U', max_length=16, verbose_name='입고현황')  # 미입고('U'), 일부입고 : P, 입고완료 : F

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='orders_items_master_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='orders_items_master_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='Orders_item_master_enterprise',
                                   verbose_name='업체')


class OrdersInItems(models.Model):
    orders = models.ForeignKey('Orders', models.PROTECT, null=True, verbose_name='발주서')
    orders_item = models.ForeignKey('OrdersItems', models.PROTECT, null=True, verbose_name='발주항목')

    num = models.CharField(max_length=12, verbose_name='입고번호')  # 입고번호
    item = models.ForeignKey('ItemMaster', models.PROTECT, verbose_name='품목')

    item_detail = models.CharField(max_length=32, null=True, verbose_name='품명상세')  # 품명상세
    item_unit = models.CharField(max_length=32, null=True, verbose_name='단위')  # 단위

    quantity = models.FloatField(default=0, verbose_name='수량')  # 발주수량
    item_price = models.FloatField(default=0, verbose_name='단가', null=True)  # 단가
    supply_price = models.FloatField(default=0, verbose_name='공급가', null=True)  # 공급가
    surtax = models.FloatField(default=0, verbose_name='부가세', null=True)  # 부가세
    item_supply_total = models.FloatField(default=0, verbose_name='합계', null=True)  # 합계

    stock = models.FloatField(default=0, null=True, verbose_name='현재재고')  # 현재재고

    in_date = models.DateField(null=True, verbose_name='입고일자')  # 입고일자
    item_created_at = models.DateField(null=True, verbose_name='자재생산일자')  # 자재생산일자 (자재입고)
    location = models.ForeignKey('CodeMaster', models.SET_NULL, null=True, verbose_name="자재위치")  # 자재위치
    etc = models.CharField(max_length=20, null=True, verbose_name='비고')  # 비고

    ins = models.BooleanField(default=True, verbose_name='미입고구분')  # 미입고구분
    in_quantity = models.FloatField(default=0, verbose_name='입고수량')  # ins true : 입고 수량, ins false : 미입고 수량
    in_faulty = models.IntegerField(default=0, verbose_name='입고된 불량수량')

    item_in = models.ForeignKey('ItemIn', models.PROTECT, null=True, verbose_name='자재입고')  # 자재입고

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='orders_items_in_master_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='orders_items_in_master_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT,
                                   related_name='Orders_item_in_master_enterprise', verbose_name='업체')


class OutsourcingItem(models.Model):
    outsourcing_code = models.CharField(max_length=32, null=True, verbose_name='외주번호')

    item = models.ForeignKey('ItemMaster', models.PROTECT, verbose_name='품목')
    customer = models.ForeignKey('CustomerMaster', models.PROTECT, verbose_name='거래처')

    item_detail = models.CharField(max_length=32, null=True, verbose_name='품명상세')  # 품명상세
    item_division = models.CharField(max_length=32, null=True, verbose_name='자재구분')  # 단위

    quantity = models.FloatField(default=0, verbose_name='출하수량')  # 출하수량
    remarks = models.CharField(max_length=128, blank=True, verbose_name='비고')  # 비고

    in_date = models.DateField(default=None, null=True, verbose_name='입고일자')  # 입고일자

    in_ed_quantity = models.FloatField(default=0, verbose_name='입고된수량')  # 입고된 수량
    in_will_quantity = models.FloatField(default=quantity, verbose_name='입고할수량')  # 입고할 수량

    item_out = models.ForeignKey('ItemOut', models.SET_NULL, null=True, verbose_name='자재출고')  # 자재출고
    out_date = models.DateField(verbose_name='출고일자')  # 출고일자

    in_status = models.CharField(default='', max_length=16, verbose_name='입고현황')  # 미입고(''), 일부입고, 입고완료

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='outsourcing_items_master_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='outsourcing_items_master_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT,
                                   related_name='outsourcing_item_master_enterprise',
                                   verbose_name='업체')


class OutsourcingInItems(models.Model):
    outsourcing_item = models.ForeignKey('OutsourcingItem', models.PROTECT, null=True, verbose_name='외주항목')

    num = models.CharField(max_length=12, null=True, verbose_name='입고번호')  # 입고번호
    item = models.ForeignKey('ItemMaster', models.PROTECT, null=True, verbose_name='품목')

    in_date = models.DateField(null=True, verbose_name='입고일자')  # 입고일자
    item_in_at = models.DateField(null=True, verbose_name='자재입고일자')  # 자재생산일자 (자재입고)
    location = models.CharField(max_length=10, null=True, default='', verbose_name='창고저장위치')  # 자재위치
    etc = models.CharField(max_length=20, null=True, verbose_name='비고')  # 비고

    in_quantity = models.FloatField(default=0, verbose_name='입고수량')

    item_in = models.ForeignKey('ItemIn', models.SET_NULL, null=True, verbose_name='자재입고')  # 자재입고

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='outsourcing_items_in_master_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='outsourcing_items_in_master_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT,
                                   related_name='outsourcing_item_in_master_enterprise', verbose_name='업체')


class OrderCompany(models.Model):
    """ 발주기업 """

    class Meta:
        unique_together = ('name',)

    name = models.CharField(max_length=16, blank=False, verbose_name='납품기업명')
    explain = models.CharField(max_length=30, blank=True, verbose_name='설명')

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='order_company_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='order_company_updated_by',
                                   verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='order_company_master_enterprise',
                                   verbose_name='업체')


class Ordering(models.Model):
    code = models.ForeignKey('CustomerMaster', models.PROTECT, null=True, verbose_name='거래처코드')  # 거래처코드
    division = models.ForeignKey('CodeMaster',
                                 models.PROTECT,
                                 null=True,
                                 verbose_name='거래처구분')
    licensee_number = models.CharField(max_length=32, null=True, verbose_name='사업자번호')  # 사업자번호
    owner_name = models.CharField(max_length=8, null=True, verbose_name='대표자명')  # 대표자명
    business_conditions = models.CharField(max_length=16, null=True, verbose_name='업태')  # 업태
    business_event = models.CharField(max_length=16, null=True, verbose_name='종목')  # 종목
    postal_code = models.CharField(max_length=12, null=True, verbose_name='우편번호')  # 우편번호
    address = models.CharField(max_length=128, null=True, verbose_name='주소')  # 주소
    office_phone = models.CharField(max_length=32, null=True, verbose_name='회사전화번호')  # 회사전화번호
    office_fax = models.CharField(max_length=32, null=True, verbose_name='회사팩스번호')  # 회사팩스번호
    charge_name = models.CharField(max_length=8, null=True, verbose_name='담당자')  # 담당자
    charge_phone = models.CharField(max_length=32, null=True, verbose_name='담당자연락처')  # 담당자연락처
    charge_level = models.CharField(max_length=8, null=True, verbose_name='직급')  # 직급
    email = models.CharField(max_length=64, null=True, verbose_name='이메일')  # email
    enable = models.BooleanField(default=True, verbose_name='사용구분')  # 사용구분
    etc = models.CharField(max_length=64, null=True, verbose_name='비고')  # 비고

    ordering_code = models.CharField(max_length=32, null=True, verbose_name='주문번호')
    export_status = models.CharField(max_length=16, null=True, verbose_name='출하현황')
    provide_sum = models.FloatField(default=0, verbose_name='공급가')
    provide_surtax = models.BooleanField(default=True, verbose_name='부가세포함')

    due_date = models.DateField(null=True, verbose_name='납기일')  # 납기일
    pay_option = models.CharField(max_length=32, null=True, verbose_name='결제조건')  # 결제조건
    guarantee_date = models.DateField(null=True, verbose_name='품질보증기한')  # 품질보증기한
    deliver_place = models.CharField(max_length=32, null=True, verbose_name='납품장소')  # 납품장소
    note = models.CharField(max_length=128, null=True, verbose_name='NOTE 내용고정')  # NOTE

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='ordering_master_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='ordering_master_updated_by',
                                   verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='ordering_master_enterprise',
                                   verbose_name='업체')


class OrderingItems(models.Model):
    ordering = models.ForeignKey('Ordering', models.PROTECT, null=True, verbose_name='주문서')
    item = models.ForeignKey('ItemMaster', models.PROTECT, verbose_name='품목')

    item_detail = models.CharField(max_length=32, null=True, verbose_name='품명상세')  # 품명상세
    item_unit = models.CharField(max_length=32, null=True, verbose_name='단위')  # 단위

    quantity = models.FloatField(verbose_name='수량')  # 수량
    item_price = models.FloatField(verbose_name='단가', null=True)  # 단가
    supply_price = models.FloatField(verbose_name='공급가', null=True)  # 공급가
    surtax_chk = models.BooleanField(default=False, verbose_name='부가세포함')  # 부가세포함
    surtax = models.FloatField(verbose_name='부가세', null=True)  # 부가세
    item_supply_total = models.FloatField(verbose_name='합계', null=True)  # 합계
    file = models.FileField(upload_to='uploads/ordering/%Y/%m/%d/', default=None, null=True, verbose_name='파일')  # 첨부파일
    remarks = models.CharField(max_length=128, verbose_name='비고')  # 비고
    location = models.ForeignKey("CodeMaster", models.PROTECT, null=True, verbose_name="창고")

    # brand = models.CharField(max_length=20, null=True, verbose_name='브랜드')  # 브랜드
    # family = models.CharField(max_length=20, null=True, verbose_name='제품군')  # 제품군
    # nice = models.CharField(max_length=20, null=True, verbose_name='나이스번호')  # 나이스번호
    # shape = models.CharField(max_length=20, null=True, verbose_name='형태')  # 형태

    stock = models.FloatField(null=True, verbose_name='현재재고')  # 현재재고
    produce_status = models.CharField(max_length=8, null=True, verbose_name='생산현황')  # 생산현황
    export_quantity = models.FloatField(null=True, verbose_name='출하수량')  # 출하수량
    export_now_quantity = models.FloatField(default=0, verbose_name='출하된수량')  # 출하된수량
    export_address = models.CharField(max_length=128, null=True, verbose_name='출하주소')  # 출하주소
    work_status = models.CharField(max_length=8, null=True, verbose_name='작업진행현황')  # 작업진행현황
    export_date = models.DateField(null=True, verbose_name='출하일자')  # 출하일자

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='ordering_items_master_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='ordering_items_master_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='Ordering_item_master_enterprise',
                                   verbose_name='업체')

    # 주문서대비 원가조회
    cost_price = models.FloatField(default=0, verbose_name='원가', null=True)  # 원가
    cost_total = models.FloatField(default=0, verbose_name='원가', null=True)  # 원가 합계


class OrderingExItems(models.Model):
    ordering = models.ForeignKey('Ordering', models.PROTECT, null=True, verbose_name='주문서')
    ordering_item = models.ForeignKey('OrderingItems', models.PROTECT, null=True, verbose_name='주문항목')

    num = models.CharField(max_length=12, verbose_name='출하번호')  # 입/출하번호
    item = models.ForeignKey('ItemMaster', models.PROTECT, verbose_name='품목')

    item_detail = models.CharField(max_length=32, null=True, verbose_name='품명상세')  # 품명상세
    item_unit = models.CharField(max_length=32, null=True, verbose_name='단위')  # 단위

    quantity = models.FloatField(verbose_name='수량')  # 주문수량
    item_price = models.FloatField(verbose_name='단가', null=True)  # 단가
    supply_price = models.FloatField(verbose_name='공급가', null=True)  # 공급가
    surtax_chk = models.BooleanField(default=False, verbose_name='부가세포함')  # 부가세포함
    surtax = models.FloatField(verbose_name='부가세', null=True)  # 부가세
    item_supply_total = models.FloatField(verbose_name='합계', null=True)  # 합계

    stock = models.FloatField(null=True, verbose_name='현재재고')  # 현재재고
    produce_status = models.CharField(max_length=8, null=True, verbose_name='생산현황')  # 생산현황
    export_quantity = models.FloatField(null=True, verbose_name='출하수량')  # 출하수량
    export_address = models.CharField(max_length=128, null=True, verbose_name='출하주소')  # 출하주소
    work_status = models.CharField(max_length=8, null=True, verbose_name='작업진행현황')  # 작업진행현황
    export_date = models.DateField(null=True, verbose_name='출하일자')  # 출하일자
    out = models.BooleanField(default=True, verbose_name='미출하구분')  # 미출하구분
    item_out = models.ForeignKey('ItemOut', models.PROTECT, null=True, verbose_name='자재출고')  # 자재출고
    location = models.ForeignKey("CodeMaster", models.PROTECT, null=True, verbose_name="창고")

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='ordering_items_ex_master_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='ordering_items_ex_master_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT,
                                   related_name='Ordering_item_ex_master_enterprise',
                                   verbose_name='업체')


class Estimate(models.Model):
    code = models.ForeignKey('CustomerMaster', models.PROTECT, null=True, verbose_name='거래처코드')  # 거래처코드
    division = models.ForeignKey('CodeMaster',
                                 models.PROTECT,
                                 null=True,
                                 verbose_name='거래처구분')
    licensee_number = models.CharField(max_length=32, null=True, verbose_name='사업자번호')  # 사업자번호
    owner_name = models.CharField(max_length=8, null=True, verbose_name='대표자명')  # 대표자명
    business_conditions = models.CharField(max_length=16, null=True, verbose_name='업태')  # 업태
    business_event = models.CharField(max_length=16, null=True, verbose_name='종목')  # 종목
    postal_code = models.CharField(max_length=12, null=True, verbose_name='우편번호')  # 우편번호
    address = models.CharField(max_length=128, null=True, verbose_name='주소')  # 주소
    office_phone = models.CharField(max_length=32, null=True, verbose_name='회사전화번호')  # 회사전화번호
    office_fax = models.CharField(max_length=32, null=True, verbose_name='회사팩스번호')  # 회사팩스번호
    charge_name = models.CharField(max_length=8, null=True, verbose_name='담당자')  # 담당자
    charge_phone = models.CharField(max_length=32, null=True, verbose_name='담당자연락처')  # 담당자연락처
    charge_level = models.CharField(max_length=8, null=True, verbose_name='직급')  # 직급
    email = models.CharField(max_length=64, null=True, verbose_name='이메일')  # email
    enable = models.BooleanField(default=True, verbose_name='사용구분')  # 사용구분
    etc = models.CharField(max_length=64, null=True, verbose_name='비고')  # 비고

    estimate_code = models.CharField(max_length=32, null=True, verbose_name='견적번호')
    export_status = models.CharField(max_length=16, null=True, verbose_name='출하현황')
    provide_sum = models.FloatField(default=0, verbose_name='공급가')
    provide_surtax = models.BooleanField(default=True, verbose_name='부가세포함')

    due_date = models.DateField(null=True, verbose_name='납기일')  # 납기일
    pay_option = models.CharField(max_length=32, null=True, verbose_name='결제조건')  # 결제조건
    guarantee_date = models.DateField(null=True, verbose_name='품질보증기한')  # 품질보증기한
    deliver_place = models.CharField(max_length=32, null=True, verbose_name='납품장소')  # 납품장소
    note = models.CharField(max_length=128, null=True, verbose_name='NOTE 내용고정')  # NOTE

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='estimate_master_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='estimate_master_updated_by',
                                   verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='estimate_master_enterprise',
                                   verbose_name='업체')


class EstimateItems(models.Model):
    estimate = models.ForeignKey('Estimate', models.PROTECT, null=False, verbose_name='견적서')
    item = models.ForeignKey('ItemMaster', models.PROTECT, null=True, verbose_name='품목')

    item_detail = models.CharField(max_length=32, null=True, verbose_name='품명상세')  # 품명상세
    item_unit = models.CharField(max_length=32, null=True, verbose_name='단위')  # 단위

    quantity = models.FloatField(verbose_name='수량', null=True)  # 수량
    item_price = models.FloatField(verbose_name='단가', null=True)  # 단가
    supply_price = models.FloatField(verbose_name='공급가', null=True)  # 공급가
    surtax = models.FloatField(verbose_name='부가세', null=True)  # 부가세
    item_supply_total = models.FloatField(verbose_name='합계', null=True)  # 합계
    remarks = models.CharField(max_length=128, verbose_name='비고')  # 비고

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='estimate_items_master_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='estimate_items_master_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='estimate_item_master_enterprise',
                                   verbose_name='업체')


class Request(models.Model):
    code = models.ForeignKey('CustomerMaster', models.PROTECT, null=True, verbose_name='거래처코드')  # 거래처코드
    division = models.ForeignKey('CodeMaster',
                                 models.PROTECT,
                                 null=True,
                                 verbose_name='거래처구분')
    licensee_number = models.CharField(max_length=32, null=True, verbose_name='사업자번호')  # 사업자번호
    owner_name = models.CharField(max_length=8, null=True,
                                  verbose_name='대표자명')  # 대표자명, it could cause length problems (due to Korean..).
    business_conditions = models.CharField(max_length=16, null=True, verbose_name='업태')  # 업태
    business_event = models.CharField(max_length=16, null=True, verbose_name='종목')  # 종목
    postal_code = models.CharField(max_length=12, null=True, verbose_name='우편번호')  # 우편번호
    address = models.CharField(max_length=128, null=True, verbose_name='주소')  # 주소
    office_phone = models.CharField(max_length=32, null=True, verbose_name='회사전화번호')  # 회사전화번호
    office_fax = models.CharField(max_length=32, null=True, verbose_name='회사팩스번호')  # 회사팩스번호
    charge_name = models.CharField(max_length=8, null=True, verbose_name='담당자')  # 담당자
    charge_phone = models.CharField(max_length=32, null=True, verbose_name='담당자연락처')  # 담당자연락처
    charge_level = models.CharField(max_length=8, null=True, verbose_name='직급')  # 직급
    email = models.CharField(max_length=64, null=True, verbose_name='이메일')  # email
    etc = models.CharField(max_length=64, null=True, verbose_name='비고')  # 비고
    request_code = models.CharField(max_length=32, null=True, verbose_name='의뢰번호')
    export_status = models.CharField(max_length=16, null=True, verbose_name='출하현황')
    provide_sum = models.FloatField(default=0, verbose_name='공급가')

    due_date = models.DateField(null=True, verbose_name='납기일')  # 납기일
    pay_option = models.CharField(max_length=32, null=True, verbose_name='결제조건')  # 결제조건
    guarantee_date = models.DateField(null=True, verbose_name='품질보증기한')  # 품질보증기한
    deliver_place = models.CharField(max_length=32, null=True, verbose_name='납품장소')  # 납품장소
    note = models.CharField(max_length=128, null=True, verbose_name='NOTE 내용고정')  # NOTE

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='request_master_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='request_master_updated_by',
                                   verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='request_master_enterprise',
                                   verbose_name='업체')


class RequestItems(models.Model):
    request = models.ForeignKey('Request', models.PROTECT, null=False, verbose_name='의뢰서')
    item = models.ForeignKey('ItemMaster', models.PROTECT, verbose_name='품목')
    item_detail = models.CharField(max_length=32, null=True, verbose_name='품명상세')  # 품명상세
    item_unit = models.CharField(max_length=32, null=True, verbose_name='단위')  # 단위

    quantity = models.FloatField(default=0, verbose_name='수량')  # 수량
    file = models.FileField(upload_to='uploads/request/%Y/%m/%d/', default="", null=True, verbose_name='파일')  # 첨부파일
    remarks = models.CharField(default="", null=True, max_length=128, verbose_name='비고')  # 비고

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='request_items_master_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='request_items_master_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='request_item_master_enterprise',
                                   verbose_name='업체')


class Qunbalance(models.Model):
    code = models.CharField(max_length=32, verbose_name='관리코드')  # 관리코드
    item_name = models.CharField(max_length=32, verbose_name="제품명")
    test_date = models.DateField(verbose_name='테스트_일자')

    date_start = models.DateTimeField(verbose_name='시작_시간', null=True)
    date_end = models.DateTimeField(verbose_name='마지막_시간', null=True)

    first_unbalance1 = models.FloatField(default=0, verbose_name='처음 unbalance1 값')
    first_angle1 = models.FloatField(default=0, verbose_name='처음 angle1 값')
    first_unbalance2 = models.FloatField(default=0, verbose_name='처음 unbalance2 값')
    first_angle2 = models.FloatField(default=0, verbose_name='처음 angle2 값')

    last_unbalance1 = models.FloatField(default=0, verbose_name='마지막 unbalance1 값')
    last_angle1 = models.FloatField(default=0, verbose_name='마지막 마지막 angle1 값')
    last_unbalance2 = models.FloatField(default=0, verbose_name='마지막 unbalance2 값')
    last_angle2 = models.FloatField(default=0, verbose_name='마지막 angle2 값')

    complete = models.BooleanField(default=False, verbose_name='완료')  # 저장 여부

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='Qunbalance_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='Qunbalance_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='Qunbalance_enterprise',
                                   verbose_name='업체', null=True)


class QunbalanceDetail(models.Model):
    num = models.ForeignKey('Qunbalance', models.PROTECT, verbose_name='unbalance num')

    unbalance1 = models.FloatField(default=0, verbose_name='unbalance1 값')
    angle1 = models.FloatField(default=0, verbose_name='angle1 값')
    unbalance2 = models.FloatField(default=0, verbose_name='unbalance2 값')
    angle2 = models.FloatField(default=0, verbose_name='angle2 값')

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='QunbalanceDetail_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='QunbalanceDetail_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='QunbalanceDetail_enterprise',
                                   verbose_name='업체', null=True)


class KpiLog(models.Model):
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='KpiLog_enterprise',
                                   verbose_name='업체')
    created_by = models.CharField(max_length=256, verbose_name='작성자')  # 작성자
    kpiDate = models.DateField(auto_now_add=True, verbose_name='처리일자')  # 처리일자
    # activeUserCnt  # 일일 접속자 수, created_by annotate 로 계산
    # systemMenuCnt  # 시스템 운영 메뉴수, 모듈 권한 정보로 계산
    module = models.CharField(max_length=256, verbose_name='사용모듈')  # 사용모듈, module annotate 로 호출된 모듈 계산
    crud = models.CharField(max_length=64, verbose_name='CRUD')  # 모델명을 사용 [조회, 추가, 수정, 삭제]
    # tableCnt  # 테이블 수, 수동 계산
    error = models.BooleanField(default=False, verbose_name='트랜잭션')  # 트랜잭션 수행 row 수


class Rotator(models.Model):
    code = models.CharField(max_length=32, null=True, verbose_name='관리코드')  # 관리코드
    item_name = models.CharField(max_length=32, null=True, verbose_name="제품명")
    test_date = models.DateField(null=True, verbose_name='테스트_일자')
    serial = models.CharField(max_length=128, null=True, verbose_name="시리얼")
    field_cnt = models.IntegerField(default=5, verbose_name='필드수')

    image = models.ImageField(upload_to='uploads', max_length=256, default=None, null=True, verbose_name='이미지')

    # 필드 F01
    F01_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_01")
    F01_Detail = models.CharField(max_length=32, default='', verbose_name="상세_01")
    F01_standard = models.CharField(max_length=32, default='', verbose_name="규격_01")
    F01_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_01")
    F01_pi = models.CharField(max_length=32, default='', verbose_name="파이_01")
    F01_vibration = models.CharField(max_length=32, default='', verbose_name="진동_01")
    F01_measure_div = models.CharField(max_length=32, default='', verbose_name="측정부분_01")
    F01_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_01")

    # 필드 F02
    F02_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_02")
    F02_Detail = models.CharField(max_length=32, default='', verbose_name="상세_02")
    F02_standard = models.CharField(max_length=32, default='', verbose_name="규격_02")
    F02_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_02")
    F02_pi = models.CharField(max_length=32, default='', verbose_name="파이_02")
    F02_vibration = models.CharField(max_length=32, default='', verbose_name="진동_02")
    F02_measure_div = models.CharField(max_length=32, default='', verbose_name="측정부분_02")
    F02_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_02")

    # 필드 F03
    F03_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_03")
    F03_Detail = models.CharField(max_length=32, default='', verbose_name="상세_03")
    F03_standard = models.CharField(max_length=32, default='', verbose_name="규격_03")
    F03_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_03")
    F03_pi = models.CharField(max_length=32, default='', verbose_name="파이_03")
    F03_vibration = models.CharField(max_length=32, default='', verbose_name="진동_03")
    F03_measure_div = models.CharField(max_length=32, default='', verbose_name="측정부분_03")
    F03_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_03")

    # 필드 F04
    F04_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_04")
    F04_Detail = models.CharField(max_length=32, default='', verbose_name="상세_04")
    F04_standard = models.CharField(max_length=32, default='', verbose_name="규격_04")
    F04_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_04")
    F04_pi = models.CharField(max_length=32, default='', verbose_name="파이_04")
    F04_vibration = models.CharField(max_length=32, default='', verbose_name="진동_04")
    F04_measure_div = models.CharField(max_length=32, default='', verbose_name="측정부분_04")
    F04_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_04")

    # 필드 F05
    F05_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_05")
    F05_Detail = models.CharField(max_length=32, default='', verbose_name="상세_05")
    F05_standard = models.CharField(max_length=32, default='', verbose_name="규격_05")
    F05_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_05")
    F05_pi = models.CharField(max_length=32, default='', verbose_name="파이_05")
    F05_vibration = models.CharField(max_length=32, default='', verbose_name="진동_05")
    F05_measure_div = models.CharField(max_length=32, default='', verbose_name="측정부분_05")
    F05_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_05")

    # 필드 F06
    F06_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_06")
    F06_Detail = models.CharField(max_length=32, default='', verbose_name="상세_06")
    F06_standard = models.CharField(max_length=32, default='', verbose_name="규격_06")
    F06_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_06")
    F06_pi = models.CharField(max_length=32, default='', verbose_name="파이_06")
    F06_vibration = models.CharField(max_length=32, default='', verbose_name="진동_06")
    F06_measure_div = models.CharField(max_length=32, default='', verbose_name="측정부분_06")
    F06_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_06")

    # 필드 F07
    F07_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_07")
    F07_Detail = models.CharField(max_length=32, default='', verbose_name="상세_07")
    F07_standard = models.CharField(max_length=32, default='', verbose_name="규격_07")
    F07_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_07")
    F07_pi = models.CharField(max_length=32, default='', verbose_name="파이_07")
    F07_vibration = models.CharField(max_length=32, default='', verbose_name="진동_07")
    F07_measure_div = models.CharField(max_length=32, default='', verbose_name="측정부분_07")
    F07_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_07")

    # 필드 F08
    F08_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_08")
    F08_Detail = models.CharField(max_length=32, default='', verbose_name="상세_08")
    F08_standard = models.CharField(max_length=32, default='', verbose_name="규격_08")
    F08_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_08")
    F08_pi = models.CharField(max_length=32, default='', verbose_name="파이_08")
    F08_vibration = models.CharField(max_length=32, default='', verbose_name="진동_08")
    F08_measure_div = models.CharField(max_length=32, default='', verbose_name="측정부분_08")
    F08_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_08")

    # 필드 F09
    F09_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_09")
    F09_Detail = models.CharField(max_length=32, default='', verbose_name="상세_09")
    F09_standard = models.CharField(max_length=32, default='', verbose_name="규격_09")
    F09_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_09")
    F09_pi = models.CharField(max_length=32, default='', verbose_name="파이_09")
    F09_vibration = models.CharField(max_length=32, default='', verbose_name="진동_09")
    F09_measure_div = models.CharField(max_length=32, default='', verbose_name="측정부분_09")
    F09_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_09")

    # 필드 F10
    F10_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_10")
    F10_Detail = models.CharField(max_length=32, default='', verbose_name="상세_10")
    F10_standard = models.CharField(max_length=32, default='', verbose_name="규격_10")
    F10_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_10")
    F10_pi = models.CharField(max_length=32, default='', verbose_name="파이_10")
    F10_vibration = models.CharField(max_length=32, default='', verbose_name="진동_10")
    F10_measure_div = models.CharField(max_length=32, default='', verbose_name="측정부분_10")
    F10_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_10")

    # 필드 F11
    F11_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_11")
    F11_Detail = models.CharField(max_length=32, default='', verbose_name="상세_11")
    F11_standard = models.CharField(max_length=32, default='', verbose_name="규격_11")
    F11_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_11")
    F11_pi = models.CharField(max_length=32, default='', verbose_name="파이_11")
    F11_vibration = models.CharField(max_length=32, default='', verbose_name="진동_11")
    F11_measure_div = models.CharField(max_length=32, default='', verbose_name="측정부분_11")
    F11_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_11")

    # 필드 F12
    F12_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_12")
    F12_Detail = models.CharField(max_length=32, default='', verbose_name="상세_12")
    F12_standard = models.CharField(max_length=32, default='', verbose_name="규격_12")
    F12_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_12")
    F12_pi = models.CharField(max_length=32, default='', verbose_name="파이_12")
    F12_vibration = models.CharField(max_length=32, default='', verbose_name="진동_12")
    F12_measure_div = models.CharField(max_length=32, default='', verbose_name="측정부분_12")
    F12_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_12")

    # 필드 F13
    F13_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_13")
    F13_Detail = models.CharField(max_length=32, default='', verbose_name="상세_13")
    F13_standard = models.CharField(max_length=32, default='', verbose_name="규격_13")
    F13_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_13")
    F13_pi = models.CharField(max_length=32, default='', verbose_name="파이_13")
    F13_vibration = models.CharField(max_length=32, default='', verbose_name="진동_13")
    F13_measure_div = models.CharField(max_length=32, default='', verbose_name="측정부분_13")
    F13_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_13")

    # 필드 F14
    F14_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_14")
    F14_Detail = models.CharField(max_length=32, default='', verbose_name="상세_14")
    F14_standard = models.CharField(max_length=32, default='', verbose_name="규격_14")
    F14_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_14")
    F14_pi = models.CharField(max_length=32, default='', verbose_name="파이_14")
    F14_vibration = models.CharField(max_length=32, default='', verbose_name="진동_14")
    F14_measure_div = models.CharField(max_length=32, default='', verbose_name="측정부분_14")
    F14_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_14")

    # 필드 F15
    F15_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_15")
    F15_Detail = models.CharField(max_length=32, default='', verbose_name="상세_15")
    F15_standard = models.CharField(max_length=32, default='', verbose_name="규격_15")
    F15_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_15")
    F15_pi = models.CharField(max_length=32, default='', verbose_name="파이_15")
    F15_vibration = models.CharField(max_length=32, default='', verbose_name="진동_15")
    F15_measure_div = models.CharField(max_length=32, default='', verbose_name="측정부분_15")
    F15_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_15")

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='Rotator_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='Rotator_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='Rotator_enterprise',
                                   verbose_name='업체')


class Stator(models.Model):
    code = models.CharField(max_length=32, null=True, verbose_name='관리코드')  # 관리코드
    item_name = models.CharField(max_length=32, null=True, verbose_name="제품명")
    test_date = models.DateField(null=True, verbose_name='테스트_일자')
    serial = models.CharField(max_length=128, null=True, verbose_name="시리얼")
    field_cnt = models.IntegerField(default=5, verbose_name='필드수')

    image1 = models.ImageField(upload_to='uploads', max_length=256, default=None, null=True, verbose_name='이미지1')
    image2 = models.ImageField(upload_to='uploads', max_length=256, default=None, null=True, verbose_name='이미지2')

    # 필드 F01
    F01_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_01")
    F01_Detail = models.CharField(max_length=32, default='', verbose_name="상세_01")
    F01_standard = models.CharField(max_length=32, default='', verbose_name="규격_01")
    F01_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_01")
    F01_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_01")

    # 필드 F02
    F02_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_02")
    F02_Detail = models.CharField(max_length=32, default='', verbose_name="상세_02")
    F02_standard = models.CharField(max_length=32, default='', verbose_name="규격_02")
    F02_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_02")
    F02_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_02")

    # 필드 F03
    F03_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_03")
    F03_Detail = models.CharField(max_length=32, default='', verbose_name="상세_03")
    F03_standard = models.CharField(max_length=32, default='', verbose_name="규격_03")
    F03_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_03")
    F03_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_03")

    # 필드 F04
    F04_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_04")
    F04_Detail = models.CharField(max_length=32, default='', verbose_name="상세_04")
    F04_standard = models.CharField(max_length=32, default='', verbose_name="규격_04")
    F04_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_04")
    F04_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_04")

    # 필드 F05
    F05_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_05")
    F05_Detail = models.CharField(max_length=32, default='', verbose_name="상세_05")
    F05_standard = models.CharField(max_length=32, default='', verbose_name="규격_05")
    F05_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_05")
    F05_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_05")

    # 필드 F06
    F06_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_06")
    F06_Detail = models.CharField(max_length=32, default='', verbose_name="상세_06")
    F06_standard = models.CharField(max_length=32, default='', verbose_name="규격_06")
    F06_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_06")
    F06_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_06")

    # 필드 F07
    F07_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_07")
    F07_Detail = models.CharField(max_length=32, default='', verbose_name="상세_07")
    F07_standard = models.CharField(max_length=32, default='', verbose_name="규격_07")
    F07_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_07")
    F07_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_07")

    # 필드 F08
    F08_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_08")
    F08_Detail = models.CharField(max_length=32, default='', verbose_name="상세_08")
    F08_standard = models.CharField(max_length=32, default='', verbose_name="규격_08")
    F08_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_08")
    F08_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_08")

    # 필드 F09
    F09_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_09")
    F09_Detail = models.CharField(max_length=32, default='', verbose_name="상세_09")
    F09_standard = models.CharField(max_length=32, default='', verbose_name="규격_09")
    F09_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_09")
    F09_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_09")

    # 필드 F10
    F10_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_10")
    F10_Detail = models.CharField(max_length=32, default='', verbose_name="상세_10")
    F10_standard = models.CharField(max_length=32, default='', verbose_name="규격_10")
    F10_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_10")
    F10_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_10")

    # 필드 F11
    F11_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_11")
    F11_Detail = models.CharField(max_length=32, default='', verbose_name="상세_11")
    F11_standard = models.CharField(max_length=32, default='', verbose_name="규격_11")
    F11_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_11")
    F11_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_11")

    # 필드 F12
    F12_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_12")
    F12_Detail = models.CharField(max_length=32, default='', verbose_name="상세_12")
    F12_standard = models.CharField(max_length=32, default='', verbose_name="규격_12")
    F12_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_12")
    F12_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_12")

    # 필드 F13
    F13_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_13")
    F13_Detail = models.CharField(max_length=32, default='', verbose_name="상세_13")
    F13_standard = models.CharField(max_length=32, default='', verbose_name="규격_13")
    F13_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_13")
    F13_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_13")

    # 필드 F14
    F14_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_14")
    F14_Detail = models.CharField(max_length=32, default='', verbose_name="상세_14")
    F14_standard = models.CharField(max_length=32, default='', verbose_name="규격_14")
    F14_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_14")
    F14_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_14")

    # 필드 F15
    F15_measure_part = models.CharField(max_length=32, default='', verbose_name="측정부_15")
    F15_Detail = models.CharField(max_length=32, default='', verbose_name="상세_15")
    F15_standard = models.CharField(max_length=32, default='', verbose_name="규격_15")
    F15_concentricity = models.CharField(max_length=32, default='', verbose_name="동심도_15")
    F15_measure_value = models.CharField(max_length=32, default='', verbose_name="측정값_15")

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='Stator_created_by', verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True,
                                   related_name='Stator_updated_by', verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='Stator_enterprise',
                                   verbose_name='업체')


def custom_upload_to(instance, filename):
    # NAS 저장 경로 설정 (예시)
    nas_base_path = 'TEST'   # NAS 공유 폴더 경로
    today = instance.created_at
    filename = instance.file.name  # 원본 파일 이름 사용

    return os.path.join(nas_base_path, today, filename)


class MyInfoMaster(models.Model):
    class Meta:
        unique_together = ('enterprise', 'company_division')

    company_division = models.CharField(max_length=32, verbose_name='사업장')  # 사업장
    company_name = models.CharField(max_length=32, verbose_name='회사명')  # 회사명
    licensee_number = models.CharField(max_length=32, verbose_name='사업자번호')  # 사업자번호
    owner_name = models.CharField(max_length=32, null=True, verbose_name='대표자명')  # 대표자명
    # file = models.FileField(upload_to='uploads/orders/%Y/%m/%d/', default=None, null=True, verbose_name='파일')  # 첨부파일
    file = models.FileField(upload_to=custom_upload_to, default=None, null=True, verbose_name='파일')  # 첨부파일
    logo = models.FileField(upload_to='uploads/orders/%Y/%m/%d/', default=None, null=True, verbose_name='로고')  # 로고파일

    business_conditions = models.CharField(max_length=32, null=True, verbose_name='업태')  # 업태
    business_event = models.CharField(max_length=32, null=True, verbose_name='종목')  # 종목
    post_code = models.CharField(max_length=12, null=True, verbose_name='우편번호')  # 우편번호, postal_code > post_code
    address = models.CharField(max_length=128, null=True, verbose_name='주소')  # 주소

    office_phone = models.CharField(max_length=32, null=True, verbose_name='전화번호')  # 전화번호
    office_fax = models.CharField(max_length=32, null=True, verbose_name='팩스번호')  # 팩스번호
    email = models.CharField(max_length=64, null=True, verbose_name='이메일')  # 이메일
    note = models.CharField(max_length=128, null=True, verbose_name='비고')  # 비고

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='myinfo_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='myinfo_updated_by',
                                   verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='my_info_enterprise',
                                   verbose_name='업체')


class UnitPrice(models.Model):
    item = models.ForeignKey('ItemMaster', models.PROTECT, verbose_name='품목')
    customer = models.ForeignKey('CustomerMaster', models.PROTECT, verbose_name='거래처')
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, verbose_name='업체')
    unit_price = models.DecimalField(max_digits=9, decimal_places=3, default=0.00, verbose_name='단가')
    fee_rate = models.DecimalField(max_digits=9, decimal_places=3, default=0.00, verbose_name='수수료율')

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, verbose_name='최초작성자',
                                   related_name='unitprice_created_by')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, verbose_name='최종작성자',
                                   related_name='unitprice_updated_by')  # 최종작성자
    del_flag = models.CharField(max_length=1, default='N')
    division = models.ForeignKey('CodeMaster', models.PROTECT, null=True, verbose_name='거래처구분')
    etc = models.CharField(max_length=128, null=True, verbose_name='기타')
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일


class MenuMaster(models.Model):
    code = models.CharField(max_length=50, null=False, verbose_name='메뉴코드')
    name = models.CharField(max_length=50, null=False, verbose_name='메뉴이름')
    path = models.CharField(max_length=256, null=False, verbose_name='경로')
    type = models.CharField(max_length=1, null=False, verbose_name='유형')
    comment = models.CharField(max_length=256, verbose_name='코멘트')
    i_class = models.CharField(max_length=64, verbose_name='class icon')
    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, verbose_name='최초작성자',
                                   related_name='menumaster_created_by')
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, verbose_name='최종작성자',
                                   related_name='menumaster_updated_by')
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')
    del_flag = models.CharField(max_length=1, default='N', verbose_name='삭제여부')


class Menu_Auth(models.Model):
    menu = models.ForeignKey('MenuMaster', models.PROTECT, null=False, verbose_name='메뉴아이디',
                             related_name='menuauth')
    alias = models.CharField(max_length=64, null=True, verbose_name='별칭')
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, verbose_name='업체')
    user = models.ForeignKey('UserMaster', models.PROTECT, null=False, verbose_name='사용자')
    # parent = models.ForeignKey('MenuMaster', models.PROTECT, null=False, verbose_name='상위키')
    parent_id = models.IntegerField(null=True, verbose_name='상위클래스')
    order = models.IntegerField(null=False, verbose_name='순서')
    use_flag = models.CharField(max_length=1, default='Y', verbose_name='사용여부')
    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, verbose_name='최초작성자',
                                   related_name='menuauth_created_by')
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, verbose_name='최종작성자',
                                   related_name='menuauth_updated_by')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name='최종작성일')
    del_flag = models.CharField(max_length=1, default='N', verbose_name='삭제여부')


class ColumnMaster(models.Model):
    menu = models.ForeignKey('MenuMaster', models.PROTECT, null=False, verbose_name='메뉴아이디', related_name='column')
    label = models.CharField(max_length=64, null=True, verbose_name='컬럼명')
    label_en = models.CharField(max_length=64, null=True, verbose_name='컬럼명(영)')
    pre_label = models.CharField(max_length=128, null=True, verbose_name='선행자')
    tag = models.CharField(max_length=128, null=True, verbose_name='tag')
    type = models.CharField(max_length=64, null=True, verbose_name='text')
    class_name = models.CharField(max_length=128, null=True, verbose_name='class')
    event = models.CharField(max_length=128, null=True, verbose_name='onclick')
    position = models.IntegerField(null=False, verbose_name='순서')
    # colmenuauth = models.ForeignKey('Menu_Auth', models.PROTECT, null=False, verbose_name='사용자권한', related_name='col_menuauth')
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, verbose_name='업체')
    user = models.ForeignKey('UserMaster', models.PROTECT, null=False, verbose_name='사용자')
    use_flag = models.BooleanField(default=True, verbose_name='사용여부')
    visual_flag = models.BooleanField(default=True, verbose_name='표시여부')
    excel_flag = models.BooleanField(default=True, verbose_name='엑셀다운로드사용여부')
    edit_flag = models.BooleanField(default=True, verbose_name='수정필드')
    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, verbose_name='최초작성자',
                                   related_name='column_created_by')
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, verbose_name='최종작성자',
                                   related_name='column_updated_by')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='최종작성일')
    attr = models.CharField(max_length=64, null=True, verbose_name='속성')
    tier = models.CharField(max_length=1, null=False, default='M', verbose_name='테이블계층')  # 메인과 sub테이블 구분 M,S


class Menu_Exam(models.Model):
    menu = models.ForeignKey('MenuMaster', models.PROTECT, null=False, verbose_name='메뉴아이디',
                             related_name='menuexam')
    alias = models.CharField(max_length=64, null=True, verbose_name='별칭')
    # enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, verbose_name='업체')
    # user = models.ForeignKey('UserMaster', models.PROTECT, null=False, verbose_name='사용자')
    parent_id = models.IntegerField(null=True, verbose_name='상위클래스')
    order = models.IntegerField(null=False, verbose_name='순서')
    use_flag = models.CharField(max_length=1, default='Y', verbose_name='사용여부')
    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, verbose_name='최초작성자',
                                   related_name='menuexam_created_by')
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, verbose_name='최종작성자',
                                   related_name='menuexam_updated_by')
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')
    del_flag = models.CharField(max_length=1, default='N', verbose_name='삭제여부')
    com_type = models.CharField(max_length=1, verbose_name='기업유형') # 운영기관(I), 고객사(C), 운영사(O), 공급사(S), 소상인(M), 서울소프트(A)
