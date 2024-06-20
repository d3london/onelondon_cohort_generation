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

def retrieve_concept_codes_from_id(access_token, value_set_id, endpoint='authoring'):
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
    
    # retrieve value set
    if response.status_code == 200:
        value_set = response.json()
        
        # extract list of codes
        concepts = value_set.get('compose', {}).get('include', [])[0].get('concept', [])
        code_list = [item.get('code', 'no code listed') for item in concepts]
        
        return code_list
    else:
        print(f"Failed to retrieve data: {response.status_code} - {response.text}")
        return []

def retrieve_concept_codes_from_desc(access_token, endpoint='authoring', query_type='url', query_value=''):
    """
    Retrieves a list of concept codes that are found in a value set, via either a FHIR url or value set name 
        access_token: OAuth2 token generated from a client ID and secret
        endpoint: default 'authoring', or 'production' (hardcoded for the OneLondon terminology server endpoints)
        query_type: either 'url' or 'name'
        query_value: corresponding FHIR url or name value
    Returns a list of concept codes
    """

    endpoints = {
        'authoring': 'https://ontology.onelondon.online/authoring/fhir/',
        'production': 'https://ontology.onelondon.online/production1/fhir/'
    }
    
    if query_type == 'url':
        query_url = f"{endpoints[endpoint]}ValueSet/?url={query_value}"
    elif query_type == 'name':
        query_url = f"{endpoints[endpoint]}ValueSet/?name={query_value}"
    else:
        raise ValueError("Invalid query_type. Use 'url' or 'name'.")

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # retrieve bundle metadata
    bundle_response = requests.get(query_url, headers=headers)
    
    if bundle_response.status_code == 200:
        bundle = bundle_response.json()
        
        # extract full url with id
        try:
            full_url = bundle['entry'][0]['fullUrl']
            
            # retrieve actual value set from full url
            response = requests.get(full_url, headers=headers)
            if response.status_code == 200:
                value_set = response.json()
                
                # extract list of codes
                concepts = value_set.get('compose', {}).get('include', [])[0].get('concept', [])
                code_list = [item.get('code', 'no code listed') for item in concepts]
                
                return code_list
            else:
                print(f"Failed to retrieve data: {response.status_code} - {response.text}")
                return []
        except IndexError:
            print("No entries found in bundle.")
            return []
    else:
        print(f"Failed to retrieve bundle: {bundle_response.status_code} - {bundle_response.text}")
        return []