import re
import json
from csv import DictReader
import logging
from django.core.management.base import BaseCommand
from master_data.models import Census,Upload
from master_setups.models import Country
from collections import OrderedDict
from core.settings import MEDIA_ROOT
logger = logging.getLogger(__name__)

class Command(BaseCommand):

    def add_arguments(self, parser):
        # parser.add_argument('country_code', type=str)
        parser.add_argument('arg1', type=str)
        parser.add_argument('arg2', type=str)

    def handle(self, *args, **options):
        print(options['arg1'])
        print(options['arg2'])




