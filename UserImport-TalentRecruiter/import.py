import csv
import requests
import json

# SCIM API Endpoints
SCIM_API_URL = "https://api.talentech.io/scim/v1"
ACCESS_TOKEN = "----YOUR-ACCESS-TOKEN-HERE----"  # Replace with your actual token

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# Function to get existing user ID by email
def get_user_id(email):
    response = requests.get(f"{SCIM_API_URL}/Users?filter=userName eq \"{email}\"", headers=HEADERS)
    if response.status_code == 200:
        users = response.json().get("Resources", [])
        if users:
            return users[0].get("id")
    return None

# Function to create or update a user
def create_or_update_user(user_data):
    user_id = get_user_id(user_data["UserName"])


    access_level = {
        "roleId": str(user_data["Role id"]),
        "externalDepartmentId": str(user_data["Department Id"])
    }

    # Construct the SCIM payload
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
                "accessLevels": [access_level]  # Single access level per user
            }
        }
    }

    if user_id:
        print(f"User {user_data['UserName']} - {user_id} already exists - SKIPPING.")
        return None
    else:
        response = requests.post(f"{SCIM_API_URL}/Users", json=payload, headers=HEADERS)

    if response.status_code in [200, 201]:
        user_id = response.json().get("id")
        print(f"User {user_data['UserName']} processed successfully with ID: {user_id}")
        return user_id
    elif response.status_code == 409:  # Handle conflict
        user_id = get_user_id(user_data["UserName"])
        if user_id:
            print(f"User {user_data['UserName']} already exists. Using existing ID: {user_id}")
            return user_id
    else:
        print(f"Failed to process user {user_data['UserName']}. Error: {response.text}")
        return None

# Function to process the CSV file
def process_csv(file_path):
    users = []

    # Read CSV and collect valid users
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Remove leading/trailing spaces from column names and values
            row = {key.strip(): value.strip() for key, value in row.items()}

            # Ignore empty rows (where all values are empty or just commas)
            if not any(row.values()):
                continue

            # Append valid user data
            users.append(row)

    # Process users
    for user in users:
        create_or_update_user(user)

# Run the script
if __name__ == "__main__":
    csv_file_path = "users.csv"  # Change this to your CSV file path
    process_csv(csv_file_path)
