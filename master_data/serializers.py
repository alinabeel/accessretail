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

class OutletSerializers(serializers.ModelSerializer):
    class Meta:
        model = Outlet
        fields = ('code',)


class PanelProfileSerializers(serializers.ModelSerializer):

    index=IndexSetupSerializers(many=False, read_only=True)
    outlet=OutletSerializers(many=False, read_only=True)
    outlet_type=OutletTypeSerializers(many=False, read_only=True)

    class Meta:
        model = PanelProfile
        fields = ('index', 'hand_nhand', 'region', 'outlet', 'outlet_type', 'outlet_status', 'audit_date', 'wtd_factor', 'num_factor', 'custom_channel_1', 'custom_channel_2', 'custom_channel_3', 'custom_channel_4', 'custom_channel_5', 'custom_channel_6', 'custom_channel_7', 'custom_channel_8', 'custom_channel_9', 'custom_channel_10', 'custom_channel_11', 'custom_channel_12', 'custom_channel_13', 'custom_channel_14', 'custom_channel_15', 'custom_channel_16', 'custom_channel_17', 'custom_channel_18', 'custom_channel_19', 'custom_channel_20', 'custom_channel_21', 'custom_channel_22', 'custom_channel_23', 'custom_channel_24', 'custom_channel_25', 'custom_channel_26', 'custom_channel_27', 'custom_channel_28', 'custom_channel_29', 'custom_channel_30', 'custom_channel_31', 'custom_channel_32', 'custom_channel_33', 'custom_channel_34', 'custom_channel_35', 'custom_channel_36', 'custom_channel_37', 'custom_channel_38', 'custom_channel_39', 'custom_channel_40', 'custom_channel_41', 'custom_channel_42', 'custom_channel_43', 'custom_channel_44', 'custom_channel_45', 'custom_channel_46', 'custom_channel_47', 'custom_channel_48', 'custom_channel_49', 'custom_channel_50', 'custom_region_1', 'custom_region_2', 'custom_region_3', 'custom_region_4', 'custom_region_5', 'custom_region_6', 'custom_region_7', 'custom_region_8', 'custom_region_9', 'custom_region_10', 'custom_region_11', 'custom_region_12', 'custom_region_13', 'custom_region_14', 'custom_region_15', 'custom_region_16', 'custom_region_17', 'custom_region_18', 'custom_region_19', 'custom_region_20', 'custom_region_21', 'custom_region_22', 'custom_region_23', 'custom_region_24', 'custom_region_25', 'custom_region_26', 'custom_region_27', 'custom_region_28', 'custom_region_29', 'custom_region_30', 'custom_region_31', 'custom_region_32', 'custom_region_33', 'custom_region_34', 'custom_region_35', 'custom_region_36', 'custom_region_37', 'custom_region_38', 'custom_region_39', 'custom_region_40', 'custom_region_41', 'custom_region_42', 'custom_region_43', 'custom_region_44', 'custom_region_45', 'custom_region_46', 'custom_region_47', 'custom_region_48', 'custom_region_49', 'custom_region_50', )


class CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductAuditSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductAudit
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
