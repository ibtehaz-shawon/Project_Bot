from __future__ import unicode_literals

import requests
import time

from blood_bank.error_handler import ErrorHandler
from blood_bank.utility import Utility
from bot.settings import REPLY_URL

TAG_RECIPIENT = 'recipient'
TAG_ID = 'id'
TAG_MESSAGE = 'message'
TAG_TEXT = 'text'
TAG_QUICK_REPLIES = 'quick_replies'
TAG_CONTENT_TYPE_TEXT = 'content_type'
TAG_TITLE = 'title'
TAG_PAYLOAD = 'payload'
TAG_IMAGE_URL = 'image_url'
TAG_SENDER_ACTION = 'sender_action'
TAG_TYPING_ON = 'typing_on'

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
        try:
            Utility().print_fucking_stuff ("echo_response()-- > "+str(response))
            if MessageReply().__typing_on(user_id) != 0:
                ## On success, it will return 0.
                Utility().print_fucking_stuff("An error occurred inside __typing_on!")
                return

            payload = {
                TAG_RECIPIENT: {
                    TAG_ID: user_id
                },
                TAG_MESSAGE: {
                    TAG_TEXT: response
                }
            }
            status = requests.post(REPLY_URL, json=payload)

            if status.status_code == 200:
                Utility().print_fucking_stuff("------------------------------\n"
                                          + str(status)
                                          +"\n-------------------------------")
            else:
                ErrorHandler().error_logger("status code "+str(status.status_code)+ " , payload is "
                                                                                    "" + str(payload),
                                            user_id, "echo_response - Message Reply")
        except BaseException as error:
            ErrorHandler().error_logger("Base exception : "+str(error), user_id, "echo_response - Message Reply")

    @classmethod
    def quick_reply_text(cls, user_id, response_text, choices, postbacks):
        """
        general function to handle quick reply in text format.
        :param user_id: str
        :param response_text: str
        :param choices: list
        :param postbacks: list
        :return:
        """
        try:
            Utility().print_fucking_stuff("quick_reply_text -- > " + str(response_text))
            if MessageReply().__typing_on(user_id) != 0:
                ## On success, it will return 0.
                Utility().print_fucking_stuff("An error occurred inside __typing_on!")
                return
            quick_replies = []
            for i in range(0, 2):
                payload = {TAG_CONTENT_TYPE_TEXT: 'text', TAG_TITLE: choices[i], TAG_PAYLOAD: postbacks[i]}
                quick_replies.append(payload)

            response_payload = MessageReply().__create_basic_recipient(user_id)
            message = {TAG_TEXT: str(response_text), TAG_QUICK_REPLIES: quick_replies}
            response_payload[TAG_MESSAGE] = message

            status = requests.post(REPLY_URL, json=response_payload)

            if status.status_code == 200:
                Utility().print_fucking_stuff("------------------------------\n"
                                              + str(status)
                                              + "\n-------------------------------")
            else:
                ErrorHandler().error_logger("status code " + str(status.status_code) + " , payload is "
                                                                                       "" + str(response_payload),
                                            user_id, "quick_reply_text - Message Reply")
        except BaseException as error:
            ErrorHandler().error_logger("Base exception : " + str(error), user_id, "quick_reply_text - Message Reply")

    @classmethod
    def __create_basic_recipient(cls, user_id):
        """

        :param user_id:
        :return: creates a dictionary containing recipient key-value.
        """
        recipient = {TAG_ID: user_id}
        payload = {TAG_RECIPIENT: recipient}
        return payload


    @classmethod
    def __typing_on(cls, user_id):
        """
        private function, turns on typing function, sleep 3s before doing anything else.
        :param user_id:
        :return:
        """
        try:
            payload = MessageReply().__create_basic_recipient(user_id)
            payload[TAG_SENDER_ACTION] = TAG_TYPING_ON
            status = requests.post(REPLY_URL, json=payload)

            if status.status_code == 200:
                Utility().print_fucking_stuff("------------------------------\n"
                                              + str(status)
                                              + "\n-------------------------------")
                time.sleep(1.5)
                return 0
            else:
                ErrorHandler().error_logger("status code " + str(status.status_code) + " , payload is "
                                                                                       "" + str(payload),
                                            user_id, "echo_response - Message Reply")
                return -1
        except BaseException as error:
            ErrorHandler().error_logger("Base exception : " + str(error), user_id, "typing_on - Message Reply")
            return -1