from django.db import models
from django.core import validators
from django.core.exceptions import ValidationError

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db.models.indexes import Index
from django.utils.translation import ugettext_lazy as _

from mptt.models import MPTTModel, TreeForeignKey
from core.mixinsModels import UpperCaseCharField,CodeNameMixIn,CreateUpdateMixIn
from core.colors import Colors
from master_setups.models import Country,IndexSetup,UserCountry,User,UserIndex,CountrySetting


try: from core.dynamic_model.CityVillageMixIn import CityVillageMixIn
except ImportError: CityVillageMixIn = None

try: from core.dynamic_model.PanelProfileMixIn import PanelProfileMixIn
except ImportError: PanelProfileMixIn = None

try: from core.dynamic_model.ProductMixin import ProductMixin
except ImportError: ProductMixin = None



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
      (APPENDUPDATE, 'Append/Update: If  records exist update otherwise add.'),
      (REFRESH, 'Reresh: Delete all records and repopulate from the source.'),
    ]

    CHOICES_UPDATE = [
      (UPDATE, 'Update: If records exist update.'),
    ]

    UPLOADING_MSG = "Uploading please wait."
    PROCESSING_MSG = "Records are processing in background, check back soon."
    COMPLETED_MSG = "Processing completed successfully."
    FAILED_MSG = "Processing faild, please try again"
    ERROR_MSG = "Error occurred due to following reason"

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

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    index = models.ForeignKey(IndexSetup, on_delete=models.SET_NULL, null=True, blank=True)

    import_mode = models.CharField(max_length=20, choices=CHOICES)
    frommodel = models.CharField(max_length=50)
    file = models.FileField(upload_to=handle_upload_logs)
    is_processing = models.CharField(max_length=20, choices=IS_PROCESSING_CHOICES,blank=True, null=True)
    process_message = models.CharField(max_length=255, blank=True, null=True)
    skiped_records = models.IntegerField(blank=True, null=True)
    updated_records = models.IntegerField(blank=True, null=True)
    created_records = models.IntegerField(blank=True, null=True)
    other = JSONField(blank=True, null=True)
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

class CityVillageDefault(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, on_delete=models.SET_NULL, null=True, blank=True)
    tehsil = models.ForeignKey(Tehsil, on_delete=models.CASCADE)
    rc_cut =  models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        abstract = True

class CityVillage(CodeNameMixIn,CityVillageDefault,CityVillageMixIn,CreateUpdateMixIn,models.Model):

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
    upload = models.ForeignKey(Upload, on_delete=models.SET_NULL, null=True, blank=True)
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
    upload = models.ForeignKey(Upload, on_delete=models.SET_NULL, null=True, blank=True)
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
    index = models.ForeignKey(IndexSetup, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category,related_name='index_category',)

    def get_index_category_list(self):
        cl ={a.id : a.name for a in self.category.all()}
        return cl

    def get_index_category_ids(self):
        cl =[a.id for a in self.category.all()]
        return cl
    def __str__(self):
        return str('{0}'.format(self.index.name))

    class Meta:
        db_table = 'index_category'
        verbose_name = 'Index Category'
        verbose_name_plural = 'Index Categries'

class OutletType(CodeNameMixIn,CreateUpdateMixIn,MPTTModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, on_delete=models.SET_NULL, null=True, blank=True)
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
    code = models.CharField(max_length=50)
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
    upload = models.ForeignKey(Upload, on_delete=models.SET_NULL, null=True, blank=True)
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

class PanelProfileDefault(models.Model):
    AUDITED = 'A'
    COPIED = 'C'
    ESTIMATED = 'E'
    AUDIT_STATUS_CHOICES = (
        (AUDITED , 'Audited'),
        (COPIED , 'Copied'),
        (ESTIMATED , 'Estimated'),
    )
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, on_delete=models.SET_NULL, null=True, blank=True)
    month = models.ForeignKey(Month,on_delete=models.CASCADE)
    index = models.ForeignKey(IndexSetup, on_delete=models.CASCADE)
    # category = models.ForeignKey(Category, on_delete=models.CASCADE)

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
        abstract = True

