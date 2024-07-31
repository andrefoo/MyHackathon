import torch
import cv2
import numpy as np
import aiohttp
import asyncio
import logging
import sys
import viewer
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv
from collections import Counter, defaultdict
from sklearn.cluster import KMeans
import yaml
import requests
from google_lens_search import google_lens_search
import upload_image
# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('API_KEY')

SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')

if not API_KEY or not SEARCH_ENGINE_ID:
    raise ValueError("API_KEY and SEARCH_ENGINE_ID must be set in the .env file.")

# Load configuration
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the YOLOv5 model
model = None

def load_yolo_model():
    global model
    if model is None:
        logging.info("Loading YOLOv5 model...")
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        logging.info("Model loaded.")
    return model

# List of consumer items to prioritize (excluding 'person')
consumer_items = config['consumer_items']

all_consumer_items = []
for category in consumer_items.values():
    all_consumer_items.extend(category)

def get_main_item(video_path, model, frame_skip=5):
    """Get the main item and its color in the video, and return the frame with the main item highlighted."""
    logging.info(f"Opening video file: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.error("Could not open video file.")
        return None
    
    person_coordinates = []
    object_distances = defaultdict(list)
    color_counts = defaultdict(Counter)
    frame_count = 0
    main_item_frame = None
    main_item_coordinates = None
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        if frame_count % frame_skip != 0:
            continue  # Skip frames
        
        logging.info(f"Processing frame {frame_count}...")
        
        # Object detection
        results = model(frame)

        # Process results if any detected objects
        if len(results.xyxy[0]) > 0:
            labels = results.names if hasattr(results, 'names') else model.names
            
            for *xyxy, conf, cls in results.xyxy[0].tolist():
                class_id = int(cls)
                class_name = labels[class_id] if class_id < len(labels) else f"unknown_{class_id}"
                logging.info(f"Detected {class_name} with confidence {conf}")
                
                x1, y1, x2, y2 = map(int, xyxy)
                object_center_x = (x1 + x2) / 2
                object_center_y = (y1 + y2) / 2
                
                if class_name == 'person':
                    person_coordinates.append((object_center_x, object_center_y))
                elif class_name in all_consumer_items:
                    object_img = frame[y1:y2, x1:x2]
                    color = detect_color(object_img)
                    item_key = f"{class_name} ({color})"
                    color_counts[class_name][color] += 1
                    object_distances[class_name].append((object_center_x, object_center_y))
                    
                    # Save the frame with the detected main item
                    if main_item_frame is None:
                        main_item_frame = frame.copy()
                        main_item_coordinates = (x1, y1, x2, y2)
                        cv2.rectangle(main_item_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(main_item_frame, item_key, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    cap.release()
    
    if not person_coordinates or not object_distances:
        logging.info("No persons or objects detected in the video.")
        return None
    
    # Calculate the minimum distance between each object and the nearest person
    min_distances = {}
    for class_name, coords in object_distances.items():
        min_distance = float('inf')
        for obj_x, obj_y in coords:
            for person_x, person_y in person_coordinates:
                distance = np.sqrt((obj_x - person_x)**2 + (obj_y - person_y)**2)
                if distance < min_distance:
                    min_distance = distance
        min_distances[class_name] = min_distance
    
    # Determine the main item by the smallest minimum distance to a person
    main_item = min(min_distances, key=min_distances.get)
    
    # Determine the most frequent color for the main item
    main_color = color_counts[main_item].most_common(1)[0][0]
    
    # Create a summary of other detected items
    other_items_summary = {item: dict(color_counts[item]) for item in color_counts if item != main_item}
    
    return {
        "main_item": f"{main_item} ({main_color})",
        "other_items_summary": other_items_summary,
        "main_item_frame": main_item_frame,
        "main_item_coordinates": main_item_coordinates
    }

def get_color_name(rgb_color):
    """Convert RGB color to a color name."""
    r, g, b = rgb_color
    color_thresholds = {
        "red": (200, 50, 50),
        "green": (50, 200, 50),
        "blue": (50, 50, 200),
        "yellow": (200, 200, 50),
        "magenta": (200, 50, 200),
        "cyan": (50, 200, 200),
        "white": (150, 150, 150),
        "black": (100, 100, 100),
        "orange": (200, 100, 50),
        "lime": (100, 200, 50),
        "violet": (150, 50, 150),
    }

    color_diffs = {color: np.linalg.norm(np.array(rgb_color) - np.array(threshold)) for color, threshold in color_thresholds.items()}
    closest_color = min(color_diffs, key=color_diffs.get)
    
    return closest_color

def detect_color(image, k=3):
    """Detect the predominant color in an image."""
    try:
        # Convert the image from BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize the image to speed up processing while maintaining aspect ratio
        height, width, _ = image_rgb.shape
        aspect_ratio = width / height
        new_height = 50
        new_width = int(aspect_ratio * new_height)
        resized_img = cv2.resize(image_rgb, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # Flatten the image pixels
        pixels = resized_img.reshape(-1, 3)
        
        # Initialize and fit KMeans
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(pixels)
        
        # Find the most common cluster
        most_common = Counter(kmeans.labels_).most_common(1)
        dominant_color = kmeans.cluster_centers_[most_common[0][0]]
        
        # Get the color name
        color_name = get_color_name(dominant_color)
        
        return color_name
    except Exception as e:
        logging.error(f"Error detecting color: {e}")
        return "unknown"

async def fetch(session, url):
    """Fetch the content from a URL."""
    try:
        async with session.get(url) as response:
            return await response.json()
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

async def search_google(keyword):
    """Search Google for a product using the detected keyword."""
    search_query = f'{keyword} buy OR shop OR price OR Amazon OR eBay'
    search_url = f'https://www.googleapis.com/customsearch/v1?q={search_query}&key={API_KEY}&cx={SEARCH_ENGINE_ID}'
    
    async with aiohttp.ClientSession() as session:
        response_json = await fetch(session, search_url)
        if response_json:
            items = response_json.get('items', [])
            products = [{'title': item['title'], 'link': item['link'], 'image': await extract_image(item['link'])} for item in items]
            return products
        return None

async def extract_image(url):
    """Extract the image URL from a given webpage URL."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    soup = BeautifulSoup(await response.text(), 'html.parser')
                    image_tag = soup.find('img')
                    if image_tag and image_tag.get('src'):
                        return image_tag['src']
        return None
    except Exception as e:
        logging.error(f"Error extracting image from {url}: {e}")
        return None

def save_images(products):
    """Save product images locally."""
    if not os.path.exists('product_images'):
        os.makedirs('product_images')
    
    for i, product in enumerate(products):
        image_url = product.get('image')
        if image_url:
            try:
                response = requests.get(image_url)
                if response.status == 200:
                    img = Image.open(BytesIO(response.content))
                    img_path = os.path.join('product_images', f"product_{i+1}.jpg")
                    img.save(img_path)
                    logging.info(f"Image saved to {img_path}")
            except Exception as e:
                logging.error(f"Error saving image from {image_url}: {e}")

async def process_video(video_path,video):
    """Process the video, identify the main item, and search for the product."""
    model = load_yolo_model()
    detection_summary = get_main_item(video_path, model)
    if detection_summary:
        main_item = detection_summary["main_item"]
        other_items_summary = detection_summary["other_items_summary"]
        main_item_frame = detection_summary["main_item_frame"]
        main_item_coordinates = detection_summary["main_item_coordinates"]

        logging.info(f"\nMain item detected: {main_item}\n")
        
        sorted_other_items = sorted(other_items_summary.items(), key=lambda x: sum(x[1].values()), reverse=True)
        logging.info("Other items detected (sorted by weight):")
        for item, colors in sorted_other_items:
            colors_str = ', '.join([f"{color}: {weight:.2f}" for color, weight in colors.items()])
            logging.info(f"{item}: {colors_str}")
        
        # Save the cropped main item
        if main_item_coordinates:
            x1, y1, x2, y2 = main_item_coordinates
            cropped_main_item = main_item_frame[y1:y2, x1:x2]
            cropped_path = './cropped_main_item_'+video.split('.')[0]+'.jpg'
            cv2.imwrite(cropped_path, cropped_main_item)
            logging.info(f"Cropped main item saved to {cropped_path}")
        
        # products = await search_google(main_item)
        # if products:
        #     logging.info("\nProducts found:")
        #     for product in products:
        #         logging.info(f"Title: {product['title']}\nLink: {product['link']}\nImage: {product['image']}\n")
        #     save_images(products)f
        # else:
        #     logging.info("No products found.")
    else:
        logging.info("No items detected in the video.")


def main(video):
    video_path = './src/videos/' + video  # Replace with your actual path

    if not os.path.exists(video_path):
        logging.error("Video file not found.")
        sys.exit(1)

    image_path = './cropped_main_item_'+video.split('.')[0]+'.jpg'
    image_url = None
    if not os.path.exists(image_path):
        asyncio.run(process_video(video_path,video))
    
    image_url = upload_image.upload_image_to_imgbb(image_path)
    return image_url

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <video file name>")
    else:
        main(sys.argv[1])