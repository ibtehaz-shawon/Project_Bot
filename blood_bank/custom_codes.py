class PostbackCodes:
    POSTBACK_BLOOD_GROUP_YES = 2001
    POSTBACK_BLOOD_GROUP_NO = 2002


class ConversationCodes:
    CONVERSATION_BLOOD_GROUP_ASK_TAG = 1001
    CONVERSATION_BLOOD_GROUP_STATUS_OPENED = "Opened"
    CONVERSATION_YES = "Yes :)"
    CONVERSATION_NO = "No :("
    CONVERSATION_ASK_BLD_GRP_AFFIRMATION = "Is this your blood group? "





class ReturnCodes:
    SuccessGeneric = 200


    #-------------------------------------------------------------------
    #-------------------------------------------------------------------
    #-------------------------------------------------------------------
    #-------------------------------------------------------------------
    #Exception Occurred
    ErrorBaseException = 500
    ErrorObjectDoesNotExist = 501
    ErrorValueError = 502
    ErrorTypeError = 503
    ErrorAttributeError = 504
    ErrorNoneValue = 505
    ErrorDBSerialization = 506
