from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from bot.settings import DEBUG
from .models import ErrorLog, DataDump


def index(request):
    template = loader.get_template('blood_bank/index.html')
    return HttpResponse(template.render())


def error_log(request):
    if DEBUG:
        template = loader.get_template('blood_bank/logger.html')
        all_error_logs = ErrorLog.objects.all()

        context = {
            'all_error_logs': all_error_logs,
        }
        return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template('blood_bank/webhook.html')
        return HttpResponse(template.render(), status=200)


def data_dump(request):
    if DEBUG:
        # template = loader.get_template('blood_bank/logger.html')
        entire_data_dump = DataDump.objects.all()

        # context = {
        #     'all_error_logs': all_error_logs,
        # }
        return HttpResponse(entire_data_dump)
    else:
        template = loader.get_template('blood_bank/webhook.html')
        return HttpResponse(template.render(), status=200)