# Example code for retrieving cohort definitions using the OneLondon terminology server

### Setting up environmental variables
Retrieving an access token requires a client ID and a secret that can be obtained from the OneLondon terminology server team. Prior to running these scripts, CLIENT_ID and CLIENT_SECRET must be set as environmental variables.

If using Linux or Mac OS:
```
export CLIENT_ID=your_client_id_here
export CLIENT_SECRET=your_client_secret_here
```

If using Windows (terminal):
```
set CLIENT_ID=your_client_id_here
set CLIENT_SECRET=your_client_secret_here
```

In the Jupyter Notebook example, these are loaded from .env which should contain the following:
```
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
```

To load from .env, python-dotenv should be installed:
```
pip install python-dotenv
```
