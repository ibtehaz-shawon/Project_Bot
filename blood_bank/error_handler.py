import binascii

import os

import requests

from blood_bank.models import ErrorLogger
from blood_bank.serializer import LoggerSerializer
from blood_bank.utility import Utility
from bot.settings import DEBUG, REPLY_URL

TAG_ERROR_INSTANCE_NO = 'instanceNumber'
TAG_ERROR_COUNTER = 'errorCounter'
TAG_ERROR_USER_ID = 'fb_user_id'
TAG_USER_ID = 'userID'
TAG_ERROR_MESSAGE = "errorMessage"
TAG_ERROR_CODE = 'errorCode'
TAG_ERROR_SUBCODE = 'errorSubCode'
TAG_ERROR_TYPE = 'errorType'
TAG_ERROR_PLACE = 'errorPlace'

TAG_RECIPIENT = 'recipient'
TAG_ID = 'id'
TAG_MESSAGE = 'message'
TAG_TEXT = 'text'

class ErrorHandler:
    """
    error_logger
    logs every error in the database
    @:parameter error_message, error_code, facebook_user_id, error_subcode, error_type, error_position
    @:returns None
    """

    @classmethod
    # noinspection SpellCheckingInspection
    def error_logger(cls, error_message, facebook_id, error_position, error_code=-1, error_subcode=-1, error_type=-1):
        Utility.print_fucking_stuff("$$$$$$$ Error occurred : " + str(error_message)
                  + " | Error pos : " + str(error_position)
                  + " | for facebook_id : " + str(facebook_id) + " $$$$$$$")

        request_query = ErrorLogger.objects.all()
        error_counter = request_query.count() + 1
        del request_query

        payload = {
            TAG_ERROR_INSTANCE_NO: str((binascii.hexlify(os.urandom(25))).decode("utf-8")),
            TAG_ERROR_COUNTER: error_counter,
            TAG_USER_ID: facebook_id,
            TAG_ERROR_MESSAGE: error_message,
            TAG_ERROR_CODE: error_code,
            TAG_ERROR_SUBCODE: error_subcode,
            TAG_ERROR_TYPE: error_type,
            TAG_ERROR_PLACE: error_position
        }
        serialized_data = LoggerSerializer(data=payload)
        if serialized_data.is_valid():
            serialized_data.save()
            if facebook_id is not None:
                ErrorHandler().__generic_error_reply(facebook_id, Utility.__GENERIC_ERROR_MESSAGE__)
            return 1
        else:
            Utility().print_fucking_stuff("$$$$$$$ error logging error! oh crap! "
                                          + str(serialized_data.error_messages) + " $$$$$$$")
            return -1


    @classmethod
    def __generic_error_reply(cls, user_id, response):
        """
        this function sends a generic error message to the user if there's an error occurred!
        :param user_id: str(facebook_user_id)
        :param response: str(GENERIC ERROR RESPONSE TEXT)
        :return: none
        """
        try:
            if DEBUG:
                print("__generic_error_reply -- > " + str(response))
            payload = {
                TAG_RECIPIENT: {
                    TAG_ID: user_id
                },
                TAG_MESSAGE: {
                    TAG_TEXT: response
                }
            }
            requests.post(REPLY_URL, json=payload)
        except BaseException as error:
            if DEBUG:
                print ("Base exception error occurred inside ->__generic_error_reply --> "+str(error))
