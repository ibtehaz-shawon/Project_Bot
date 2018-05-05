"""
nlp parser parses fb's nlp to strip the confidence out of it. :P
"""
from bot.settings import DEBUG
from decouple import config

def nlp_parser(message_data, keyword):
    if keyword in message_data['message']['nlp']['entities']:
        for entry in message_data['message']['nlp']['entities'][keyword]:
            return entry['confidence']
    else:
        return 0.00


class Utility:
    """
    These are utility variable needed throughout the universe. Change here might have resulted in unparalleled catastrophic behavior.
    """
    __INTRO_MESSAGE_QUICK_REPLY_FRESH__ = "I see you're new in this services! I am a friendly messenger chat bot"
    __INTRO_OPTION_DONOR_QUICK_REPLY_FRESH__ = "Want to donate <3"
    __INTRO_OPTION_PATIENT_QUICK_REPLY_FRESH__ = "Need emergency blood"
    __GENERIC_ERROR_MESSAGE__ = "I'm sorry. An error occurred while processing your request! :("

    @classmethod
    def print_fucking_stuff(cls, message):
        """
        does exactly what the function name says!
        :param message:
        :return:
        """
        if DEBUG:
            print(message)

    @staticmethod
    def get_postback_keys_fresh():
        """
        returns the fresh donor and patient key from env
        :return:
        """
        return [config('REPLY_KEY_FRESH_DONOR'),config('REPLY_KEY_FRESH_PATIENT')]


    """
    check the payload keys for quick reply
    1 -> QUICK_REPLY_DONOR
    2 -> NEED EMERGENCY DONATION
    """
    @staticmethod
    def check_quick_reply_keys(payload):
        ## TODO: these function needs a better implemnetation
        ## TODO: I am flying blind
        stored_keys = Utility.get_postback_keys_fresh()

        if str(payload) == str(stored_keys[0]):
            return 1
        elif str(payload) == str(stored_keys[1]):
            return 2
        else:
            return 0

