import traceback
from datetime import date, datetime
import time
from decimal import *

from django.db import IntegrityError, transaction
from django.db.models import Sum, Avg, Q, Count
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

from api import bom
from api.models import CodeMaster, CustomerMaster, GroupCodeMaster, Process, Subprocess, SubprocessProgress, \
    RentalMaster, Rental, EnterpriseMaster, FacilitiesMaster, ItemRein, Sensor, SensorValue, ItemWarehouseIn, \
    ItemWarehouseOut, ItemWarehouseRein, ItemWarehouseAdjust, ItemWarehouseStock, FacilitiesFiles, SensorPC, \
    SensorPCValue, Order, OrderIn, OrderCompany, Ordering, OrderingItems, Estimate, EstimateItems, Request, \
    RequestItems, \
    SensorH2, SensorH2Value, SubprocessTemplet, SubprocessFaultReason, OrderingExItems, Qunbalance, QunbalanceDetail, \
    Rotator, Stator, \
    MyInfoMaster, Orders, OrdersItems, OrdersInItems, OutsourcingItem, OutsourcingInItems, ItemLed, ItemOutOrder, \
    Device, SubprocessLog, UnitPrice, MenuMaster, ColumnMaster
from api.models import UserMaster
from api.models import ItemMaster
from api.models import BomMaster, Bom, BomLog
from api.models import ItemIn, ItemOut, ItemAdjust


def subprocess_log(subprocess, data, separator):
    if separator == "itemIn":
        create = SubprocessLog.objects.create(
            subprocess=subprocess,
            itemIn=data
        )
    else:
        create = SubprocessLog.objects.create(
            subprocess=subprocess,
            itemOut=data
        )

    return create


def generate_code(prefix1, model, model_field_prefix, user):
    today = date.today()
    prefix2 = str(today.year * 10000 + today.month * 100 + today.day)
    kwargs = {
        model_field_prefix + '__istartswith': prefix1 + prefix2,
        'enterprise': user.enterprise
    }
    res = model.objects.filter(**kwargs).order_by(model_field_prefix)
    if res.exists() is False:
        return prefix1 + str(int(prefix2) * 1000)

    last_order = res.values(model_field_prefix).last()[model_field_prefix]
    return prefix1 + str(int(prefix2) * 1000 + int(last_order[-3:]) + 1)


def generate_lot_code(code_id, model, model_field_prefix, user):
    if not code_id:
        raise ValidationError('자재구분 코드를 입력해주세요.')

    prefix1 = CodeMaster.objects.filter(id=code_id).values('code').first().get('code')

    if not prefix1:
        raise ValidationError('자재구분 코드가 존재하지 않습니다.')

    today = date.today()
    prefix2 = f"{today.year}{today.month:02d}{today.day:02d}"

    kwargs = {
        model_field_prefix + '__istartswith': prefix1 + '-' + prefix2 + '-',
        'enterprise': user.enterprise
    }

    cnt = model.objects.filter(**kwargs).aggregate(cnt=Count('*'))['cnt']
    print("cnt   : " + str(cnt))
    if cnt == 0:
        return prefix1 + '-' + prefix2 + '-' + '01'
    elif 0 < cnt < 9:
        return prefix1 + '-' + prefix2 + '-' + '0' + str(int(cnt) + 1)
    elif cnt == 99:
        raise ValidationError('당일 순번이 99를 초과하여 입고등록을 진행 할 수 없습니다.')
    else:
        return prefix1 + '-' + prefix2 + '-' + str(int(cnt) + 1)


class BaseSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(required=False, read_only=True)  # 최종작성일
    updated_by = serializers.CharField(required=False, read_only=True)  # 최종작성자

    def __init__(self, *args, **kwargs):
        super(BaseSerializer, self).__init__(*args, **kwargs)

        # override fields' error messages.
        for field in self.fields:
            f = self.fields[field]
            for k, v in f.error_messages.items():
                try:
                    verbose_name = getattr(f.parent.Meta.model, getattr(f, 'field_name')).field.verbose_name
                    f.error_messages[k] = verbose_name + ": " + str(v)
                except:
                    continue

    def get_by_username(self):
        return self.context['request'].user

    def create(self, instance):
        instance['created_by'] = self.get_by_username()
        instance['updated_by'] = self.get_by_username()

        return super().create(instance)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.get_by_username()

        return super().update(instance, validated_data)

    def code_validator(self, code_master, group_code):
        if code_master is None:
            return code_master

        qs = GroupCodeMaster.objects.filter(pk=code_master.group_id, code=group_code)
        if qs.exists() is not True:
            message = '잘못된 코드 code must be a multiple of %d.' % group_code
            raise serializers.ValidationError(message)

        return code_master

    def to_internal_value(self, data):
        self.unlock_data(data)

        if 'enterprise' not in data:
            enterprise = self.context['request'].user.enterprise
            data['enterprise'] = enterprise.id

        return super(BaseSerializer, self).to_internal_value(data)

    def unlock_data(self, data):
        if type(data) is not dict:
            data._mutable = True


class EnterpriseMasterSerializer(serializers.ModelSerializer):
    master = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = EnterpriseMaster
        fields = '__all__'

    def get_master(self, obj):
        res = UserMaster.objects.filter(enterprise=obj, is_master=True)
        if res.count() > 1:
            raise ValidationError('[에러] 관리자 master id가 1명 이상입니다. 시스템 관리자에게 보고해주십시오.')

        return UserMasterSerializer(res.first()).data


class GroupCodeMasterSerializer(BaseSerializer):
    class Meta:
        model = GroupCodeMaster
        fields = '__all__'


class CodeMasterSerializer(BaseSerializer):
    class Meta:
        model = CodeMaster
        fields = '__all__'

    #
    # def get_generated_id(self, obj):
    #     return 1000 * obj['group'].code + obj['code']

    def create(self, instance):
        # validated_data['id'] = self.get_generated_id(validated_data)

        try:
            return super().create(instance)
        except IntegrityError:
            raise ValidationError('중복되는 id 이므로 생성할 수 없습니다.')

    def to_representation(self, instance):

        self.fields['group'] = GroupCodeMasterSerializer()
        return super(CodeMasterSerializer, self).to_representation(instance)


class CodeMasterSelectSerializer(BaseSerializer):
    class Meta:
        model = CodeMaster
        fields = '__all__'

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name,
        }


class CustomerMasterSerializer(BaseSerializer):
    class Meta:
        model = CustomerMaster
        fields = '__all__'

    def validate_division(self, value):
        return self.code_validator(value, 108)

    def to_representation(self, instance):
        self.fields['division'] = CodeMasterSerializer()

        return super(CustomerMasterSerializer, self).to_representation(instance)


class CustomerMasterSelectSerializer(BaseSerializer):  # Select2 id, name 만 가져오는 경우
    class Meta:
        model = CustomerMaster
        fields = '__all__'

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name,
        }


class CustomerMasterPartSerializer(BaseSerializer):  # Select2 일부분 정보를 가져오는 경우
    class Meta:
        model = CustomerMaster
        fields = '__all__'

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'code': instance.code,
            'name': instance.name,
            'licensee_number': instance.licensee_number,  # 사업자번호
            'owner_name': instance.owner_name,  # 대표자명
            'business_conditions': instance.business_conditions,  # 업태
            'business_event': instance.business_event,  # 종목
            'postal_code': instance.postal_code,  # 우편번호
            'address': instance.address,  # 주소
            'office_phone': instance.office_phone,  # 회사전화번호
            'office_fax': instance.office_fax,  # 팩스번호
            'charge_name': instance.charge_name,  # 담당자
            'charge_level': instance.charge_level,  # 직급
            'charge_phone': instance.charge_phone,  # 담당자 연락처
            'email': instance.email,  # 이메일
            'etc': instance.etc,  # 비고
        }


class UserMasterSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=8, required=False, read_only=True)
    password = serializers.CharField(write_only=True)

    created_by = serializers.CharField(required=False, read_only=True)  # 최종작성일
    created_at = serializers.CharField(required=False, read_only=True)  # 최초작성일

    enterprise_name = serializers.SerializerMethodField(read_only=True, required=False)
    enterprise_manage = serializers.SerializerMethodField(read_only=True, required=False)  # 관리명

    # enterprise = serializers.IntegerField(required=False, read_only=True)

    class Meta:
        model = UserMaster
        # fields = ['id', 'user_id', 'code', 'username', 'factory_classification',
        #           'employment_division', 'employment_date', 'job_position', 'department_position',
        #           'postal_code', 'address', 'enable', 'etc', 'created_by', 'created_at']
        fields = '__all__'
        optional_fields = ['enterprise']
        # exclude = ['enterprise']

    def get_enterprise_name(self, obj):
        if obj.enterprise:
            return obj.enterprise.name
        else:
            return "Seoul-soft"

    def get_enterprise_manage(self, obj):
        if obj.enterprise:
            return obj.enterprise.manage
        else:
            return ""

    def get_at_date(self):
        return date.today()

    def get_by_username(self):
        return self.context['request'].user

    def get_code(self, obj):
        if obj['is_master'] is True:
            return obj['enterprise'].code + "0000"

        # print(obj['factory_classification'].id)
        # factory = str(obj['factory_classification'].id)[0]
        # division = str(obj['department_position'].id)[0]
        date = str(obj['employment_date']).replace('-', '')[2:6]
        order = '00'

        # prefix = factory + division + date
        prefix = 'UN' + date
        res = UserMaster.objects.filter(code__istartswith=prefix)
        if res.exists():
            num = res.order_by('-code').first().code[-2:]
            order = str(int(num) + 1)
            if len(order) == 1:
                order = '0' + order

        return 'UN' + date + order

    def create(self, instance):
        instance['code'] = self.get_code(instance)
        instance['created_at'] = self.get_at_date()
        instance['created_by'] = self.get_by_username()

        # is_master
        if instance['is_master'] is False:
            # if None in (instance['username']):
            #     raise ValidationError('유저이름은 필수 항목들입니다.')

            instance['enterprise'] = self.context['request'].user.enterprise
        else:
            instance['permissions'] = instance['enterprise'].permissions
            # 마스터 계정 생성 에러 관련
            instance['username'] = instance['enterprise'].name + ' 관리자'

        try:
            user = super().create(instance)
            user.set_password(instance['password'])
            user.save()
            return user
        except IntegrityError:
            raise ValidationError('유효하지 않은 code 이므로 생성할 수 없습니다.')  # TODO: Error message

    def update(self, instance, validated_data):

        if 'permissions' in validated_data:
            # invalidate token
            tokens = Token.objects.filter(user=instance).all()
            tokens.delete()

            # if (instance.enterprise.permissions | validated_data['permissions']) != instance.enterprise.permissions:
            #     raise ValidationError('유효하지 않은 permission 입니다. 기업의 권한을 넘을 수 없습니다.')

            user_data = validated_data['permissions']
            enterprise_data = instance.enterprise.permissions

            num = 0
            for i in range(0, len(enterprise_data)):
                if (int(enterprise_data[i]) < int(user_data[i])):
                    raise ValidationError('유효하지 않은 permission 입니다. 기업의 권한을 넘을 수 없습니다.')
                    break

                num = num + 1

        user = super().update(instance, validated_data)
        if 'password' in validated_data:
            user.set_password(validated_data['password'])
            user.save()

        return user

    def validate_factory_classification(self, value):
        return self.code_validator(value, 104)

    def validate_employment_division(self, value):
        return self.code_validator(value, 112)

    def validate_job_position(self, value):
        return self.code_validator(value, 114)

    def validate_department_position(self, value):
        return self.code_validator(value, 113)

    def code_validator(self, code_master, group_code):
        if code_master is None:
            return code_master

        qs = GroupCodeMaster.objects.filter(pk=code_master.group_id, code=group_code)
        if qs.exists() is not True:
            message = '잘못된 코드 code must be a multiple of %d.' % group_code
            raise serializers.ValidationError(message)

        return code_master

    def to_internal_value(self, data):
        if type(data) is not dict:
            data._mutable = True

        if 'enterprise' not in data and self.context['view'].action == 'create':
            enterprise = self.context['request'].user.enterprise
            data['enterprise'] = enterprise.id

        return super(UserMasterSerializer, self).to_internal_value(data)

    def to_representation(self, instance):
        self.fields['factory_classification'] = CodeMasterSerializer()
        self.fields['employment_division'] = CodeMasterSerializer()
        self.fields['job_position'] = CodeMasterSerializer()
        self.fields['department_position'] = CodeMasterSerializer()
        self.fields['order_company'] = OrderCompanySerializer()

        return super(UserMasterSerializer, self).to_representation(instance)


class UserMasterSelectSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=8, required=False, read_only=True)
    created_by = serializers.CharField(required=False, read_only=True)  # 최종작성일
    created_at = serializers.CharField(required=False, read_only=True)  # 최초작성일
    enterprise_name = serializers.SerializerMethodField(read_only=True, required=False)

    class Meta:
        model = UserMaster
        fields = '__all__'
        optional_fields = ['enterprise']

    def get_enterprise_name(self, obj):
        if obj.enterprise:
            return obj.enterprise.name
        else:
            return "Seoul-soft"

    def get_at_date(self):
        return date.today()

    def get_by_username(self):
        return self.context['request'].user

    def get_code(self, obj):
        if obj['is_master'] is True:
            return obj['enterprise'].code + "0000"

        # print(obj['factory_classification'].id)
        # factory = str(obj['factory_classification'].id)[0]
        # division = str(obj['department_position'].id)[0]
        date = str(obj['employment_date']).replace('-', '')[2:6]
        order = '00'

        # prefix = factory + division + date
        prefix = 'UN' + date
        res = UserMaster.objects.filter(code__istartswith=prefix)
        if res.exists():
            num = res.order_by('-code').first().code[-2:]
            order = str(int(num) + 1)
            if len(order) == 1:
                order = '0' + order

        return 'UN' + date + order

    def create(self, instance):
        instance['code'] = self.get_code(instance)
        instance['created_at'] = self.get_at_date()
        instance['created_by'] = self.get_by_username()

        # is_master
        if instance['is_master'] is False:
            # if None in (instance['username']):
            #     raise ValidationError('유저이름은 필수 항목들입니다.')

            instance['enterprise'] = self.context['request'].user.enterprise
        else:
            instance['permissions'] = instance['enterprise'].permissions
            # 마스터 계정 생성 에러 관련
            instance['username'] = instance['enterprise'].name + ' 관리자'

        try:
            user = super().create(instance)
            user.set_password(instance['password'])
            user.save()
            return user
        except IntegrityError:
            raise ValidationError('유효하지 않은 code 이므로 생성할 수 없습니다.')  # TODO: Error message

    def update(self, instance, validated_data):

        if 'permissions' in validated_data:
            # invalidate token
            tokens = Token.objects.filter(user=instance).all()
            tokens.delete()

            # if (instance.enterprise.permissions | validated_data['permissions']) != instance.enterprise.permissions:
            #     raise ValidationError('유효하지 않은 permission 입니다. 기업의 권한을 넘을 수 없습니다.')

            user_data = validated_data['permissions']
            enterprise_data = instance.enterprise.permissions

            num = 0
            for i in range(0, len(enterprise_data)):
                if (int(enterprise_data[i]) < int(user_data[i])):
                    raise ValidationError('유효하지 않은 permission 입니다. 기업의 권한을 넘을 수 없습니다.')
                    break

                num = num + 1

        user = super().update(instance, validated_data)
        if 'password' in validated_data:
            user.set_password(validated_data['password'])
            user.save()

        return user

    def validate_factory_classification(self, value):
        return self.code_validator(value, 104)

    def validate_employment_division(self, value):
        return self.code_validator(value, 112)

    def validate_job_position(self, value):
        return self.code_validator(value, 114)

    def validate_department_position(self, value):
        return self.code_validator(value, 113)

    def code_validator(self, code_master, group_code):
        if code_master is None:
            return code_master

        qs = GroupCodeMaster.objects.filter(pk=code_master.group_id, code=group_code)
        if qs.exists() is not True:
            message = '잘못된 코드 code must be a multiple of %d.' % group_code
            raise serializers.ValidationError(message)

        return code_master

    def to_internal_value(self, data):
        if type(data) is not dict:
            data._mutable = True

        if 'enterprise' not in data and self.context['view'].action == 'create':
            enterprise = self.context['request'].user.enterprise
            data['enterprise'] = enterprise.id

        return super(UserMasterSelectSerializer, self).to_internal_value(data)

    def to_representation(self, instance):
        self.fields['factory_classification'] = CodeMasterSerializer()
        self.fields['employment_division'] = CodeMasterSerializer()
        self.fields['job_position'] = CodeMasterSerializer()
        self.fields['department_position'] = CodeMasterSerializer()
        self.fields['order_company'] = OrderCompanySerializer()

        return super(UserMasterSelectSerializer, self).to_representation(instance)


