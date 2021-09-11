from django.http import Http404
from django.shortcuts import render

from taiwan_einvoice.models import ESCPOSWeb


def index(request):
    escpos_webs = ESCPOSWeb.objects.all().order_by('id')
    return render(request, 'taiwan_einvoice/index.html', {
        'escpos_webs': escpos_webs
    })


def escpos_web(request, escpos_web_id):
    try:
        escpos_web = ESCPOSWeb.objects.get(id=escpos_web_id)
    except ESCPOSWeb.DoesNotExist:
        raise Http404("ESCPOS Web does not exist!")
    return render(request,
                  'taiwan_einvoice/escpos_web.html',
                  {"escpos_web": escpos_web})