from django.db import models
from django.core import validators
from django.core.exceptions import ValidationError

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _

from mptt.models import MPTTModel, TreeForeignKey
from core.mixinsModels import UpperCaseCharField,CodeNameMixIn,CreateUpdateMixIn
from core.colors import Colors
from master_setups.models import Country,IndexSetup,UserCountry,User,UserIndex,Threshold, CountrySetting

UserModel = get_user_model()


#BigIntegerField = 9223372036854775807(8 Bytes) - nine quintillion two hundred twenty-three quadrillion three hundred seventy-two trillion ...
#IntegerField = 2147483647 (4 Bytes) - two billion one hundred forty-seven million ...



def handle_upload_logs(instance, filename):
    return f"masterdata/{instance.country.code}/{instance.frommodel}/{filename}"

class Upload(CreateUpdateMixIn, models.Model):

    APPEND = 'APPEND'
    UPDATE = 'UPDATE'
    APPENDUPDATE = 'APPENDUPDATE'
    REFRESH = 'REFRESH'

    CHOICES = [
      (APPEND, 'Append: Add records in the table.'),
      (UPDATE, 'Update: If records exist update.'),
      (APPENDUPDATE, 'Append/Update: If  records exist update otherwise add.'),
      (REFRESH, 'Reresh: Delete all records and repopulate from the source.'),
    ]

    CHOICES_UPDATE = [
      (UPDATE, 'Update: If records exist update.'),
    ]

    UPLOADING = "UPLOADING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ERROR = "ERROR"

    IS_PROCESSING_CHOICES = [
        (UPLOADING, 'Uploading'),
        (PROCESSING, 'Processing'),
        (COMPLETED, 'Completed'),
        (ERROR, 'Error'),
    ]

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    import_mode = models.CharField(max_length=20, choices=CHOICES)
    frommodel = models.CharField(max_length=50)
    file = models.FileField(upload_to=handle_upload_logs)
    is_processing = models.CharField(max_length=20, choices=IS_PROCESSING_CHOICES,blank=True, null=True)
    process_message = models.CharField(max_length=255, blank=True, null=True)
    skiped_records = models.IntegerField(blank=True, null=True)
    updated_records = models.IntegerField(blank=True, null=True)
    created_records = models.IntegerField(blank=True, null=True)
    log = models.TextField(blank=True, null=True)

    def __str__(self):
        return str('{0} - {1}'.format(self.country.code, self.file))

    class Meta:
        db_table = 'upload'
        verbose_name = 'Upload'
        verbose_name_plural = 'Uploads'




class RegionType(CreateUpdateMixIn,models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('country','name',),)
        db_table = 'region_type'
        verbose_name = 'Region Type'
        verbose_name_plural = 'Region Types'
        ordering = ['name']

class Region(CodeNameMixIn,CreateUpdateMixIn,MPTTModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, related_name="region_uplaod", on_delete=models.CASCADE, null=True, blank=True)
    region_type = models.ForeignKey(RegionType, on_delete=models.CASCADE,)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True,blank=True, related_name='child')
    description = models.TextField(blank=True,default='')
    order_insertion_by = ['name']

    class Meta:
        unique_together = (('country','code','parent',),)
        db_table = 'region'
        verbose_name = 'Region'
        verbose_name_plural = 'Regions'
        ordering = ['name']

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name


class Category(CreateUpdateMixIn,CodeNameMixIn,MPTTModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, related_name="category_uploads", on_delete=models.CASCADE, null=True, blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True,blank=True, related_name='child')
    description = models.TextField(blank=True,default='')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = (('country','parent', 'code',))
        db_table = 'category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class IndexCategory(CreateUpdateMixIn,models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    index_setup = models.ForeignKey(IndexSetup, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category)

    def __str__(self):
        return str('{0}'.format(self.index_setup.name))

    class Meta:
        db_table = 'index_category'
        verbose_name = 'Index Category'
        verbose_name_plural = 'Index Categries'


class OutletType(CodeNameMixIn,CreateUpdateMixIn,MPTTModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE, null=True, blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True,blank=True, related_name='child')
    urbanity = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True,  blank=True,default='')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = (('country','parent', 'code',))
        db_table = 'outlet_type'
        verbose_name = 'Outlet Type'
        verbose_name_plural = 'Outlet Types'
        ordering = ['name']

    def __str__(self):
        return self.name

