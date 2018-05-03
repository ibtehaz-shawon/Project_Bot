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
