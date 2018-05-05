from __future__ import unicode_literals

from django.http import HttpResponse

from blood_bank.db_handler import DB_HANDLER
from blood_bank.error_handler import ErrorHandler
from blood_bank.message_reply import MessageReply
from blood_bank.utility import Utility

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
                    Utility().print_fucking_stuff("Unknown handler box inside entry['messaging']")
                    Parser().unknown_handle(message)
                    return HttpResponse(status=200)
        elif 'standby' in entry:
            Parser().standby(str(entry))
            return HttpResponse(status=200)
        else:
            Utility().print_fucking_stuff("Unknown totally box")
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
        Utility.print_fucking_stuff("Echo Box")
        return HttpResponse(status=200)

    """
    quick_reply function description here
    """

    @classmethod
    def quick_reply(cls, message_data):
        Utility.print_fucking_stuff("Quick Reply box "+str(message_data))
        db_hanlder = DB_HANDLER()
        try:
            user_id = Parser.__parse_user_id(message_data)
            if user_id is None:
                Utility.print_fucking_stuff("USER_ID came NONE. Parsing Error occurred! Parser.QUICK_REPLY")
                return HttpResponse(status=200)

            if db_hanlder.unique_user_check(user_id):
                return_val = db_hanlder.user_table_insertion(user_id)
                Utility.print_fucking_stuff("return_value user table insertion "+str(return_val))

            if 'payload' in message_data['message']['quick_reply']:
                status = Utility.check_quick_reply_keys(str(message_data['message']['quick_reply']['payload']))
                if status == 1:
                    # donor
                    Parser.quick_reply_donate(user_id)
                elif status == 2:
                    ## emergency
                    Parser.quick_reply_emergency_blood(user_id)

            ## NOTHING TO Parse anymore.
        except ValueError as error:
            ErrorHandler.error_logger("Error: "+str(error), user_id, "quick_reply")
        except BaseException as error:
            ErrorHandler.error_logger("Base exception Error: "+str(error), user_id, "quick_reply")
        finally:
            return HttpResponse(status=200)

    """
    unknown message request handler
    """

    @classmethod
    def unknown_handle(cls, message_data):
        ErrorHandler().error_logger(str(message_data), None, "JSON_Parser_Class -> Unknown_handle()")
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
        Utility.print_fucking_stuff("Postback box")
        return HttpResponse(status=200)

    """
    standby function definition
    """

    @classmethod
    def standby(cls, entry):
        Utility.print_fucking_stuff("Standby box")
        return HttpResponse(status=200)

    """
    process all normal facebook messages from here
    """

    @classmethod
    # noinspection PyBroadException
    def basic_reply(cls, message_data):
        Utility.print_fucking_stuff("Basic Reply box")
        db_handler = DB_HANDLER()
        user_id = None
        try:
            # insert_queue(message_data)  # insert data to database.
            user_id = str(message_data['sender']['id'])
            return_val = db_handler.user_table_insertion(user_id)

            if return_val < 0:
                # An error occurred during user table insertion. System exit.
                return HttpResponse(status=200)
            else:
                ## all good. returnVal came 1.
                ### Find the user's current status here.
                user_status = db_handler.check_user_status(user_id)
                if user_status is None:
                    Utility.print_fucking_stuff ("user status came null")
                    ErrorHandler.error_logger("user status is none, closing service!",
                                              user_id, "basic_reply_if user_status is None:")
                    return HttpResponse(status=200)

            if 'text' not in message_data['message']:
                ## unknown type came like attachment
                ErrorHandler().error_logger("text not available --> "+str(message_data),
                             user_id, "basic_reply")
                return HttpResponse(status=200)

            if 'nlp' in message_data['message']:
                # handle nlp data function from here
                status = Parser().facebook_nlp(user_id, message_data['message'])
            else:
                status = [False, 0]

            if user_status is not None:
                if user_status == 100 and status[1] == 100:
                    MessageReply.quick_reply_text(user_id, Utility.__INTRO_MESSAGE_QUICK_REPLY_FRESH__,
                                                  [Utility.__INTRO_OPTION_DONOR_QUICK_REPLY_FRESH__,
                                                   Utility.__INTRO_OPTION_PATIENT_QUICK_REPLY_FRESH__],
                                                  Utility.get_postback_keys_fresh())
                    return HttpResponse(status=200)
                print("Current user id --> " + str(user_id) + " result is --> " + str(user_status))

            # TODO --------------------------------------------------------------
            # TODO --------------------------------------------------------------
            # TODO -> this echo back reply is not necessary on future references.
            # TODO --------------------------------------------------------------
            # TODO --------------------------------------------------------------
            if not status[0]:
                ## Parse message for location, blood group and emergency blood needed from here
                MessageReply().echo_response(user_id, str(message_data['message']['text']).lower())
            return HttpResponse(status=200)
        except ValueError as error:
            Utility().print_fucking_stuff("Error occurred in basic reply "
                                         + str(error) + "\n" + "message data --> " + str(message_data))
            ErrorHandler().error_logger(str(error), user_id, "basic reply")
            return HttpResponse(status=200)
        except BaseException as error:
            Utility().print_fucking_stuff("Broad exception handling (basic reply) "
                                         + str(error) + "\n" + "message data --> " + str(message_data))
            ErrorHandler().error_logger("Broad exception handling " + str(error), user_id, "basic reply")
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
        Utility.print_fucking_stuff("Facebook's NLP box")
        status_bye = status_greet = status_thank = status_loc = False
        payload = [False, 0]
        message_reply = MessageReply()
        try:
            if 'bye' in message_data["nlp"]['entities']:
                bye_val = float(message_data["nlp"]['entities']['bye'][0]['confidence'])
            else:
                bye_val = 0.0

            if 'thanks' in message_data["nlp"]['entities']:
                thanks_val = float(message_data["nlp"]['entities']['thanks'][0]['confidence'])
            else:
                thanks_val = 0.0

            if 'greetings' in message_data["nlp"]['entities']:
                greetings_val = float(message_data["nlp"]['entities']['greetings'][0]['confidence'])
            else:
                greetings_val = 0.0

            if 'location' in message_data["nlp"]['entities']:
                location_val = float(message_data["nlp"]['entities']['location'][0]['confidence'])
            else:
                location_val = 0.0

            if bye_val > thanks_val and bye_val > greetings_val and bye_val > location_val:
                if bye_val >= 0.85:
                    status_bye = True
                    ## Bye will cut all running processing for this user for a while.
                    message_reply.echo_response(user_id, "Bye :)")
                    payload[0] = status_bye
                    payload[1] = 101
            elif thanks_val > bye_val and  thanks_val > greetings_val and thanks_val > location_val:
                if thanks_val >= 0.85:
                    status_thank = True
                    ## Thanks will do nothing.
                    message_reply.echo_response(user_id, "Thanks :)")
                    payload[0] = status_thank
                    payload[1] = 102
            elif greetings_val > bye_val and greetings_val > thanks_val and greetings_val > location_val:
                if greetings_val >= 0.85:
                    status_greet = True
                    ##TODO: Start work here.
                    message_reply.echo_response(user_id, "Hello :)")
                    payload[0] = status_greet
                    payload[1] = 100
            else:
                pass ## passing on location for now.
        except ValueError as error:
            Utility().print_fucking_stuff(str(error) + " Inside facebook_nlp")
            ErrorHandler().error_logger(str(error), user_id, "facebook_nlp")
        except BaseException as error:
            Utility().print_fucking_stuff(str(error) + " Inside facebook_nlp")
            ErrorHandler().error_logger(str(error), user_id, "facebook_nlp")
        finally:
            return payload


    """
    This handles all the necessary information required for create donate identity.
    """
    @classmethod
    def quick_reply_donate(cls, user_id):
        ## check user status and unique user first
        ## find missing information
        ## ask those.
        Utility.print_fucking_stuff("QUICK_REPLY_DONATE "+str(user_id))

        message_reply = MessageReply
        db_handler = DB_HANDLER

        message_reply.echo_response(user_id, "Great :)")
        user_status = db_handler.check_user_status(user_id)
        if user_status < 0:
            return HttpResponse(status=200)
        del user_status
        ## user is either fresh or have some missing information.
        missing_information_status = db_handler.check_user_information(user_id)

        ## find the missing information
        if missing_information_status == 100:
            #missing blood group
            MessageReply.echo_response(user_id, "Blood group")
        if missing_information_status == 101:
            #missing location. GET THEM
            MessageReply.echo_response(user_id, "LOCOLOCO")
        return None

    """
    This handles all the necessary information regarding emergency blood needed!
    """
    @classmethod
    def quick_reply_emergency_blood(cls, user_id):
        return

    """
    This friendly method parses the user id off the JSON.
    """
    @classmethod
    def __parse_user_id(cls, response_text):
        Utility.print_fucking_stuff("__parse_user_id")
        try:
            return str(response_text['sender']['id'])
        except ValueError as error:
            ErrorHandler.error_logger("Error ::: "+str(error)
                                      + " || Response text ::: "+str(response_text),
                                      None, "__parse_user_id")
            return None
        except BaseException as error:
            ErrorHandler.error_logger("Base Exception ::: " + str(error)
                                      + " || Response text ::: " + str(response_text),
                                      None, "__parse_user_id")
            return None