class ItemLedSerializer(BaseSerializer):
    class Meta:
        model = ItemLed
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['code01'] = ItemMasterSerializer()
        self.fields['code02'] = ItemMasterSerializer()
        self.fields['code03'] = ItemMasterSerializer()
        self.fields['code04'] = ItemMasterSerializer()
        self.fields['code05'] = ItemMasterSerializer()
        self.fields['code06'] = ItemMasterSerializer()
        self.fields['code07'] = ItemMasterSerializer()
        self.fields['code08'] = ItemMasterSerializer()
        self.fields['code09'] = ItemMasterSerializer()
        self.fields['code10'] = ItemMasterSerializer()
        self.fields['code11'] = ItemMasterSerializer()
        self.fields['code12'] = ItemMasterSerializer()
        return super(ItemLedSerializer, self).to_representation(instance)


class ItemMasterSerializer(BaseSerializer):
    class Meta:
        model = ItemMaster
        fields = '__all__'

    def to_internal_value(self, data):
        self.unlock_data(data)
        if data['code'] == "" or 'code' not in data:
            data['code'] = generate_code('I', ItemMaster, 'code', self.context['request'].user)

        return super(ItemMasterSerializer, self).to_internal_value(data)

    def to_representation(self, instance):
        if (instance.item_division):
            item_division_id = instance.item_division.id
            item_division_name = instance.item_division.name
        else:
            item_division_id = ''
            item_division_name = ''

        if (instance.model):
            item_model_id = instance.model.id
            item_model_name = instance.model.name
        else:
            item_model_id = ''
            item_model_name = ''

        if (instance.container):
            container_id = instance.container.id
            container_name = instance.container.name
        else:
            container_id = ''
            container_name = ''

        if (instance.color):
            color_id = instance.color.id
            color_name = instance.color.name
        else:
            color_id = ''
            color_name = ''

        if (instance.type):
            type_id = instance.type.id
            type_name = instance.type.name
        else:
            type_id = ''
            type_name = ''

        if (instance.unit):
            unit_id = instance.unit.id
            unit_name = instance.unit.name
        else:
            unit_id = ''
            unit_name = ''

        if (instance.purchase_from):
            purchase_from_id = instance.purchase_from.id
            purchase_from_name = instance.purchase_from.name
        else:
            purchase_from_id = ''
            purchase_from_name = ''

        # if (instance.purchase_from2):
        #     purchase_from2_id = instance.purchase_from2.id
        #     purchase_from2_name = instance.purchase_from2.name
        # else:
        #     purchase_from2_id = ''
        #     purchase_from2_name = ''
        #
        # if (instance.purchase_from3):
        #     purchase_from3_id = instance.purchase_from3.id
        #     purchase_from3_name = instance.purchase_from3.name
        # else:
        #     purchase_from3_id = ''
        #     purchase_from3_name = ''

        if (instance.bom_division):
            bom_division_id = instance.bom_division.id
        else:
            bom_division_id = ''

        if (instance.qr_path):
            qr_path = instance.qr_path
        else:
            qr_path = ''

        if (instance.brand):
            brand_id = instance.brand.id
            brand_name = instance.brand.name
        else:
            brand_id = ''
            brand_name = ''

        if (instance.item_group):
            item_group_id = instance.item_group.id
            item_group_name = instance.item_group.name
        else:
            item_group_id = ''
            item_group_name = ''

        if (instance.nice_number):
            nice_number = instance.nice_number
        else:
            nice_number = ''

        if (instance.shape):
            shape = instance.shape
        else:
            shape = ''

        if (instance.safe_amount):
            safe_amount = instance.safe_amount
        else:
            safe_amount = ''

        return {
            'id': instance.id,  # id
            'code': instance.code,  # 품번
            'name': instance.name,  # 품명
            'detail': instance.detail,  # 품명상세
            'division_id': item_division_id,  # 자재분류
            'division_name': item_division_name,

            'model_id': item_model_id,  # 모델
            'model_name': item_model_name,

            'container_id': container_id,  # 용기타입
            'container_name': container_name,

            'color_id': color_id,  # 칼라구분
            'color_name': color_name,

            'type_id': type_id,  # 품종구분
            'type_name': type_name,

            'unit_id': unit_id,  # 단위
            'unit_name': unit_name,

            'from_id': purchase_from_id,  # 거래처
            'from_name': purchase_from_name,

            # 'from2_id': purchase_from2_id,  # 거래처
            # 'from2_name': purchase_from2_name,
            #
            # 'from3_id': purchase_from3_id,  # 거래처
            # 'from3_name': purchase_from3_name,

            'moq': instance.moq,  # MOQ
            'etc': instance.etc,  # 비고
            'standard_price': instance.standard_price,  # 표준단가
            'stock': instance.stock,  # 현 재고

            'bom_division_id': bom_division_id,  # BOM 구분
            'qr_path': qr_path,

            'brand_id': brand_id,
            'brand_name': brand_name,
            'item_group_id': item_group_id,
            'item_group_name': item_group_name,
            'nice_number': nice_number,
            'shape': shape,
            'safe_amount': safe_amount
        }


class ItemMasterSelectSerializer(BaseSerializer):  # Select2 id, code, name 만 가져오는 경우

    class Meta:
        model = ItemMaster
        fields = '__all__'

    def to_representation(self, instance):
        return {
            'id': instance.id,  # id
            'code': instance.code,  # 품번
            'name': instance.name,  # 품명
            'nice_number': instance.nice_number
        }


class FacilitiesMasterSerializer(BaseSerializer):
    class Meta:
        model = FacilitiesMaster
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['factory'] = CodeMasterSerializer()
        self.fields['process'] = CodeMasterSerializer()
        self.fields['workshop'] = CodeMasterSerializer()
        self.fields['type'] = CodeMasterSerializer()

        return super(FacilitiesMasterSerializer, self).to_representation(instance)


class FacilitiesFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilitiesFiles
        fields = '__all__'


class BomMasterSerializer(BaseSerializer):
    # bom_number = serializers.IntegerField(required=False, read_only=True)
    templet_cnt = serializers.SerializerMethodField(label='템플릿 수량')
    now_stock = serializers.SerializerMethodField(label='현재고')
    order_amount = serializers.SerializerMethodField(label='주문수량')
    moq = serializers.SerializerMethodField(label='Item MOQ')

    class Meta:
        model = BomMaster
        fields = '__all__'

    def get_now_stock(self, obj):
        now_stock = 0

        qs = ItemMaster.objects.filter(bom_division_id=obj.id)
        for item in qs:
            now_stock = item.stock
            moq = item.moq

        return now_stock

    def get_moq(self, obj):
        moq = 0

        qs = ItemMaster.objects.filter(bom_division_id=obj.id)
        for item in qs:
            moq = item.moq

        return moq

    def get_order_amount(self, obj):
        order_amount = 0

        items = ItemMaster.objects.filter(bom_division_id=obj.id)
        for item in items:
            ordering_items = OrderingItems.objects.filter(item_id=item.id)
            for ordering_item in ordering_items:
                order_amount += ordering_item.quantity - ordering_item.export_now_quantity

        return order_amount

    def get_templet_cnt(self, obj):
        templet_cnt = 0

        qs = SubprocessTemplet.objects.filter(master_id=obj.id)
        templet_cnt = qs.count()
        return templet_cnt

    # TODO: self.generate_code('O', MaterialsOut, 'num') 사용 가능?
    def get_bom_number(self):
        today = date.today()
        prefix = today.year * 10000 + today.month * 100 + today.day
        prefix = str(prefix)[2:]
        res = BomMaster.objects.filter(bom_number__istartswith=prefix).order_by('bom_number')
        if res.exists():
            return res.last().bom_number + 1

        return int(prefix) * 100

    def to_representation(self, instance):
        self.fields['master_customer'] = CustomerMasterSerializer()
        self.fields['item_division'] = CodeMasterSerializer()
        self.fields['model_name'] = CodeMasterSerializer()
        self.fields['container'] = CodeMasterSerializer()
        self.fields['color'] = CodeMasterSerializer()
        self.fields['type'] = CodeMasterSerializer()
        self.fields['brand'] = CodeMasterSerializer()
        self.fields['item_group'] = CodeMasterSerializer()
        # File 오류로 인하여 Serialize 변경 못했음

        return super(BomMasterSerializer, self).to_representation(instance)

    def to_internal_value(self, data):
        self.unlock_data(data)
        if 'bom_number' not in data or data['bom_number'] == '':
            data['bom_number'] = self.get_bom_number()

        return super(BomMasterSerializer, self).to_internal_value(data)


# ==================================================================================================
# get_product_cost 함수 Test 시 sample data : hjlim
# 1111001		a001 (100)		*1			b002 (200)		*2		=	500
# 1111002		1111001 (BOM)	*1			c003 (300)		*2		= 	500	+ 600
# 1111003		1111002 (BOM)	*1			d004 (100)		*2		= 	1100	+ 200		= 1300
# 1111004		1111003	(BOM)	*2			e005 (100)		*3		=	2600 	+ 400		= 2900
# ==================================================================================================

def get_Avg(_id):  # 평균단가로.. 처음 요청했으나, 표준단가(입고 마지막 단가)로 변경 됨
    sum = 0
    Bom_qs = Bom.objects.filter(master_id=_id)

    try:
        for row in Bom_qs:
            num = row.required_amount

            ItemMaster_row = ItemMaster.objects.get(id=row.item_id)
            if ItemMaster_row.bom_division:  # 구성 제품 자체가 BOM 인 경우
                # value = get_Avg(ItemMaster_row.bom_division)
                value = ItemMaster_row.standard_price

            else:
                # res = ItemIn.objects.filter(item_id=row.item_id).aggregate(Avg('in_price'))
                # value = res['in_price__avg']

                value = ItemMaster_row.standard_price

            if value is None:
                value = 0

            sum += num * value

    except:
        sum = 0
        print("get_Avg 에러")

    return sum


class BomMasterSelectSerializer(BaseSerializer):
    class Meta:
        model = BomMaster
        fields = '__all__'

    def to_representation(self, instance):
        if (instance.item_group):
            item_group = instance.item_group.name
        else:
            item_group = ''
        if (instance.brand):
            brand = instance.brand.name
        else:
            brand = ''

        return {
            'id': instance.id,  # id
            'product_name': instance.product_name,  # 생산제품명
            'bom_number': instance.bom_number,
            'nice_number': instance.nice_number,
            'detail': instance.detail,
            'brand': brand,
            'item_group': item_group,
            'item_shape': instance.shape
        }


class BomMasterCostSerializer(BaseSerializer):
    product_cost = serializers.SerializerMethodField(label='제품원가')  # 입하 수량

    class Meta:
        model = BomMaster
        fields = '__all__'

    def get_product_cost(self, obj):
        print(obj.id)
        ret = 0
        ret = get_Avg(obj.id)
        return ret

    def get_bom_number(self):
        today = date.today()
        prefix = today.year * 10000 + today.month * 100 + today.day
        prefix = str(prefix)[2:]
        res = BomMaster.objects.filter(bom_number__istartswith=prefix).order_by('bom_number')
        if res.exists():
            return res.last().bom_number + 1

        return int(prefix) * 100

    def to_representation(self, instance):
        self.fields['master_customer'] = CustomerMasterSerializer()
        self.fields['model_name'] = CodeMasterSerializer()

        return super(BomMasterCostSerializer, self).to_representation(instance)

    def to_internal_value(self, data):
        return super(BomMasterCostSerializer, self).to_internal_value(data)


class BomSerializer(BaseSerializer):
    class Meta:
        model = Bom
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['master'] = BomMasterSerializer()
        self.fields['item'] = ItemMasterSerializer()
        self.fields['customer'] = CustomerMasterSerializer()
        self.fields['manufacturer'] = CustomerMasterSerializer()
        self.fields['location'] = CodeMasterSerializer()

        return super(BomSerializer, self).to_representation(instance)


class BomLogSerializer(BaseSerializer):
    class Meta:
        model = BomLog
        fields = '__all__'

    def create(self, instance):
        return super().create(instance)

    def to_representation(self, instance):
        self.fields['master'] = BomMasterSerializer()

        return super(BomLogSerializer, self).to_representation(instance)


