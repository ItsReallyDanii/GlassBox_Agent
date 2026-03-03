import os
import json
import base64
import requests
from typing import Dict, Optional, Union, Any

CLOUD_RUN_URL = "https://glassbox-brain-454249288947.us-central1.run.app/"

def get_ui_coordinates(image_source: Union[str, bytes], user_issue: str) -> Optional[Dict[str, Any]]:
    """
    Thin client to communicate with the Cloud Run Gemini backend.
    Takes memory-optimized inline bytes (or a file path) and returns JSON coordinates.
    """
    if not isinstance(image_source, (str, bytes)):
        print(f"Error: Invalid image_source type: {type(image_source)}")
        return None

    # 1. Base64 Encode the Image Paylaod
    if isinstance(image_source, bytes):
        try:
            image_b64 = base64.b64encode(image_source).decode('utf-8')
            print("Successfully encoded raw bytes to base64.")
        except Exception as e:
            print(f"Failed to encode raw bytes: {e}")
            return None
    else:
        try:
            with open(image_source, "rb") as f:
                image_bytes = f.read()
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            print(f"Successfully read and encoded file: {image_source}")
        except Exception as e:
            print(f"Failed to read image file {image_source}: {e}")
            return None

    # 2. Prepare JSON Payload
    payload = {
        "image_b64": image_b64,
        "user_issue": user_issue
    }
    
    headers = {
        "Content-Type": "application/json"
    }

    # 3. Transmit Payload to Cloud Run
    print(f"Contacting Cloud Run Backend at {CLOUD_RUN_URL}...")
    try:
        response = requests.post(CLOUD_RUN_URL, json=payload, headers=headers)
        
        # 4. Robust Error Decoding
        if response.status_code != 200:
            print(f"HTTP ERROR: Cloud Run server returned status code {response.status_code}")
            try:
                print(f"Raw Server Response:\n{response.text}")
            except Exception:
                pass
            return None

        response_data = response.json()
        print(f"Parsed Server JSON Response metadata: {response_data.get('element_description', 'No description found')}")

        if "error" in response_data:
            print(f"Server returned an explicit error object: {response_data['error']}")
            return None
            
        required_keys = ["x", "y", "width", "height"]
        if not all(k in response_data for k in required_keys):
            print(f"ValidationError: Response is missing coordinate keys. Expected {required_keys}, Got: {list(response_data.keys())}")
            return None
            
        print("Coordinates successfully matched!")
        return response_data

    except requests.exceptions.RequestException as e:
        print(f"Network Request Failed. Could not reach {CLOUD_RUN_URL}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to parse server response as JSON: {e}")
        try:
            if hasattr(response, 'text'):
                print(f"Raw Invalid Output:\n{response.text}")
        except Exception:
            pass
        return None

if __name__ == "__main__":
    if os.path.exists("current_screen.png"):
        coords = get_ui_coordinates("current_screen.png", "Test issue")
        print(f"Coords: {coords}")
