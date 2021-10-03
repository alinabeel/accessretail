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

    rc_cut =  models.CharField(max_length=500, null=True, blank=True)
    extra_1 =  models.CharField(max_length=500, null=True, blank=True)
    extra_2 =  models.CharField(max_length=500, null=True, blank=True)
    extra_3 =  models.CharField(max_length=500, null=True, blank=True)
    extra_4 =  models.CharField(max_length=500, null=True, blank=True)
    extra_5 =  models.CharField(max_length=500, null=True, blank=True)
    extra_6 =  models.CharField(max_length=500, null=True, blank=True)
    extra_7 =  models.CharField(max_length=500, null=True, blank=True)
    extra_8 =  models.CharField(max_length=500, null=True, blank=True)
    extra_9 =  models.CharField(max_length=500, null=True, blank=True)
    extra_10 =  models.CharField(max_length=500, null=True, blank=True)
    extra_11 =  models.CharField(max_length=500, null=True, blank=True)
    extra_12 =  models.CharField(max_length=500, null=True, blank=True)
    extra_13 =  models.CharField(max_length=500, null=True, blank=True)
    extra_14 =  models.CharField(max_length=500, null=True, blank=True)
    extra_15 =  models.CharField(max_length=500, null=True, blank=True)
    extra_16 =  models.CharField(max_length=500, null=True, blank=True)
    extra_17 =  models.CharField(max_length=500, null=True, blank=True)
    extra_18 =  models.CharField(max_length=500, null=True, blank=True)
    extra_19 =  models.CharField(max_length=500, null=True, blank=True)
    extra_20 =  models.CharField(max_length=500, null=True, blank=True)
    extra_21 =  models.CharField(max_length=500, null=True, blank=True)
    extra_22 =  models.CharField(max_length=500, null=True, blank=True)
    extra_23 =  models.CharField(max_length=500, null=True, blank=True)
    extra_24 =  models.CharField(max_length=500, null=True, blank=True)
    extra_25 =  models.CharField(max_length=500, null=True, blank=True)
    extra_26 =  models.CharField(max_length=500, null=True, blank=True)
    extra_27 =  models.CharField(max_length=500, null=True, blank=True)
    extra_28 =  models.CharField(max_length=500, null=True, blank=True)
    extra_29 =  models.CharField(max_length=500, null=True, blank=True)
    extra_30 =  models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('country','code',),)
        db_table = 'city_village'
        verbose_name = 'CityVillage'
        verbose_name_plural = 'CityVillages'
        ordering = ['name']

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

    is_locked = models.BooleanField(default=False)
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


