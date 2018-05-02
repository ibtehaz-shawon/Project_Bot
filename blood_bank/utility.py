"""
nlp parser parses fb's nlp to strip the confidence out of it. :P
"""
from bot.settings import DEBUG


def nlp_parser(message_data, keyword):
    if keyword in message_data['message']['nlp']['entities']:
        for entry in message_data['message']['nlp']['entities'][keyword]:
            return entry['confidence']
    else:
        return 0.00


class Utility:
    @classmethod
    def print_fucking_stuff(cls, message):
        if DEBUG:
            print(message)
