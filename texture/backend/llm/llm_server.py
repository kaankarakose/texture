from flask import Flask, request, jsonify
import json
from llm import QwenModel

app = Flask(__name__)

llm = QwenModel()

@app.route('/kaan', methods=['GET'])
def kaan():
    return jsonify({"text": "Hi! From LLM engine"})


@app.route('/generate_answer', methods=['POST'])
def generate_answer():
    try:
        # Get the JSON data from the request
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400

        if not data.get("messages"):
            return jsonify({"error": "No messages provided"}), 400

        # Extract parameters from data
        messages = data.get("messages", [])
        temperature = data.get("temperature", 0.7)
        max_tokens = data.get("max_tokens", 500)

        # Generate answer with the processed messages
        answer = llm.generate(
            messages=messages,
            temperature=temperature,
            max_new_tokens=max_tokens
        )

        response = {
            "status": "success",
            "message": "Received JSON data",
            "received_data": {"answer": answer},
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=8187, debug=True, use_reloader=False)