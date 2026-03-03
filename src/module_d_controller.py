import time
import sys
import msvcrt
import threading
from pynput.mouse import Button, Controller
import module_a_vision
import module_b_brain
import module_c_cloud

def _timed_input(prompt_text, timeout=10):
    """
    Non-blocking input with timeout to protect against Dynamic UI Shifts.
    Windows-only relying on msvcrt.
    """
    print(prompt_text, end='', flush=sys.stdout)
    start_time = time.time()
    result = ""
    while True:
        if msvcrt.kbhit():
            char = msvcrt.getwche()
            if char in ('\r', '\n'):
                print()
                return result
            elif char == '\x08': # backspace
                if len(result) > 0:
                    result = result[:-1]
                    print(" \x08", end="", flush=True)
            else:
                result += char
        if time.time() - start_time > timeout:
            print()
            return None
        time.sleep(0.05)

def run_it_support_task(user_issue):
    mouse = Controller()
    
    print(f"\n--- Starting IT Support Task (Enterprise Gen) ---")
    print(f"User Issue: '{user_issue}'")
    
    # 1. Capture screen with inline memory optimization and multi-monitor extraction
    screenshot_bytes, monitor_bounds = module_a_vision.capture_screen(return_bytes=True)
    
    # 2. Extract Coordinates (bypassing slow file IO)
    coords = module_b_brain.get_ui_coordinates(screenshot_bytes, user_issue)
    
    if not coords:
        print("Failed to identify the correct UI element.")
        return
        
    x = coords.get("x", 0)
    y = coords.get("y", 0)
    width = coords.get("width", 0)
    height = coords.get("height", 0)
    
    # 3. Coordinate Bounds Validation (Multi-monitor scale check)
    if x < 0 or y < 0 or x > monitor_bounds["width"] or y > monitor_bounds["height"]:
        print(f"[ERROR] Coordinate Out-of-Bounds Detected: ({x}, {y}). Action intercepted to prevent catastrophic mis-click.")
        module_c_cloud.log_ticket(user_issue, coords, "OUT_OF_BOUNDS_ERROR", system_meta={"monitor": monitor_bounds})
        return
        
    # Scale bounds into absolute Virtual Screen coordinates
    abs_x = monitor_bounds["left"] + x
    abs_y = monitor_bounds["top"] + y
    
    center_x = abs_x + (width // 2)
    center_y = abs_y + (height // 2)
    
    print(f"\nTarget area identified: {x}, {y} | Dimensions: {width}x{height}")
    print(f"Scaled Absolute Target Point: ({center_x}, {center_y})")
    
    # 4. Highlight UI element asynchronously
    module_a_vision.draw_glass_box(abs_x, abs_y, width, height, duration=5000)
    
    # 5. Non-blocking Authorization with Timeout (Dynamic UI Shift Protection)
    print("\n" + "="*50)
    print("WARNING: You have 10 seconds to authorize before forced abort for UI sync protection.")
    user_input = _timed_input("Do you authorize the agent to click here? [Y/N, Enter=Y]: ", timeout=10)
    
    if user_input is None:
        print("\n[TIMEOUT] Authorization timed out. Aborted to prevent clicking shifted UI.")
        module_c_cloud.log_ticket(user_issue, coords, "TIMEOUT_ABORTED", system_meta={"monitor": monitor_bounds})
        return
        
    if user_input.strip().upper() == 'N':
        print("Action aborted by user.")
        module_c_cloud.log_ticket(user_issue, coords, "REJECTED_BY_USER", system_meta={"monitor": monitor_bounds})
        return
        
    # 6. Proceed securely to click
    print(f"Authorization granted. Moving mouse to ({center_x}, {center_y})...")
    
    mouse.position = (center_x, center_y)
    time.sleep(0.5)
    mouse.click(Button.left, 1)
    
    # 7. Log enterprise audit securely
    module_c_cloud.log_ticket(
        user_issue, 
        coords, 
        "AUTHORIZED", 
        system_meta={
            "monitor_bounds": monitor_bounds, 
            "resolution": f"{monitor_bounds['width']}x{monitor_bounds['height']}"
        }
    )
    print("Left click performed. Task complete.")

if __name__ == "__main__":
    test_issue = "I am ready to send my application but I can't find the finish button."
    run_it_support_task(test_issue)