class Outlet(CreateUpdateMixIn, models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    code = UpperCaseCharField(max_length=50,validators=[validators.validate_slug])
    insert_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.code
    class Meta:
        unique_together = (('country', 'code',))
        db_table = 'outlet'
        verbose_name = 'Outlet'
        verbose_name_plural = 'Outlets'


class CensusManager(models.Manager):
    pass

class Census(CreateUpdateMixIn,models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, related_name="census_uploads", on_delete=models.CASCADE)
    censusdata = JSONField()
    heads = JSONField()
    objects = CensusManager()

    # def get_absolute_url(self):
    #     return reverse('master-data:census-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.country.name

    class Meta:
        db_table = 'census'
        verbose_name = 'Census'
        verbose_name_plural = 'Censuses'


class Month(CreateUpdateMixIn,models.Model):
    JANUARY = "January"
    FEBRUARY = "February"
    MARCH = "March"
    APRIL = "Aapril"
    MAY = "May"
    JUNE = "June"
    JULY = "July"
    AUGUST = "August"
    SEPTEMBER = "September"
    OCTOBER = "October"
    NOVEMBER = "November"
    DECEMBER = "December"


    MONTH_CHOICES = [
        (JANUARY, "January"),
        (FEBRUARY, "February"),
        (MARCH, "March"),
        (APRIL, "Aapril"),
        (MAY, "May"),
        (JUNE, "June"),
        (JULY, "July"),
        (AUGUST, "August"),
        (SEPTEMBER, "September"),
        (OCTOBER, "October"),
        (NOVEMBER, "November"),
        (DECEMBER, "December"),
    ]

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, choices=MONTH_CHOICES)
    code = UpperCaseCharField(max_length=50,validators=[validators.validate_slug])

    date = models.DateField(null=True, blank=True)

    month = models.SmallIntegerField()
    year = models.SmallIntegerField()

    is_locked = models.BooleanField(default=True)
    is_current_month = models.BooleanField(default=False)

    def __str__(self):
        return self.code
    class Meta:
        unique_together = (('country','code',),)
        db_table = 'month'
        verbose_name = 'Mont'
        verbose_name_plural = 'Months'
        ordering = ['month','year']

    def save(self, *args, **kwargs):
            self.date ='{0}-{1}-{2}'.format(self.year, self.month,1)
            self.is_locked = True
            super(self.__class__, self).save(*args, **kwargs)

class UsableOutlet(CreateUpdateMixIn,models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE, null=True, blank=True)
    month = models.ForeignKey(Month,on_delete=models.CASCADE)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    index = models.ForeignKey(IndexSetup, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.outlet.code
    class Meta:
        unique_together = (('country','month','index','outlet'),)
        db_table = 'usable_outlet'
        verbose_name = 'UsableOutlet'
        verbose_name_plural = 'UsableOutlets'


class PanelProfile(CreateUpdateMixIn,models.Model):

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE, null=True, blank=True)
    month = models.ForeignKey(Month,on_delete=models.CASCADE)

    index = models.ForeignKey(IndexSetup, on_delete=models.CASCADE)
    hand_nhand = models.CharField(max_length=50, null=True, blank=True)
    region = models.CharField(max_length=50, null=True, blank=True)

    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    outlet_type = models.ForeignKey(OutletType, on_delete=models.CASCADE)
    outlet_status = models.CharField(max_length=50, null=True, blank=True)

    audit_date = models.DateField(null=True, blank=True)
    wtd_factor = models.DecimalField(max_digits=15,decimal_places=6, default=0)
    num_factor = models.DecimalField(max_digits=15,decimal_places=6, default=0)
    turnover = models.DecimalField(max_digits=15,decimal_places=6, default=0)

    custom_channel_1 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_2 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_3 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_4 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_5 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_6 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_7 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_8 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_9 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_10 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_11 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_12 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_13 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_14 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_15 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_16 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_17 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_18 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_19 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_20 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_21 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_22 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_23 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_24 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_25 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_26 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_27 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_28 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_29 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_30 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_31 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_32 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_33 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_34 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_35 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_36 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_37 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_38 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_39 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_40 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_41 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_42 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_43 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_44 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_45 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_46 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_47 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_48 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_49 = models.CharField(max_length=80, null=True, blank=True)
    custom_channel_50 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_1 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_2 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_3 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_4 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_5 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_6 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_7 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_8 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_9 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_10 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_11 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_12 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_13 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_14 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_15 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_16 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_17 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_18 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_19 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_20 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_21 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_22 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_23 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_24 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_25 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_26 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_27 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_28 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_29 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_30 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_31 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_32 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_33 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_34 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_35 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_36 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_37 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_38 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_39 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_40 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_41 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_42 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_43 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_44 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_45 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_46 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_47 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_48 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_49 = models.CharField(max_length=80, null=True, blank=True)
    custom_region_50 = models.CharField(max_length=80, null=True, blank=True)
    class Meta:
        unique_together = (('country','outlet', 'month'))
        db_table = 'panel_profile'
        verbose_name = 'PanelProfile'
        verbose_name_plural = 'PanelProfiles'

    def __str__(self):
        return self.country