class PanelProfile(PanelProfileDefault,PanelProfileMixIn,CreateUpdateMixIn,models.Model):
    class Meta:
        unique_together = (('country','outlet', 'month','index'))
        db_table = 'panel_profile'
        verbose_name = 'Panel Profile'
        verbose_name_plural = 'Panel Profiles'

    def __str__(self):
        return self.outlet.code

class PanelProfileChild(PanelProfileDefault,PanelProfileMixIn,CreateUpdateMixIn,models.Model):
    is_valid = models.BooleanField(default=True)
    price_variation = models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default=0)

    class Meta:
        unique_together = (('country','outlet', 'month','index'))
        db_table = 'panel_profile_child'
        verbose_name = 'Panel Profile Child'
        verbose_name_plural = 'Panel Profiles Child'

    def __str__(self):
        return self.outlet.code

class ProductDefault(models.Model):

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, on_delete=models.SET_NULL, null=True, blank=True)
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
    class Meta:
        abstract = True

class Product(CreateUpdateMixIn,CodeNameMixIn,ProductDefault,ProductMixin,models.Model):
    class Meta:
        unique_together = (('country','code'))
        db_table = 'product'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.code

class AuditDataDefault(models.Model):
    AUDITED = 'A'
    COPIED = 'C'
    ESTIMATED = 'E'
    AUDIT_STATUS_CHOICES = (
        (AUDITED , 'Audited'),
        (COPIED , 'Copied'),
        (ESTIMATED , 'Estimated'),
    )

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, on_delete=models.SET_NULL, null=True, blank=True)
    month = models.ForeignKey(Month,on_delete=models.CASCADE)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    period = models.CharField(max_length=50, null=True, blank=True)

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

    class Meta:
        abstract = True

class AuditData(CreateUpdateMixIn,AuditDataDefault,models.Model):

    class Meta:
        unique_together = (('country','outlet','product','month'))
        db_table = 'audit_data'
        verbose_name = 'Audit Data'
        verbose_name_plural = 'Audit Data'

    def __str__(self):
        return self.id

class AuditDataChild(CreateUpdateMixIn,AuditDataDefault,models.Model):


    price_variation = models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default=0)
    purchase_variation = models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default=0)
    sales_variation = models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default=0)
    stock_variation = models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default=0)
    avg_sales = models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default=0)
    sd_sales = models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default=0)
    sd_range_min = models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default=0)
    sd_range_max = models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default=0)
    is_valid = models.BooleanField(default=True)
    flag_price = models.BooleanField(default=False)
    flag_neg_sales_corr = models.BooleanField(default=False)
    flag_outlier = models.BooleanField(default=False)
    flag_copied_previous = models.BooleanField(default=False)

    class Meta:

        unique_together = (('country','outlet','product','month'))
        db_table = 'audit_data_child'
        verbose_name = 'Audit Data Child'
        verbose_name_plural = 'Audit Data Child'

    def __str__(self):
        return self.id

class Cell(CreateUpdateMixIn,models.Model):

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, on_delete=models.SET_NULL, null=True, blank=True)
    index = models.ForeignKey(IndexSetup, on_delete=models.CASCADE)
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
        unique_together = (('country','name','index'))
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
    index = models.ForeignKey(IndexSetup, on_delete=models.CASCADE)
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE)
    cell_acv = models.DecimalField(max_digits=18,decimal_places=6,default=0)

    class Meta:
        unique_together = (('country','month','cell','index'))
        db_table = 'cell_month_acv'
        verbose_name = 'CellMonthACV'
        verbose_name_plural = 'CellMonthACVs'

    def __str__(self):
        return self.cell_acv

