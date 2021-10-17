import re
import time
import datetime
import sys, os
import json
import decimal
import logging
from inspect import CO_OPTIMIZED
from csv import DictReader
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
from dateutil.rrule import *
from dateutil.parser import *
from dateutil import parser
from urllib.parse import parse_qs,urlparse
from pathlib import Path

from django.utils.dateparse import parse_date
from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Q, Avg, Count, Min,Max, Sum
from django.forms.models import model_to_dict

from core.colors import Colors
from pprint import pprint
from var_dump import var_dump,var_export
from core.settings import MEDIA_ROOT,MEDIA_URL
from core.utils import (trace,prettyprint_query,prettyprint_queryset,
            format_datetime,parse_date,cdebug,find_location,csvHeadClean,
            printr,replaceIndex,convertSecond2Min,get_max_str,camelTerms)

from core.helpers import (getDictArray,getDicGroupList,getGroupFilter,getGroupFilterHuman,
            dropzeros,remove_exponent,getCategories,getMonths,modelValidFields,modelForeignFields,
            uploadStatusMessage,IdCodeModel,chkMonthLocked,getCode2AnyModelFieldList)
logger = logging.getLogger(__name__)