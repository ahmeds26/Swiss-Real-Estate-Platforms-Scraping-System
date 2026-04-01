import requests
import json


def check_object_with_api(object_url):

    object_api_url = "https://api.we-net.ch/api/listings/check-url"

    object_data = {
        "detail_url": object_url
    }

    object_request = requests.post(object_api_url, json=object_data)
    object_response = object_request.json()["exists"]

    return object_response

def check_contact_with_api(contact_payload):

    contact_api_url = "https://api.we-net.ch/api/advertisers/check"

    contact_data = contact_payload
    
    contact_request = requests.post(contact_api_url, json=contact_data)
    contact_response = contact_request.json()
    if contact_response["found"] == False:
        return "false"
    elif contact_response["found"] == True and contact_request.json()["blocked"] == True:
        return "blocked"
    else:
        return contact_response["id"]

