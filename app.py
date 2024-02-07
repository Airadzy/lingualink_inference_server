from flask import Flask, jsonify, request
import Cambridge_API

app = Flask(__name__)


@app.route("/generate-quiz")
def generate_quiz_file():
    data = request.get_json()
    json_file_path = data.get("json_file_path", "content.json")
    quiz_data = Cambridge_API.model(json_file_path)
    return jsonify(quiz_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8080,debug=True)
