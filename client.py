import requests

url = "http://54.236.18.163:8080/generate-quiz"

data = {
    "difficulty": "B",
    "article": "A Tour of Machine Learning Algorithms Machine Learning Algorithms algorithms in the field to get a feeling of what methods are available.\n\nThere are so many algorithms that it can feel overwhelming when algorithm names are thrown around and you are expected to just know what they are and where they fit.\n\nI want to give you two ways to think about and categorize the algorithms you may come across in the field.\n\nThe first is a grouping of algorithms by their learning style."
}

response = requests.post(url, json=data)
try:
    print(response.json())
except requests.exceptions.JSONDecodeError as e:
    print("Error decoding JSON response:", e)
    print("Response text:", response.text)
