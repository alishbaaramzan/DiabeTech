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
        "message": "Diabetes Report Processing API",
        "endpoints": ["/process_report"]
    })

@app.route('/process_report', methods=['POST'])
def process_report():
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

        # Encode the report image
        report = encode_image(temp_path)

        # Extract blood sugar level
        llm_response_1 = llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract only the numeric blood sugar level from the medical report in mg/dL."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract blood sugar level"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{report}"}},
                    ],
                },
            ],
        )

        # Convert blood sugar level to integer
        try:
            blood_sugar_level = int(float(llm_response_1.choices[0].message.content.strip()))
        except (ValueError, TypeError):
            return jsonify({"error": "Failed to extract blood sugar level"}), 500

        # Categorize patient
        if blood_sugar_level < 100:
            category = "No Diabetes"
        elif 100 <= blood_sugar_level <= 125:
            category = "Pre-diabetic"
        else:
            category = "Diabetic"

        # Generate diet plan
        llm_response_3 = llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Generate a diabetes management plan in clear JSON format."},
                {
                    "role": "user",
                    "content": f"""
                    Create a detailed diet and lifestyle plan.
                    Category: {category}
                    Fasting glucose: {blood_sugar_level} mg/dL
                    
                    Provide recommendations in this JSON format:
                    {{
                        "foods_to_include": {{"item1": "reason", "item2": "reason"}},
                        "foods_to_avoid": {{"item1": "reason", "item2": "reason"}},
                        "lifestyle_changes": {{"change1": "reason", "change2": "reason"}}
                    }}
                    """,
                },
            ],
        )

        # Parse diet plan
        try:
            diet_plan = llm_response_3.choices[0].message.content.strip()
        except Exception:
            diet_plan = "Unable to generate diet plan"

        return jsonify({
            "blood_sugar_level": blood_sugar_level,
            "category": category,
            "diet_plan": diet_plan,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Remove temporary file
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)