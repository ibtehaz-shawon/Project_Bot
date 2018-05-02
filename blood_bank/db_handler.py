import binascii
import os
from time import gmtime, strftime

from django.core.exceptions import ObjectDoesNotExist

from blood_bank.models import UserTable, UserStatus, ErrorLogger
from blood_bank.serializer import DumpMessageSerializer, LoggerSerializer, UserSerializer, StatusSerializer
from blood_bank.utility import nlp_parser
from bot.settings import DEBUG

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
TAG_ERROR_COUNTER = 'errorCounter'
TAG_ERROR_USER_ID = 'fb_user_id'


"""
DB_Hanlder class inserts objects inside database.
"""
class DB_HANDLER(object):

    @classmethod
    def insert_queue(cls, message_data):
        """
        insert_queue - basically data dumping
        message insertion queue in the database
        this is vanilla message insertion queue. And It will insert everything
        @:parameter message_data holds the entire JSON Data from messaging parameter
        """
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
    unique_user_check
    This function will check and return boolean whether user_id is unique in the table or not.
    user_id is facebook user id on the table -> UserTable
    """

    @classmethod
    def unique_user_check(cls, fb_user_id):
        print ("unique_user_check "+str(fb_user_id))
        try:
            request_query = UserTable.objects.filter(facebookUserID=fb_user_id)
            if request_query.count() == 0:
                print("user id " + str(fb_user_id) + " is unique")
                return True
            else:
                print("user id " + str(fb_user_id) + " is [NOT] unique")
                return False
        except ObjectDoesNotExist as obj:
            error_logger(str(obj), fb_user_id, 'unique_user_check')
            return True

    """
    user_table_insertion
    This function will create a new user on the user table, based on userID. if the user is new.
    """

    @classmethod
    def user_table_insertion(cls, fb_user_id):
        try:
            print ("user_table_insertion "+str(fb_user_id))
            if not DB_HANDLER().unique_user_check(fb_user_id):
                return -2 ## user is old.
            db_id = str(binascii.hexlify(os.urandom(14)))
            print ("user_table_insertion where db id is -- > "+str(db_id))
            payload = {
                TAG_USER_TABLE_ID: db_id,
                TAG_FB_USERID: fb_user_id,
            }
            print ("user_table_insertion where payload -- > "+str(payload))

            serialized_data = UserSerializer(data=payload)
            if serialized_data.is_valid():
                print ("---------------------------------------------------------------------")
                serialized_data.save()
                print (" ----------------- successful user_table_insertion ------------------")
                # DB_HANDLER().create_user_status(fb_user_id=fb_user_id)
                return 1 ## http 200
            else:
                error_message = serialized_data.error_messages()
                print ("error occurred inside user_table_insertion --> "+str(error_message))
                error_logger(error_message, fb_user_id, 'user_table_insertion')
                return -1 ## error with database insertion.
        except ObjectDoesNotExist as obj:
            error_logger("Exception :-> " + str(obj), fb_user_id, "user_table_insertion")
        except BaseException as bsc:
            error_logger("Base Exception :-> " + str(bsc), fb_user_id, "user_table_insertion")

    """
    update_user_table
    this function will update the existing users data
    @:caution this function can ONLY be used for existing user {CAUTION}
    """
    @classmethod
    def update_user_table(cls, user_id, blood_group=None, mobile_number=None,
                          mobile_verify=None, home=None, current_loc=None):
        if DB_HANDLER().unique_user_check(user_id):
            request_query = DB_HANDLER().get_user_table_object(fb_user_id=user_id)
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

    @classmethod
    def find_actual_user_id(cls, fb_user_id):
        try:
            print ("find_actual_user_id "+str(fb_user_id))
            request_query = UserTable.objects.filter(facebookUserID=fb_user_id)
            if request_query is None:
                error_logger('request_query came NONE', fb_user_id, 'find_actual_user_id')
                return None
            else:
                print ("request query counter --?> "+str(request_query.count()) + " and type "+ type(request_query))
                if request_query.count() > 0:
                    return request_query[0].userID
                else:
                    return None
        except ObjectDoesNotExist as obj:
            error_logger("Exception :-> " + str(obj), fb_user_id, "find_actual_user_id")
            return None

    """
    check_user_status
    this function will check users current status from USERSTATUS based on UserID (which is actual USER ID)
    @:param is FB_USER_ID, which will fetch the actual USER ID from USER TABLE
    @:return 100 for new user, 101 for missing information, 102 for information complete.
    """

    @classmethod
    def check_user_status(cls, fb_user_id):
        print ("check_user_Status")
        """
        :param fb_user_id:
        :return: Integer (error = -1), success (100, 101, 102)
        """
        user_id = DB_HANDLER().find_actual_user_id(fb_user_id)

        if user_id is None:
            error_logger(error_message="USER_ID is NONE in DB for " + str(fb_user_id), facebook_id=fb_user_id,
                         error_position="check_user_status - db_handler")
            return -1
        else:
            request_query = DB_HANDLER().get_user_status_object(fb_user_id=fb_user_id)
            print ("check_user_status --> "+str(request_query)
                   + " length is "  + str(len(request_query)))
            if request_query is None:
                error_logger(error_message="request_query came NONE", facebook_id=fb_user_id,
                             error_position="check_user_status - db_handler")
                return -1
            elif request_query.count() > 0:
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
            else:
                error_logger("no user status object for " +str(fb_user_id), fb_user_id, "check_user_status")
                return -2 ## no user status object

    """
    create_user_status
    this function will automatically creates a new entry for each new user, in UserTable in UserStatus table.
    """

    @classmethod
    def create_user_status(cls, fb_user_id):
        try:
            print ("create user status")
            user_id = DB_HANDLER().find_actual_user_id(fb_user_id)
            if user_id is not None:
                print ("create user status --> user id "+str(user_id) + " when fb_id --> "+str(fb_user_id))
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
                    error_logger(str(error_message), fb_user_id, 'create_user_status')
                    return -1
            else:
                error_logger("user id came none from db for "+str(fb_user_id), fb_user_id, "create_user_Status")
                return -2 ## user id came none
        except ObjectDoesNotExist as obj:
            error_logger("Exception :-> " + str(obj), fb_user_id, "create_user_status")
        except BaseException as bsc:
            error_logger("BaseException :-> " + str(bsc), fb_user_id, "create_user_status")

    """
    user_status_info
    Checks user's status from UserTable and UserStatus Table. sends the information required to complete users information
    @:param fb_user_id, user_status_code
    @:return
    """

    @classmethod
    def user_status_info(cls, fb_user_id, user_status_code):
        user_id = DB_HANDLER().find_actual_user_id(fb_user_id)

        if user_id is None:
            error_logger(error_message="USER_ID is NONE in DB for " + str(fb_user_id), facebook_id=fb_user_id,
                         error_position="user_status_info - db_handler")
            return -1
        else:
            request_query = DB_HANDLER().get_user_status_object(fb_user_id=fb_user_id)
            del request_query
            return -100 ##TODO not implemented yet
            # if request_query is None:
            #     return -1
            # else:
            #     if user_status_code == 100:
            #         #  user is fresh. Check the necessary information list from UserTable
            #         return 10
            #     elif user_status_code == 101:
            #         return 11
            #     elif user_status_code == 102:
            #         return 12
            # return 0

    """
    get_user_status_object
    this receives the fb_user_id and returns the user_Status_object query as the result.
    @:parameter fb_user_id
    @:returns User_Status request query object | None
    """

    @classmethod
    def get_user_status_object(cls, fb_user_id):
        print ("get_user_status_object")
        try:
            request_query = UserStatus.objects.filter(facebookUserID=fb_user_id)
            if request_query.count() > 0:
                return request_query[0]
            else:
                print("Request query is none get_user_status_object "+str(fb_user_id))
                error_logger("Request query is none", fb_user_id, 'get_user_status_object')
                return None
        except ObjectDoesNotExist as obj:
            print("ObjectDoesNotExist occurred in get_user_status_object " + str(obj))
            error_logger(str(obj), fb_user_id, 'get_user_status_object')
            return None
        except AttributeError as attr:
            print("AttributeError occurred in get_user_status_object " + str(attr))
            error_logger(str(attr), fb_user_id, 'get_user_status_object')
            return None
        except TypeError as terr:
            print("TypeError occurred in get_user_status_object " + str(terr))
            error_logger(str(terr), fb_user_id, 'get_user_status_object')
            return None


    """
    get_user_table_object
    this function returns the request query object for user_table information request
    @:parameter fb_user_id
    @:returns request query
    """

    @classmethod
    def get_user_table_object(cls, fb_user_id):
        print ("get_user_table_object")
        try:
            if fb_user_id is not None:
                request_query = UserTable.objects.filter(facebookUserID=fb_user_id)
                if request_query.count() > 0:
                    return request_query[0]
                else:
                    error_logger("request_query came [NONE]", fb_user_id, 'get_user_table_object')
                    return None
            else:
                error_logger("fb_user_id came [NONE]", fb_user_id, 'get_user_table_object')
                return None
        except ObjectDoesNotExist as obj:
            error_logger(str(obj), fb_user_id, 'get_user_table_object')
            return None
        except AttributeError as attr:
            error_logger(str(attr), fb_user_id, 'get_user_table_object')
            return None
        except TypeError as terr:
            error_logger(str(terr), fb_user_id, 'get_user_table_object')
            return None


"""
error_logger
logs every error in the database
@:parameter error_message, error_code, facebook_user_id, error_subcode, error_type, error_position
@:returns None
"""


# noinspection SpellCheckingInspection
def error_logger(error_message, facebook_id, error_position, error_code=-1, error_subcode=-1, error_type=-1):
    if DEBUG: # This message will only print if the debug is TRUE
        print("$$$$$$$ Error occurred : " + str(error_message)
              + " | Error pos : "+str(error_position)
              + " | for facebook_id : "+ str(facebook_id) + " $$$$$$$")

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
        TAG_ERROR_INSTANCE_NO: str(binascii.hexlify(os.urandom(30))),
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
                  + str(serialized_data.error_messages) +" $$$$$$$")
        return -1
