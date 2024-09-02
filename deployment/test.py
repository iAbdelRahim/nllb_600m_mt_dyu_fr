import requests
import json
import time

# Define the URL for the inference endpoint
url = "http://0.0.0.0:8080/v2/models/model/infer"

# Define the input data for the model
input_data = {
    "inputs": [
        {
            "name": "input-0",
            "shape": [1],
            "datatype": "BYTES",
            "data": ["i tɔgɔ bi cogodɔ"]
        }
    ]
}

# Function to send POST request with retries
def send_request(url, data, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(data))
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(delay)
    return None

# Send the POST request to the model server
response = send_request(url, input_data)

# Print the response from the server
if response:
    print(response)
else:
    print("Failed to get a response from the server.")
