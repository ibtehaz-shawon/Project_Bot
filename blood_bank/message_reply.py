from __future__ import unicode_literals

import requests

from django.http import HttpResponse

from bot.settings import REPLY_URL

TAG_RECIPIENT = 'recipient'
TAG_ID = 'id'
TAG_MESSAGE = 'message'
TAG_TEXT = 'text'

"""
Message Response class
"""


class MessageReply:
    @classmethod
    def echo_response(cls, user_id, response):
        """
        echo back the given message without any consequence
        :param user_id: account holder user id
        :param response: response sring that has to be sent
        :return: void
        """
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
