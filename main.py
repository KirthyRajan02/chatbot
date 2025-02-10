from flask import Flask, request, jsonify
from flask_cors import CORS
from function_tools import DataTools

app = Flask(__name__)
CORS(app)

# Initialize the data tools
tools = DataTools()

# API endpoint
API_URL = "https://tourismbackendwebapp.azurewebsites.net/api/overview/en"

# PDF directory
PDF_DIR = "pdfs"

# Initialize both PDF and API data sources
print("Initializing PDF index...")
tools.initialize_pdf_index(PDF_DIR)

print("Initializing API index...")
tools.initialize_api_index(API_URL)

def get_basic_response(user_input):
    # Convert to lowercase for easier matching
    user_input = user_input.lower().strip()
    
    # Basic greeting patterns
    greetings = {
        'hi': 'Hi! How can I help you today?',
        'hello': 'Hello! How may I assist you?',
        'hey': 'Hey there! What can I do for you?',
        'good morning': 'Good morning! How can I help you today?',
        'good afternoon': 'Good afternoon! How may I assist you?',
        'good evening': 'Good evening! What can I do for you?'
    }
    
    # Check for exact matches first
    if user_input in greetings:
        return greetings[user_input]
    
    # Check if input starts with any greeting
    for greeting in greetings:
        if user_input.startswith(greeting):
            return greetings[greeting]
    
    # Return None if no basic response is appropriate
    return None

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '').strip()
    
    if not user_input:
        return jsonify({"response": "Please enter a message."})
    
    # First check for basic responses
    basic_response = get_basic_response(user_input)
    if basic_response:
        return jsonify({"response": basic_response})
    
    # If not a basic interaction, proceed with data sources
    responses = tools.get_response(user_input, "both")
    
    # Combine responses into a single response
    response_text = ""
    if responses:
        if "pdf" in responses:
            response_text += responses["pdf"]
        if "api" in responses:
            response_text += " " + responses["api"]
    
    return jsonify({"response": response_text.strip() or "I couldn't find a relevant response."})

if __name__ == "__main__":
    app.run(debug=True)
