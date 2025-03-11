from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/generate_recipe', methods=['POST'])
def generate_recipe():
    """Generate a recipe based on provided ingredients using Google Gemini."""
    data = request.get_json()
    ingredients = data.get("ingredients", [])

    if not ingredients:
        return jsonify({"error": "No ingredients provided"}), 400

    prompt = f"Suggest a simple, delicious recipe using these ingredients: {', '.join(ingredients)}. Keep it clear and short."

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")  # "gemini-1.5-pro" is another option
        response = model.generate_content(prompt)

        recipe = response.text.strip()
        return jsonify({"recipe": recipe})

    except Exception as e:
        print("Error:", e)  # Debugging
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