class OutletStatus(CodeNameMixIn,CreateUpdateMixIn,models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    class Meta:
        unique_together = (('country','code'),)
        db_table = 'outlet_status'
        verbose_name = 'OutletStatus'
        verbose_name_plural = 'OutletStatuses'

class PanelProfile(CreateUpdateMixIn,models.Model):
    AUDITED = 'A'
    COPIED = 'C'
    ESTIMATED = 'E'
    AUDIT_STATUS_CHOICES = (
        (AUDITED , 'Audited'),
        (COPIED , 'Copied'),
        (ESTIMATED , 'Estimated'),
    )
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE, null=True, blank=True)
    month = models.ForeignKey(Month,on_delete=models.CASCADE)

    index = models.ForeignKey(IndexSetup, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    hand_nhand = models.CharField(max_length=50, null=True, blank=True)
    city_village = models.ForeignKey(CityVillage, on_delete=models.CASCADE)
    region = models.CharField(max_length=50, null=True, blank=True)

    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    outlet_type = models.ForeignKey(OutletType, on_delete=models.CASCADE)
    outlet_status = models.ForeignKey(OutletStatus, on_delete=models.CASCADE)

    nra_tagging = models.SmallIntegerField(null=True, blank=True, default=0)
    ra_tagging = models.SmallIntegerField(null=True, blank=True, default=0)
    ret_tagging = models.SmallIntegerField(null=True, blank=True, default=0)

    lms = models.CharField(max_length=50, null=True, blank=True)
    cell_description = models.CharField(max_length=1000, null=True, blank=True)

    audit_date = models.DateField(null=True, blank=True)

    wtd_factor = models.DecimalField(max_digits=18,decimal_places=6, default=0)
    num_factor = models.DecimalField(max_digits=18,decimal_places=6, default=0)
    turnover = models.DecimalField(max_digits=18,decimal_places=6, default=0)
    acv = models.DecimalField(max_digits=18,decimal_places=6, default=0)
    audit_status = models.CharField(max_length=1, choices=AUDIT_STATUS_CHOICES,default=AUDITED)

    class Meta:
        unique_together = (('country','outlet', 'month'))
        db_table = 'panel_profile'
        verbose_name = 'PanelProfile'
        verbose_name_plural = 'PanelProfiles'

    def __str__(self):
        return self.outlet.code



class Product(CodeNameMixIn,CreateUpdateMixIn,models.Model):

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE, null=True, blank=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=150, null=True, blank=True)
    sku = models.CharField(max_length=150, null=True, blank=True)
    brand = models.CharField(max_length=150, null=True, blank=True)
    variant = models.CharField(max_length=150, null=True, blank=True)
    size = models.CharField(max_length=150, null=True, blank=True)
    packaging = models.CharField(max_length=150, null=True, blank=True)

    origin = models.CharField(max_length=150, null=True, blank=True)
    country_of_origin = models.CharField(max_length=150, null=True, blank=True)

    manufacture = models.CharField(max_length=150, null=True, blank=True)

    price_segment = models.CharField(max_length=150, null=True, blank=True)
    super_manufacture = models.CharField(max_length=150, null=True, blank=True)
    super_brand = models.CharField(max_length=150, null=True, blank=True)

    weight = models.DecimalField(max_digits=18,decimal_places=6, null=True, blank=True)
    number_in_pack = models.IntegerField(null=True, blank=True)
    price_per_unit = models.DecimalField(max_digits=18,decimal_places=6, null=True, blank=True)

    extra_1 =  models.CharField(max_length=500, null=True, blank=True)
    extra_2 =  models.CharField(max_length=500, null=True, blank=True)
    extra_3 =  models.CharField(max_length=500, null=True, blank=True)
    extra_4 =  models.CharField(max_length=500, null=True, blank=True)
    extra_5 =  models.CharField(max_length=500, null=True, blank=True)
    extra_6 =  models.CharField(max_length=500, null=True, blank=True)
    extra_7 =  models.CharField(max_length=500, null=True, blank=True)
    extra_8 =  models.CharField(max_length=500, null=True, blank=True)
    extra_9 =  models.CharField(max_length=500, null=True, blank=True)
    extra_10 =  models.CharField(max_length=500, null=True, blank=True)
    extra_11 =  models.CharField(max_length=500, null=True, blank=True)
    extra_12 =  models.CharField(max_length=500, null=True, blank=True)
    extra_13 =  models.CharField(max_length=500, null=True, blank=True)
    extra_14 =  models.CharField(max_length=500, null=True, blank=True)
    extra_15 =  models.CharField(max_length=500, null=True, blank=True)
    extra_16 =  models.CharField(max_length=500, null=True, blank=True)
    extra_17 =  models.CharField(max_length=500, null=True, blank=True)
    extra_18 =  models.CharField(max_length=500, null=True, blank=True)
    extra_19 =  models.CharField(max_length=500, null=True, blank=True)
    extra_20 =  models.CharField(max_length=500, null=True, blank=True)
    extra_21 =  models.CharField(max_length=500, null=True, blank=True)
    extra_22 =  models.CharField(max_length=500, null=True, blank=True)
    extra_23 =  models.CharField(max_length=500, null=True, blank=True)
    extra_24 =  models.CharField(max_length=500, null=True, blank=True)
    extra_25 =  models.CharField(max_length=500, null=True, blank=True)
    extra_26 =  models.CharField(max_length=500, null=True, blank=True)
    extra_27 =  models.CharField(max_length=500, null=True, blank=True)
    extra_28 =  models.CharField(max_length=500, null=True, blank=True)
    extra_29 =  models.CharField(max_length=500, null=True, blank=True)
    extra_30 =  models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        unique_together = (('country','code'))
        db_table = 'product'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.country