class ItemInSerializer(BaseSerializer):
    num = serializers.CharField(required=False, read_only=True)
    in_amount = serializers.FloatField(required=False, read_only=True)
    current_amount = serializers.FloatField(required=False, read_only=True)

    # remain_stock = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = ItemIn
        fields = '__all__'

    #  hjlim : 불용자재 파악을 위한 선입선출 식 임시 계산 >> 추후 필요하면 사용할 것
    # def get_remain_stock(self, obj):
    #     ret = 7
    #     out_will = 0
    #     remain = 0
    #     a = obj.item_id
    #
    #     # 현재 계산할 ID 의 입하수량
    #     b = obj.in_amount
    #
    #     # 출고합
    #     qs_out = ItemOut.objects.filter(item_id=obj.item_id)
    #     if qs_out:
    #         amount_out = qs_out.aggregate(sum=Coalesce(Sum('out_amount'), 0))
    #         out_will = amount_out['sum']
    #
    #     # 입고 계산
    #     qs_in = ItemIn.objects.filter(item_id=obj.item_id, id__lte=obj.id).order_by('-id')
    #     if qs_in:
    #         for row in qs_in:
    #             if out_will > 0:
    #                 if out_will >= row.in_amount:
    #                     out_will = out_will - row.in_amount
    #
    #                 else:
    #                     remain = row.in_amount - out_will
    #                     out_will = 0
    #                     # if remain > obj.in_amount:
    #                     #     remain = obj.in_amount
    #
    #             else:
    #                 remain = obj.in_amount
    #
    #     return remain

    def create(self, instance):

        if self.context['request'].user.enterprise_id == 54:  # 스마트름뱅이는 입고번호를 lot번호로 사용
            instance['num'] = generate_lot_code(self.context['request'].POST.get('it_division_add', ''), ItemIn, 'num',
                                                self.context['request'].user)
        else:
            instance['num'] = generate_code('I', ItemIn, 'num', self.context['request'].user)

        instance['current_amount'] = ItemMaster.objects.get(pk=instance['item'].id).stock

        """
        QR 입고 처리
        키로 사용할 dict를 생성하여 카테고리와 함께 넘김 
        """

        qs = super().create(instance)

        try:
            # dict_qr = {'id': instance['item'].id, 'code': instance['item'].code}
            dict_qr = {'id': qs.id, 'item_id': instance['item'].id}

            from api.QRCode.QRCodeManager import QRCodeGen
            # qrcodePath = QRCodeGen(dict_qr, 'ItemIn')
            filename = QRCodeGen(dict_qr, 'ItemIn')

            print(filename)

            # instance['qr_path'] = filename
            qs.qr_path = filename
            qs.save()


        except:
            raise ValidationError('QR Code 생성에러. 관리자에게 문의하세요.')

        # 아이템에 QR코드 이미지 경로 업데이트
        # ex : previous.item.qrpath = qrcodePath
        # ex : previous.item.save()

        return qs

    # Todo : 현재는 QR 에 ItemMaster 의 id 만을 사용하고 있음, 필요할 때 아래 내용 하기 바람
    def update(self, instance, validated_data):
        location = validated_data['location']

        if location == "" or location is None:
            code = CodeMaster.objects.get(name="입고창고")
            validated_data['location'] = code
        #
        #     # 아이템에 QR코드에 영향을 주는 값이 변경되는 경우
        #     dict_qr = {'id': validated_data['item'].id, 'code': validated_data['item'].code}
        #     from api.QRCode.QRCodeManager import QRCodeGen
        #     # 3번째 파라미터가 기존 path
        #     qrcodePath = QRCodeGen(dict_qr, 'ItemIn', "uploads/qrcodeIMG/1628227966.png")
        #     # 아이템에 QR코드 이미지 경로 업데이트
        #     # ex : previous.item.qrpath = qrcodePath
        #     # ex : previous.item.save()
        #
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        self.fields['item'] = ItemMasterSerializer()
        self.fields['customer'] = CustomerMasterSerializer()
        self.fields['location'] = CodeMasterSerializer()

        return super(ItemInSerializer, self).to_representation(instance)


class ItemOutSerializer(BaseSerializer):
    num = serializers.CharField(required=False, read_only=True)
    current_amount = serializers.FloatField(required=False, read_only=True)

    class Meta:
        model = ItemOut
        fields = '__all__'

    def create(self, instance):
        instance['num'] = generate_code('O', ItemOut, 'num', self.context['request'].user)
        instance['current_amount'] = ItemMaster.objects.get(pk=instance['item'].id).stock
        return super().create(instance)

    def update(self, instance, validated_data):
        try:
            location = validated_data['location']
        except:
            location = ""
        print(location)
        if location == "" or location is None:
            code = CodeMaster.objects.get(name="입고창고")
            validated_data['location'] = code
        else:
            code = CodeMaster.objects.get(id=location.id)
            validated_data['location'] = code

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        self.fields['item'] = ItemMasterSerializer()
        self.fields['purchase_from'] = CustomerMasterSerializer()
        self.fields['location'] = CodeMasterSerializer()

        return super(ItemOutSerializer, self).to_representation(instance)


class ItemOutOrderSerializer(BaseSerializer):
    num = serializers.CharField(required=False, read_only=True)

    class Meta:
        model = ItemOutOrder
        fields = '__all__'

    def create(self, instance):
        instance['num'] = generate_code('O', ItemOutOrder, 'num', self.context['request'].user)
        return super().create(instance)

    def to_representation(self, instance):
        self.fields['item'] = ItemMasterSerializer()
        return super(ItemOutOrderSerializer, self).to_representation(instance)


class ItemReinSerializer(BaseSerializer):
    class Meta:
        model = ItemRein
        fields = '__all__'

    def create(self, instance):
        instance['current_amount'] = ItemMaster.objects.get(pk=instance['item'].id).stock
        return super().create(instance)

    def to_representation(self, instance):
        self.fields['item'] = ItemMasterSerializer()
        self.fields['location'] = CodeMasterSerializer()
        self.fields['customer'] = CustomerMasterSerializer()

        return super(ItemReinSerializer, self).to_representation(instance)


class ItemMasterAdjustSerializer(BaseSerializer):
    adjusts = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = ItemMaster
        fields = '__all__'

    def get_adjusts(self, obj):
        data = ItemAdjust.objects.filter(item_id=obj.id).order_by('created_at').all()
        s = ItemAdjustSerializer(data, many=True)
        return s.data

    def to_representation(self, instance):
        if (instance.item_division):
            item_division_id = instance.item_division.id
            item_division_name = instance.item_division.name
        else:
            item_division_id = ''
            item_division_name = ''

        if (instance.model):
            item_model_id = instance.model.id
            item_model_name = instance.model.name
        else:
            item_model_id = ''
            item_model_name = ''

        if (instance.unit):
            unit_id = instance.unit.id
            unit_name = instance.unit.name
        else:
            unit_id = ''
            unit_name = ''

        if (instance.purchase_from):
            purchase_from_id = instance.purchase_from.id
            purchase_from_name = instance.purchase_from.name
        else:
            purchase_from_id = ''
            purchase_from_name = ''

        if (instance.bom_division):
            bom_division_id = instance.bom_division.id
        else:
            bom_division_id = ''
        itemAdjust = ItemAdjust.objects.filter(item_id=instance.id).last()
        if (itemAdjust):
            reason = itemAdjust.reason
        else:
            reason = ''

        if (instance.updated_by):
            username = instance.updated_by.username
        else:
            username = ''

        if (instance.brand):
            brand_id = instance.brand.id
            brand_name = instance.brand.name
        else:
            brand_id = ''
            brand_name = ''

        if (instance.item_group):
            item_group_id = instance.item_group.id
            item_group_name = instance.item_group.name
        else:
            item_group_id = ''
            item_group_name = ''

        if (instance.nice_number):
            nice_number = instance.nice_number
        else:
            nice_number = ''

        if (instance.shape):
            shape = instance.shape
        else:
            shape = ''

        if (instance.safe_amount):
            safe_amount = instance.safe_amount
        else:
            safe_amount = ''

        if (instance.location):
            location = CodeMaster.objects.filter(id=instance.location).values_list('name', flat=True).first()
        else:
            location = ''

        return {
            'id': instance.id,  # id
            'code': instance.code,  # 품번
            'name': instance.name,  # 품명
            'detail': instance.detail,  # 품명상세
            'division_id': item_division_id,  # 자재분류
            'division_name': item_division_name,

            'model_id': item_model_id,  # 모델
            'model_name': item_model_name,
            'unit_id': unit_id,  # 단위
            'unit_name': unit_name,
            'from_id': purchase_from_id,  # 거래처
            'from_name': purchase_from_name,

            'brand_id': brand_id,
            'brand_name': brand_name,
            'nice_number': nice_number,
            'shape': shape,
            'item_group_id': item_group_id,
            'item_group_name': item_group_name,

            'moq': instance.moq,  # MOQ
            'etc': instance.etc,  # 비고
            'reason': reason,  # 조정사유
            'standard_price': instance.standard_price,  # 표준단가
            'stock': instance.stock,  # 현 재고

            'bom_division_id': bom_division_id,  # BOM 구분

            # 'adjusts': adjusts,
            'created_at': instance.created_at,  # 조정날짜
            'username': username,  # 작성자z
            'current_amount': instance.current_amount,
            'previous_amount': instance.previous_amount,
            'adjust_created_at': instance.adjust_created_at,
            'location': location
        }


class ItemAdjustSerializer(BaseSerializer):
    previous_amount = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = ItemAdjust
        fields = '__all__'

    def create(self, instance):
        instance['previous_amount'] = ItemMaster.objects.get(pk=instance['item'].id).stock
        instance['current_amount'] = instance['previous_amount'] + instance['current_amount']
        return super().create(instance)

    def to_representation(self, instance):
        self.fields['item'] = ItemMasterSerializer()
        self.fields['location'] = CodeMasterSerializer()

        return super(ItemAdjustSerializer, self).to_representation(instance)


def custom_from_to_date(data):
    log_from = data.get('log_from', '1970-01-01')
    log_to = data.get('log_to', '9999-12-31')
    log_from = '1970-01-01' if log_from == '' else log_from
    log_to = '9999-12-31' if log_to == '' else log_to
    return log_from, log_to


class ItemAmountCalculateSerializer(BaseSerializer):
    in_receive_amount = serializers.SerializerMethodField(label='입하 수량')  # 입하 수량
    in_faulty_amount = serializers.SerializerMethodField(label='입하 불량 수량')  # 입하 불량 수량

    out_amount = serializers.SerializerMethodField(label='반출 수량')  # 출고 수량
    rein_amount = serializers.SerializerMethodField(label='반입 수량')  # 반입 수량
    actual_amount = serializers.SerializerMethodField(label='현재 수량')
    adjust_amount = serializers.SerializerMethodField(label="조정 수량")

    # avg_price = serializers.SerializerMethodField(label='평균 단가')
    cost_price = serializers.SerializerMethodField(label='원가')

    class Meta:
        model = ItemMaster
        fields = '__all__'

    # def get_avg_price(self, obj):  # hjlim 평균단가를 다시 사용할지 모르니 삭제 하지 말 것
    #     log_from, log_to = custom_from_to_date(self.context['request'].query_params)
    #     res = ItemIn.objects.filter(item__code=obj.code,
    #                                 in_at__gte=log_from,
    #                                 in_at__lte=log_to).aggregate(Avg('in_price'))
    #     result = res['in_price__avg']
    #     return result if result is not None else 0

    def get_cost_price(self, obj):

        if obj.bom_division:
            result = get_Avg(obj.bom_division)

        else:
            result = obj.standard_price

        return result if result is not None else 0

    def get_in_receive_amount(self, obj):
        log_from, log_to = custom_from_to_date(self.context['request'].query_params)
        res = ItemIn.objects.filter(~Q(etc='재고조정'),
                                    enterprise=obj.enterprise_id,
                                    item__id=obj.id,
                                    in_at__gte=log_from,
                                    in_at__lte=log_to,
                                    ).aggregate(Sum('receive_amount'))
        result = res['receive_amount__sum']
        return result if result is not None else 0

    def get_in_adjust_amount(self, obj):
        log_from, log_to = custom_from_to_date(self.context['request'].query_params)
        res1 = ItemIn.objects.filter(enterprise=obj.enterprise_id,
                                     item__id=obj.id,
                                     in_at__gte=log_from,
                                     in_at__lte=log_to,
                                     etc="재고조정").aggregate(Sum('receive_amount'))
        res2 = ItemOut.objects.filter(enterprise=obj.enterprise_id,
                                      item__id=obj.id,
                                      out_at__gte=log_from,
                                      out_at__lte=log_to,
                                      purpose="재고조정").aggregate(Sum('out_amount'))
        res1['receive_amount__sum'] = res1['receive_amount__sum'] or 0
        res2["out_amount__sum"] = res2["out_amount__sum"] or 0
        result = res1['receive_amount__sum'] - res2["out_amount__sum"]
        return result if result is not None else 0

    def get_in_faulty_amount(self, obj):
        log_from, log_to = custom_from_to_date(self.context['request'].query_params)
        In = ItemIn.objects.filter(enterprise=obj.enterprise_id,
                                   item__id=obj.id,
                                   in_at__gte=log_from,
                                   in_at__lte=log_to).aggregate(Sum('in_faulty_amount'))
        if In['in_faulty_amount__sum'] == None:
            In['in_faulty_amount__sum'] = 0
        result = In['in_faulty_amount__sum']
        return result if result is not None else 0

    def get_out_amount(self, obj):
        log_from, log_to = custom_from_to_date(self.context['request'].query_params)
        res = ItemOut.objects.filter(~Q(purpose='재고조정'),
                                     enterprise=obj.enterprise_id,
                                     item__id=obj.id,
                                     out_at__gte=log_from,
                                     out_at__lte=log_to).aggregate(Sum('out_amount'))
        result = res['out_amount__sum']
        return result if result is not None else 0

    def get_rein_amount(self, obj):
        log_from, log_to = custom_from_to_date(self.context['request'].query_params)
        res = ItemRein.objects.filter(enterprise=obj.enterprise_id,
                                      item__id=obj.id,
                                      created_at__gte=log_from,
                                      created_at__lte=log_to).aggregate(
            sum=Sum('rein_amount') - Sum("out_faulty_amount"))
        # sum = Sum('rein_amount') - Sum('out_faulty_amount'))

        result = res['sum']
        return result if result is not None else 0

    def get_actual_amount(self, obj):
        in_amount = self.get_in_receive_amount(obj) - self.get_in_faulty_amount(obj)
        out_amount = self.get_out_amount(obj)
        rein_amount = self.get_rein_amount(obj)
        # diff = self.get_diff_amount(obj)

        return in_amount - out_amount + rein_amount  # + diff

    def to_representation(self, instance):
        if (instance.item_division):
            item_division_id = instance.item_division.id
            item_division_name = instance.item_division.name
        else:
            item_division_id = ''
            item_division_name = ''

        if (instance.brand):
            brand_id = instance.brand.id
            brand_name = instance.brand.name
        else:
            brand_id = ''
            brand_name = ''

        if (instance.item_group):
            item_group_id = instance.item_group.id
            item_group_name = instance.item_group.name
        else:
            item_group_id = ''
            item_group_name = ''

        if (instance.nice_number):
            nice_number = instance.nice_number
        else:
            nice_number = ''

        if (instance.shape):
            shape = instance.shape
        else:
            shape = ''

        if (instance.safe_amount):
            safe_amount = instance.safe_amount
        else:
            safe_amount = ''

        if (instance.model):
            item_model_id = instance.model.id
            item_model_name = instance.model.name
        else:
            item_model_id = ''
            item_model_name = ''

        if (instance.unit):
            unit_id = instance.unit.id
            unit_name = instance.unit.name
        else:
            unit_id = ''
            unit_name = ''

        if (instance.purchase_from):
            purchase_from_id = instance.purchase_from.id
            purchase_from_name = instance.purchase_from.name
        else:
            purchase_from_id = ''
            purchase_from_name = ''

        if (instance.bom_division):
            bom_division_id = instance.bom_division.id
        else:
            bom_division_id = ''

        if (instance.safe_amount):
            safe_amount = instance.safe_amount
        else:
            safe_amount = ''

        in_receive_amount = self.get_in_receive_amount(instance)  # 입하수량
        in_faulty_amount = self.get_in_faulty_amount(instance)  # 입하불량수량
        in_out_amount = self.get_out_amount(instance)  # 출고수량
        in_rein_amount = self.get_rein_amount(instance)  # 반입수량
        in_adjust_amount = self.get_in_adjust_amount(instance)

        return {
            'id': instance.id,  # id
            'code': instance.code,  # 품번
            'name': instance.name,  # 품명
            'detail': instance.detail,  # 품명상세
            'division_id': item_division_id,  # 자재분류
            'division_name': item_division_name,

            'model_id': item_model_id,  # 모델
            'model_name': item_model_name,
            'unit_id': unit_id,  # 단위
            'unit_name': unit_name,
            'from_id': purchase_from_id,  # 거래처
            'from_name': purchase_from_name,

            'brand_id': brand_id,
            'brand_name': brand_name,
            'item_group_id': item_group_id,
            'item_group_name': item_group_name,
            'nice_number': nice_number,
            'shape': shape,

            'moq': instance.moq,  # MOQ
            'etc': instance.etc,  # 비고
            'standard_price': instance.standard_price,  # 표준단가
            'stock': instance.stock,  # 현 재고

            'bom_division_id': bom_division_id,  # BOM 구분

            'in_receive_amount': in_receive_amount,  # 입하수량
            'in_faulty_amount': in_faulty_amount,  # 입하불량수량
            'in_out_amount': in_out_amount,  # 출고수량
            'in_rein_amount': in_rein_amount,  # 반입수량
            'in_adjust_amount': in_adjust_amount,
            'safe_amount': safe_amount
        }