class RBD(CreateUpdateMixIn,models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    index = models.ForeignKey(IndexSetup, on_delete=models.CASCADE)
    name = models.CharField(max_length=500,)
    description = models.TextField(null=True, blank=True)
    cell = models.ManyToManyField(Cell)

    class Meta:
        unique_together = (('country','name','index'))
        db_table = 'rbd'
        verbose_name = 'RBD'
        verbose_name_plural = 'RBDs'

    def __str__(self):
        return self.name

class UsableOutlet(CreateUpdateMixIn,models.Model):

    USABLE = 'USABLE'
    NOTUSABLE = 'NOTUSABLE'
    DROP = 'DROP'
    QUARANTINE = 'QUARANTINE'
    USABLE_STATUS_CHOICES = (
        (USABLE , 'Usable'),
        (NOTUSABLE , 'Not Usable'),
        (DROP , 'Drop'),
        (QUARANTINE , 'Quarantine'),
    )
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    index = models.ForeignKey(IndexSetup, on_delete=models.CASCADE)
    upload = models.ForeignKey(Upload, on_delete=models.SET_NULL, null=True, blank=True)
    month = models.ForeignKey(Month,on_delete=models.CASCADE)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
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

    CityVillage = 'CityVillage'
    Product = 'Product'
    PanelProfile = 'PanelProfile'

    MODEL_CHOICES = (
        (CityVillage , 'CityVillage'),
        (Product , 'Product'),
        (PanelProfile, 'PanelProfile'),
    )

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    model_name = models.CharField(max_length=150, choices=MODEL_CHOICES,default=CityVillage)
    col_name =  models.CharField(max_length=150)
    col_label =  models.CharField(max_length=150)

    def __str__(self):
        return self.col_label

    class Meta:
        unique_together = (('country','model_name','col_name'),)
        db_table = 'col_label'
        verbose_name = 'ColLabel'
        verbose_name_plural = 'ColLabels'



class Threshold(CreateUpdateMixIn, models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    index = models.ForeignKey(IndexSetup, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    audited_data_purchase_min= models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='-10')
    audited_data_purchase_max= models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='10')

    audited_data_sales_min= models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='-10')
    audited_data_sales_max= models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='10')

    audited_data_stock_min= models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='-10')
    audited_data_stock_max= models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='10')

    audited_data_price_min= models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='-10' )
    audited_data_price_max= models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='10', help_text="Apply Last Month Price Cleaning on the Stores + P_Codes")


    audited_data_stddev_min= models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='-3')
    audited_data_stddev_max= models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='3', help_text="(Store + P_code Actual Sales) Shall lie in between Avg (P_code Sales) +/- 3 SD ")
    stddev_sample = models.BooleanField(default=True, help_text="Use StdDev Sample if enable else StdDev Population")

    outlet_factor_numaric_min = models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='0')
    outlet_factor_numaric_max = models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='1')

    common_outlet_accept = models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='5', help_text="ABS (Store Actual Sales /  Store Last Month Sales - 1) <= c")
    common_outlet_copy = models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='5', help_text="ABS (Store Actual Sales /  Store Census Sales - 1) > c")
    new_outlet_accept_a = models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='5', help_text="ABS (Store Actual Sales /  Store Census Sales - 1) <= a")
    new_outlet_drop_a = models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='5', help_text="ABS (Store Actual Sales /  Store Census Sales - 1) > a" )
    new_outlet_accept_b = models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='5', help_text="ABS (Store Actual Sales /  Avg Cell Sales - 1) <= b")
    new_outlet_drop_b = models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='5', help_text="ABS (Store Actual Sales /  Avg Cell Sales - 1) > b")
    drop_outlet_copied = models.BooleanField(default=True)
    drop_outlet_copied_once = models.BooleanField(default=True)
    weighted_store = models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='80')
    weighted_cell = models.DecimalField(max_digits=11, decimal_places=2,null=True,blank=True,default='80')

    def __str__(self):
        return str('{0}'.format(self.country))

    class Meta:
        unique_together = (('country', 'index','category'))
        db_table = 'threshold'
        verbose_name = 'Threshold'
        verbose_name_plural = 'Thresholds'