from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.forms.utils import ErrorList
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from django.views import generic
from django.contrib.auth import logout
from django.contrib import messages
from master_setups.models import UserCountry
from core.colors import Colors

from .forms import (
    CustomUserCreationForm,
)

from django.urls import reverse

class SignupView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse("login")



class NoCountry(generic.TemplateView):
    template_name = "registration/no_country.html"

def adminLoginProcess(request):
    username=request.POST.get("username")
    password=request.POST.get("password")

    user=authenticate(request=request,username=username,password=password)
    if user is not None:
        auth = login(request=request,user=user)
        usercountries = UserCountry.objects.filter(user=user).count()

        if usercountries <= 0:
            logout(request)
            # messages.add_message(request, messages.warning, 'You are not assigned in any country, please contact your Manager')
            return HttpResponseRedirect(reverse("nocountry"))
        request.session['_user'] = user.id
        return HttpResponseRedirect(reverse("home"))
    else:
        messages.error(request,"Error in Login! Invalid Login Details!")
        return HttpResponseRedirect(reverse("login"))
