import json
import os
from json import dump
import requests
import config
import time
import db

def auth():
    if "credentials.json" in os.listdir():
        with open("credentials.json", "r") as f:
            credentials = json.load(f)
            f.close()
    else:
        credentials = {"access_token": "", "refresh_token": "", "expires": 0}

    if credentials["expires"] == 0:
        print("No credentials found, authenticating with HelloAsso")
        url = "https://api.helloasso-sandbox.com/oauth2/token"
        body = {
            "client_id": config.helloasso_client_id,
            "client_secret": config.helloasso_client_secret,
            "grant_type": "client_credentials"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(url, data=body, headers=headers)
        response_data = response.json()
        if "access_token" in response_data:
            with open("credentials.json", "w") as f:
                credentials["access_token"] = response_data["access_token"]
                credentials["refresh_token"] = response_data["refresh_token"]
                credentials["expires"] = time.time() + response_data["expires_in"]
                dump(credentials, f, indent=4)
                f.close()
        else:
            raise IOError(f"Failed to authenticate with HelloAsso: {response_data}")
    elif credentials["expires"] < time.time():
        print("Credentials expired, refreshing with HelloAsso")
        url = "https://api.helloasso-sandbox.com/oauth2/token"
        body = {
            "grant_type": "refresh_token",
            "refresh_token": credentials["refresh_token"],
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(url, data=body, headers=headers)
        response_data = response.json()
        if "access_token" in response_data:
            with open("credentials.json", "w") as f:
                credentials["access_token"] = response_data["access_token"]
                credentials["refresh_token"] = response_data["refresh_token"]
                credentials["expires"] = time.time() + response_data["expires_in"]
                dump(credentials, f, indent=4)
                f.close()
        else:
            raise IOError(f"Failed to authenticate for refresh with HelloAsso: {response_data}")
    
def get_members():
    with open("credentials.json", "r") as f:
        credentials = json.load(f)
        f.close()

    url = f"https://api.helloasso-sandbox.com/v5/organizations/{config.helloasso_organization_slug}/forms/Membership/{config.helloasso_form_slug}/items"
    headers = {"Authorization": f"Bearer {credentials['access_token']}"}
    params = {
        "pageSize": 100,
        "pageIndex": 1,
        "withDetails": True,
        "itemStates": "Processed"
    }
    raw_response = requests.get(url, headers=headers, params=params)  # retrieve page 1
    if raw_response.ok:
        response = raw_response.json()
        first_page = int(response["pagination"]["pageIndex"])
        last_page = min(100, int(response["pagination"]["totalPages"]))
        members: list = response["data"]
        print("Received,", len(response["data"]), "members from page", response["pagination"]["pageIndex"], "over", response["pagination"]["totalPages"])
        for _ in list(range(first_page, last_page)):
            params["pageIndex"] += 1
            raw_response = requests.get(url, headers=headers, params=params)  # retrieve page 2 and above
            if raw_response.ok:
                response = raw_response.json()
                members.extend(response["data"])
                print("Received,", len(response["data"]), f"members from page {response['pagination']['pageIndex']}/{response['pagination']['totalPages']}")
            else:
                raise IOError(f"Retrieving page failed with HTTP error {raw_response.status_code} from HelloAsso")
        return members
    print(f"Failed to get HelloAsso members:", raw_response.text)

def saveToJson(data, filename):
    with open(filename, "w") as f:
        dump(data, f, indent=4)


if __name__ == "__main__":
    auth()
    members = get_members()

    # Save members to database
    db = db.Db()
    db.save_members(members)