class ItemCostCalculateSerializer(BaseSerializer):
    in_receive_amount = serializers.SerializerMethodField(label='입하 수량')  # 입하 수량
    cost_price = serializers.SerializerMethodField(label='원가')

    class Meta:
        model = ItemMaster
        fields = '__all__'

    def get_in_receive_amount(self, obj):
        log_from, log_to = custom_from_to_date(self.context['request'].query_params)
        res = ItemIn.objects.filter(enterprise=obj.enterprise_id,
                                    item__id=obj.id,
                                    in_at__gte=log_from,
                                    in_at__lte=log_to).aggregate(Sum('receive_amount'))
        result = res['receive_amount__sum']
        return result if result is not None else 0

    def get_cost_price(self, obj):
        result = obj.standard_price
        return result if result is not None else 0

    def to_representation(self, instance):
        if (instance.purchase_from):
            purchase_from_id = instance.purchase_from.id
            purchase_from_name = instance.purchase_from.name
        else:
            purchase_from_id = ''
            purchase_from_name = ''

        if (instance.item_division):
            item_division_id = instance.item_division.id
            item_division_name = instance.item_division.name
        else:
            item_division_id = ''
            item_division_name = ''

        return {
            'id': instance.id,  # id
            'code': instance.code,  # 품번
            'name': instance.name,  # 품명
            'detail': instance.detail,  # 품명상세
            'division_id': item_division_id,  # 자재분류 /
            'division_name': item_division_name,

            'from_id': purchase_from_id,  # 거래처 /
            'from_name': purchase_from_name,

            'stock': instance.stock,  # 현재수량
            'standard_price': instance.standard_price,  # 표준단가
            'etc': instance.etc,  # 비고
        }


class ItemInMobileSerializer(BaseSerializer):
    in_amount_by_in_at = serializers.SerializerMethodField(label='입고일 입고수량')  # 입고일의 동일품번의 입고수량

    class Meta:
        model = ItemIn
        fields = '__all__'

    def get_in_amount_by_in_at(self, obj):
        res = ItemIn.objects.filter(enterprise=obj.enterprise_id, in_at=obj.in_at, item_id=obj.item_id). \
            aggregate(Sum('receive_amount'), Sum('in_faulty_amount'))

        receive_amount_sum = res['receive_amount__sum']
        in_faulty_amount_sum = res['in_faulty_amount__sum']
        result = receive_amount_sum - in_faulty_amount_sum

        return result if result is not None else 0

    def to_representation(self, instance):
        self.fields['item'] = ItemMasterSerializer()
        return super(ItemInMobileSerializer, self).to_representation(instance)


class ProcessSerializer(BaseSerializer):
    code = serializers.CharField(required=False, read_only=True)
    now_fnum = serializers.SerializerMethodField(label='현재 불량수')

    class Meta:
        model = Process
        fields = '__all__'

    @transaction.atomic
    def get_now_fnum(self, obj):
        result = 0

        subProcess = Subprocess.objects.filter(process_id=obj.id)
        if subProcess:
            for row in subProcess:
                result += row.faulty_amount

        return result if result is not None else 0

    def create(self, instance):
        instance['code'] = generate_code("P", Process, 'code', self.context['request'].user)
        process = super().create(instance)

        return process

    def to_representation(self, instance):
        self.fields['customer'] = CustomerMasterSerializer()
        self.fields['bom_master'] = BomMasterSerializer()
        self.fields['factory_classification'] = CodeMasterSerializer()

        return super(ProcessSerializer, self).to_representation(instance)

    def validate_factory_classification(self, value):
        return self.code_validator(value, 104)


class SubprocesstempletSerializer(BaseSerializer):
    class Meta:
        model = SubprocessTemplet
        fields = '__all__'

    def create(self, instance):
        qs = SubprocessTemplet.objects.filter(master=instance['master'],
                                              enterprise_id=instance['enterprise'].id,
                                              type=instance['type']
                                              )
        if qs.count() != 0:
            raise ValidationError('세부공정이 이미 존재합니다.')

        return super().create(instance)

    def to_representation(self, instance):
        self.fields['type'] = CodeMasterSerializer()
        self.fields['workshop'] = CodeMasterSerializer()
        self.fields['charge'] = UserMasterSerializer()

        return super(SubprocesstempletSerializer, self).to_representation(instance)


class SubprocessSerializer(BaseSerializer):
    now_fnum = serializers.SerializerMethodField(label='현재 불량수')

    class Meta:
        model = Subprocess
        fields = '__all__'

    @transaction.atomic
    def get_now_fnum(self, obj):
        result = 0

        subProcess = Subprocess.objects.filter(process_id=obj.process)
        if subProcess:
            for row in subProcess:
                result += row.faulty_amount

        return result if result is not None else 0

    @transaction.atomic
    def update(self, instance, validated_data):
        print(instance)

        amount = instance.amount

        today = date.today()
        location = self.initial_data['location']
        complete_amount = instance.complete_amount
        faulty_amount = instance.faulty_amount

        subprocess = super().update(instance, validated_data)

        try:
            bom_number = subprocess.process.bom_master.bom_number
            item = ItemMaster.objects.get(enterprise_id=subprocess.enterprise.id, bom_division__bom_number=bom_number)
            item_id = item.id
            subpro = Subprocess.objects.get(id=subprocess.id)

            if subpro.actual_to_date is None:
                self.initial_data["actual_to_date"] = today

            num = generate_code('I', ItemIn, 'num', self.get_by_username())

            # 생산제품 입고 진행
            item_in = ItemIn.objects.create(
                num=num,
                item_id=item_id,
                item_created_at=today,
                in_at=today,
                location_id=location,
                package_amount=complete_amount,
                receive_amount=complete_amount + faulty_amount,
                in_faulty_amount=faulty_amount,
                created_by=self.get_by_username(),
                updated_by=self.get_by_username(),
                created_at=today,
                updated_at=today,
                enterprise_id=subprocess.enterprise.id,
                qr_path='',
            )

            in_amount = int(complete_amount)

            item = get_object_or_404(ItemMaster, pk=item_id)
            item.stock = item.stock + in_amount
            item.save()

            item_in.current_amount = item.stock

            # QR 생성
            # dict_qr = {'id': item.id, 'code': item.code}
            dict_qr = {'id': item_in.id, 'item_id': item.id}
            from api.QRCode.QRCodeManager import QRCodeGen
            filename = QRCodeGen(dict_qr, 'ItemIn')
            print(filename)

            item_in.qr_path = filename
            item_in.save()

            log = subprocess_log(subprocess, item_in, separator="itemIn")
            log.save()

            # 생산 제품의 자재 출고 진행
            qs_bom = Bom.objects.filter(master_id=subprocess.process.bom_master)  # bom id

            for row in qs_bom:
                out_item_id = row.item_id
                out_num = generate_code('O', ItemOut, 'num', self.get_by_username())
                current_amount = ItemMaster.objects.get(pk=out_item_id).stock
                try:
                    bom_location = self.initial_data['bom_location[' + str(row.item_id) + ']']
                except:
                    bom_location = None

                export_quantity = row.required_amount * (complete_amount + faulty_amount)

                out = ItemOut.objects.create(
                    num=out_num,  # 출하번호
                    item_id=out_item_id,  # 품번
                    out_at=today,  # 출하일자
                    current_amount=current_amount,  # 현재재고
                    out_amount=export_quantity,  # 출고수량
                    purpose="공정완료",  # 출고목적
                    location_id=bom_location,

                    created_by=self.get_by_username(),
                    updated_by=self.get_by_username(),
                    created_at=today,
                    updated_at=today,
                    enterprise_id=subprocess.enterprise.id
                )

                item_out = ItemMaster.objects.get(pk=out_item_id)
                item_out.stock = item_out.stock - int(export_quantity)
                item_out.save()
                log = subprocess_log(subprocess, out, separator="itemOut")
                log.save()

        except Exception as e:
            print(e)
            print(traceback.format_exc())

            raise ValidationError('관리자에게 문의하세요.')

        return subprocess

    @transaction.atomic
    def create(self, instance):
        print(instance)
        try:
            amount = Subprocess.objects.filter(process_id=self.initial_data['process']).last().remain_amount
        except:
            amount = instance['process'].amount
        today = date.today()
        location = self.initial_data['location']
        complete_amount = instance["complete_amount"]
        faulty_amount = instance["faulty_amount"]
        instance['amount'] = Decimal(str(amount))
        instance['remain_amount'] = Decimal(str(amount)) - Decimal(str(complete_amount))
        instance['fr_date'] = today
        instance['to_date'] = instance['finished_at']
        # instance['to_date'] = today
        subprocess = super().create(instance)
        if instance['remain_amount'] <= 0:
            complete = 1
        else:
            complete = 0
        try:
            bom_number = subprocess.process.bom_master.bom_number
            item = ItemMaster.objects.get(enterprise_id=subprocess.enterprise.id, bom_division__bom_number=bom_number)
            item_id = item.id
            subpro = Subprocess.objects.get(id=subprocess.id)

            if subpro.actual_to_date is None:
                self.initial_data["actual_to_date"] = today

            qs = Subprocess.objects.filter(process_id=subprocess.process_id)

            for processRow in qs:
                if processRow.status != "완료":

                    processRow.status = "완료"
                    processRow.save()
                    num = generate_code('I', ItemIn, 'num', self.get_by_username())

                    # 생산제품 입고 진행
                    item_in = ItemIn.objects.create(
                        num=num,
                        item_id=item_id,
                        item_created_at=today,
                        in_at=today,
                        location_id=location,
                        package_amount=complete_amount,
                        receive_amount=complete_amount + faulty_amount,
                        in_faulty_amount=faulty_amount,
                        created_by=self.get_by_username(),
                        updated_by=self.get_by_username(),
                        created_at=today,
                        updated_at=today,
                        enterprise_id=subprocess.enterprise.id,
                        qr_path='',
                    )

                    in_amount = int(complete_amount)

                    item = get_object_or_404(ItemMaster, pk=item_id)
                    item.stock = item.stock + in_amount
                    item.save()

                    item_in.current_amount = item.stock

                    # QR 생성
                    # dict_qr = {'id': item.id, 'code': item.code}
                    dict_qr = {'id': item_in.id, 'item_id': item.id}
                    from api.QRCode.QRCodeManager import QRCodeGen
                    filename = QRCodeGen(dict_qr, 'ItemIn')
                    print(filename)

                    item_in.qr_path = filename
                    item_in.save()

                    log = subprocess_log(subprocess, item_in, separator="itemIn")
                    log.save()

                    # 생산 제품의 자재 출고 진행
                    qs_bom = Bom.objects.filter(master_id=subprocess.process.bom_master)  # bom id

                    for row in qs_bom:
                        out_item_id = row.item_id
                        out_num = generate_code('O', ItemOut, 'num', self.get_by_username())
                        current_amount = ItemMaster.objects.get(pk=out_item_id).stock
                        try:
                            bom_location = self.initial_data['bom_location[' + str(row.item_id) + ']']
                        except:
                            bom_location = None

                        export_quantity = row.required_amount * (complete_amount + faulty_amount)

                        out = ItemOut.objects.create(
                            num=out_num,  # 출하번호
                            item_id=out_item_id,  # 품번
                            out_at=today,  # 출하일자
                            current_amount=current_amount,  # 현재재고
                            out_amount=export_quantity,  # 출고수량
                            purpose="공정완료",  # 출고목적
                            location_id=bom_location,

                            created_by=self.get_by_username(),
                            updated_by=self.get_by_username(),
                            created_at=today,
                            updated_at=today,
                            enterprise_id=subprocess.enterprise.id
                        )

                        item_out = ItemMaster.objects.get(pk=out_item_id)
                        item_out.stock = item_out.stock - int(export_quantity)
                        item_out.save()
                        log = subprocess_log(subprocess, out, separator="itemOut")
                        log.save()

            if complete == 1:
                subprocess.status = "완료"
                subprocess.save()
                process = Process.objects.get(id=subprocess.process_id)
                process.complete = 1
                process.actual_to_date = today
                process.save()

        except Exception as e:
            print(e)
            print(traceback.format_exc())

            raise ValidationError('관리자에게 문의하세요.')

        return subprocess

    def to_representation(self, instance):
        self.fields['type'] = CodeMasterSerializer()
        self.fields['workshop'] = CodeMasterSerializer()
        self.fields['charge'] = UserMasterSerializer()
        self.fields['process'] = ProcessSerializer()
        self.fields['fault_reason'] = SubprocessFaultManageSerializer()
        # self.fields['status'] = CodeMasterSerializer()
        return super(SubprocessSerializer, self).to_representation(instance)

    def validate_type(self, value):
        return self.code_validator(value, 109)

    def validate_workshop(self, value):
        return self.code_validator(value, 110)

    def validate_unit(self, value):
        return self.code_validator(value, 105)


