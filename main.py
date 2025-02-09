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

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '').strip()
    
    # Determine the source based on prefix
    if user_input.lower().startswith("pdf:"):
        source = "pdf"
        query = user_input[4:].strip()
    elif user_input.lower().startswith("api:"):
        source = "api"
        query = user_input[4:].strip()
    else:
        source = "both"
        query = user_input
    
    # Get response(s)
    responses = tools.get_response(query, source)
    
    # Format response
    response_text = ""
    if "pdf" in responses:
        response_text += "\nFrom PDF:\n" + responses["pdf"] + "\n\n"
    if "api" in responses:
        response_text += "\nFrom API:\n" + responses["api"]
    
    return jsonify({"response": response_text.strip()})

if __name__ == "__main__":
    app.run(debug=True)
