import logging

from django.http import HttpResponse
from django.template import loader

log = logging.getLogger('django.trainerdex')

def terms(request):
    template = loader.get_template('text/privacy_policy.html')
    return HttpResponse(template.render(None, request))
