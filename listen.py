import openai
import requests
import os

# Set up OpenAI API key from environment variables
openai.api_key = os.getenv("openai_api_key")

# Assistant ID
ASSISTANT_ID = "asst_GWYzLER5Vn2HhH9eVqRTISFl"

# Flask app endpoint
FLASK_ENDPOINT = "https://salesforceintegration.onrender.com/create-lead"

# Function to handle assistant function calls
def handle_assistant_function_call(function_name, arguments):
    if function_name == "create_salesforce_lead":
        # Forward the arguments to the Flask app
        response = requests.post(FLASK_ENDPOINT, json=arguments)
        if response.status_code == 201:
            return {"message": "Lead successfully created in Salesforce."}
        else:
            return {"error": response.json()}
    else:
        return {"error": f"Function {function_name} not recognized."}

# Poll for assistant function calls
def listen_to_assistant():
    # Simulate a user message and interaction with the assistant
    response = openai.ChatCompletion.create(
        model="gpt-4",
        assistant_id=ASSISTANT_ID,  # Include the assistant ID
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "My name is John Smith and my email is john.smith@example.com."}
        ],
        functions=[
            {
                "name": "create_salesforce_lead",
                "description": "Send user details to Salesforce as a new lead.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "The user's name"},
                        "email": {"type": "string", "description": "The user's email"},
                        "conversation_summary": {
                            "type": "string",
                            "description": "A summary of the conversation"
                        }
                    },
                    "required": ["name", "email", "conversation_summary"]
                }
            }
        ]
    )

    # Extract the function call if present
    function_call = response["choices"][0]["message"].get("function_call")
    if function_call:
        function_name = function_call["name"]
        arguments = eval(function_call["arguments"])  # Parse arguments as JSON
        # Handle the function call
        result = handle_assistant_function_call(function_name, arguments)
        print(result)
    else:
        print("No function call detected.")

# Run the listener
if __name__ == "__main__":
    listen_to_assistant()