class SubprocessProgressSerializer(BaseSerializer):
    class Meta:
        model = SubprocessProgress
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['subprocess'] = SubprocessSerializer()
        self.fields['status'] = CodeMasterSerializer()

        return super(SubprocessProgressSerializer, self).to_representation(instance)

    def validate_status(self, value):
        return self.code_validator(value, 124)

    def validate(self, attrs):
        if attrs['reason'] in (None, '') and attrs['subprocess'].by < attrs['finished_at']:  # 늦은 경우 지연 사유 필요
            raise ValidationError('작업이 지연 되었습니다. 지연 사유를 등록 바랍니다.')

        if attrs['reason'] in (None, '') and attrs['subprocess'].by < date.today():  # 늦은 경우 지연 사유 필요
            raise ValidationError('작업이 지연 되었습니다. 지연 사유를 등록 바랍니다.')

        return super(SubprocessProgressSerializer, self).validate(attrs)

    def to_internal_value(self, data):
        # 늦었는데 완료예정일, 지연 사유 없는 경우 이 처리는 validator 들어가기 전에 해줘야 함. (date format)
        sub_by = get_object_or_404(Subprocess, pk=data['subprocess']).by
        if data.get('reason', None) in (None, '') and sub_by < date.today() and \
                data.get('finished_at', None) in (None, ''):
            # 늦은 경우 지연 사유 필요
            # run_validation dict 형태 필요하기 때문
            raise ValidationError({'temp': '작업이 지연 되었습니다. 완료예정일과 지연 사유를 등록 바랍니다.'})

        return super(SubprocessProgressSerializer, self).to_internal_value(data)


class SubprocessFaultManageSerializer(BaseSerializer):
    class Meta:
        model = SubprocessFaultReason
        fields = '__all__'

    @transaction.atomic
    def create(self, instance):
        fault_reason = super(SubprocessFaultManageSerializer, self).create(instance)
        subpro = Subprocess.objects.get(id=instance['master'].id)

        subpro.fault_reason_id = fault_reason.id
        if subpro.faulty_amount < fault_reason.amount_sum:
            raise ValidationError({'남은 불량 수량을 확인 해 주시기 바랍니다. 음수가 될 수 없습니다.'})

        subpro.save()

        master_pro = Process.objects.get(id=subpro.process_id)
        if master_pro.has_fault_reason is False:
            master_pro.has_fault_reason = True
            master_pro.save()

        return fault_reason

    def to_representation(self, instance):
        self.fields['R01_upper'] = CodeMasterSerializer()
        self.fields['R01_lower'] = CodeMasterSerializer()

        self.fields['R02_upper'] = CodeMasterSerializer()
        self.fields['R02_lower'] = CodeMasterSerializer()

        self.fields['R03_upper'] = CodeMasterSerializer()
        self.fields['R03_lower'] = CodeMasterSerializer()

        self.fields['R04_upper'] = CodeMasterSerializer()
        self.fields['R04_lower'] = CodeMasterSerializer()

        self.fields['R05_upper'] = CodeMasterSerializer()
        self.fields['R05_lower'] = CodeMasterSerializer()

        self.fields['R06_upper'] = CodeMasterSerializer()
        self.fields['R06_lower'] = CodeMasterSerializer()

        self.fields['R07_upper'] = CodeMasterSerializer()
        self.fields['R07_lower'] = CodeMasterSerializer()

        self.fields['R08_upper'] = CodeMasterSerializer()
        self.fields['R08_lower'] = CodeMasterSerializer()

        self.fields['R09_upper'] = CodeMasterSerializer()
        self.fields['R09_lower'] = CodeMasterSerializer()

        self.fields['R10_upper'] = CodeMasterSerializer()
        self.fields['R10_lower'] = CodeMasterSerializer()

        self.fields['R11_upper'] = CodeMasterSerializer()
        self.fields['R11_lower'] = CodeMasterSerializer()

        self.fields['R12_upper'] = CodeMasterSerializer()
        self.fields['R12_lower'] = CodeMasterSerializer()

        self.fields['R13_upper'] = CodeMasterSerializer()
        self.fields['R13_lower'] = CodeMasterSerializer()

        self.fields['R14_upper'] = CodeMasterSerializer()
        self.fields['R14_lower'] = CodeMasterSerializer()

        self.fields['R15_upper'] = CodeMasterSerializer()
        self.fields['R15_lower'] = CodeMasterSerializer()

        return super(SubprocessFaultManageSerializer, self).to_representation(instance)


