import binascii

import os

from blood_bank.models import ErrorLogger
from blood_bank.serializer import LoggerSerializer
from bot.settings import DEBUG


TAG_ERROR_INSTANCE_NO = 'instanceNumber'
TAG_ERROR_COUNTER = 'errorCounter'
TAG_ERROR_USER_ID = 'fb_user_id'
TAG_USER_ID = 'userID'
TAG_ERROR_MESSAGE = "errorMessage"
TAG_ERROR_CODE = 'errorCode'
TAG_ERROR_SUBCODE = 'errorSubCode'
TAG_ERROR_TYPE = 'errorType'
TAG_ERROR_PLACE = 'errorPlace'

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
        if DEBUG:  # This message will only print if the debug is TRUE
            print("$$$$$$$ Error occurred : " + str(error_message)
                  + " | Error pos : " + str(error_position)
                  + " | for facebook_id : " + str(facebook_id) + " $$$$$$$")

        request_query = ErrorLogger.objects.all()
        error_counter = request_query.count() + 1
        del request_query

        if error_code is None:
            error_code = -1
        if error_subcode is None:
            error_subcode = -1
        if error_type is None:
            error_type = -1

        payload = {
            TAG_ERROR_INSTANCE_NO: str(binascii.hexlify(os.urandom(25))),
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
            return 1
        else:
            if DEBUG:
                print("$$$$$$$ error logging error! oh crap! "
                      + str(serialized_data.error_messages) + " $$$$$$$")
            return -1
