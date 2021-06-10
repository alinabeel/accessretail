from pprint import pprint
from master_setups.models import Country,UserCountry,UserIndex,IndexSetup
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
import core.settings as settings
from pprint import pprint







def global_context(request,*args):
    context = {}
    user = request.session.get('_user', None)


    usercountries = UserCountry.objects.filter(user=user)
    # country_code = Country.objects.only('name').get(code=args['country_code']).code

    context['app_name'] = settings.APP_NAME
    context['app_env'] = settings.DEVELOPMENT


    context["usercountries"] = usercountries
    context["country_id"] = request.session.get('country_id')
    context["country_code"] = request.session.get('country_code')
    context["country_name"] = request.session.get('country_name')
    return {'global': context}