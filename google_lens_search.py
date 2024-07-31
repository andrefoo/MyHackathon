import requests
import os
import json
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Retrieve the SERPAPI API key from environment variables
SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')

if not SERPAPI_API_KEY:
    raise ValueError("SERPAPI_API_KEY must be set in the .env file.")

def save_to_json(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data saved to {filename}")

def google_lens_search(image_url):
    """
    Perform a Google Lens search using the given image URL.

    Parameters:
    image_url (str): The URL of the image to search.

    Returns:
    list: A list of visual matches if the search is successful, None otherwise.
    """
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_lens",
        "url": image_url,
        "api_key": SERPAPI_API_KEY
    }

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        visual_matches = data.get('visual_matches', [])
        return visual_matches
    else:
        print("Failed to search image", response.text)
        return None

