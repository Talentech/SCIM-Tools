import csv
import requests
import json

# SCIM API Endpoints
SCIM_API_URL = "https://api.talentech.io/scim/v1"
ACCESS_TOKEN = "----YOUR-ACCESS-TOKEN-HERE----"  # Replace with your actual token
GROUP_NAME = "Talent-Recruiter-Users"  # Puts all users in a group called Talent-Recruiter-Users

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def get_user_id(email):
    response = requests.get(f"{SCIM_API_URL}/Users?filter=userName eq \"{email}\"", headers=HEADERS)
    if response.status_code == 200:
        users = response.json().get("Resources", [])
        if users:
            return users[0].get("id")
    return None

def get_group_id(group_name):
    response = requests.get(f"{SCIM_API_URL}/Groups?filter=displayName eq \"{group_name}\"", headers=HEADERS)
    if response.status_code == 200:
        groups = response.json().get("Resources", [])
        if groups:
            return groups[0].get("id")
    return None

def create_or_get_group(group_name):
    payload = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
        "displayName": group_name,
        "externalId": group_name
    }

    response = requests.post(f"{SCIM_API_URL}/Groups", headers=HEADERS, json=payload)

    if response.status_code in [200, 201]:
        group_id = response.json().get("id")
        print(f"Group '{group_name}' created with ID: {group_id}")
        return group_id
    elif response.status_code == 409:
        group_id = get_group_id(group_name)
        if group_id:
            print(f"Group '{group_name}' already exists. Using ID: {group_id}")
            return group_id
    else:
        print(f"Failed to create or fetch group '{group_name}': {response.text}")
        return None

def add_user_to_group(user_id, group_id):
    patch_payload = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
        "Operations": [
            {
                "op": "Add",
                "path": "members",
                "value": [{"value": user_id}]
            }
        ]
    }

    response = requests.patch(f"{SCIM_API_URL}/Groups/{group_id}", headers=HEADERS, json=patch_payload)

    if response.status_code in [200, 204]:
        print(f"User {user_id} added to group {group_id}")
    else:
        print(f"Failed to add user {user_id} to group {group_id}: {response.text}")

def create_or_update_user(user_data):
    user_id = get_user_id(user_data["UserName"])

    access_level = {
        "roleId": str(user_data["Role id"]),
        "externalDepartmentId": str(user_data["Department Id"])
    }

    payload = {
        "schemas": [
            "urn:ietf:params:scim:schemas:core:2.0:User",
            "urn:ietf:params:scim:schemas:extension:talentech:talentrecruiter"
        ],
        "externalId": user_data["UserName"],
        "userName": user_data["UserName"],
        "active": True,
        "name": {
            "givenName": user_data["FirstName"],
            "familyName": user_data["LastName"]
        },
        "emails": [
            {
                "value": user_data["UserName"],
                "type": "work",
                "primary": True
            }
        ],
        "urn:ietf:params:scim:schemas:extension:talentech:talentrecruiter": {
            "schemaversion": "1.0",
            "schemadata": {
                "accessLevels": [access_level]
            }
        }
    }

    if user_id:
        print(f"User {user_data['UserName']} - {user_id} already exists - SKIPPING.")
    else:
        response = requests.post(f"{SCIM_API_URL}/Users", json=payload, headers=HEADERS)
        if response.status_code in [200, 201]:
            user_id = response.json().get("id")
            print(f"User {user_data['UserName']} created with ID: {user_id}")
        elif response.status_code == 409:
            user_id = get_user_id(user_data["UserName"])
            if user_id:
                print(f"User {user_data['UserName']} already exists. Using existing ID: {user_id}")
        else:
            print(f"Failed to process user {user_data['UserName']}. Error: {response.text}")
            return None

    return user_id

def process_csv(file_path, group_name):
    users = []
    group_id = create_or_get_group(group_name)

    if not group_id:
        print("Aborting import due to missing group.")
        return

    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            row = {key.strip(): value.strip() for key, value in row.items()}
            if not any(row.values()):
                continue
            users.append(row)

    for user in users:
        user_id = create_or_update_user(user)
        if user_id:
            add_user_to_group(user_id, group_id)

# Run the script
if __name__ == "__main__":
    csv_file_path = "users.csv"  # Change to your CSV file path
    process_csv(csv_file_path, GROUP_NAME)
