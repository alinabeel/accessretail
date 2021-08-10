import os
import logging
import json
from subprocess import Popen
from sys import stdout, stdin, stderr
import time, os, signal


from pprint import pprint
from inspect import getmembers
from csv import DictReader
from datetime import datetime
from django import contrib
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse,reverse_lazy
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (HttpResponse, HttpResponseBadRequest,
                        HttpResponseForbidden,HttpResponseRedirect,
                        JsonResponse)
from django.views import generic
from django.core import serializers
from core.settings import MEDIA_ROOT
from core.colors import Colors
from master_setups.models import *
from master_data.models import *
from master_data.forms import *
from django.core import management
# from django.core.management.commands import import_census
from master_data.management.commands import import_census

from master_setups.models import User
from rest_framework import viewsets
from rest_framework import permissions
from master_data.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

