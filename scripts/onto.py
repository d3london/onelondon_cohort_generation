import os
import requests
import json

def get_access_token():
    """
    Given a CLIENT_ID and CLIENT_SECRET (set as environmental variables)
    Returns access token for session from OneLondon terminology server
    """
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')

    if not client_id or not client_secret:
        raise ValueError("Client ID and/or Client Secret not set in environment variables.")

    # endpoint url (see https://ontology.onelondon.online/)
    url = 'https://ontology.onelondon.online/authorisation/auth/realms/terminology/protocol/openid-connect/token'
    
    # define request contents
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    # POST request
    try:
        response = requests.post(url, headers=headers, data=data)
    
        # check HTTP status code
        response.raise_for_status()
    
        # get access token
        access_token = response.json().get('access_token')
        if not access_token:
            raise ValueError("Failed to find access token.")

        return access_token
    
    except requests.RequestException as e:
        print(f"Unable to request: {e}")
        return None

if __name__ == "__main__":
    token = get_access_token()
    if token:
        print(f"Access Token: {token}")
    else:
        print("Failed to retrieve access token")

def retrieve_concept_codes(access_token, value_set_id, endpoint='authoring'):
    """
    Retrieves a list of concept codes that are found in a value set
        access_token: OAuth2 token generated from a client ID and secret
        value_set_id: id of the target FHIR value set
        endpoint: default 'authoring', or 'production' (hardcoded for the OneLondon terminology server endpoints)
    Returns a list of concept codes 
    """
    endpoints = {
        'authoring': 'https://ontology.onelondon.online/authoring/fhir/',
        'production': 'https://ontology.onelondon.online/production1/fhir/'
    }
    
    url = f"{endpoints[endpoint]}ValueSet/{value_set_id}"
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    
    # check response
    if response.status_code == 200:
        value_set = response.json()
        
        # extract list of codes
        concepts = value_set.get('compose', {}).get('include', [])[0].get('concept', [])
        code_list = [item.get('code', 'no code listed') for item in concepts]
        
        return code_list
    else:
        print(f"Failed to retrieve data: {response.status_code} - {response.text}")
        return []
    