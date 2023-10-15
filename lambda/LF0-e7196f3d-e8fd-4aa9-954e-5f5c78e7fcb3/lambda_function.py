import json
import dateutil.parser
import datetime
import time
import os
import math
import random
import logging
from utils import *
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def respond_event(msg):
    print(msg)
    message = msg['message']
    if message:
        message = message
    else:
        message = 'Oops, something went wrong'
    
    if msg.get('sessionState') and msg['sessionState'].get('sessionAttributes'):
        current_session_id = msg['sessionState']['sessionAttributes']['current_session_id']
    else:
        current_session_id = None
        
    return close(
        None,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': message
        },
        current_session_id
    )

""" --- Main handler --- """

def validate(message):
    return message


def connect_to_lex(message):
    client = boto3.client('lex-runtime')
    response = client.post_text(
        botName='Bot',
        botAlias='DiningChatBot',
        userId='string',
        sessionAttributes={
            'string': 'string'
        },
        inputText=message
        )
    print("Response from lex :: ", response)
    # print("Current session :: ", response['sessionState']['sessionAttributes'])
    return response
    
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    print(event)
    
    message = event['messages'][0]
    message = message['unstructured']['text']

    validate(message)
    lex_response = connect_to_lex(message)
    logger.debug(message)
    
    return respond_event(lex_response)
