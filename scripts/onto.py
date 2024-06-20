import time
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Literal, Optional

import requests

# Endpoint url (see https://ontology.onelondon.online/)
_ONELONDON_OPENID_ENDPOINT = "https://ontology.onelondon.online/authorisation/auth/realms/terminology/protocol/openid-connect/token"


def auto_refresh_token(func) -> Callable:
    """
    This function decorator checks if the access token has expired and refreshes it if necessary.
    """

    @wraps(func)
    def wrap(self, *args, **kwargs):
        if time.time() > self._access_token_expire_time:
            print("[INFO] Access token expired. Auto-refreshing...")
            self._initialise_access_token()
        return func(self, *args, **kwargs)

    return wrap


@dataclass
class OneLondonEndpoints:
    authoring: str = "https://ontology.onelondon.online/authoring/fhir/"
    production: str = "https://ontology.onelondon.online/production1/fhir/"


class FHIRTerminologyClient:
    """
    A client for querying FHIR terminology services, such as the OneLondon terminology server.

    Attributes:
        client_id: client ID for the FHIR server
        client_secret: client secret for the FHIR server
        endpoint: the endpoint URL for the FHIR server (default: OneLondon authoring endpoint)
        open_id_token_url: the URL for the OpenID token endpoint (default: OneLondon OpenID endpoint)

    Methods:
        retrieve_concept_codes_from_id: retrieves a list of concept codes from a value set ID
        retrieve_concept_codes_from_desc: retrieves a list of concept codes from a value set URL or name
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        endpoint: str = OneLondonEndpoints.authoring,
        open_id_token_url: str = _ONELONDON_OPENID_ENDPOINT,
    ):
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.endpoint: str = endpoint

        self._open_id_token_url: str = open_id_token_url
        self._access_token: str
        self._access_token_expire_time: int

        self._initialise_access_token()

    def _initialise_access_token(self):
        self._access_token, self._access_token_expire_time = self._get_access_token()

    def _get_access_token(self) -> tuple[str, int]:

        # define request contents
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        # Request access token
        try:
            response = requests.post(
                self._open_id_token_url, headers=headers, data=data
            )

            # check HTTP status code
            response.raise_for_status()

            # == Get access token ==
            # May fail if the response does not contain the expected keys
            # Likely as a result of incorrect client_id or client_secret
            # (Don't need to try / except this - we want a failure!)
            access_token: str = response.json()["access_token"]
            expiry_time: int = round(time.time()) + response.json()["expires_in"]

            return access_token, expiry_time

        except requests.RequestException as e:
            print(f"Unable to request: {e}")
            print("Check client_id or client_secret, or connectivity.")
            raise ValueError("Failed to retrieve access token.")

    @auto_refresh_token
    def retrieve_concept_codes_from_id(self, value_set_id: str) -> list[Optional[str]]:
        """
        Retrieves a list of concept codes that are found in a value set
            value_set_id: id of the target FHIR value set
        Returns a list of concept codes
        """

        url = f"{self.endpoint}ValueSet/{value_set_id}"

        headers = {"Authorization": f"Bearer {self._access_token}"}

        response = requests.get(url, headers=headers)

        # retrieve value set
        if response.status_code == 200:
            value_set = response.json()

            # extract list of codes
            concepts = (
                value_set.get("compose", {}).get("include", [])[0].get("concept", [])
            )
            code_list = [item.get("code", "no code listed") for item in concepts]

            return code_list
        else:
            print(f"Failed to retrieve data: {response.status_code} - {response.text}")
            return []

    @auto_refresh_token
    def retrieve_concept_codes_from_desc(
        self, query_value: str, query_type: Literal["url", "name"] = "url"
    ) -> list[Optional[str]]:
        """
        Retrieves a list of concept codes that are found in a value set, via either a FHIR url or value set name
            query_type: either 'url' or 'name'
            query_value: corresponding FHIR url or name value
        Returns a list of concept codes
        """

        # Guard against invalid query types
        if query_type not in ["url", "name"]:
            raise ValueError("Invalid query_type. Use 'url' or 'name'.")

        query_url = f"{self.endpoint}ValueSet/?{query_type}={query_value}"

        headers = {"Authorization": f"Bearer {self._access_token}"}

        # retrieve bundle metadata
        bundle_response = requests.get(query_url, headers=headers)

        if bundle_response.status_code == 200:
            bundle = bundle_response.json()

            # extract full url with id
            try:
                full_url = bundle["entry"][0]["fullUrl"]

                # retrieve actual value set from full url
                response = requests.get(full_url, headers=headers)
                if response.status_code == 200:
                    value_set = response.json()

                    # extract list of codes
                    concepts = (
                        value_set.get("compose", {})
                        .get("include", [])[0]
                        .get("concept", [])
                    )
                    code_list = [
                        item.get("code", "no code listed") for item in concepts
                    ]

                    return code_list
                else:
                    print(
                        f"Failed to retrieve data: {response.status_code} - {response.text}"
                    )
                    return []
            except IndexError:
                print("No entries found in bundle.")
                return []
        else:
            print(
                f"Failed to retrieve bundle: {bundle_response.status_code} - {bundle_response.text}"
            )
            return []
