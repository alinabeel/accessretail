from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from master_data.models import *
from master_setups.models import *


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']

class IndexSetupSerializers(serializers.ModelSerializer):
    class Meta:
        model = IndexSetup
        fields = '__all__'

class UsableOutletSerializers(serializers.ModelSerializer):
    class Meta:
        model = UsableOutlet
        fields = '__all__'

class MonthOutletSerializers(serializers.ModelSerializer):
    class Meta:
        model = Month
        fields = '__all__'


class OutletTypeSerializers(serializers.ModelSerializer):
    class Meta:
        model = OutletType
        fields = '__all__'

class OutletStatusSerializers(serializers.ModelSerializer):
    class Meta:
        model = OutletStatus
        fields = '__all__'

class OutletSerializers(serializers.ModelSerializer):
    class Meta:
        model = Outlet
        fields = ('code',)


class CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class AuditDataSerializers(serializers.ModelSerializer):
    class Meta:
        model = AuditData
        fields = '__all__'


class ProductSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class RBDSerializers(serializers.ModelSerializer):
    class Meta:
        model = RBD
        fields = '__all__'

class CellSerializers(serializers.ModelSerializer):
    rbd=RBDSerializers(many=False, read_only=True)
    class Meta:
        model = Cell
        exclude = ['country','created','updated',]

class ProvinceSerializers(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = '__all__'

class DistrictSerializers(serializers.ModelSerializer):
    province = ProvinceSerializers(many=False, read_only=True)
    class Meta:
        model = District
        fields = '__all__'

class TehsilSerializers(serializers.ModelSerializer):
    district = DistrictSerializers(many=False, read_only=True)
    class Meta:
        model = Tehsil
        fields = '__all__'


class CityVillageSerializers(serializers.ModelSerializer):
    tehsil=TehsilSerializers(many=False, read_only=True)
    class Meta:
        model = CityVillage
        fields = '__all__'

class PanelProfileSerializers(serializers.ModelSerializer):
    index=IndexSetupSerializers(many=False, read_only=True)
    outlet=OutletSerializers(many=False, read_only=True)
    outlet_type=OutletTypeSerializers(many=False, read_only=True)
    outlet_status=OutletStatusSerializers(many=False, read_only=True)
    category = CategorySerializers(many=False, read_only=True)
    city_village = CityVillageSerializers(many=False, read_only=True)

    class Meta:
        model = PanelProfile
        fields = ('index','category', 'outlet', 'outlet_type', 'outlet_status','city_village' ,'audit_date', 'acv', )
