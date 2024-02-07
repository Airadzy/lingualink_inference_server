import requests
import json

url = "http://54.236.18.163:8080/generate-quiz"

# Read the content of the JSON file
with open("content.json", "r") as json_file:
    content = json.load(json_file)

# Send a POST request with the JSON content as data
response = requests.post(url, json=content)

# Check if the request was successful
if response.status_code == 200:
    # Print the response from the server
    print(response.json())
else:
    # Print an error message if the request failed
    print("Error:", response.text)