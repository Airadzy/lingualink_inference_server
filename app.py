from flask import Flask, jsonify, request, make_response
import Cambridge_API
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/generate-quiz", methods=["POST"])
def generate_quiz_file():
    json_file_path = request.get_json()
    quiz_data = Cambridge_API.model(json_file_path)
    response = make_response(jsonify(quiz_data))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
