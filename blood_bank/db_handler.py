import binascii
import os
from time import gmtime, strftime

from django.core.exceptions import ObjectDoesNotExist

from blood_bank.models import UserTable, UserStatus
from blood_bank.serializer import DumpMessageSerializer, LoggerSerializer, UserSerializer, StatusSerializer
from blood_bank.utility import nlp_parser

TAG_TEXT = 'incomingText'
TAG_USER_ID = 'userID'
TAG_TIME = 'recordedTime'
TAG_CONFIDENCE_BYE = 'confidenceBye'
TAG_CONFIDENCE_GREET = 'confidenceGreet'
TAG_CONFIDENCE_THANK = 'confidenceThank'
TAG_CONFIDENCE_LOC = 'confidenceLoc'
TAG_ERROR_MESSAGE = "errorMessage"
TAG_ERROR_CODE = 'errorCode'
TAG_ERROR_SUBCODE = 'errorSubCode'
TAG_ERROR_TYPE = 'errorType'
TAG_ERROR_PLACE = 'errorPlace'
TAG_FB_USERID = 'facebookUserID'
TAG_USER_TABLE_ID = 'userID'
TAG_USER_BLOOD_GRP = 'bloodGroup'
TAG_USER_MOBILE_NUMBER = 'mobileNumber'
TAG_MOBILE_VERIFIED = 'mobileVerified'
TAG_USER_HOME = 'homeCity'
TAG_USER_CURRENT = 'currentCity'
TAG_FRESH_USER = 'freshUser'
TAG_GET_STARTED = 'getStartedStatus'
TAG_DONATION_STATUS = 'donationStatus'
TAG_INFORMATION_STATUS = 'informationStatus'
TAG_DONATION_AVAILABLE_DATE = 'donationAvailDate'

TAG_MESSAGE_TYPE = 'messageType'
TAG_BASIC_TYPE = 'basic_reply'
TAG_QUICK_TYPE = 'quick_reply'
TAG_NLP_TYPE = 'nlp_reply'
TAG_ERROR_INSTANCE_NO = 'instanceNumber'

"""
insert_queue - basically data dumping
message insertion queue in the database
this is vanilla message insertion queue. And It will insert everything 
@:parameter message_data holds the entire JSON Data from messaging parameter
"""


def insert_queue(message_data):
    message_text = message_data['message']['text']
    user_id = message_data['sender']['id']
    bye_val = 0.00
    greet_val = 0.00
    thank_val = 0.00
    loc_val = 0.00

    if 'nlp' in message_data['message']:
        message_type = TAG_NLP_TYPE
    else:
        message_type = TAG_BASIC_TYPE

    if 'bye' in message_data['message']['nlp']['entities']:
        bye_val = nlp_parser(message_data, 'bye')
    if 'thanks' in message_data['message']['nlp']['entities']:
        thank_val = nlp_parser(message_data, 'thanks')
    if 'greetings' in message_data['message']['nlp']['entities']:
        greet_val = nlp_parser(message_data, 'greetings')
    if 'location' in message_data['message']['nlp']['entities']:
        loc_val = nlp_parser(message_data, 'location')

    if len(message_text) > 10000:
        message_text = message_text[0:10000]

    payload = {
        TAG_USER_ID: user_id,
        TAG_TEXT: message_text,
        TAG_TIME: strftime("%Y-%m-%d %H:%M:%S", gmtime()),
        TAG_CONFIDENCE_BYE: bye_val,
        TAG_CONFIDENCE_GREET: greet_val,
        TAG_CONFIDENCE_LOC: loc_val,
        TAG_CONFIDENCE_THANK: thank_val,
        TAG_MESSAGE_TYPE: message_type
    }
    serialized_data = DumpMessageSerializer(data=payload)
    if serialized_data.is_valid():
        serialized_data.save()
        return 1
    else:
        error_message = serialized_data.error_messages()
        error_logger(error_message, user_id, 'insert_queue')
        return -1


