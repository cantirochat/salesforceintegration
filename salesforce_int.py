import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Environment variables from Render
SALESFORCE_CONSUMER_KEY = os.getenv("SALESFORCE_CONSUMER_KEY")
SALESFORCE_CONSUMER_SECRET = os.getenv("SALESFORCE_CONSUMER_SECRET")
SALESFORCE_INSTANCE_URL = os.getenv("SALESFORCE_INSTANCE_URL")
SALESFORCE_LOGIN_URL = os.getenv("SALESFORCE_LOGIN_URL")
SALESFORCE_API_VERSION = "v57.0"  # Update this if needed


# Function to obtain access token
def get_access_token():
    data = {
        "grant_type": "client_credentials",
        "client_id": SALESFORCE_CONSUMER_KEY,
        "client_secret": SALESFORCE_CONSUMER_SECRET
    }
    response = requests.post(f"{SALESFORCE_LOGIN_URL}/services/oauth2/token", data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception(f"Error obtaining access token: {response.json()}")


# Function to handle function calls
@app.route('/handle-function-call', methods=['POST'])
def handle_function_call():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    function_name = data.get("function_name")
    arguments = data.get("arguments")

    if not function_name or not arguments:
        return jsonify({"error": "Missing function_name or arguments"}), 400

    if function_name == "create_salesforce_lead":
        # Forward the arguments to the create-lead route
        response = requests.post(
            "http://127.0.0.1:5000/create-lead",  # Internal call to create-lead route
            json=arguments
        )
        if response.status_code == 201:
            return jsonify({"message": "Function call executed successfully"}), 201
        else:
            return jsonify({"error": response.json()}), response.status_code
    else:
        return jsonify({"error": f"Unsupported function: {function_name}"}), 400


@app.route('/create-lead', methods=['POST'])
def create_lead():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name")
    email = data.get("email")
    conversation_summary = data.get("conversation_summary")
    company = data.get("company", "Not Provided")  # Default value for Company

    if not all([name, email, conversation_summary]):
        return jsonify({"error": "Missing required fields"}), 400

    # Get access token
    try:
        access_token = get_access_token()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Make Salesforce API request
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    lead_data = {
        "FirstName": name.split()[0],
        "LastName": name.split()[1] if " " in name else "Unknown",
        "Email": email,
        "Description": conversation_summary,
        "Company": company  # Add Company field
    }

    salesforce_url = f"{SALESFORCE_INSTANCE_URL}/services/data/{SALESFORCE_API_VERSION}/sobjects/Lead"
    response = requests.post(salesforce_url, headers=headers, json=lead_data)

    if response.status_code == 201:
        return jsonify({"message": "Lead created successfully!"}), 201
    else:
        return jsonify({"error": response.json()}), response.status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

