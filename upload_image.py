import os
import base64
import requests
import sys
from dotenv import load_dotenv


load_dotenv()

IMG_API_KEY = os.getenv('IMG_API_KEY')

if not IMG_API_KEY:
    raise ValueError("IMG_API_KEY must be set in the .env file.")

def upload_image_to_imgbb(image_path):
    url = "https://api.imgbb.com/1/upload"
    with open(image_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        payload = {
            'key': IMG_API_KEY,
            'image': encoded_image
        }
        response = requests.post(url, data=payload)
    
    if response.status_code == 200:
        return response.json()['data']['url']
    else:
        print("Failed to upload image", response.text)
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <filepath>")
    else:
        upload_image_to_imgbb(sys.argv[1])
