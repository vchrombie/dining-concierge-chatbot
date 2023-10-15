import json
from pprint import pprint

from opensearchpy import OpenSearch, RequestsHttpConnection
from secrets import OS_HOST, OS_AUTH

OS_INDEX = "restaurants"

print("Uploading Restaurant data to OpenSearch...")
    
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

with open("../misc/yelp_restaurants_data.json") as json_file:
    json_data = json_file.read()
    
restaurants = json.loads(json_data)

print(len(restaurants))

pprint(restaurants[0])

for restaurant in restaurants:    
    document = {
        "id": restaurant['id'],
        "cuisine": restaurant.get('cuisine', 'unknown')
    }
    opensearch.index(index=OS_INDEX, body=document)

print("Uploading Restaurant data to OpenSearch completed!")
