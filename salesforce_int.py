import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Environment variables from Render
SALESFORCE_TOKEN = os.getenv("SALESFORCE_TOKEN")
SALESFORCE_URL = os.getenv("SALESFORCE_URL")

@app.route('/create-lead', methods=['POST'])
def create_lead():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name")
    email = data.get("email")
    conversation_summary = data.get("conversation_summary")

    if not all([name, email, conversation_summary]):
        return jsonify({"error": "Missing required fields"}), 400

    # Make Salesforce API request
    headers = {
        "Authorization": f"Bearer {SALESFORCE_TOKEN}",
        "Content-Type": "application/json"
    }
    lead_data = {
        "FirstName": name.split()[0],
        "LastName": name.split()[1] if " " in name else "Unknown",
        "Email": email,
        "Description": conversation_summary
    }

    response = requests.post(SALESFORCE_URL, headers=headers, json=lead_data)

    if response.status_code == 201:
        return jsonify({"message": "Lead created successfully!"}), 201
    else:
        return jsonify({"error": response.json()}), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

