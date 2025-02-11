from flask import Flask, render_template, request, flash
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flash messages

# API endpoint URL - adjust to match your actual FastAPI/Flask server
FASTAPI_URL_1 = "http://127.0.0.1:5000/process_report"
FASTAPI_URL_2 = "http://127.0.0.1:5003/process_food"
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/diet-help', methods=["GET", "POST"])
def diet_help():
    result = None
    if request.method == "POST":
        # Get the uploaded file
        file = request.files.get("report")
        if file:
            try:
                # Send the file to the API endpoint
                response = requests.post(FASTAPI_URL_1, files={"file": (file.filename, file.read(), file.mimetype)})
                
                if response.status_code == 200:
                    result = response.json()
                else:
                    flash(
                        f"Error: API returned status code {response.status_code}. Please try again later.",
                        "danger"
                    )
            except requests.exceptions.RequestException as e:
                flash(f"Error communicating with the AI model: {e}", "danger")
        else:
            flash("No file selected. Please upload a file.", "warning")
    
    return render_template('diet-help.html', result=result)

@app.route('/scan-label')
def scan_label():
    result = None
    if request.method == "POST":
        # Get the uploaded file
        file = request.files.get("report")
        if file:
            try:
                # Send the file to the API endpoint
                response = requests.post(FASTAPI_URL_2, files={"file": (file.filename, file.read(), file.mimetype)})
                
                if response.status_code == 200:
                    result = response.json()
                else:
                    flash(
                        f"Error: API returned status code {response.status_code}. Please try again later.",
                        "danger"
                    )
            except requests.exceptions.RequestException as e:
                flash(f"Error communicating with the AI model: {e}", "danger")
        else:
            flash("No file selected. Please upload a file.", "warning")
    
    return render_template('scan-label.html', result=result)

if __name__ == '__main__':
    app.run(debug=True, port=5001)