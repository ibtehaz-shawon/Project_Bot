from __future__ import unicode_literals

from django.http import HttpResponse

from blood_bank.db_handler import error_logger, unique_user_check, user_table_insertion
from blood_bank.message_reply import MessageReply
from bot.settings import DEBUG

"""
:argument incoming_message contains the incoming message data from facebook.
this function sends the parsing request to appropriate function
"""


def facebook_message(incoming_message):
    for entry in incoming_message['entry']:
        if 'messaging' in entry:
            for message in entry['messaging']:
                if 'message' in message:
                    if 'is_echo' in message['message']:
                        Parser().is_echo(message)
                        return HttpResponse(status=200)
                    elif 'quick_reply' in message['message']:
                        Parser().quick_reply(message)
                        return HttpResponse(status=200)
                    else:
                        Parser().basic_reply(message)
                        return HttpResponse(status=200)
                elif 'delivery' in message:
                    Parser().delivery_result(message)
                    return HttpResponse(status=200)
                elif 'read' in message:
                    Parser().message_read(message)
                    return HttpResponse(status=200)
                elif 'postback' in message:
                    Parser().postback_response(message)
                    return HttpResponse(status=200)
                else:
                    Parser().print_fucking_stuff("Unknown handler box inside entry['messaging']")
                    Parser().unknown_handle(message)
                    return HttpResponse(status=200)
        elif 'standby' in entry:
            Parser().standby(str(entry))
            return HttpResponse(status=200)
        else:
            Parser().print_fucking_stuff("Unknown totally box")
            Parser().unknown_handle(str(entry))
            return HttpResponse(status=200)
    return HttpResponse(status=200)


# -----------------------------------------------------------
# -----------------------------------------------------------
# -----------------------------------------------------------
# -----------------------------------------------------------
# -----------------------------------------------------------
class Parser:
    """
    is_echo function description here
    """

    @classmethod
    def is_echo(cls, message_data):
        print("Echo Box")
        return HttpResponse(status=200)

    """
    quick_reply function description here
    """

    @classmethod
    def quick_reply(cls, message_data):
        print("Quick Reply box")
        return HttpResponse(status=200)

    """
    unknown message request handler
    """

    @classmethod
    def unknown_handle(cls, message_data):
        error_logger(str(message_data), None, "JSON_Parser_Class -> Unknown_handle()")
        return HttpResponse(status=200)

    """
    delivery result handler
    """

    @classmethod
    def delivery_result(cls, message_data):
        # Do nothing function
        return HttpResponse(status=200)

    """
    message read function definition
    """

    @classmethod
    def message_read(cls, message_data):
        # Do nothing function
        return HttpResponse(status=200)

    """
    postback function definition
    """

    @classmethod
    def postback_response(cls, message_data):
        print("Postback box")
        return HttpResponse(status=200)

    """
    standby function definition
    """

    @classmethod
    def standby(cls, entry):
        print("Standby box")
        return HttpResponse(status=200)

    """
    process all normal facebook messages from here
    """

    @classmethod
    # noinspection PyBroadException
    def basic_reply(cls, message_data):
        print("Basic Reply box")
        status = False
        user_id = None
        try:
            # insert_queue(message_data)  # insert data to database.
            user_id = str(message_data['sender']['id'])
            user_table_insertion(user_id)

            if 'nlp' in message_data['message']:
                # handle nlp data function from here
                # TODO -> Status is always false here people.
                status = Parser().facebook_nlp(user_id, message_data['message'])

            if not status:
                MessageReply().echo_response(user_id, str(message_data['message']['text']).lower())
            return HttpResponse(status=200)
        except ValueError as error:
            Parser().print_fucking_stuff("Error occurred in basic reply "
                                         + str(error) + "\n" + "message data --> " + str(message_data))
            error_logger(str(error), user_id, "basic reply")
            return HttpResponse(status=200)
        except BaseException as error:
            Parser().print_fucking_stuff("Broad exception handling (basic reply) "
                                         + str(error) + "\n" + "message data --> " + str(message_data))
            error_logger("Broad exception handling " + str(error), user_id, "basic reply")
            return HttpResponse(status=200)

    """
    This function handles facebook's nlp response and if they are successful they take care from here.
    """

    @classmethod
    def facebook_nlp(cls, user_id, message_data):
        print("Facebook's NLP box")

        try:
            byeVal = str(message_data["nlp"]['entities']['bye'][0]['confidence'])
            thanksVal = ""
            greetingsVal = ""
            locationVal = ""

            print ("Bye value is --> "+byeVal)
        except ValueError as error:
            Parser().print_fucking_stuff(str(error) + " Inside facebook_nlp")
            error_logger(str(error), user_id, "facebook_nlp")
        except BaseException as error:
            Parser().print_fucking_stuff(str(error) + " Inside facebook_nlp")
            error_logger(str(error), user_id, "facebook_nlp")

        # {'entities': {'location': [
        #     {'suggested': True, 'confidence': 0.83492, 'value': 'ilkhlkhlk', 'type': 'value', '_entity': 'location',
        #      '_body': 'ilkhlkhlk', '_start': 0, '_end': 9}],
        #               'bye': [{'confidence': 0.04040062643157, 'value': 'true', '_entity': 'bye'}],
        #               'thanks': [{'confidence': 0.013509658888707, 'value': 'true', '_entity': 'thanks'}],
        #               'greetings': [{'confidence': 0.3768811814592, 'value': 'true', '_entity': 'greetings'}]}}
        return False

    """
    new_user_handler
    this table will handle data from echo, quick reply and basic reply and
    check if the user_id is already there.
    Simple function handler.
    """

    @classmethod
    @DeprecationWarning
    def new_user_handler(cls, user_id):
        if not unique_user_check(user_id):
            user_table_insertion(user_id)
            return True
        else:
            return False

    @classmethod
    def print_fucking_stuff(cls, message):
        if DEBUG:
            print(message)
