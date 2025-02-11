import os
import tempfile
from flask import Flask, request, jsonify
import base64
from openai import OpenAI

app = Flask(__name__)

llm = OpenAI(api_key="your api key")

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

@app.route('/')
def home():
    return jsonify({
        "message": "Food Label Processing API",
        "endpoints": ["/process_food"]
    })

@app.route('/process_food', methods=['POST'])
def process_food():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    temp_path = None
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        # Encode the image
        report = encode_image(temp_path)
        
        # Extract nutritional information
        llm_response = llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract detailed nutritional information in a clear JSON format."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract nutritional details from food label"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{report}"}}
                    ]
                }
            ]
        )
        
        nutritional_info = llm_response.choices[0].message.content.strip()
        
        # Categorize food for pre-diabetic patient
        llm_response2 = llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Categorize food for a pre-diabetic patient."},
                {
                    "role": "user",
                    "content": f"""Categorize this food for a pre-diabetic patient:
                    {nutritional_info}
                    
                    Categories:
                    1. "Okay to eat"
                    2. "Try to avoid"
                    3. "Avoid at all costs"
                    """
                }
            ]
        )
        
        recommendation = llm_response2.choices[0].message.content.strip()
        
        return jsonify({
            "nutritional_info": nutritional_info,
            "recommendation": recommendation
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Remove temporary file
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == '__main__':
    app.run(debug=True, port=5003)