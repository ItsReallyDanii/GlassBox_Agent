import os
import json
from google import genai
from google.genai import types
from typing import Dict, Optional

def get_ui_coordinates(image_path: str, user_issue: str) -> Optional[Dict[str, int]]:
    """
    Uses Gemini 3.0 Pro to analyze a screenshot and identify the UI element 
    needed to resolve the user's issue. Returns coordinates in JSON format.
    """
    # 1. API Configuration (Using environment variable for security)
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        return None
        
    client = genai.Client(api_key=api_key)

    # 2. Upload the screenshot to the Gemini API
    print(f"Uploading image {image_path} to Gemini...")
    try:
         captured_file = client.files.upload(file=image_path)
    except Exception as e:
         print(f"Failed to upload image: {e}")
         return None

    # 3. Prompt Setup
    # Instructing the model specifically for UI detection and JSON formatting
    prompt = f"""
    Analyize this screenshot. The user is reporting the following issue: "{user_issue}"
    
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
            contents=[captured_file, prompt]
        )
        
        # 5. Parse the JSON response
        text_response = response.text.strip()
        
        # Handle cases where the model might still wrap in markdown code blocks
        if text_response.startswith("```"):
            # Extract content from inside triple backticks
            lines = text_response.splitlines()
            # Find the first line that is just "```json" or "```"
            start_idx = 1 if lines[0].startswith("```") else 0
            # Find the last line that is "```"
            if lines[-1].strip() == "```":
                text_response = "\n".join(lines[start_idx:-1]).strip()
            else:
                text_response = "\n".join(lines[start_idx:]).strip()

        coordinates = json.loads(text_response)
        print(f"Element identified: {coordinates}")
        return coordinates

    except Exception as e:
        print(f"Failed to retrieve or parse coordinates: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Raw Response: {response.text}")
        return None

if __name__ == "__main__":
    # Test case: Finding the "Submit" button in a local screenshot
    # Note: Requires a valid GOOGLE_API_KEY environment variable
    test_image = "current_screen.png"
    test_issue = "I am ready to send my application but I can't find the finish button."
    
    if os.path.exists(test_image):
        coords = get_ui_coordinates(test_image, test_issue)
        if coords:
            print(f"Successfully found coordinates: {coords}")
        else:
            print("Failed to find UI element.")
    else:
        print(f"Please run module_a_vision.py first to generate {test_image}")
