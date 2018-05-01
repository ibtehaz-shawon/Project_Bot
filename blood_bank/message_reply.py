from __future__ import unicode_literals

import requests

from django.http import HttpResponse

from bot.settings import REPLY_URL

TAG_RECIPIENT = 'recipient'
TAG_ID = 'id'
TAG_MESSAGE = 'message'
TAG_TEXT = 'text'

"""
Dummy Response will only be used for testing purpose
"""


class MessageReply:
    @classmethod
    def echo_response(cls, user_id, response):
        print ("Message reply -- > "+str(response))
        payload = {
            TAG_RECIPIENT: {
                TAG_ID: user_id
            },
            TAG_MESSAGE: {
                TAG_TEXT: response
            }
        }
        status = requests.post(REPLY_URL, json=payload)
        print("------------------------------")
        print(status)
        print("-------------------------------")
