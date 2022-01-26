import csv
import re
import time
import sys
import os
import json
import decimal
import logging
import signal
import base64
import traceback
from termcolor import cprint
from sys import stdout, stdin, stderr

from xmlrpc.client import boolean
from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *
from datetime import datetime,date,timedelta
# from datetime import *
from dateutil.relativedelta import relativedelta


from pprint import pprint
from var_dump import var_dump,var_export
from subprocess import Popen
from inspect import getmembers
from csv import DictReader
from itertools import chain
from collections import OrderedDict
from inspect import CO_OPTIMIZED
from urllib.parse import parse_qs,urlparse,urlencode, quote_plus,quote
from pathlib import Path

from django.utils.dateparse import parse_date
from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.core.files.storage import FileSystemStorage
from django.core.serializers import serialize
from django.core.exceptions import ValidationError


from django.db import models
from django.db.models import Q,Avg, Count, Min,Max, Sum
from django.db.models.aggregates import StdDev,Avg
from django.db import IntegrityError

from django.forms.models import model_to_dict
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse,reverse_lazy


from django.http import (HttpResponseRedirect,HttpResponse,JsonResponse)
from django.views import generic
from rest_framework.generics import ListAPIView


from core.pagination import StandardResultsSetPagination
from core.mixinsViews import PassRequestToFormViewMixin
from core.colors import Colors
from pprint import pprint
from var_dump import var_dump,var_export
from core.settings import MEDIA_ROOT,MEDIA_URL


from core.utils import (trace,prettyprint_query,prettyprint_queryset,
            format_datetime,parse_date,cdebug,find_location,csvHeadClean,
            printr,replaceIndex,convertSecond2Min,get_max_str,camelTerms,
            percentChange,percentChangeAbs,timeSpent)

from core.helpers import (getDictArray,getDicGroupList,getGroupFilter,getGroupFilterHuman,
            dropzeros,remove_exponent,getCategories,getMonths,modelValidFields,modelForeignFields,
            uploadStatusMessage,IdCodeModel,chkMonthLocked,getCode2AnyModelFieldList,updateUploadStatus,
            getTwoMonthFromDate,calculateSales)


from master_data.serializers import PanelProfileSerializers
from ajax_datatable.views import AjaxDatatableView
from django_datatables_view.base_datatable_view import BaseDatatableView


logger = logging.getLogger(__name__)