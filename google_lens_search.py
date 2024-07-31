import requests
import os
import json
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Retrieve the SERPAPI API key from environment variables
SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')

if not SERPAPI_API_KEY:
    logging.error("SERPAPI_API_KEY must be set in the .env file.")
    raise ValueError("SERPAPI_API_KEY must be set in the .env file.")

def save_to_json(data, video):
    filename = 'visual_matches_'+video.split('.')[0]+'.json'
    try:
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        logging.info(f"Data saved to {filename}")
    except Exception as e:
        logging.error(f"Failed to save data to {filename}: {e}")

def google_lens_search(image_url, video):
    """
    Perform a Google Lens search using the given image URL.

    Parameters:
    image_url (str): The URL of the image to search.
    output_filename (str): The filename to save the search results.

    Returns:
    list: A list of visual matches if the search is successful, None otherwise.
    """
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_lens",
        "url": image_url,
        "api_key": SERPAPI_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        visual_matches = data.get('visual_matches', [])
        logging.info(f"Google Lens search successful. Found {len(visual_matches)} visual matches.")
        save_to_json(visual_matches,video)
        return visual_matches
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logging.error(f"An error occurred: {err}")
    return None

# Example usage
if __name__ == "__main__":
    image_url = "https://example.com/image.jpg"
    output_filename = "results.json"
    results = google_lens_search(image_url, output_filename)
    if results:
        logging.info("Visual matches saved successfully.")
    else:
        logging.info("No visual matches found.")
