import json
import boto3

from datetime import datetime
from pprint import pprint
from decimal import Decimal

from opensearchpy import OpenSearch, RequestsHttpConnection
from secrets import OS_HOST, OS_AUTH

OS_INDEX = "restaurants"

DYDB_TABLE = "yelp-restaurants"


def lambda_handler(event, context):
    
    print("Uploading Restaurant data to OpenSearch and DynamoDB...")
    
    # DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DYDB_TABLE)
    
    # OpenSearch
    opensearch = OpenSearch(
        hosts = [OS_HOST],
        http_auth = OS_AUTH,
        use_ssl = True,
        verify_certs = True,
        ssl_assert_hostname = False,
        ssl_show_warn = False,
        connection_class = RequestsHttpConnection
    )
    
    mapping = {
        "mappings": {
            "properties": {
                "id": {
                    "type": "text"
                },
                "cuisine": {
                    "type": "text"
                }
            }
        }
    }
    opensearch.indices.create(index=OS_INDEX, body=mapping)
    
    with open("yelp_restaurants_data.json") as json_file:
        json_data = json_file.read()
        
    restaurants = json.loads(json_data)
    print(len(restaurants))
    
    pprint(restaurants[0])
    
    for restaurant in restaurants:
        
        # DynamoDB Item
        item = {
            'id': restaurant['id'],
            'name': restaurant['name'],
            'address': restaurant['location']['address1'],
            'coordinates': {
                'latitude': Decimal(str(restaurant['coordinates']['latitude'])),
                'longitude': Decimal(str(restaurant['coordinates']['longitude']))
            },
            'num_reviews': restaurant['review_count'],
            'rating': Decimal(str(restaurant['rating'])),
            'zip_code': restaurant['location']['zip_code'],
            'insertedAtTimestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }
        table.put_item(Item=item)
        
        # OpenSearch Document
        document = {
            "id": restaurant['id'],
            "cuisine": restaurant.get('cuisine', 'unknown')
        }
        opensearch.index(index=OS_INDEX, body=document)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Restaurant data uploaded successfully!')
    }
