from flask import Flask, render_template, request, jsonify
from ela_engine import perform_ela

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    img_file = request.files["image"]
    quality = int(request.form.get("quality", 75))
    amp = int(request.form.get("amplification", 15))

    img_bytes = img_file.read()
    data = perform_ela(img_bytes, quality, amp)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
