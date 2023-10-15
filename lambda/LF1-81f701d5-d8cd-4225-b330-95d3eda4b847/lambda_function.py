import re
import json
from datetime import datetime
from dateutil import parser
import time
import os
import dateutil.parser
import logging
from utils import *
import boto3

from secrets import QUEUE_URL

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def is_valid_city(city):
    valid_cities = ['new york', 'los angeles', 'chicago', 'houston', 'philadelphia', 'phoenix', 'san antonio',
                    'san diego', 'dallas', 'san jose', 'austin', 'jacksonville', 'san francisco', 'indianapolis',
                    'columbus', 'fort worth', 'charlotte', 'detroit', 'el paso', 'seattle', 'denver', 'washington dc',
                    'memphis', 'boston', 'nashville', 'baltimore', 'portland','manhattan']
    return city.lower() in valid_cities
    
def is_valid_cuisine(cuisine):
    valid_cuisines = ['italian', 'mexican', 'chinese', 'indian', 'japanese', 'thai']
    return cuisine.lower() in valid_cuisines

def is_valid_number_of_people(number_of_people):
    return number_of_people.isdigit() and int(number_of_people) > 0

def is_valid_date(date):
    try:
        parsed_date = parser.parse(date).date()
        today = datetime.today().date()
        return parsed_date >= today
    except ValueError:
        return False
        
def is_valid_time(time):
    try:
        current_time = datetime.now().time()
        provided_time = parser.parse(time).time()
        today = datetime.now().date()

        if today == datetime.now().date():
            return provided_time > current_time
        else:
            return True
    except ValueError:
        return False

def is_valid_email(email):
    # Regular expression pattern for a basic email validation
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None


def build_validation_result(is_valid, violated_slot, message_content):
    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }

def validate(slots):
    city = try_ex(lambda: slots['city'])
    cuisine = try_ex(lambda: slots['cuisine'])
    number_of_people = try_ex(lambda: slots['number_of_people'])
    date = try_ex(lambda: slots['date'])
    time = try_ex(lambda: slots['time'])
    email = try_ex(lambda: slots['email'])
    
    if city and not is_valid_city(city):
        return build_validation_result(
            False,
            'location',
            'We currently do not support {} as a valid destination.  Can you try a different city?'.format(location)
        )
        
    if cuisine and not is_valid_cuisine(cuisine):
        return build_validation_result(
            False,
            'cuisine',
            'We do not currently offer {} cuisine. Please choose a different cuisine.'.format(cuisine)
        )
        
    if number_of_people and not is_valid_number_of_people(number_of_people):
        return build_validation_result(
            False,
            'number_of_people',
            'Number of people should be greater than zero. Can you enter again?'.format(number_of_people)
        )
        
    if date and not is_valid_date(date):
        return build_validation_result(
            False,
            'date',
            'Please enter a proper date starting from today'.format(date)
        )
        
    if time and not is_valid_time(time):
        return build_validation_result(
            False,
            'time',
            'Please enter a proper time starting from now'.format(time)
        )
        
    if email and not is_valid_email(email):
        return build_validation_result(
            False,
            'email',
            'Please enter a proper email.'.format(email)
        )
        
    return {'isValid': True}


""" --- Functions that control the bot's behavior --- """


def push_to_sqs(reservation):
    
    sqs = boto3.client('sqs')

    queue_url = QUEUE_URL
    
    # Send message to SQS queue
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=reservation
    )
    

def fetch_restaurant(intent_request):
    """
    Performs dialog management and fulfillment for fetching a restaurant.

    Beyond fulfillment, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of sessionAttributes to pass information that can be used to guide conversation
    """
    close_flag = False

    city = try_ex(lambda: intent_request['currentIntent']['slots']['city'])
    cuisine = try_ex(lambda: intent_request['currentIntent']['slots']['cuisine'])
    number_of_people = try_ex(lambda: intent_request['currentIntent']['slots']['number_of_people'])
    date = try_ex(lambda: intent_request['currentIntent']['slots']['date'])
    time = try_ex(lambda: intent_request['currentIntent']['slots']['time'])
    email = try_ex(lambda: intent_request['currentIntent']['slots']['email'])

    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    # Load confirmation history and track the current reservation.
    
    reservation_dict = {
        'city': city,
        'cuisine': cuisine,
        'number_of_people': number_of_people,
        'date': date,
        'time': time,
        'email': email
        
    }
    reservation = json.dumps(reservation_dict)

    session_attributes['currentReservation'] = reservation

    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Validate any slots which have been specified.  If any are invalid, re-elicit for their value
        validation_result = validate(intent_request['currentIntent']['slots'])
        print('validation_result',validation_result)
        if not validation_result['isValid']:
            slots = intent_request['currentIntent']['slots']
            slots[validation_result['violatedSlot']] = None
            print('slots',slots)
            print("184") 
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            )

        # Otherwise, let native DM rules determine how to elicit for slots and prompt for confirmation.  Pass price
        # back in sessionAttributes once it can be calculated; otherwise clear any setting from sessionAttributes.
        
        print("195")
        session_attributes['currentReservation'] = reservation
        print('Session_attributes', session_attributes)
        print(intent_request)
        
        if all(reservation_dict.values()): 
            push_to_sqs(reservation)
            close_flag = True
        else:
            return delegate(session_attributes, intent_request['currentIntent']['slots'])

    # In a real application, this would likely involve a call to a backend service.

    try_ex(lambda: session_attributes.pop('currentReservationPrice'))
    try_ex(lambda: session_attributes.pop('currentReservation'))
    session_attributes['lastConfirmedReservation'] = reservation
    
    if close_flag:
        return close(
            session_attributes,
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': 'Thanks, I have placed your reservation.'
            }
        )


# --- Intents ---


def dispatch(intent_request):
    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    if intent_name == 'DiningSuggestionsIntent':
        return fetch_restaurant(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


# --- Main handler ---


def lambda_handler(event, context):
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    print(event)
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    
    return dispatch(event)
