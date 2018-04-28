"""
nlp parser parses fb's nlp to strip the confidence out of it. :P
"""


def nlp_parser(message_data, keyword):
    if keyword in message_data['message']['nlp']['entities']:
        for entry in message_data['message']['nlp']['entities'][keyword]:
            return entry['confidence']
    else:
        return 0.00
