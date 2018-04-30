from __future__ import unicode_literals

from django.http import HttpResponse

from blood_bank.db_handler import insert_queue, error_logger, unique_user_check, user_table_insertion
from blood_bank.message_reply import echo_response

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
                        is_echo(message)
                        return HttpResponse(status=200)
                    elif 'quick_reply' in message['message']:
                        quick_reply(message)
                        return HttpResponse(status=200)
                    else:
                        basic_reply(message)
                        return HttpResponse(status=200)
                elif 'delivery' in message:
                    delivery_result(message)
                    return HttpResponse(status=200)
                elif 'read' in message:
                    message_read(message)
                    return HttpResponse(status=200)
                elif 'postback' in message:
                    postback_response(message)
                    return HttpResponse(status=200)
                else:
                    print("Unknown handler box inside entry['messaging']")
                    unknown_handle(message)
                    return HttpResponse(status=200)
        elif 'standby' in entry:
            standby(str(entry))
            return HttpResponse(status=200)
        else:
            print("Unknown totally box")
            unknown_handle(str(entry))
            return HttpResponse(status=200)
    return HttpResponse(status=200)


"""
is_echo function description here
"""


def is_echo(message_data):
    print("Echo Box")
    return HttpResponse(status=200)


"""
quick_reply function description here
"""


def quick_reply(message_data):
    print("Quick Reply box")
    return HttpResponse(status=200)


"""
unknown message request handler
"""


def unknown_handle(message_data):
    return HttpResponse(status=200)


"""
delivery result handler
"""


def delivery_result(message_data):
    print("Delivery status")
    return HttpResponse(status=200)


"""
message read function definition
"""


def message_read(message_data):
    print("Read box")
    return HttpResponse(status=200)


"""
postback function definition
"""


def postback_response(message_data):
    print("Postback box")
    return HttpResponse(status=200)


"""
standby function definition
"""


def standby(entry):
    print("Standby box")
    return HttpResponse(status=200)


"""
process all normal facebook messages from here
"""


# noinspection PyBroadException
def basic_reply(message_data):
    print("Basic Reply box")
    status = False
    try:
        insert_queue(message_data)  # insert data to database.
        user_id = str(message_data['sender']['id'])
        user_table_insertion(user_id)

        if 'nlp' in message_data['message']:
            # handle nlp data function from here
            status = facebook_nlp(message_data)

        if not status:
            echo_response(user_id, str(message_data['message']['text'].lower()))
        return HttpResponse(status=200)
    except ValueError as error:
        print("Error occurred in basic reply " + str(error))
        error_logger(str(error), user_id, "basic reply")
        return HttpResponse(status=200)
    except BaseException as error:
        print("Broad exception handling "+str(error))
        error_logger("Broad exception handling "+str(error), user_id, "basic reply")
        return HttpResponse(status=200)


"""
This function handles facebook's nlp response and if they are successful they take care from here.
"""


def facebook_nlp(message_data):
    return False


"""
new_user_handler
this table will handle data from echo, quick reply and basic reply and
check if the user_id is already there.
Simple function handler.
"""


@DeprecationWarning
def new_user_handler(user_id):
    if not unique_user_check(user_id):
        user_table_insertion(user_id)
        return True
    else:
        return False
