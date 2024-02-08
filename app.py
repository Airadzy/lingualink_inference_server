from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import Cambridge_API

app = Flask(__name__)
CORS(app)


@app.route("/generate-quiz", methods=["POST"])
@cross_origin()
def generate_quiz_file():
    json_file_path = request.get_json()
    quiz_data = Cambridge_API.model(json_file_path)
    return jsonify(quiz_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