class ProductAudit(CreateUpdateMixIn,models.Model):
    AUDITED = 'A'
    COPIED = 'C'
    ESTIMATED = 'E'
    AUDIT_STATUS_CHOICES = (
        (AUDITED , 'Audited'),
        (COPIED , 'Copied'),
        (ESTIMATED , 'Estimated'),
    )

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE, null=True, blank=True)
    month = models.ForeignKey(Month,on_delete=models.CASCADE)

    period = models.CharField(max_length=50, null=True, blank=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


    audit_date = models.DateField(null=True, blank=True)
    purchase_1 = models.IntegerField(default=0,null=True, blank=True)
    purchase_2 = models.IntegerField(default=0,null=True, blank=True)
    purchase_3 = models.IntegerField(default=0,null=True, blank=True)
    purchase_4 = models.IntegerField(default=0,null=True, blank=True)
    purchase_5 = models.IntegerField(default=0,null=True, blank=True)
    opening_stock = models.IntegerField(default=0,null=True, blank=True)
    stock_1 = models.IntegerField(default=0,null=True, blank=True)
    stock_2 = models.IntegerField(default=0,null=True, blank=True)
    stock_3 = models.IntegerField(default=0,null=True, blank=True)
    total_stock = models.IntegerField(default=0,null=True, blank=True)

    price = models.DecimalField(default=0, max_digits=18,decimal_places=6,)

    vd_factor = models.DecimalField(default=0, max_digits=18,decimal_places=6,)
    total_purchase = models.IntegerField(default=0, null=True, blank=True)
    rev_purchase = models.IntegerField(default=0, null=True, blank=True)
    sales = models.DecimalField(default=0, max_digits=18, decimal_places=6,)
    sales_vol = models.DecimalField(default=0,max_digits=18,decimal_places=6,)
    sales_val = models.DecimalField(default=0,max_digits=18,decimal_places=6,)
    audit_status = models.CharField(max_length=1, choices=AUDIT_STATUS_CHOICES,default=AUDITED)

    # product_details = models.TextField(null=True, blank=True)
    # avaibility = models.BooleanField(default=True)
    # facing_empty = models.IntegerField(default=0,null=True, blank=True)
    # facing_not_empty = models.IntegerField(default=0)
    # forward = models.IntegerField(default=0)
    # reserve = models.IntegerField(default=0)
    # total_none_empty_facing_forward_reserve = models.IntegerField(default=0)
    # purchaseother1 = models.IntegerField(default=0)
    # purchaseother2 = models.IntegerField(default=0)
    # purchasediary = models.IntegerField(default=0)
    # purchaseinvoice = models.IntegerField(default=0)
    # price_in_unit = models.DecimalField(max_digits=18,decimal_places=6,)
    # price_in_pack = models.DecimalField(max_digits=18,decimal_places=6,)
    # priceother = models.DecimalField(max_digits=18,decimal_places=6,)
    # cash_discount = models.DecimalField(max_digits=18,decimal_places=6,)
    # product_foc = models.IntegerField(default=0)
    # gift_with_purchase = models.IntegerField(default=0)
    # appreciation_award = models.IntegerField(default=0)
    # other_trade_promotion = models.IntegerField(default=0)

    # sales_unprojected_volume = models.DecimalField(max_digits=18,decimal_places=6,default=0)
    # sales_unprojected_value = models.DecimalField(max_digits=18,decimal_places=6,default=0)
    # sales_unprojected_units = models.DecimalField(max_digits=18,decimal_places=6,default=0)

    # sales_projected_volume = models.DecimalField(max_digits=18,decimal_places=6,default=0)
    # sales_projected_value = models.DecimalField(max_digits=18,decimal_places=6,default=0)
    # sales_projected_units = models.DecimalField(max_digits=18,decimal_places=6,default=0)

    # pack_without_graphic_health_warning = models.IntegerField(default=0,)
    # no_of_pack_without_graphic_health_warning_facing = models.IntegerField(default=0)
    # no_of_pack_without_graphic_health_warning_total_stock = models.IntegerField(default=0)
    # no_of_pack_without_none_tax_stamp = models.IntegerField(default=0)
    # point_of_sales_signboard = models.IntegerField(default=0)
    # point_of_sales_poster = models.IntegerField(default=0)
    # point_of_sales_counter_shield = models.IntegerField(default=0)
    # point_of_sales_price_sticker = models.IntegerField(default=0)
    # point_of_sales_umbrella = models.IntegerField(default=0)
    # point_of_sales_counter_top_display = models.IntegerField(default=0)
    # point_of_sales_lighter = models.IntegerField(default=0)
    # point_of_sales_others = models.IntegerField(default=0)
    # point_of_sales_none = models.IntegerField(default=0)

    class Meta:
        unique_together = (('country','outlet','product','month'))
        db_table = 'product_audit'
        verbose_name = 'Audit Data'
        verbose_name_plural = 'Audit Data'

    def __str__(self):
        return self.country


class CellStructure(CreateUpdateMixIn,models.Model):

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=500,)
    description = models.TextField(null=True, blank=True)

    cell_acv = models.DecimalField(max_digits=18,decimal_places=6,default=0)
    num_universe = models.DecimalField(max_digits=18,decimal_places=6,default=0)
    optimal_panel = models.IntegerField(default=0)

    condition_html = models.TextField(null=True, blank=True)
    serialize_str = models.TextField(null=True, blank=True)
    condition_json = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = (('country','name'))
        db_table = 'cell_structure'
        verbose_name = 'CellStructure'
        verbose_name_plural = 'CellStructures'

    def __str__(self):
        return self.name

