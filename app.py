from flask import Flask, jsonify, request
import Cambridge_API

app = Flask(__name__)


@app.route("/generate-quiz", methods=["POST"])
def generate_quiz_file():
    json_file_path = request.get_json()
    quiz_data = Cambridge_API.model(json_file_path)
    return jsonify(quiz_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
