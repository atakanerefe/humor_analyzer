from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import base64
import io

# Load API key from .env file
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

# Ensure an 'uploads' directory exists
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/analyze_meme', methods=['POST'])
def analyze_meme():
    """Analyze a meme and explain its humor."""
    if "meme" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["meme"]
    
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save image
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        # Convert image to base64
        with open(filepath, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode("utf-8")

        # Send image to Gemini API
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            ["Explain why this meme is funny. Describe any cultural, linguistic, or visual humor it uses.", 
            {"mime_type": "image/jpeg", "data": image_base64}]
        )

        explanation = response.text.strip()
        return jsonify({"explanation": explanation, "image_url": filepath})

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
