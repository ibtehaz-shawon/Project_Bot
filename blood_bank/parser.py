from __future__ import unicode_literals

from django.http import HttpResponse

from blood_bank.db_handler import error_logger, user_table_insertion
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
            return_val = user_table_insertion(user_id)

            if return_val == -1:
                # TODO: error occurred in user table insertion checking. might need to kill the script for this user
                pass

            if 'nlp' in message_data['message']:
                # handle nlp data function from here
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
        """
        checks and parse facebook's nlp data, if more than 0.85 (except Location) it handles it here.
        :param user_id: account holder user id.
        :param message_data: nlp message data.
        :return: boolean
        """
        print("Facebook's NLP box")
        status_bye = status_greet = status_thank = status_loc = False
        message_reply = MessageReply()
        try:
            bye_val = float(message_data["nlp"]['entities']['bye'][0]['confidence'])
            thanks_val = float(message_data["nlp"]['entities']['thanks'][0]['confidence'])
            greetings_val = float(message_data["nlp"]['entities']['greetings'][0]['confidence'])
            location_val = float(message_data["nlp"]['entities']['location'][0]['confidence'])

            if bye_val > thanks_val and bye_val > greetings_val and bye_val > location_val:
                if bye_val >= 0.85:
                    status_bye = True
                    ## Bye will cut all running processing for this user for a while.
                    message_reply.echo_response(user_id, "Bye")
            elif thanks_val > bye_val and  thanks_val > greetings_val and thanks_val > location_val:
                if thanks_val >= 0.85:
                    status_thank = True
                    ## Thanks will do nothing.
                    message_reply.echo_response(user_id, "Thanks")
            elif greetings_val > bye_val and greetings_val > thanks_val and greetings_val > location_val:
                if greetings_val >= 0.85:
                    status_greet = True
                    ##TODO: Start work here.
                    message_reply.echo_response(user_id, "Hello :)")
            else:
                pass
        except ValueError as error:
            Parser().print_fucking_stuff(str(error) + " Inside facebook_nlp")
            error_logger(str(error), user_id, "facebook_nlp")
        except BaseException as error:
            Parser().print_fucking_stuff(str(error) + " Inside facebook_nlp")
            error_logger(str(error), user_id, "facebook_nlp")
        finally:
            if status_bye or status_thank or status_greet:
                return True
            else:
                return False

    @classmethod
    def print_fucking_stuff(cls, message):
        if DEBUG:
            print(message)