class ProcessStatusSerializer(BaseSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Process
        fields = '__all__'

    def get_status(self, obj):
        user = self.context['request'].user

        res = {
            'types': [],
            'order_amounts': [],
            'produce_amounts': [],
            'faulty_amounts': [],
            'progresses': []
        }

        def append_none():
            res['produce_amounts'].append(None)
            res['faulty_amounts'].append(None)
            res['progresses'].append(None)

        # TODO: group-by and aggregate to improve performance.

        sub = Subprocess.objects.filter(enterprise=user.enterprise, process_id=obj.id)
        for qs in sub:

            # latest_sub = sub.order_by('-created_at').first()
            # res['order_amounts'].append(latest_sub.amount)
            # sp = latest_sub.subprocess_progress_subprocess.order_by('-created_at').first()
            # if sp is None:
            #     append_none()
            #     continue

            res['order_amounts'].append(qs.amount)
            res['produce_amounts'].append(qs.complete_amount)
            res['faulty_amounts'].append(qs.faulty_amount)

            if qs.status:
                res['progresses'].append(qs.status)
            else:
                res['progresses'].append(None)

        return res

    def validate_rental_class(self, value):
        return self.code_validator(value, 122)

    def validate_factory_class(self, value):
        return self.code_validator(value, 109)

    def to_representation(self, instance):
        # self.fields['customer'] = CustomerMasterSerializer()

        # return super(ProcessStatusSerializer, self).to_representation(instance)
        status = self.get_status(instance)
        if instance.bom_master.brand:
            brand = instance.bom_master.brand.name
        else:
            brand = None
        if instance.bom_master.item_group:
            item_group = instance.bom_master.item_group.name
        else:
            item_group = None
        return {
            'id': instance.id,  # id
            'code': instance.code,  # 공정등록코드
            'name': instance.name,  # 생산공정명
            # 'customer': instance.customer,  # 고객사
            'brand': brand,  # bom_master
            'item_group': item_group,  # bom_master
            'nice_number': instance.bom_master.nice_number,  # bom_master
            'item_code': instance.bom_master.bom_number,
            # 'factory_classification': instance.factory_classification,  # 공장구분
            'amount': instance.amount,  # 생산수량
            'fr_date': instance.fr_date,  # From_Date
            'to_date': instance.to_date,  # To_Date
            'actual_fr_date': instance.actual_fr_date,  # From_Date
            'actual_to_date': instance.actual_to_date,  # To_Date
            'complete': instance.complete,
            # 'created_by': instance.created_by,  # 최초작성자
            # 'updated_by': instance.updated_by,  # 최종작성자
            # 'created_at': instance.created_at,  # 최초작성일
            # 'updated_at': instance.updated_at,  # 최종작성일
            # 'enterprise': instance.enterprise,  # 업체

            'status': status,  # get_status
        }


class RentalMasterSerializer(BaseSerializer):
    code = serializers.CharField(required=False, read_only=True)

    class Meta:
        model = RentalMaster
        fields = '__all__'

    def create(self, instance):
        instance['code'] = generate_code('R', RentalMaster, 'code', self.context['request'].user)
        return super().create(instance)

    def to_representation(self, instance):
        self.fields['item'] = ItemMasterSerializer()
        self.fields['factory_class'] = CodeMasterSerializer()
        self.fields['rental_class'] = CodeMasterSerializer()

        return super(RentalMasterSerializer, self).to_representation(instance)


class RentalSerializer(BaseSerializer):
    class Meta:
        model = Rental
        fields = '__all__'

    def to_internal_value(self, data):
        self.unlock_data(data)

        # is_returned
        # TODO: string 'false' to bool is "True"??
        is_returned = data.get('is_returned', None)
        # TODO: string 'false' to bool is "True"??
        # if is_returned is False:
        if is_returned == 'false':
            data['return_date'] = None
            data['return_condition'] = None
            data['return_name'] = None
            data['return_phone'] = None

        return super(RentalSerializer, self).to_internal_value(data)

    def to_representation(self, instance):
        self.fields['master'] = RentalMasterSerializer()
        self.fields['customer'] = CustomerMasterSerializer()

        return super(RentalSerializer, self).to_representation(instance)


class SensorSerializer(BaseSerializer):
    class Meta:
        model = Sensor
        fields = '__all__'

    def validate_factory(self, value):
        return self.code_validator(value, 104)

    def validate_type(self, value):
        return self.code_validator(value, 123)

    def to_internal_value(self, data):
        # 온습도 API 받는 input 없고, 1개의 sensor만 사용한다고 하였기 때문.
        self.unlock_data(data)

        if self.context['request'].user.enterprise.name == '시온테크놀러지':
            data['api_url'] = "http://x3.webscada.kr/daedan/api/getData/1806/msth_200625/3"
        elif self.context['request'].user.enterprise.name == 'JA푸드':
            data['api_url'] = "https://x3.webscada.kr/daedan/api/getMSTH/2109/5678/1"
        else:
            # TODO: 용법
            raise ValidationError({'error': '허가받지 않은 업체입니다.'}, code='invalid')

        return super(SensorSerializer, self).to_internal_value(data)

    def to_representation(self, instance):
        self.fields['factory'] = CodeMasterSerializer()
        self.fields['facilities'] = FacilitiesMasterSerializer()
        self.fields['type'] = CodeMasterSerializer()

        return super(SensorSerializer, self).to_representation(instance)


class SensorH2Serializer(BaseSerializer):
    class Meta:
        model = SensorH2
        fields = '__all__'

    def validate_factory(self, value):
        return self.code_validator(value, 104)

    def validate_workshop(self, value):
        return self.code_validator(value, 110)

    def to_internal_value(self, data):
        return super(SensorH2Serializer, self).to_internal_value(data)

    def to_representation(self, instance):
        # self.fields['factory'] = CodeMasterSerializer()
        # self.fields['workshop'] = CodeMasterSerializer()
        #
        # # return super(SensorH2Serializer, self).to_representation(instance)

        qs = SensorH2Value.objects.all()
        row = qs.filter(mac=instance.mac).last()
        temp = 0
        hue = 0

        if row:
            # row = qs.last()
            temp = row.temp
            hue = row.hue

        if (instance.factory):
            factory_id = instance.factory.id
            factory_name = instance.factory.name
        else:
            factory_id = ''
            factory_name = ''

        if (instance.workshop):
            workshop_id = instance.workshop.id
            workshop_name = instance.workshop.name
        else:
            workshop_id = ''
            workshop_name = ''

        if (instance.created_by):
            created_by = instance.created_by.username
        else:
            created_by = ''

        if (instance.updated_by):
            updated_by = instance.updated_by.username
        else:
            updated_by = ''

        return {
            'id': instance.id,  # id
            'device': instance.device,  # 장비명
            'mac': instance.mac,  # mac
            'factory_id': factory_id,  # 공장명
            'factory_name': factory_name,
            'workshop_id': workshop_id,  # 작업장
            'workshop_name': workshop_name,
            'model': instance.model,  # 모델명
            'etc': instance.etc,  # 기타
            'created_by': created_by,  # 최초작성자
            'updated_by': updated_by,  # 최종작성자
            'created_at': instance.created_at,  # 최초작성일
            'enterprise_id': instance.enterprise.id,  # 업체
            'enterprise_name': instance.enterprise.name,

            'temp': temp,  # temp
            'hue': hue,  # hue

        }


class DeviceSerializer(BaseSerializer):
    class Meta:
        model = Device
        fields = '__all__'

    def validate_factory(self, value):
        return self.code_validator(value, 104)

    def validate_workshop(self, value):
        return self.code_validator(value, 110)

    def to_internal_value(self, data):
        return super(DeviceSerializer, self).to_internal_value(data)

    def to_representation(self, instance):
        # self.fields['factory'] = CodeMasterSerializer()
        # self.fields['workshop'] = CodeMasterSerializer()
        #
        # # return super(DeviceSerializer, self).to_representation(instance)

        if (instance.factory):
            factory_id = instance.factory.id
            factory_name = instance.factory.name
        else:
            factory_id = ''
            factory_name = ''

        if (instance.workshop):
            workshop_id = instance.workshop.id
            workshop_name = instance.workshop.name
        else:
            workshop_id = ''
            workshop_name = ''

        if (instance.created_by):
            created_by = instance.created_by.username
        else:
            created_by = ''

        if (instance.updated_by):
            updated_by = instance.updated_by.username
        else:
            updated_by = ''

        return {
            'id': instance.id,  # id
            'device': instance.device,  # 장비명
            'mac': instance.mac,  # mac
            'factory_id': factory_id,  # 공장명
            'factory_name': factory_name,
            'workshop_id': workshop_id,  # 작업장
            'workshop_name': workshop_name,
            'model': instance.model,  # 모델명
            'etc': instance.etc,  # 기타
            'created_by': created_by,  # 최초작성자
            'updated_by': updated_by,  # 최종작성자
            'created_at': instance.created_at,  # 최초작성일
            'enterprise_id': instance.enterprise.id,  # 업체
            'enterprise_name': instance.enterprise.name,

        }


class SensorValueSerializer(BaseSerializer):
    class Meta:
        model = SensorValue
        fields = '__all__'


class SensorH2ValueSerializer(BaseSerializer):
    enterprise = serializers.SerializerMethodField()

    class Meta:
        model = SensorH2Value
        fields = '__all__'

    def get_enterprise(self, obj):
        user = self.context['request'].user.enterprise.name

        return user


class ItemMasterWarehouseSerializer(ItemMasterSerializer):
    class Meta:
        model = ItemMaster
        fields = '__all__'

    def to_representation(self, instance):
        # 창고에 맞게 stock 덮어쓰기
        wh_stock = ItemWarehouseStock.objects.filter(item=instance,
                                                     warehouse__group__code=109,
                                                     warehouse__code=self.context['warehouse_code'])
        instance.stock = wh_stock.first().stock if wh_stock.exists() else 0

        return super(ItemMasterWarehouseSerializer, self).to_representation(instance)


class ItemWarehouseInSerializer(ItemInSerializer):
    warehouse = serializers.IntegerField(write_only=True)

    class Meta:
        model = ItemIn
        fields = '__all__'

    # def validate_warehouse(self, value):
    #     return self.code_validator(value, 109)

    def update(self, instance, validated_data):
        # 당일만 가능
        if instance.created_at != date.today():
            raise ValidationError('오늘에 해당하는 객체만 수정/삭제가 가능합니다.')

        # restore previous iws's stock
        iwi = instance.item_warehouse_in_item_in
        iws = get_object_or_404(ItemWarehouseStock, item=instance.item, warehouse=iwi.warehouse)
        iws.update_stock(iws.stock - instance.in_amount)

        # update extension
        if 'warehouse' in validated_data:
            wh_id = validated_data.pop('warehouse', 0)
            wh = get_object_or_404(CodeMaster,
                                   enterprise=self.context['request'].user.enterprise,
                                   group__code=109,
                                   code=wh_id)
            iwi.warehouse = wh
            iwi.save()

        res = super(ItemWarehouseInSerializer, self).update(instance, validated_data)

        # apply to new iws's stock
        iwi = instance.item_warehouse_in_item_in
        iws = get_object_or_404(ItemWarehouseStock, item=instance.item, warehouse=iwi.warehouse)
        in_amount = instance.receive_amount - instance.in_faulty_amount
        iws.update_stock(iws.stock + in_amount)

        return res

    def create(self, instance):
        _warehouse = instance.pop('warehouse', 0)
        # ItemIn 모델 생성
        res = super(ItemWarehouseInSerializer, self).create(instance)

        # ItemWarehouseIn 모델 생성
        wh = get_object_or_404(CodeMaster,
                               enterprise=self.context['request'].user.enterprise,
                               group__code=109,
                               code=_warehouse)
        ItemWarehouseIn.objects.create(item_in=res, warehouse=wh)  # 창고관리 확장 모델 생성

        # ItemWarehouseStock Lazy하게 get_or_create 및 stock만큼 추가
        iws = ItemWarehouseStock.objects.get_or_create(item=res.item, warehouse=wh)[0]
        # stock 가져온 이후에 기존 ItemIn의 current_amount 변경
        res.current_amount = iws.stock
        res.save()
        # stock 반영
        in_amount = instance['receive_amount'] - instance['in_faulty_amount']
        iws.update_stock(iws.stock + in_amount)

        return res


class ItemWarehouseOutSerializer(BaseSerializer):
    num = serializers.CharField(required=False, read_only=True)
    current_amount = serializers.FloatField(required=False, read_only=True)
    # extension
    bom = serializers.SerializerMethodField(read_only=True, source='get_bom')
    warehouse_to = serializers.SerializerMethodField(read_only=True, source='get_warehouse_to')
    customer_to = serializers.SerializerMethodField(read_only=True, source='get_customer_to')

    warehouse = serializers.IntegerField(write_only=True)
    bom_pk = serializers.IntegerField(write_only=True)
    warehouse_to_code = serializers.IntegerField(write_only=True, required=False)
    customer_to_id = serializers.IntegerField(write_only=True, required=False)
    wh_is_auto = serializers.BooleanField()

    class Meta:
        model = ItemOut
        fields = '__all__'

    def get_bom(self, obj):
        return BomMasterSerializer(obj.item_warehouse_out_item_out.bom).data

    def get_warehouse_to(self, obj):
        return CodeMasterSerializer(obj.item_warehouse_out_item_out.warehouse_to).data

    def get_customer_to(self, obj):
        return CustomerMasterSerializer(obj.item_warehouse_out_item_out.customer_to).data

    # def validate_warehouse(self, value):
    #     return self.code_validator(value, 109)

    # def validate_warehouse_to_code(self, value):
    #     return self.code_validator(value, 109)

    def update(self, instance, validated_data):
        # 당일만 가능
        if instance.created_at != date.today():
            raise ValidationError('오늘에 해당하는 객체만 수정/삭제가 가능합니다.')

        ext = instance.item_warehouse_out_item_out
        # ItemWarehouseStock stock 계산
        iws = get_object_or_404(ItemWarehouseStock, item=instance.item, warehouse=ext.warehouse)
        diff = instance.out_amount - validated_data['out_amount']
        iws.update_stock(iws.stock + diff)

        # 창고관리 확장모델도 업데이트
        if 'bom_pk' in validated_data:
            bom = get_object_or_404(BomMaster,
                                    enterprise=self.context['request'].user.enterprise,
                                    pk=validated_data['bom_pk'])
            ext.bom = bom

        if 'warehouse_to_code' in validated_data:
            if ext.customer_to is not None:  # 거래처 등록되어 있을 시, 반출처 변경 불가.
                raise ValidationError('거래처 등록되어 있을 시, 반출처 변경이 불가능합니다.')

            wh_to = get_object_or_404(CodeMaster,
                                      enterprise=self.context['request'].user.enterprise,
                                      group__code=109,
                                      code=validated_data['warehouse_to_code'])
            ext.warehouse_to = wh_to
            validated_data.pop('warehouse_to_code')

        if 'customer_to_id' in validated_data:
            if ext.warehouse_to is not None:  # 반출처 등록되어 있을 시, 거래처 변경 불가.
                raise ValidationError('반출처 등록되어 있을 시, 거래처 변경이 불가능합니다.')

            customer_to = get_object_or_404(CustomerMaster,
                                            enterprise=self.context['request'].user.enterprise,
                                            pk=validated_data['customer_to_id'])
            ext.customer_to = customer_to
            validated_data.pop('customer_to_id')
        ext.save()

        # 한쪽의 출고는 한쪽의 입고 ItemWarehouseIn
        if ext.warehouse_to is not None:
            iwis = ItemWarehouseInSerializer(ext.related_itemwarehousein.item_in, data={
                'item': ext.item_out.item.id,
                'receive_amount': validated_data['out_amount'],
                'warehouse': ext.warehouse_to.code,
                'in_at': ext.related_itemwarehousein.item_in.in_at,
                'in_faulty_amount': ext.related_itemwarehousein.item_in.in_faulty_amount,
            }, context={'request': self.context['request']})
            iwis.is_valid(raise_exception=True)
            iwis.save()

        validated_data.pop('warehouse')
        validated_data.pop('bom_pk')
        return super(ItemWarehouseOutSerializer, self).update(instance, validated_data)

    def create(self, instance):
        # 재료
        wh = get_object_or_404(CodeMaster,
                               enterprise=self.context['request'].user.enterprise,
                               group__code=109,
                               code=instance['warehouse'])
        bom = get_object_or_404(BomMaster, enterprise=self.context['request'].user.enterprise, pk=instance['bom_pk'])
        wh_to, customer_to = None, None
        # 반출처와 거래처(완제품 창고)는 둘 중 하나만 입력이 가능.
        if 'warehouse_to_code' in instance:  # 반출처
            wh_to = get_object_or_404(CodeMaster,
                                      enterprise=self.context['request'].user.enterprise,
                                      group__code=109,
                                      code=instance['warehouse_to_code'])
            instance.pop('warehouse_to_code')
        elif 'customer_to_id' in instance:  # 거래처 (완제품 창고)
            customer_to = get_object_or_404(CustomerMaster,
                                            enterprise=self.context['request'].user.enterprise,
                                            id=instance['customer_to_id'])
            instance.pop('customer_to_id')
        else:
            raise ValidationError('반출처와 거래처 중 하나는 입력하세요.')

        wh_is_auto = instance.pop('wh_is_auto', None)
        iws = ItemWarehouseStock.objects.get_or_create(item=instance['item'], warehouse=wh)[0]
        instance.pop('warehouse')
        instance.pop('bom_pk')

        # 한쪽의 출고는 한쪽의 입고 ItemWarehouseIn
        iwi = None
        if wh_to is not None:
            iwis = ItemWarehouseInSerializer(data={
                'item': instance['item'].id,
                'in_at': instance['out_at'],
                'receive_amount': instance['out_amount'],
                'in_faulty_amount': 0,
                'warehouse': wh_to.code,
                'etc': '창고관리 반출 생성 적용'
            }, context={'request': self.context['request']})
            iwis.is_valid(raise_exception=True)
            iwi = iwis.save()

        # 모델 생성
        instance['num'] = generate_code('O', ItemOut, 'num', self.context['request'].user)
        instance['current_amount'] = iws.stock
        res = super(ItemWarehouseOutSerializer, self).create(instance)

        # ItemWarehouseStock stock 계산
        iws.update_stock(iws.stock - instance['out_amount'])

        # ItemWarehouseOut(창고관리 확장) 모델 생성
        ItemWarehouseOut.objects.create(item_out=res, warehouse=wh, is_auto=wh_is_auto, bom=bom,
                                        warehouse_to=wh_to,
                                        customer_to=customer_to,
                                        related_itemwarehousein=iwi.item_warehouse_in_item_in if iwi is not None else None)
        return res

    def to_representation(self, instance):
        self.fields['item'] = ItemMasterSerializer()

        return super(ItemWarehouseOutSerializer, self).to_representation(instance)


class ItemWarehouseReinSerializer(BaseSerializer):
    warehouse = serializers.IntegerField(write_only=True)
    warehouse_from = serializers.SerializerMethodField(read_only=True)
    warehouse_from_code = serializers.IntegerField(write_only=True)

    class Meta:
        model = ItemRein
        fields = '__all__'

    # def validate_warehouse(self, value):
    #     return self.code_validator(value, 109)
    #
    # def validate_warehouse_from_pk(self, value):
    #     return self.code_validator(value, 109)

    def get_warehouse_from(self, obj):
        return CodeMasterSerializer(obj.item_warehouse_rein_item_rein.warehouse_from).data

    def update(self, instance, validated_data):
        # 당일만 가능
        if instance.created_at != date.today():
            raise ValidationError('오늘에 해당하는 객체만 수정/삭제가 가능합니다.')

        ext = instance.item_warehouse_rein_item_rein
        # ItemWarehouseStock stock 계산
        rein_amount, out_faulty_amount = instance['rein_amount'], instance['out_faulty_amount']
        newone = rein_amount - out_faulty_amount
        oldone = instance.rein_amount - instance.out_faulty_amount

        iws = get_object_or_404(ItemWarehouseStock, item=instance.item, warehouse=ext.warehouse)
        iws.update_stock(iws.stock + oldone + newone)

        # 확장모델도 업데이트
        if 'warehouse_from_code' in validated_data:
            wh_from = get_object_or_404(CodeMaster,
                                        enterprise=self.context['request'].user.enterprise,
                                        group__code=109,
                                        code=validated_data['warehouse_from_code'])
            ext.warehouse_from = wh_from
        ext.save()

        # 기능 보류: 자동기능의 부적절함
        # # 한쪽의 반입은 한쪽의 출고 ItemWarehouseOut
        # ItemWarehouseOutSerializer(data={
        #     'item': instance.item,
        #     'out_at': datetime.now(),
        #     'out_amount': rein_amount + out_faulty_amount,
        #     'warehouse': wh_from,
        #     'warehouse_to_pk': instance.item_warehouse_rein_warehouse.id,
        #     'purpose': '창고관리 반입 생성 적용',
        #     'etc': '창고관리 반입 생성 적용'
        # }).save()

        validated_data.pop('warehouse')
        validated_data.pop('warehouse_from_code')
        return super(ItemWarehouseReinSerializer, self).update(instance, validated_data)

    def create(self, instance):
        # 재료
        wh = get_object_or_404(CodeMaster,
                               enterprise=self.context['request'].user.enterprise,
                               group__code=109,
                               code=instance['warehouse'])
        wh_from = get_object_or_404(CodeMaster,
                                    enterprise=self.context['request'].user.enterprise,
                                    group__code=109,
                                    code=instance['warehouse_from_code'])
        iws = get_object_or_404(ItemWarehouseStock, item=instance['item'], warehouse=wh)
        instance.pop('warehouse')
        instance.pop('warehouse_from_code')

        # 모델 생성
        instance['current_amount'] = iws.stock
        res = super(ItemWarehouseReinSerializer, self).create(instance)

        # ItemWarehouseStock stock 계산
        rein_amount, out_faulty_amount = instance['rein_amount'], instance['out_faulty_amount']
        iws.update_stock(iws.stock + rein_amount - out_faulty_amount)

        # ItemWarehouseRein(창고관리 확장) 모델 생성
        ItemWarehouseRein.objects.create(item_rein=res, warehouse=wh, warehouse_from=wh_from)

        # 기능 보류: 자동기능의 부적절함
        # # 한쪽의 반입은 한쪽의 출고 ItemWarehouseOut
        # ItemWarehouseOutSerializer(data={
        #     'item': res.item,
        #     'out_at': datetime.now(),
        #     'out_amount': rein_amount + out_faulty_amount,
        #     'warehouse': wh_from,
        #     'warehouse_to_pk': wh,
        #     'purpose': '창고관리 반입 생성 적용',
        #     'etc': '창고관리 반입 생성 적용'
        # }).save()

        return res

    def to_representation(self, instance):
        self.fields['item'] = ItemMasterSerializer()

        return super(ItemWarehouseReinSerializer, self).to_representation(instance)


class ItemWarehouseAdjustSerializer(ItemAdjustSerializer):
    warehouse = serializers.IntegerField(write_only=True)
    previous_amount = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = ItemAdjust
        fields = '__all__'

    # def validate_warehouse(self, value):
    #     return self.code_validator(value, 109)

    def create(self, instance):
        wh = get_object_or_404(CodeMaster,
                               enterprise=self.context['request'].user.enterprise,
                               group__code=109,
                               code=instance['warehouse'])
        instance.pop('warehouse')

        res = super(ItemWarehouseAdjustSerializer, self).create(instance)
        ItemWarehouseAdjust.objects.create(item_adjust=res, warehouse=wh)  # 창고관리 확장 모델 생성

        # ItemWarehouseStock stock 계산
        iws = get_object_or_404(ItemWarehouseStock, item=instance['item'], warehouse=wh)
        res.previous_amount = iws.stock
        res.save()  # res 업데이트
        iws.update_stock(instance['current_amount'])
        return res


class ItemWarehouseAmountCalculateSerializer(BaseSerializer):
    in_receive_amount = serializers.SerializerMethodField(label='입하 수량')  # 입하 수량
    in_faulty_amount = serializers.SerializerMethodField(label='입하 불량 수량')  # 입하 불량 수량

    out_amount = serializers.SerializerMethodField(label='반출 수량')  # 출고 수량
    rein_amount = serializers.SerializerMethodField(label='반입 수량')  # 반입 수량
    actual_amount = serializers.SerializerMethodField(label='현재 수량')

    class Meta:
        model = ItemMaster
        fields = '__all__'

    def get_in_receive_amount(self, obj):
        log_from, log_to = custom_from_to_date(self.context['request'].query_params)
        wh = self.context['warehouse_code']
        res = ItemIn.objects.filter(item__id=obj.id,
                                    in_at__gte=log_from,
                                    in_at__lte=log_to,
                                    item_warehouse_in_item_in__warehouse__group__code=109,
                                    item_warehouse_in_item_in__warehouse__code=wh).aggregate(Sum('receive_amount'))
        result = res['receive_amount__sum']
        return result if result is not None else 0

    def get_in_faulty_amount(self, obj):
        log_from, log_to = custom_from_to_date(self.context['request'].query_params)
        wh = self.context['warehouse_code']
        res = ItemIn.objects.filter(item__id=obj.id,
                                    in_at__gte=log_from,
                                    in_at__lte=log_to,
                                    item_warehouse_in_item_in__warehouse__group__code=109,
                                    item_warehouse_in_item_in__warehouse__code=wh).aggregate(Sum('in_faulty_amount'))
        result = res['in_faulty_amount__sum']
        return result if result is not None else 0

    def get_out_amount(self, obj):
        log_from, log_to = custom_from_to_date(self.context['request'].query_params)
        wh = self.context['warehouse_code']
        res = ItemOut.objects.filter(item__id=obj.id,
                                     out_at__gte=log_from,
                                     out_at__lte=log_to,
                                     item_warehouse_out_item_out__warehouse__group__code=109,
                                     item_warehouse_out_item_out__warehouse__code=wh).aggregate(Sum('out_amount'))
        result = res['out_amount__sum']
        return result if result is not None else 0

    def get_rein_amount(self, obj):
        log_from, log_to = custom_from_to_date(self.context['request'].query_params)
        wh = self.context['warehouse_code']
        res = ItemRein.objects.filter(item__id=obj.id,
                                      created_at__gte=log_from,
                                      created_at__lte=log_to,
                                      item_warehouse_rein_item_rein__warehouse__group__code=109,
                                      item_warehouse_rein_item_rein__warehouse__code=wh).aggregate(
            sum=Sum('rein_amount') - Sum('out_faulty_amount'))
        result = res['sum']
        return result if result is not None else 0

    def get_actual_amount(self, obj):
        in_amount = self.get_in_receive_amount(obj) - self.get_in_faulty_amount(obj)
        out_amount = self.get_out_amount(obj)
        rein_amount = self.get_rein_amount(obj)
        # diff = self.get_diff_amount(obj)

        return in_amount - out_amount + rein_amount  # + diff

    def to_representation(self, instance):
        self.fields['type'] = CodeMasterSerializer()
        self.fields['model'] = CodeMasterSerializer()
        self.fields['item_division'] = CodeMasterSerializer()
        self.fields['factory_division'] = CodeMasterSerializer()
        self.fields['color_division'] = CodeMasterSerializer()
        self.fields['unit'] = CodeMasterSerializer()
        self.fields['container_type'] = CodeMasterSerializer()
        self.fields['warehouse_keep_location'] = CodeMasterSerializer()

        self.fields['purchase_from'] = CustomerMasterSerializer()
        self.fields['sales_to'] = CustomerMasterSerializer()

        # stock 만 ItemWarehouseStock으로 바꿔치기 함.
        wh = get_object_or_404(CodeMaster,
                               enterprise=self.context['request'].user.enterprise,
                               group__code=109,
                               code=self.context['warehouse_code'])
        iws = ItemWarehouseStock.objects.get_or_create(item=instance, warehouse=wh)[0]
        instance.stock = iws.stock

        return super(ItemWarehouseAmountCalculateSerializer, self).to_representation(instance)


class ItemMasterWarehouseAdjustSerializer(ItemMasterAdjustSerializer):

    def get_adjusts(self, obj):
        data = ItemAdjust.objects.filter(item_id=obj.id,
                                         item_warehouse_adjust_item_adjust__warehouse__code=self.context[
                                             'warehouse_code']) \
            .order_by('created_at').all()
        s = ItemAdjustSerializer(data, many=True)
        return s.data

    def to_representation(self, instance):
        # 창고에 맞게 stock 덮어쓰기
        wh_stock = ItemWarehouseStock.objects.filter(item=instance,
                                                     warehouse__group__code=109,
                                                     warehouse__code=self.context['warehouse_code'])
        instance.stock = wh_stock.first().stock if wh_stock.exists() else 0
        return super(ItemMasterWarehouseAdjustSerializer, self).to_representation(instance)


class ItemWarehouseLogSerializer(serializers.Serializer):
    """창고-자재이력 조회를 위한 serialzier. ItemIn과 ItemOut을 하나의 serializer에서 처리하기 위함."""
    created_at = serializers.DateField(required=False)
    item = ItemMasterSerializer(required=False)
    previous_amount = serializers.SerializerMethodField(read_only=True, source='get_previous_amount')
    in_amount = serializers.SerializerMethodField(required=False, read_only=True, source='get_in_amount')
    out_amount = serializers.FloatField(required=False)
    current_amount = serializers.FloatField(required=False)
    created_by = UserMasterSerializer(required=False)
    purpose = serializers.CharField(required=False)
    etc = serializers.CharField(required=False)

    def get_previous_amount(self, obj):
        if 'previous_amount' in obj:
            return obj['previous_amount']
        elif 'in_amount' in obj:
            return obj['current_amount'] - obj['in_amount']
        elif 'out_amount' in obj:
            return obj['current_amount'] + obj['out_amount']
        elif 'current_amount' in obj:
            return obj['current_amount']
        return 0

    def get_in_amount(self, obj):
        if 'receive_amount' in obj and 'in_faulty_amount' in obj:
            return obj['receive_amount'] - obj['in_faulty_amount']

        return 0


class SensorPCSerializer(BaseSerializer):
    class Meta:
        model = SensorPC
        fields = '__all__'

    def validate_factory(self, value):
        return self.code_validator(value, 104)

    def to_representation(self, instance):
        self.fields['factory'] = CodeMasterSerializer()
        # self.fields['company'] = UserMasterSerializer()
        self.fields['order_company'] = OrderCompanySerializer()

        return super(SensorPCSerializer, self).to_representation(instance)


class SensorPCValueSerializer(BaseSerializer):
    class Meta:
        model = SensorPCValue
        fields = '__all__'


class OrderSerializer(BaseSerializer):
    po = serializers.CharField(required=False, read_only=True)
    cpo = serializers.CharField(required=False, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def gen_po(self, item):
        user = self.context['request'].user

        # 앞부분
        _id = "{:<10}".format(user.user_id)[:10]
        today = date.today()
        _date = str((today.year % 100) * 10000 + today.month * 100 + today.day)
        _former = _id + 'PO' + _date

        # 순번 체크
        res = Order.objects.filter(po__istartswith=_former, enterprise=user.enterprise).order_by('po')
        _last_order = "{}".format(int(res.values('po').last()['po'][18:21]) + 1 if res.exists() else 11).zfill(3)

        # 버전
        target_item = ItemMaster.objects.filter(pk=item).first()
        _ect = "{:<5}".format(target_item.etc if target_item.etc else "") if target_item is not None else "     "

        return _former + _last_order + '-' + _ect

    def gen_cpo(self):
        user = self.context['request'].user

        # 앞부분
        today = date.today()
        _date = str((today.year % 100) * 100 + today.month)
        _former = _date + "#"

        # 순번 체크
        res = Order.objects.filter(cpo__istartswith=_former, enterprise=user.enterprise).order_by('cpo')
        _last_order = "{}".format(int(res.values('cpo').last()['cpo'][5:7]) + 1 if res.exists() else 11).zfill(2)

        return _former + _last_order

    def create(self, instance):
        instance['po'] = self.gen_po(instance['item'].id)
        instance['cpo'] = self.gen_cpo()
        return super(OrderSerializer, self).create(instance)

    def to_representation(self, instance):
        # # print('Hi!')
        self.fields['item'] = ItemMasterSerializer()
        self.fields['customer'] = CustomerMasterSerializer()

        return super(OrderSerializer, self).to_representation(instance)


class OrdersSerializer(BaseSerializer):

    class Meta:
        model = Orders
        fields = '__all__'

    def create(self, instance):
        instance['po_no'] = generate_code('O', Orders, 'po_no', self.context['request'].user)
        instance['in_status'] = ''

        return super(OrdersSerializer, self).create(instance)

    def to_representation(self, instance):
        return super(OrdersSerializer, self).to_representation(instance)


class OrdersItemsSerializer(BaseSerializer):
    class Meta:
        model = OrdersItems
        fields = '__all__'

    def create(self, instance):
        return super(OrdersItemsSerializer, self).create(instance)

    def to_representation(self, instance):
        self.fields['item'] = ItemMasterSerializer()
        self.fields['location'] = CodeMasterSerializer()
        return super(OrdersItemsSerializer, self).to_representation(instance)


class OrdersInItemsSerializer(BaseSerializer):
    class Meta:
        model = OrdersInItems
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['item'] = ItemMasterSerializer()
        self.fields['updated_by'] = UserMasterSerializer()
        self.fields['location'] = CodeMasterSerializer()
        return super(OrdersInItemsSerializer, self).to_representation(instance)


class OutsourcingItemSerializer(BaseSerializer):
    class Meta:
        model = OutsourcingItem
        fields = '__all__'

    def create(self, instance):
        user = self.context['request'].user
        item_id = instance['item'].id
        export_date = instance['out_date']
        export_quantity = instance['quantity']
        num = generate_code('O', ItemOut, 'num', user)

        instance['outsourcing_code'] = generate_code('H', OutsourcingItem, 'outsourcing_code', user)
        instance['in_will_quantity'] = float(instance['quantity'])
        instance['in_ed_quantity'] = 0
        instance['in_date'] = None
        instance['in_status'] = ''

        # 재고출고 진행
        current_amount = ItemMaster.objects.get(pk=item_id).stock

        item_out = ItemOut.objects.create(
            num=num,  # 출하번호
            item_id=item_id,  # 품번
            out_at=export_date,  # 출하일자
            current_amount=current_amount,  # 현재재고
            out_amount=export_quantity,  # 출고수량
            purpose="외주출고",  # 출고목적

            created_by=user,
            updated_by=user,
            created_at=user,
            updated_at=user,
            enterprise=self.context['request'].user.enterprise
        )

        instance['item_out'] = item_out

        # ItemMaster 재고 계산
        item = ItemMaster.objects.get(pk=item_id)
        item.stock = round(float(item.stock) - float(export_quantity), 2)
        item.save()

        return super(OutsourcingItemSerializer, self).create(instance)

    def update(self, instance, validated_data):
        if validated_data['quantity'] < instance.in_ed_quantity:
            raise ValidationError('출고 수량을 확인 해 주세요.')

        validated_data['in_will_quantity'] = round(float(validated_data['quantity']) - float(instance.in_ed_quantity),
                                                   2)

        out = ItemOut.objects.get(pk=instance.item_out.id)
        out.out_amount = float(validated_data['quantity'])

        item = ItemMaster.objects.get(pk=instance.item.id)
        item.stock = round(float(item.stock) + float(instance.quantity) - float(validated_data['quantity']), 2)
        item.save()
        out.save()

        return super(OutsourcingItemSerializer, self).update(instance, validated_data)

    def to_representation(self, instance):
        self.fields['item'] = ItemMasterSerializer()
        self.fields['customer'] = CustomerMasterSerializer()
        return super(OutsourcingItemSerializer, self).to_representation(instance)


class OutsourcingInItemsSerializer(BaseSerializer):
    class Meta:
        model = OutsourcingInItems
        fields = '__all__'

    def create(self, instance):

        outsourcing = OutsourcingItem.objects.get(pk=instance['outsourcing_item'].id)

        if outsourcing.in_will_quantity < instance['in_quantity']:
            raise ValidationError('입고 수량을 확인 해 주세요.')

        instance['item'] = outsourcing.item

        user = self.context['request'].user
        item_id = instance['item'].id
        import_date = instance['in_date']
        import_quantity = instance['in_quantity']
        num = generate_code('I', ItemIn, 'num', user)

        instance['num'] = num
        instance['item_in_at'] = None

        current_amount = ItemMaster.objects.get(pk=item_id).stock

        item_in = ItemIn.objects.create(
            num=num,  # 출하번호
            item_id=item_id,  # 품번
            in_at=import_date,  # 출하일자
            current_amount=current_amount,  # 현재재고
            receive_amount=import_quantity,  # 출고수량
            in_faulty_amount=0,

            created_by=user,
            updated_by=user,
            created_at=user,
            updated_at=user,
            enterprise=self.context['request'].user.enterprise
        )

        try:
            dict_qr = {'id': item_in.id, 'item_id': item_id}

            from api.QRCode.QRCodeManager import QRCodeGen
            # qrcodePath = QRCodeGen(dict_qr, 'ItemIn')
            filename = QRCodeGen(dict_qr, 'ItemIn')

            print(filename)

            # instance['qr_path'] = filename
            item_in.qr_path = filename
            item_in.save()

        except:
            raise ValidationError('QR Code 생성에러. 관리자에게 문의하세요.')

        instance['item_in'] = item_in

        item = ItemMaster.objects.get(pk=item_id)
        item.stock = round(float(item.stock) + float(import_quantity), 2)
        item.save()

        outsourcing.in_ed_quantity = round(float(outsourcing.in_ed_quantity) + float(import_quantity), 2)
        outsourcing.in_will_quantity = round(float(outsourcing.in_will_quantity) - float(import_quantity), 2)

        if outsourcing.in_ed_quantity == 0:
            outsourcing.in_status = ''

        elif outsourcing.quantity <= outsourcing.in_ed_quantity:
            outsourcing.in_status = '입고완료'

        else:
            outsourcing.in_status = '일부입고'

        if not outsourcing.in_date:
            outsourcing.in_date = import_date
        else:
            outsourcing.in_date = import_date if time.strptime(str(outsourcing.in_date), "%Y-%m-%d") < time.strptime(
                str(import_date), "%Y-%m-%d") else outsourcing.in_date

        outsourcing.save()

        return super(OutsourcingInItemsSerializer, self).create(instance)

    def update(self, instance, validated_data):
        # Outsourcing 입고될 수량, 입고된 수량 update
        outsourcing = OutsourcingItem.objects.get(pk=validated_data['outsourcing_item'].id)

        if outsourcing.in_will_quantity < validated_data['in_quantity']:
            raise ValidationError('입고 수량을 확인 해 주세요.')

        fixed_quantity = round(float(instance.in_quantity) - (validated_data['in_quantity']), 2)

        outsourcing.in_will_quantity = round(float(outsourcing.in_will_quantity) + float(fixed_quantity), 2)
        outsourcing.in_ed_quantity = round(float(outsourcing.in_ed_quantity) - float(fixed_quantity), 2)

        # 재고 입고 수정
        item_in = ItemIn.objects.get(pk=instance.item_in.id)

        item_in.receive_amount = round(float(item_in.receive_amount) - float(fixed_quantity), 2)
        item_in.save()
        # ItemMaster 재고 계산
        item = ItemMaster.objects.get(pk=instance.item.id)

        item.stock = round(float(item.stock) - float(fixed_quantity), 2)
        item.save()

        # Outsourcing 입고여부 변경
        if outsourcing.in_ed_quantity == 0:
            outsourcing.in_status = ''

        elif outsourcing.quantity <= outsourcing.in_ed_quantity:
            outsourcing.in_status = '입고완료'

        else:
            outsourcing.in_status = '일부입고'

        outsourcing.save()

        return super(OutsourcingInItemsSerializer, self).update(instance, validated_data)

    def to_representation(self, instance):
        self.fields['item'] = ItemMasterSerializer()

        return super(OutsourcingInItemsSerializer, self).to_representation(instance)


class OrderInSerializer(BaseSerializer):
    in_amount = serializers.FloatField(required=False, read_only=True)

    class Meta:
        model = OrderIn
        fields = '__all__'

    def create(self, instance):
        num = generate_code('I', ItemIn, 'num', self.context['request'].user)
        ItemIn.objects.create(num=num,
                              current_amount=instance['master'].item.stock,
                              in_at=instance['in_at'],
                              receive_amount=instance['receive_amount'],
                              in_faulty_amount=instance['in_faulty_amount'],
                              # package_amount=instance['package_amount'],
                              enterprise_id=instance['enterprise'].id,
                              item_id=instance['master'].item_id,
                              item_created_at=instance['item_created_at'],
                              check_at=instance['check_at'],
                              etc=instance['etc'],
                              )
        return super(OrderInSerializer, self).create(instance)

    def to_representation(self, instance):
        self.fields['master'] = OrderSerializer()
        self.fields['is_in'] = CodeMasterSerializer()

        return super(OrderInSerializer, self).to_representation(instance)


class OrderCompanySerializer(BaseSerializer):
    class Meta:
        model = OrderCompany
        fields = '__all__'

    def create(self, instance):
        return super(OrderCompanySerializer, self).create(instance)

    def to_representation(self, instance):
        return super(OrderCompanySerializer, self).to_representation(instance)


#  hjlim new-module
class OrderingSerializer(BaseSerializer):
    class Meta:
        model = Ordering
        fields = '__all__'

    def create(self, instance):
        instance['ordering_code'] = generate_code('O', Ordering, 'ordering_code', self.context['request'].user)

        return super(OrderingSerializer, self).create(instance)

    def to_representation(self, instance):

        if (instance.updated_by):
            username = instance.updated_by.username
        else:
            username = ''

        return {
            'id': instance.id,  # id
            'ordering_code': instance.ordering_code,  # 주문번호
            'created_at': instance.created_at,  # 주문일자

            'code_id': instance.code.id,  # 거래처 코드
            'code_name': instance.code.name,  # 거래처명
            'licensee_number': instance.licensee_number,  # 사업자번호
            'owner_name': instance.owner_name,  # 대표자명
            'business_conditions': instance.business_conditions,  # 업태
            'business_event': instance.business_event,  # 종목
            'postal_code': instance.postal_code,  # 우편번호
            'address': instance.address,  # 주소
            'office_phone': instance.office_phone,  # 회사전화번호
            'office_fax': instance.office_fax,  # 팩스번호

            'charge_name': instance.charge_name,  # 거래처담당자
            'charge_level': instance.charge_level,  # 직급
            'charge_phone': instance.charge_phone,  # 담당자연락처

            'email': instance.email,  # 이메일
            'etc': instance.etc,  # 비고
            'pay_option': instance.pay_option,  # 결제조건
            'due_date': instance.due_date,  # 납기일
            'guarantee_date': instance.guarantee_date,  # 품질보증기한
            'deliver_place': instance.deliver_place,  # 남품장소
            'note': instance.note,  # NOTE 내용고정

            'provide_sum': instance.provide_sum,  # 공급가
            'provide_surtax': instance.provide_surtax,  # 부가세포함
            'username': username,  # 작성자

            'export_status': instance.export_status,  # 출하현황
        }


class OrderingPartSerializer(BaseSerializer):
    class Meta:
        model = Ordering
        fields = '__all__'

    def to_representation(self, instance):

        if (instance.updated_by):
            username = instance.updated_by.username
        else:
            username = ''

        return {
            'id': instance.id,  # id
            'ordering_code': instance.ordering_code,  # 주문번호
            'created_at': instance.created_at,  # 주문일자

            'code_id': instance.code.id,  # 거래처 코드
            'code_name': instance.code.name,  # 거래처명
            'licensee_number': instance.licensee_number,  # 사업자번호
            'owner_name': instance.owner_name,  # 대표자명
            'business_conditions': instance.business_conditions,  # 업태
            'business_event': instance.business_event,  # 종목
            'postal_code': instance.postal_code,  # 우편번호
            'address': instance.address,  # 주소
            'office_phone': instance.office_phone,  # 회사전화번호
            'office_fax': instance.office_fax,  # 팩스번호

            'charge_name': instance.charge_name,  # 거래처담당자
            'charge_level': instance.charge_level,  # 직급
            'charge_phone': instance.charge_phone,  # 담당자연락처

            'email': instance.email,  # 이메일
            'etc': instance.etc,  # 비고

            'pay_option': instance.pay_option,  # 결제조건
            'due_date': instance.due_date,  # 납기일
            'guarantee_date': instance.guarantee_date,  # 품질보증기한
            'deliver_place': instance.deliver_place,  # 남품장소
            'note': instance.note,  # NOTE 내용고정

            'provide_sum': instance.provide_sum,  # 공급가
            'provide_surtax': instance.provide_surtax,  # 부가세포함
            'username': username,  # 작성자
        }


class OrderingStatusSerializer(BaseSerializer):
    class Meta:
        model = Ordering
        fields = '__all__'

    def to_representation(self, instance):
        return super(OrderingStatusSerializer, self).to_representation(instance)


class OrderingItemsStatusSerializer(BaseSerializer):
    class Meta:
        model = OrderingItems
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['item'] = ItemMasterSerializer()
        self.fields['location'] = CodeMasterSerializer()
        return super(OrderingItemsStatusSerializer, self).to_representation(instance)


class OrderingItemsSerializer(BaseSerializer):
    class Meta:
        model = OrderingItems
        fields = '__all__'

    def create(self, instance):
        return super(OrderingItemsSerializer, self).create(instance)

    def to_representation(self, instance):
        self.fields['item'] = ItemMasterSerializer()
        self.fields['location'] = CodeMasterSerializer()
        return super(OrderingItemsSerializer, self).to_representation(instance)


class OrderingItemsPartSerializer(BaseSerializer):
    class Meta:
        model = OrderingItems
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['item'] = ItemMasterSerializer()
        self.fields['location'] = CodeMasterSerializer()

        # File 오류로 인하여 Serialize 변경 못했음
        return super(OrderingItemsPartSerializer, self).to_representation(instance)


class OrderingExItemsSerializer(BaseSerializer):
    class Meta:
        model = OrderingExItems
        fields = '__all__'

    def create(self, instance):
        return super(OrderingExItemsSerializer, self).create(instance)

    def to_representation(self, instance):
        self.fields['item'] = ItemMasterSerializer()
        self.fields['location'] = CodeMasterSerializer()
        return super(OrderingExItemsSerializer, self).to_representation(instance)


class RequestSerializer(BaseSerializer):
    class Meta:
        model = Request
        fields = '__all__'

    def create(self, instance):
        instance['request_code'] = generate_code('R', Request, 'request_code', self.context['request'].user)

        return super().create(instance)

    def to_representation(self, instance):
        self.fields['code'] = CustomerMasterSerializer()
        self.fields['created_by'] = UserMasterSerializer()
        self.fields['updated_by'] = UserMasterSerializer()

        return super(RequestSerializer, self).to_representation(instance)


class RequestItemsSerializer(BaseSerializer):
    class Meta:
        model = RequestItems
        fields = '__all__'

    def create(self, instance):
        return super(RequestItemsSerializer, self).create(instance)

    def to_representation(self, instance):
        self.fields['item'] = ItemMasterSerializer()
        return super(RequestItemsSerializer, self).to_representation(instance)


class EstimateSerializer(BaseSerializer):
    class Meta:
        model = Estimate
        fields = '__all__'

    def create(self, instance):
        instance['estimate_code'] = generate_code('E', Estimate, 'estimate_code', self.context['request'].user)

        return super().create(instance)

    def to_representation(self, instance):

        if (instance.updated_by):
            username = instance.updated_by.username
        else:
            username = ''

        return {
            'id': instance.id,  # id
            'estimate_code': instance.estimate_code,  # 견적번호
            'created_at': instance.created_at,  # 견적일자

            'code_id': instance.code.id,  # 거래처 코드
            'code_name': instance.code.name,  # 거래처명
            'licensee_number': instance.licensee_number,  # 사업자번호
            'owner_name': instance.owner_name,  # 대표자명
            'business_conditions': instance.business_conditions,  # 업태
            'business_event': instance.business_event,  # 종목
            'postal_code': instance.postal_code,  # 우편번호
            'address': instance.address,  # 주소
            'office_phone': instance.office_phone,  # 회사전화번호
            'office_fax': instance.office_fax,  # 팩스번호

            'charge_name': instance.charge_name,  # 거래처담당자
            'charge_level': instance.charge_level,  # 직급
            'charge_phone': instance.charge_phone,  # 담당자연락처

            'email': instance.email,  # 이메일
            'etc': instance.etc,  # 비고

            'pay_option': instance.pay_option,  # 결제조건
            'due_date': instance.due_date,  # 납기일
            'guarantee_date': instance.guarantee_date,  # 품질보증기한
            'deliver_place': instance.deliver_place,  # 남품장소
            'note': instance.note,  # NOTE 내용고정

            'provide_sum': instance.provide_sum,  # 공급가
            'provide_surtax': instance.provide_surtax,  # 부가세포함
            'username': username,  # 작성자
        }


class EstimateItemsSerializer(BaseSerializer):
    class Meta:
        model = EstimateItems
        fields = '__all__'

    def create(self, instance):
        return super(EstimateItemsSerializer, self).create(instance)

    def to_representation(self, instance):
        self.fields['item'] = ItemMasterSerializer()
        return super(EstimateItemsSerializer, self).to_representation(instance)


class UnbalanceSerializer(BaseSerializer):
    class Meta:
        model = Qunbalance
        fields = '__all__'

    def create(self, instance):
        instance['code'] = generate_code('Q', Qunbalance, 'code', self.context['request'].user)

        res = super(UnbalanceSerializer, self).create(instance)

        from django.utils import timezone
        res.date_start = timezone.now()
        res.save()
        return res

    def update(self, instance, validated_data):
        res = super().update(instance, validated_data)

        from django.utils import timezone
        res.date_end = timezone.now()
        res.save()
        return res

    def to_representation(self, instance):
        return super(UnbalanceSerializer, self).to_representation(instance)


class UnbalanceDetailSerializer(BaseSerializer):
    class Meta:
        model = QunbalanceDetail
        fields = '__all__'

    def create(self, instance):
        return super(UnbalanceDetailSerializer, self).create(instance)

    def to_representation(self, instance):
        return super(UnbalanceDetailSerializer, self).to_representation(instance)


class RotatorSerializer(BaseSerializer):
    class Meta:
        model = Rotator
        fields = '__all__'

    def create(self, instance):
        instance['code'] = generate_code('R', Rotator, 'code', self.context['request'].user)
        return super(RotatorSerializer, self).create(instance)

    def to_representation(self, instance):
        self.fields['created_by'] = UserMasterSerializer()
        self.fields['updated_by'] = UserMasterSerializer()
        return super(RotatorSerializer, self).to_representation(instance)


class StatorSerializer(BaseSerializer):
    class Meta:
        model = Stator
        fields = '__all__'

    def create(self, instance):
        instance['code'] = generate_code('S', Stator, 'code', self.context['request'].user)
        return super(StatorSerializer, self).create(instance)

    def to_representation(self, instance):
        self.fields['created_by'] = UserMasterSerializer()
        self.fields['updated_by'] = UserMasterSerializer()
        return super(StatorSerializer, self).to_representation(instance)


class MyInfoSerializer(BaseSerializer):
    class Meta:
        model = MyInfoMaster
        fields = '__all__'


class ItemAmountCalculateNonZeroSerializer(BaseSerializer):
    class Meta:
        model = ItemMaster
        fields = '__all__'

    in_receive_amount = serializers.SerializerMethodField(label='입하 수량')  # 입하 수량
    in_faulty_amount = serializers.SerializerMethodField(label='입하 불량 수량')  # 입하 불량 수량

    out_amount = serializers.SerializerMethodField(label='반출 수량')  # 출고 수량
    rein_amount = serializers.SerializerMethodField(label='반입 수량')  # 반입 수량
    actual_amount = serializers.SerializerMethodField(label='현재 수량')
    adjust_amount = serializers.SerializerMethodField(label="조정 수량")

    # avg_price = serializers.SerializerMethodField(label='평균 단가')
    cost_price = serializers.SerializerMethodField(label='원가')

    def to_representation(self, instance):
        if instance.item_division:
            item_division_id = instance.item_division.id
            item_division_name = instance.item_division.name
        else:
            item_division_id = ''
            item_division_name = ''

        if instance.brand:
            brand_id = instance.brand.id
            brand_name = instance.brand.name
        else:
            brand_id = ''
            brand_name = ''

        if instance.item_group:
            item_group_id = instance.item_group.id
            item_group_name = instance.item_group.name
        else:
            item_group_id = ''
            item_group_name = ''

        if instance.nice_number:
            nice_number = instance.nice_number
        else:
            nice_number = ''

        if instance.shape:
            shape = instance.shape
        else:
            shape = ''

        if instance.safe_amount:
            safe_amount = instance.safe_amount
        else:
            safe_amount = ''

        if instance.model:
            item_model_id = instance.model.id
            item_model_name = instance.model.name
        else:
            item_model_id = ''
            item_model_name = ''

        if instance.unit:
            unit_id = instance.unit.id
            unit_name = instance.unit.name
        else:
            unit_id = ''
            unit_name = ''

        if (instance.purchase_from):
            purchase_from_id = instance.purchase_from.id
            purchase_from_name = instance.purchase_from.name
        else:
            purchase_from_id = ''
            purchase_from_name = ''

        if (instance.bom_division):
            bom_division_id = instance.bom_division.id
        else:
            bom_division_id = ''

        if (instance.safe_amount):
            safe_amount = instance.safe_amount
        else:
            safe_amount = ''

        return {
            'id': instance.id,  # id
            'code': instance.code,  # 품번
            'name': instance.name,  # 품명
            'detail': instance.detail,  # 품명상세
            'division_id': item_division_id,  # 자재분류
            'division_name': item_division_name,

            'model_id': item_model_id,  # 모델
            'model_name': item_model_name,
            'unit_id': unit_id,  # 단위
            'unit_name': unit_name,
            'from_id': purchase_from_id,  # 거래처
            'from_name': purchase_from_name,

            'brand_id': brand_id,
            'brand_name': brand_name,
            'item_group_id': item_group_id,
            'item_group_name': item_group_name,
            'nice_number': nice_number,
            'shape': shape,

            'moq': instance.moq,  # MOQ
            'etc': instance.etc,  # 비고
            'standard_price': instance.standard_price,  # 표준단가
            'stock': instance.stock,  # 현 재고

            'bom_division_id': bom_division_id,  # BOM 구분

            'in_receive_amount': instance.in_receive_amount,  # 입하수량
            'in_faulty_amount': instance.in_faulty_amount,  # 입하불량수량
            'in_out_amount': instance.in_out_amount,  # 출고수량
            'in_rein_amount': instance.in_rein_amount,  # 반입수량
            'in_adjust_amount': instance.in_adjust_amount,  # 조정수량
            'safe_amount': safe_amount

        }


class UnitPriceSerializer(BaseSerializer):
    class Meta:
        model = UnitPrice
        fields = '__all__'

    def to_representation(self, instance):
        # print(instance.division)
        if instance.division is not None:
            division_name = instance.division.name
        else:
            division_name = None  # 또는 적절한 기본값 설정

        return {
            'id': instance.id,
            'code': instance.customer.code,
            'name': instance.customer.name,
            'licensee_number': instance.customer.licensee_number,
            'division_id': instance.division_id,
            'division_name': division_name,
            'unit_price': instance.unit_price,
            'fee_rate': instance.fee_rate,
            'etc': instance.etc
        }


class MenuSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='alias')

    class Meta:
        model = MenuMaster
        fields = '__all__'

    def to_representation(self, instance):
        return super(MenuSerializer, self).to_representation(instance)


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColumnMaster
        fields = '__all__'

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'label': instance.label,
            'label_en': instance.label_en,
            'pre_label': instance.pre_label,
            'tag': instance.tag,
            'type': instance.type,
            'class_name': instance.class_name,
            'event': instance.event,
            'position': instance.position,
            'use_flag': instance.use_flag,
            'visual_flag': instance.visual_flag,
            'excel_flag': instance.excel_flag,
            'edit_flag': instance.edit_flag,
            'menu_id': instance.menu_id,
            'code': instance.menu.code
        }
