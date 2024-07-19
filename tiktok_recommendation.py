import torch
import cv2
import numpy as np
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv
from collections import Counter, defaultdict
from sklearn.cluster import KMeans

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('API_KEY')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')

if not API_KEY or not SEARCH_ENGINE_ID:
    raise ValueError("API_KEY and SEARCH_ENGINE_ID must be set in the .env file.")

# Initialize the YOLOv5 model
model = None
def load_yolo_model():
    global model
    if model is None:
        print("Loading YOLOv5 model...")
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        print("Model loaded.")
    return model

# List of consumer items to prioritize (excluding 'person')
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

def get_main_item(video_path, model, frame_skip=5):
    """Get the main item and its color in the video."""
    print(f"Opening video file: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video file.")
        return None
    
    item_counts = defaultdict(int)
    color_counts = defaultdict(Counter)
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

        # Process results if any detected objects
        if len(results.xyxy[0]) > 0:
            labels = results.names if hasattr(results, 'names') else model.names
            
            print(f"Labels: {labels}")
            
            frame_height, frame_width = frame.shape[:2]
            center_x, center_y = frame_width / 2, frame_height / 2
            
            for *xyxy, conf, cls in results.xyxy[0].tolist():
                class_id = int(cls)
                class_name = labels[class_id] if class_id < len(labels) else f"unknown_{class_id}"
                print(f"Detected {class_name} with confidence {conf}")
                
                if class_name in consumer_items:
                    x1, y1, x2, y2 = map(int, xyxy)
                    object_img = frame[y1:y2, x1:x2]
                    
                    object_center_x = (x1 + x2) / 2
                    object_center_y = (y1 + y2) / 2
                    distance_from_center = np.sqrt((object_center_x - center_x)**2 + (object_center_y - center_y)**2)
                    
                    max_distance = np.sqrt(center_x**2 + center_y**2)
                    weight = 1 - (distance_from_center / max_distance)
                    
                    color = detect_color(object_img)
                    item_key = f"{class_name} ({color})"
                    
                    item_counts[class_name] += weight
                    color_counts[class_name][color] += weight
    
    cap.release()
    
    if not item_counts:
        print("No items detected in the video.")
        return None
    
    # Determine the main item by highest weighted count
    main_item = max(item_counts, key=item_counts.get)
    
    # Determine the most frequent color for the main item
    main_color = color_counts[main_item].most_common(1)[0][0]
    
    # Create a summary of other detected items
    other_items_summary = {item: dict(color_counts[item]) for item in item_counts if item != main_item}
    
    return {
        "main_item": f"{main_item} ({main_color})",
        "other_items_summary": other_items_summary
    }

def detect_color(image, k=1):
    """Detect the predominant color in an image."""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    resized_img = cv2.resize(image_rgb, (50, 50), interpolation=cv2.INTER_AREA)
    pixels = resized_img.reshape(-1, 3)
    
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(pixels)
    most_common = Counter(kmeans.labels_).most_common(1)
    dominant_color = kmeans.cluster_centers_[most_common[0][0]]
    
    return get_color_name(dominant_color)

def get_color_name(rgb_color):
    """Convert RGB color to a color name."""
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

def search_google(keyword):
    """Search Google for a product using the detected keyword."""
    try:
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
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def extract_image(url):
    """Extract the image URL from a given webpage URL."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            image_tag = soup.find('img')
            if image_tag and image_tag.get('src'):
                return image_tag['src']
        return None
    except Exception as e:
        print(f"Error extracting image from {url}: {e}")
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
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    img_path = os.path.join('product_images', f"product_{i+1}.jpg")
                    img.save(img_path)
                    print(f"Image saved to {img_path}")
            except Exception as e:
                print(f"Error saving image from {image_url}: {e}")

def process_video(video_path):
    """Process the video, identify the main item, and search for the product."""
    model = load_yolo_model()
    detection_summary = get_main_item(video_path, model)
    if detection_summary:
        main_item = detection_summary["main_item"]
        other_items_summary = detection_summary["other_items_summary"]
        
        print(f"Main item detected: {main_item}")
        print("Other items detected:")
        for item, colors in other_items_summary.items():
            print(f"{item}: {dict(colors)}")
        
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

if __name__ == "__main__":
    video_path = './src/videos/video1.mp4'  # Replace with your actual path

    process_video(video_path)
