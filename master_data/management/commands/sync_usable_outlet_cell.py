from core.common_libs import *
from master_data.models import *
from master_setups.models import *

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('upload_id', type=int)

    def handle(self, *args, **options):
        start_time = time.time()
        upload_id = options['upload_id']
        upload = Upload.objects.get(pk=upload_id)
        country = Country.objects.get(pk=upload.country.id)
        log = ""

        # Get Valid Model Fields
        valid_fields = modelValidFields("UsableOutlet")
        foreign_fields = modelForeignFields("UsableOutlet")
        valid_fields_all = valid_fields + foreign_fields

        for ff in foreign_fields:
                valid_fields_all.append(f"{ff}_id")

        objs = Cell.objects.filter(country=upload.country,index=upload.index).values('id','name')
        cell_list = dict()
        for obj in objs:
            cell_list[str(obj['name']).lower()] = obj['id']

        month_list = getCode2AnyModelFieldList(upload.country.id,'Month','id')
        outlet_list = getCode2AnyModelFieldList(upload.country.id,'Outlet','id')
        month_islocked_list = getCode2AnyModelFieldList(upload.country.id,'Month','is_locked')

        updated_list = []
        # printr(Colors.BRIGHT_PURPLE,form_obj.file)
        try:
            n=0
            skiped_records = 0
            updated_records = 0
            created_records = 0

            month_qs = Month.objects.filter(country = upload.country,is_locked=False).order_by('date')
            print(month_qs)
            for month in month_qs:
                total_month = len(month_qs)
                pp_qs = PanelProfile.objects.filter(country = upload.country,month_id = month.id ) \
                    .values_list('outlet__id', flat=True).distinct()
                total_outlet = len(pp_qs)
                total_cell = len(cell_list)
                total_rec = total_month*total_outlet*total_cell
                for cell in cell_list:
                    for outlet_id in pp_qs:
                        # print(month.id,cell_list[cell],outlet_id)
                        if n%1000==0:
                            print(n,end=' ',flush=True)
                            updateUploadStatus(
                                id=upload_id,
                                msg=f'Processing {n} of {total_rec}',
                                is_processing = Upload.PROCESSING )

                        obj, created = UsableOutlet.objects.update_or_create(
                            country=upload.country,
                            cell_id=cell_list[cell],
                            outlet_id=outlet_id,
                            month_id=month.id,
                            index=upload.index,
                        )

                        n+=1



        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(Colors.RED, "Exception:",exc_type, fname, exc_tb.tb_lineno,Colors.WHITE)
            logger.error(Colors.BOLD_RED+'Sync failed. Error Msg:'+ str(e)+Colors.WHITE )
            log += 'CSV file processing failed. Error Msg:'+ str(e)
            upload.is_processing = Upload.ERROR
            upload.process_message = "Sync failed. Error Msg:"+str(e)
            upload.log  = log
            upload.save()
