import os
import requests

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