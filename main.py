import sys
import viewer
import os
from google_lens_search import google_lens_search
import tiktok_recommendation

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <video>")
        sys.exit(1)
    video = sys.argv[1]
    
    image_url = tiktok_recommendation.main(video)
    os.system(f"start {image_url}")

    visual_match_file = 'visual_matches_'+video.split('.')[0]+'.json'

    if not os.path.exists(visual_match_file):
        print("Visual matches not found. Searching for visual matches...")
        google_lens_search(image_url, video)
        print("Visual matches found. Please run the script again.")
    
    if os.path.exists(visual_match_file):
        viewer.main(visual_match_file)
    sys.exit(0)