"""
error_logger
logs every error in the database
@:parameter error_message, error_code, facebook_user_id, error_subcode, error_type, error_position
@:returns None
"""


# noinspection SpellCheckingInspection
def error_logger(error_message, facebook_id, error_position, error_code=-1, error_subcode=-1, error_type=-1):
    if facebook_id is not None:
        db_user_id = find_actual_user_id(facebook_id)
    else:
        db_user_id = None
    if error_code is None:
        error_code = -1
    if error_subcode is None:
        error_subcode = -1
    if error_type is None:
        error_type = -1

    payload = {
        TAG_ERROR_INSTANCE_NO: str(binascii.hexlify(os.urandom(30))),
        TAG_USER_ID: db_user_id,
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
        print("error logging error! oh crap! " + str(serialized_data.error_messages))
        return -1


"""
unique_user_check
This function will check and return boolean whether user_id is unique in the table or not.
user_id is facebook user id on the table -> UserTable
"""


def unique_user_check(user_id):
    try:
        request_query = UserTable.objects.filter(facebookUserID=user_id)
        if request_query.count() == 0:
            return True
        else:
            return False
    except ObjectDoesNotExist as obj:
        print("error occurred in unique user check")
        error_logger(str(obj), user_id, 'unique_user_check')
        return True


"""
user_table_insertion
This function will create a new user on the user table, based on userID. if the user is new.
"""


def user_table_insertion(user_id):
    if not unique_user_check(user_id):
        return -1
    database_user_id = str(binascii.hexlify(os.urandom(4)))
    payload = {
        TAG_USER_TABLE_ID: database_user_id,
        TAG_FB_USERID: user_id,
    }
    serialized_data = UserSerializer(data=payload)
    if serialized_data.is_valid():
        serialized_data.save()
        create_user_status(fb_user_id=user_id)
        return 1
    else:
        error_message = serialized_data.error_messages()
        error_logger(error_message, user_id, 'user_table_insertion')
        return -1


"""
update_user_table
this function will update the existing users data
@:caution this function can ONLY be used for existing user {CAUTION}
"""


def update_user_table(user_id, blood_group, mobile_number, mobile_verify, home, current_loc):
    if unique_user_check(user_id):
        request_query = get_user_table_object(fb_user_id=user_id)
        if request_query is None:
            if blood_group is not None:
                request_query.bloodGroup = blood_group
            if mobile_number is not None:
                request_query.mobileNumber = mobile_number
            if mobile_verify is not None:
                request_query.mobileVerified = mobile_verify
            if home is not None:
                request_query.homeCity = home
            if current_loc is not None:
                request_query.currentCity = current_loc
            request_query.save()
            return 1
        else:
            error_logger(error_message='request_query came NONE', facebook_id=user_id,
                         error_position='update_user_table')
            return 0
    else:
        error_logger(error_message='USER DOES NOT EXIST', facebook_id=user_id,
                     error_position='update_user_table')
        return -1


"""
find_actual_user_id
this function will return the actual user id of a user in the database from the facebook id.
"""


def find_actual_user_id(fb_user_id):
    request_query = get_user_table_object(fb_user_id=fb_user_id)
    if request_query is None:
        print("request_query came NONE")
        error_logger('request_query came NONE', None, 'find_actual_user_id')
        return None
    else:
        return request_query.userID


"""
check_user_status
this function will check users current status from USERSTATUS based on UserID (which is actual USER ID)
@:param is FB_USER_ID, which will fetch the actual USER ID from USER TABLE
@:return 100 for new user, 101 for missing information, 102 for information complete.
"""


def check_user_status(fb_user_id):
    user_id = find_actual_user_id(fb_user_id)

    if user_id is None:
        error_logger(error_message="USER_ID is NONE in DB for " + str(fb_user_id), facebook_id=fb_user_id,
                     error_position="check_user_status - db_handler")
        return -1
    else:
        request_query = get_user_status_object(fb_user_id=fb_user_id)
        if request_query is None:
            error_logger(error_message="request_query came NONE", facebook_id=fb_user_id,
                         error_position="check_user_status - db_handler")
            return -1
        else:
            if request_query.freshUser is True:
                return 100  # user is new. Take all the necessary information needed from the table. User not given
                # anything yet.
            else:
                if request_query.getStartedStatus is True and request_query.informationStatus is False:
                    return 101  # user is not new. Bt There are missing information on the table abt this user. Ask
                    # those.
                else:
                    if request_query.informationStatus is True:
                        return 102  # user will be able to donate blood nw. All information complete.


"""
create_user_status
this function will automatically creates a new entry for each new user, in UserTable in UserStatus table.
"""


def create_user_status(fb_user_id):
    user_id = find_actual_user_id(fb_user_id)
    if user_id is not None:
        payload = {
            TAG_USER_ID: user_id,
            TAG_FRESH_USER: True,
        }
        serialized_data = StatusSerializer(data=payload)
        if serialized_data.is_valid():
            serialized_data.save()
            print("New User Status Object Created!")
            return 1
        else:
            # Error occurred!
            error_message = serialized_data.error_messages()
            print("Error occurred creating new User Status " + str(error_message))
            error_logger(error_message, fb_user_id, 'create_user_status')
            return -1
    else:
        return -1


"""
user_status_info
Checks user's status from UserTable and UserStatus Table. sends the information required to complete users information
@:param fb_user_id, user_status_code
@:return
"""


def user_status_info(fb_user_id, user_status_code):
    user_id = find_actual_user_id(fb_user_id)

    if user_id is None:
        error_logger(error_message="USER_ID is NONE in DB for " + str(fb_user_id), facebook_id=fb_user_id,
                     error_position="user_status_info - db_handler")
        return -1
    else:
        request_query = get_user_table_object(fb_user_id=fb_user_id)

        if request_query is None:
            return -1
        else:
            if user_status_code == 100:
                #  user is fresh. Check the necessary information list from UserTable
                return 10
            elif user_status_code == 101:
                return 11
            elif user_status_code == 102:
                return 12
        return 0


"""
get_user_status_object
this receives the fb_user_id and returns the user_Status_object query as the result.
@:parameter fb_user_id
@:returns User_Status request query object | None
"""


def get_user_status_object(fb_user_id):
    user_id = find_actual_user_id(fb_user_id)

    if user_id is None:
        error_logger(error_message="USER_ID is NONE in DB for " + str(fb_user_id), facebook_id=fb_user_id,
                     error_position="check_user_status - db_handler")
        return None
    else:
        try:
            request_query = UserStatus.objects.get(userID=user_id)
            return request_query
        except ObjectDoesNotExist as obj:
            print("ObjectDoesNotExist occurred in find_actual_user_id " + str(obj))
            error_logger(str(obj), fb_user_id, 'find_actual_user_id')
            return None
        except AttributeError as attr:
            print("AttributeError occurred in find_actual_user_id " + str(attr))
            error_logger(str(attr), fb_user_id, 'find_actual_user_id')
            return None
        except TypeError as terr:
            print("TypeError occurred in find_actual_user_id " + str(terr))
            error_logger(str(terr), fb_user_id, 'find_actual_user_id')
            return None


"""
get_user_table_object
this function returns the request query object for user_table information request
@:parameter fb_user_id
@:returns request query
"""


def get_user_table_object(fb_user_id):
    try:
        request_query = UserTable.objects.get(facebookUserID=fb_user_id)
        return request_query
    except ObjectDoesNotExist as obj:
        print("ObjectDoesNotExist occurred in find_actual_user_id " + str(obj))
        error_logger(str(obj), None, 'get_user_table_object')
        return None
    except AttributeError as attr:
        print("AttributeError occurred in find_actual_user_id " + str(attr))
        error_logger(str(attr), None, 'get_user_table_object')
        return None
    except TypeError as terr:
        print("TypeError occurred in find_actual_user_id " + str(terr))
        user_table_insertion(100)
        error_logger(str(terr), None, 'get_user_table_object')
        return None
