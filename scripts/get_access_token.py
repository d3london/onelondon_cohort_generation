import os
import requests

def get_access_token():
    # Retrieve client ID and secret from environment variables
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')

    if not client_id or not client_secret:
        raise ValueError("Client ID and/or Client Secret not set in environment variables.")

    # Endpoint URL
    url = 'https://ontology.nhs.uk/authorisation/auth/realms/nhs-digital-terminology/protocol/openid-connect/token'
    
    # Headers and data for the POST request
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    # Make the POST request
    response = requests.post(url, headers=headers, data=data)
    
    # Raise an exception if the request was unsuccessful
    response.raise_for_status()
    
    # Get the access token from the response
    access_token = response.json().get('access_token')
    if not access_token:
        raise ValueError("Failed to retrieve access token.")
    
    return access_token

if __name__ == "__main__":
    token = get_access_token()
    print(f"Access Token: {token}")