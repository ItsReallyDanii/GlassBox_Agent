import time
from pynput.mouse import Button, Controller
import module_a_vision
import module_b_brain
import module_c_cloud

def run_it_support_task(user_issue):
    mouse = Controller()
    
    print(f"\n--- Starting IT Support Task ---")
    print(f"User Issue: '{user_issue}'")
    
    # 1. Capture the screen
    screenshot_path = module_a_vision.capture_screen()
    
    # 2. Pass image to Brain and get JSON coordinates
    coords = module_b_brain.get_ui_coordinates(screenshot_path, user_issue)
    
    if not coords:
        print("Failed to identify the correct UI element.")
        return
        
    # 3. Extract exact X and Y coordinates (calculating center)
    x = coords.get("x", 0)
    y = coords.get("y", 0)
    width = coords.get("width", 0)
    height = coords.get("height", 0)
    
    center_x = x + (width // 2)
    center_y = y + (height // 2)
    
    print(f"\nTarget area identified: {x}, {y} | Dimensions: {width}x{height}")
    print(f"Target center point calculated at: ({center_x}, {center_y})")
    
    # 4. Call Module A to draw the red glass box
    # The draw_glass_box function will highlight the element for 3 seconds then return
    module_a_vision.draw_glass_box(x, y, width, height, duration=3000)
    
    # 5. Pause terminal and ask the user for authorization
    print("\n" + "="*50)
    user_input = input("Do you authorize the agent to click here? (Press Enter for Yes, type 'N' for No): ")
    
    if user_input.strip().upper() == 'N':
        print("Action aborted by user.")
        module_c_cloud.log_ticket(user_issue, coords, "REJECTED_BY_USER")
        return
        
    # 6. Move mouse to coordinates and perform a left click
    print(f"Authorization granted. Moving mouse to ({center_x}, {center_y})...")
    
    # Move mouse
    mouse.position = (center_x, center_y)
    
    # Slight pause to let human eye track the move before clicking
    time.sleep(0.5)
    
    # Perform left click
    mouse.click(Button.left, 1)
    
    # 7. Log to Cloud Database
    module_c_cloud.log_ticket(user_issue, coords, "AUTHORIZED")
    
    print("Left click performed. Task complete.")

if __name__ == "__main__":
    # Test execution
    test_issue = "I am ready to send my application but I can't find the finish button."
    run_it_support_task(test_issue)
