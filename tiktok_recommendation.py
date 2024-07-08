import torch
import cv2
import numpy as np
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import os

# Load YOLOv5 model from torch.hub
print("Loading YOLOv5 model...")
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)  # Using a smaller model for speed
print("Model loaded.")

# Define a list of consumer items to prioritize (excluding 'person')
consumer_items = [
    'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
    'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
    'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe',
    'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard',
    'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
    'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich',
    'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
    'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard',
    'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase',
    'scissors', 'teddy bear', 'hair drier', 'toothbrush'
]

# Google Custom Search API credentials
API_KEY = 'AIzaSyAGLJPsiwPOpv0QacWTsXW-Og7H3zQW-rc'
SEARCH_ENGINE_ID = '22350c10cd0c04cda'

# Function to get the main item and its color in the video
def get_main_item(video_path, frame_skip=5):
    print(f"Opening video file: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video file.")
        return None
    
    item_counts = {}
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        if frame_count % frame_skip != 0:
            continue  # Skip frames
        
        print(f"Processing frame {frame_count}...")
        
        # Object detection
        results = model(frame)
        
        if hasattr(results, 'names'):
            labels = results.names
        else:
            labels = model.names  # Fallback to model's names if available
        
        print(f"Labels: {labels}")
        
        frame_height, frame_width = frame.shape[:2]
        center_x, center_y = frame_width / 2, frame_height / 2
        
        for *xyxy, conf, cls in results.xyxy[0].tolist():
            class_id = int(cls)
            class_name = labels[class_id] if class_id < len(labels) else f"unknown_{class_id}"
            print(f"Detected {class_name} with confidence {conf}")
            
            # Only count items in the consumer_items list
            if class_name in consumer_items:
                x1, y1, x2, y2 = map(int, xyxy)
                object_img = frame[y1:y2, x1:x2]
                
                # Calculate the distance from the center of the frame
                object_center_x = (x1 + x2) / 2
                object_center_y = (y1 + y2) / 2
                distance_from_center = np.sqrt((object_center_x - center_x)**2 + (object_center_y - center_y)**2)
                
                # Normalize the distance and determine weight
                max_distance = np.sqrt(center_x**2 + center_y**2)
                weight = 1 - (distance_from_center / max_distance)
                
                # Detect the predominant color of the object
                color = detect_color(object_img)
                item_key = f"{class_name} ({color})"
                
                # Weighted counting
                item_counts[item_key] = item_counts.get(item_key, 0) + weight
    
    cap.release()
    
    if not item_counts:
        print("No items detected in the video.")
        return None
    
    # Return the most frequent item detected
    main_item = max(item_counts, key=item_counts.get)
    return main_item

# Function to detect the predominant color in an image
def detect_color(image):
    # Convert image to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Resize image to a small size for faster processing
    resized_img = cv2.resize(image_rgb, (25, 25), interpolation=cv2.INTER_AREA)
    # Convert image to a 2D array of pixels
    pixels = resized_img.reshape(-1, 3)
    
    # Get the most frequent color
    counts = {}
    for pixel in pixels:
        pixel_tuple = tuple(pixel)
        counts[pixel_tuple] = counts.get(pixel_tuple, 0) + 1
    
    # Get the color with the highest count
    predominant_color = max(counts, key=counts.get)
    
    # Convert RGB to a color name
    color_name = get_color_name(predominant_color)
    
    return color_name

# Function to convert RGB color to a color name
def get_color_name(rgb_color):
    # Simplified color naming function
    r, g, b = rgb_color
    if r > 200 and g < 50 and b < 50:
        return "red"
    elif r < 50 and g > 200 and b < 50:
        return "green"
    elif r < 50 and g < 50 and b > 200:
        return "blue"
    elif r > 200 and g > 200 and b < 50:
        return "yellow"
    elif r > 200 and g < 50 and b > 200:
        return "pink"
    elif r < 50 and g > 200 and b > 200:
        return "cyan"
    elif r > 200 and g > 200 and b > 200:
        return "white"
    elif r < 50 and g < 50 and b < 50:
        return "black"
    else:
        return "unknown"

# Function to search Google for a product using the detected keyword
def search_google(keyword):
    # Modify the search query to increase chances of product links
    search_query = f'{keyword} buy OR shop OR price OR Amazon OR eBay'
    search_url = f'https://www.googleapis.com/customsearch/v1?q={search_query}&key={API_KEY}&cx={SEARCH_ENGINE_ID}'
    response = requests.get(search_url)

    if response.status_code == 200:
        search_results = response.json()
        items = search_results.get('items', [])
        products = [{'title': item['title'], 'link': item['link'], 'image': extract_image(item['link'])} for item in items]
        return products
    else:
        print(f"Error: {response.status_code}")
        return None

# Function to extract image from the provided link
def extract_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Adjust the following selector based on the common structure for product images
            image_tag = soup.find('img')
            if image_tag and image_tag.get('src'):
                return image_tag['src']
        return None
    except Exception as e:
        print(f"Error extracting image from {url}: {e}")
        return None

# Function to save images locally
def save_images(products):
    if not os.path.exists('product_images'):
        os.makedirs('product_images')
    
    for i, product in enumerate(products):
        image_url = product.get('image')
        if image_url:
            try:
                response = requests.get(image_url)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    img_path = os.path.join('product_images', f"product_{i+1}.jpg")
                    img.save(img_path)
                    print(f"Image saved to {img_path}")
            except Exception as e:
                print(f"Error saving image from {image_url}: {e}")

# Main function to process the video, identify the main item, and search for the product
def process_video(video_path):
    main_item = get_main_item(video_path)
    if main_item:
        print(f"Main item detected: {main_item}")
        products = search_google(main_item)
        if products:
            print("Products found:")
            for product in products:
                print(f"Title: {product['title']}, Link: {product['link']}, Image: {product['image']}")
            save_images(products)
        else:
            print("No products found.")
    else:
        print("No items detected in the video.")

# Example usage
video_path = '/Users/yusutong/Downloads/tiktok_video.mp4'  # Replace with your actual path
process_video(video_path)