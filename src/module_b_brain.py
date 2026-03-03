import os
import json
from google import genai
from google.genai import types
from typing import Dict, Optional, Union

def get_ui_coordinates(image_source: Union[str, bytes], user_issue: str) -> Optional[Dict[str, int]]:
    """
    Uses Gemini 3.0 Pro to analyze a screenshot and identify the UI element 
    needed to resolve the user's issue. Returns coordinates in JSON format.
    Optimized to support raw memory bytes (inline base64 processing) to prevent
    leakage on Google file storage.
    """
    # 1. API Configuration
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        return None
        
    client = genai.Client(api_key=api_key)

    # 2. Upload / Format image representation
    if isinstance(image_source, bytes):
        print("Uploading image to Gemini via highly-optimized inline base64 processing...")
        gemini_image = types.Part.from_bytes(data=image_source, mime_type="image/png")
    else:
        print(f"Uploading image {image_source} to Gemini via files.upload...")
        try:
             gemini_image = client.files.upload(file=image_source)
        except Exception as e:
             print(f"Failed to upload image: {e}")
             return None

    # 3. Prompt Setup
    prompt = f"""
    Analyze this screenshot. The user is reporting the following issue: "{user_issue}"
    
    Identify the single most relevant UI element (button, link, field, etc.) that the user should interact with to resolve this.
    
    Return ONLY a raw JSON object with the bounding box coordinates of that element. 
    Use the following schema:
    {{
      "x": integer,
      "y": integer,
      "width": integer,
      "height": integer
    }}
    
    Do not include any conversational text, markdown formatting, or explanations. Just the JSON.
    """

    # 4. Generate Content using the requested model
    print("Awaiting UI analysis from Gemini 2.5 Pro...")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[gemini_image, prompt]
        )
        
        # 5. Parse the JSON response
        text_response = response.text.strip()
        
        # Robust markdown cleanup
        if text_response.startswith("```"):
            lines = text_response.splitlines()
            start_idx = 1 if lines[0].startswith("```") else 0
            if lines[-1].strip() == "```":
                text_response = "\n".join(lines[start_idx:-1]).strip()
            else:
                text_response = "\n".join(lines[start_idx:]).strip()

        coordinates = json.loads(text_response)
        print(f"Element identified: {coordinates}")
        
        # 6. Cleanup if using File API
        if not isinstance(image_source, bytes):
            try:
                gemini_image.delete()
                print("Cleaned up File API upload to prevent resource leak.")
            except Exception:
                pass
                
        return coordinates

    except Exception as e:
        print(f"Failed to retrieve or parse coordinates: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Raw Response: {response.text}")
        return None

if __name__ == "__main__":
    # Test case: requires valid GOOGLE_API_KEY
    if os.path.exists("current_screen.png"):
        coords = get_ui_coordinates("current_screen.png", "Test issue")
        print(f"Coords: {coords}")