class Cell(CreateUpdateMixIn,models.Model):

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=500,)
    description = models.TextField(null=True, blank=True)

    cell_acv = models.DecimalField(max_digits=18,decimal_places=6,default=0)
    num_universe = models.DecimalField(max_digits=18,decimal_places=6,default=0)
    optimal_panel = models.IntegerField(default=0)

    condition_html = models.TextField(null=True, blank=True)
    serialize_str = models.TextField(null=True, blank=True)
    condition_json = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = (('country','name'))
        db_table = 'cell'
        verbose_name = 'Cell'
        verbose_name_plural = 'Cells'

    def __str__(self):
        return self.name

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }

class CellMonthACV(CreateUpdateMixIn,models.Model):

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE)
    cell_acv = models.DecimalField(max_digits=18,decimal_places=6,default=0)

    class Meta:
        unique_together = (('country','month','cell'))
        db_table = 'cell_month_acv'
        verbose_name = 'CellMonthACV'
        verbose_name_plural = 'CellMonthACVs'

    def __str__(self):
        return self.cell_acv


class RBD(CreateUpdateMixIn,models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=500,)
    description = models.TextField(null=True, blank=True)
    cell = models.ManyToManyField(Cell)

    class Meta:
        unique_together = (('country','name'))
        db_table = 'rbd'
        verbose_name = 'RBD'
        verbose_name_plural = 'RBDs'

    def __str__(self):
        return self.name

class UsableOutlet(CreateUpdateMixIn,models.Model):

    USABLE = 'UA'
    NOTUSABLE = 'NU'
    DROP = 'DR'
    QUARANTINE = 'QA'
    USABLE_STATUS_CHOICES = (
        (USABLE , 'Usable'),
        (NOTUSABLE , 'Not Usable'),
        (DROP , 'Drop'),
        (QUARANTINE , 'Quarantine'),
    )
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE, null=True, blank=True)
    month = models.ForeignKey(Month,on_delete=models.CASCADE)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    index = models.ForeignKey(IndexSetup, on_delete=models.CASCADE)
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=USABLE_STATUS_CHOICES,default=USABLE)
    # is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.outlet.code
    class Meta:
        unique_together = (('country','month','index','outlet','cell'),)
        db_table = 'usable_outlet'
        verbose_name = 'UsableOutlet'
        verbose_name_plural = 'UsableOutlets'


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



