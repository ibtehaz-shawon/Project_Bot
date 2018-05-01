from __future__ import unicode_literals

import json

from django.http import HttpResponse
from django.template import loader

from django.views.decorators.csrf import csrf_exempt

from blood_bank.db_handler import error_logger
from blood_bank.parser import facebook_message
from bot.settings import MESSENGER_VERIFY_TOKEN

template = loader.get_template('blood_bank/webhook.html')

"""
index function will receive the occasional facebook verify token request 
and sends every scrap data to facebook_message file to handle and parsing.
"""


# noinspection SpellCheckingInspection,PyBroadException
@csrf_exempt
def index(request):
    if request.method == 'GET':
        if str(request.GET.get('hub.verify_token', 'no_verify_token')) == MESSENGER_VERIFY_TOKEN:
            return HttpResponse(request.GET.get('hub.challenge'))
        else:
            error_logger("Unknown Request came in GET - Web-hook", None, 'GET - Webhook')
            return HttpResponse(template.render(), status=200)
    elif request.method == 'POST':
        try:
            incoming_message = json.loads(request.body.decode('utf-8'))
            print("Incoming message :: " + str(incoming_message))
            facebook_message(incoming_message)
            return HttpResponse(status=200)
        except ValueError as err:
            print("Error Occurred: " + str(err))
            error_logger(str(err) + "\n" + str(json.loads(request.body.decode('utf-8'))),
                         None, "POST - ValueError - Webhook")
            return HttpResponse(status=200)
        except BaseException as error:
            print("Broad exception handling "+str(error))
            error_logger(str(error) + "\n" + str(json.loads(request.body.decode('utf-8'))),
                         None, "POST - Unknown - Webhook")
            return HttpResponse(status=200)
    else:
        return HttpResponse(template.render(), status=200)
