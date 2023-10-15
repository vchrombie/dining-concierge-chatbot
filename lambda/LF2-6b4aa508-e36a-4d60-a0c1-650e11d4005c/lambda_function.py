import boto3
import json
import random

from opensearchpy import OpenSearch, RequestsHttpConnection


QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/906796636311/queue'

OS_HOST = "https://search-vt2182-a1-opensearch-7du75aoy5n67vfbqksdvyvvnyy.us-east-1.es.amazonaws.com/"
OS_AUTH = ('admin', 'OpenSearchr0cks!')
OS_INDEX = "restaurants"

DYDB_TABLE = "yelp-restaurants"

EMAIL_ADDRESS = "vt2182@nyu.edu"


def pull_msg_from_sqs_queue(sqs, ):
    response = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10
    )
    message = response['Messages'][0]
    
    receipt_handle = message["ReceiptHandle"]
    message = json.loads(message['Body'])
    return receipt_handle, message


def get_restaurant_cuisne_opensearch_dynamodb(
    cuisine,
    opensearch,
    table
):
    search_body = {
        "query": {
            "match": {
                "cuisine": cuisine
            }
        },
        "size": 100
    }
    search_response = opensearch.search(
        index=OS_INDEX,
        body=search_body
    )
    hits = search_response['hits']['hits']
    if not hits:
        # No matching restaurant found, handle appropriately
        return
    
    random_hits = random.sample(hits, 3)
    
    restaurants = []
    for random_hit in random_hits:
        restaurant_id = random_hit['_source']['id']

        # Fetch more details from DynamoDB
        restaurant = table.get_item(Key={"id": str(restaurant_id)})
        restaurants.append(restaurant)

    return restaurants


def format_email_content(message, restaurants):
    email_content = f"Hello! Here are my {message['cuisine']} restaurant suggestions for {message['number_of_people']} people, for {message['date']} at {message['time']}\n"
    
    for idx, restaurant in enumerate(restaurants, start=1):
        item = restaurant.get('Item', {})
        name = item.get('name', 'N/A')
        address = item.get('address', 'N/A')

        email_content += f"{idx}. {name}, located at {address}.\n"

    return email_content


def send_the_email(message, email_content, ses):
    email_address = message['email']
    ses.send_email(
        Source=EMAIL_ADDRESS,
        Destination={
            'ToAddresses': [email_address]
        },
        Message={
            'Subject': {'Data': 'Your Restaurant Recommendation'},
            'Body': {'Text': {'Data': email_content}}
        }
    )


def lambda_handler(event, context):
    
    # Initialize SQS, DynamoDB, OpenSearch and SES clients
    
    sqs = boto3.client('sqs')
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DYDB_TABLE)
    
    ses = boto3.client('ses')
    
    opensearch = OpenSearch(
        hosts = [OS_HOST],
        http_auth = OS_AUTH,
        use_ssl = True,
        verify_certs = True,
        ssl_assert_hostname = False,
        ssl_show_warn = False,
        connection_class = RequestsHttpConnection
    )

    # i) Pull message from SQS Queue
    receipt_handle, message = pull_msg_from_sqs_queue(sqs)

    # ii) Get random restaurant recommendation & details
    # from OpenSearch and DynamoDB based on cuisine
    restaurants = get_restaurant_cuisne_opensearch_dynamodb(
        message['cuisine'],
        opensearch,
        table
    )
    
    # iii) Format the email content
    email_content = format_email_content(message, restaurants)

    # iv) Send email using SES
    send_the_email(message, email_content, ses)

    # Delete message from SQS to ensure it's not processed again
    sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)

    return {
        'statusCode': 200,
        'body': json.dumps('Email sent!')
    }