class Product(CodeNameMixIn,CreateUpdateMixIn,models.Model):

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE, null=True, blank=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    pack_type = models.CharField(max_length=150, null=True, blank=True)
    aggregation_level = models.CharField(max_length=150, null=True, blank=True)
    company = models.CharField(max_length=150, null=True, blank=True)
    brand = models.CharField(max_length=150, null=True, blank=True)
    family = models.CharField(max_length=150, null=True, blank=True)
    flavour_type = models.CharField(max_length=150, null=True, blank=True)
    weight = models.DecimalField(max_digits=15,decimal_places=6, null=True, blank=True)
    price_segment = models.CharField(max_length=150, null=True, blank=True)
    length_range = models.CharField(max_length=150, null=True, blank=True)
    number_in_pack = models.IntegerField(null=True, blank=True)
    price_per_stick = models.DecimalField(max_digits=15,decimal_places=6, null=True, blank=True)

    class Meta:
        unique_together = (('country','code'))
        db_table = 'product'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.country


class ProductAudit(CreateUpdateMixIn,models.Model):

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE, null=True, blank=True)
    month = models.ForeignKey(Month,on_delete=models.CASCADE)

    period = models.CharField(max_length=50, null=True, blank=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    product_details = models.TextField(null=True, blank=True)
    avaibility = models.BooleanField(default=True)
    facing_empty = models.IntegerField(default=0)
    facing_not_empty = models.IntegerField(default=0)
    forward = models.IntegerField(default=0)
    reserve = models.IntegerField(default=0)
    total_none_empty_facing_forward_reserve = models.IntegerField(default=0)
    purchaseother1 = models.IntegerField(default=0)
    purchaseother2 = models.IntegerField(default=0)
    purchasediary = models.IntegerField(default=0)
    purchaseinvoice = models.IntegerField(default=0)
    price_in_unit = models.DecimalField(max_digits=15,decimal_places=6,)
    price_in_pack = models.DecimalField(max_digits=15,decimal_places=6,)
    priceother = models.DecimalField(max_digits=15,decimal_places=6,)
    cash_discount = models.DecimalField(max_digits=15,decimal_places=6,)
    product_foc = models.IntegerField(default=0)
    gift_with_purchase = models.IntegerField(default=0)
    appreciation_award = models.IntegerField(default=0)
    other_trade_promotion = models.IntegerField(default=0)

    sales_unprojected_volume = models.DecimalField(max_digits=15,decimal_places=6,default=0)
    sales_unprojected_value = models.DecimalField(max_digits=15,decimal_places=6,default=0)
    sales_unprojected_units = models.DecimalField(max_digits=15,decimal_places=6,default=0)

    sales_projected_volume = models.DecimalField(max_digits=15,decimal_places=6,default=0)
    sales_projected_value = models.DecimalField(max_digits=15,decimal_places=6,default=0)
    sales_projected_units = models.DecimalField(max_digits=15,decimal_places=6,default=0)

    pack_without_graphic_health_warning = models.IntegerField(default=0,)
    no_of_pack_without_graphic_health_warning_facing = models.IntegerField(default=0)
    no_of_pack_without_graphic_health_warning_total_stock = models.IntegerField(default=0)
    no_of_pack_without_none_tax_stamp = models.IntegerField(default=0)
    point_of_sales_signboard = models.IntegerField(default=0)
    point_of_sales_poster = models.IntegerField(default=0)
    point_of_sales_counter_shield = models.IntegerField(default=0)
    point_of_sales_price_sticker = models.IntegerField(default=0)
    point_of_sales_umbrella = models.IntegerField(default=0)
    point_of_sales_counter_top_display = models.IntegerField(default=0)
    point_of_sales_lighter = models.IntegerField(default=0)
    point_of_sales_others = models.IntegerField(default=0)
    point_of_sales_none = models.IntegerField(default=0)

    class Meta:
        unique_together = (('country','outlet','product','month'))
        db_table = 'product_audit'
        verbose_name = 'Audit Data'
        verbose_name_plural = 'Audit Data'

    def __str__(self):
        return self.country


class Cell(CreateUpdateMixIn,models.Model):

    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    name = models.CharField(max_length=500,)
    code = UpperCaseCharField(max_length=500,validators=[validators.validate_slug])
    description = models.TextField(null=True, blank=True)

    cell_acv = models.DecimalField(max_digits=15,decimal_places=6,default=0)
    num_universe = models.DecimalField(max_digits=15,decimal_places=6,default=0)
    optimal_panel = models.IntegerField(default=0)

    condition_html = models.TextField(null=True, blank=True)
    serialize_str = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = (('country','code'))
        db_table = 'cell'
        verbose_name = 'Cell'
        verbose_name_plural = 'Cells'

    def __str__(self):
        return self.name

class RBD(CreateUpdateMixIn,models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=500,)
    code = UpperCaseCharField(max_length=500,validators=[validators.validate_slug])
    description = models.TextField(null=True, blank=True)
    cell = models.ManyToManyField(Cell)

    class Meta:
        unique_together = (('country','code'))
        db_table = 'rbd'
        verbose_name = 'RBD'
        verbose_name_plural = 'RBDs'

    def __str__(self):
        return self.name

class Province(CodeNameMixIn,CreateUpdateMixIn,models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('country','code',),)
        db_table = 'province'
        verbose_name = 'Province'
        verbose_name_plural = 'Provinces'

class District(CodeNameMixIn,CreateUpdateMixIn,models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('country','code',),)
        db_table = 'district'
        verbose_name = 'District'
        verbose_name_plural = 'Districts'

class Tehsil(CodeNameMixIn,CreateUpdateMixIn,models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    urbanity =  models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('country','code',),)
        db_table = 'tehsil'
        verbose_name = 'Tehsil'
        verbose_name_plural = 'Tehsils'



class CityVillage(CodeNameMixIn,CreateUpdateMixIn,models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE, null=True, blank=True)
    tehsil = models.ForeignKey(Tehsil, on_delete=models.CASCADE)
    rc_cut =  models.CharField(max_length=500)
    extra_1 =  models.CharField(max_length=500)
    extra_2 =  models.CharField(max_length=500)
    extra_3 =  models.CharField(max_length=500)
    extra_4 =  models.CharField(max_length=500)
    extra_5 =  models.CharField(max_length=500)
    extra_6 =  models.CharField(max_length=500)
    extra_7 =  models.CharField(max_length=500)
    extra_8 =  models.CharField(max_length=500)
    extra_9 =  models.CharField(max_length=500)
    extra_10 =  models.CharField(max_length=500)
    extra_11 =  models.CharField(max_length=500)
    extra_12 =  models.CharField(max_length=500)
    extra_13 =  models.CharField(max_length=500)
    extra_14 =  models.CharField(max_length=500)
    extra_15 =  models.CharField(max_length=500)
    extra_16 =  models.CharField(max_length=500)
    extra_17 =  models.CharField(max_length=500)
    extra_18 =  models.CharField(max_length=500)
    extra_19 =  models.CharField(max_length=500)
    extra_20 =  models.CharField(max_length=500)
    extra_21 =  models.CharField(max_length=500)
    extra_22 =  models.CharField(max_length=500)
    extra_23 =  models.CharField(max_length=500)
    extra_24 =  models.CharField(max_length=500)
    extra_25 =  models.CharField(max_length=500)
    extra_26 =  models.CharField(max_length=500)
    extra_27 =  models.CharField(max_length=500)
    extra_28 =  models.CharField(max_length=500)
    extra_29 =  models.CharField(max_length=500)
    extra_30 =  models.CharField(max_length=500)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('country','code',),)
        db_table = 'city_village'
        verbose_name = 'CityVillage'
        verbose_name_plural = 'CityVillages'
        ordering = ['name']


class ColLabel(CreateUpdateMixIn,models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    model_name = models.CharField(max_length=150)
    col_name =  models.CharField(max_length=150)
    col_label =  models.CharField(max_length=150)

    def __str__(self):
        return self.col_label

    class Meta:
        unique_together = (('country','model_name','col_name'),)
        db_table = 'col_label'
        verbose_name = 'ColLabel'
        verbose_name_plural = 'ColLabels'
