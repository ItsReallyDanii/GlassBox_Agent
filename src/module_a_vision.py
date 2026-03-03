import tkinter as tk
import mss
import mss.tools
import time
import threading

def capture_screen(filename="current_screen.png", return_bytes=False):
    """
    Takes a full screen capture using mss.
    Returns the file path or raw image bytes based on return_bytes.
    Memory-optimized for inline base64 image processing.
    """
    print("Capturing screen state using mss...")
    with mss.mss() as sct:
        # captures the primary monitor and saves to filename
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        
        if return_bytes:
            print("Returning raw inline bytes for memory-optimized LLM analysis.")
            png_bytes = mss.tools.to_png(screenshot.rgb, screenshot.size)
            return png_bytes, monitor
            
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=filename)
    
    print(f"Screenshot saved as {filename}")
    return filename, monitor

def _draw_box_thread(x, y, width, height, duration):
    # Initialize the transparent window
    root = tk.Tk()
    root.overrideredirect(True) # Removes the standard window borders/close buttons
    root.attributes("-alpha", 0.4) # Sets transparency (0.0 to 1.0)
    root.attributes("-topmost", True) # Forces the box to stay on top of all other windows
    
    # Create the red highlight box
    canvas = tk.Canvas(root, width=width, height=height, bg='red', highlightthickness=3, highlightbackground='darkred')
    canvas.pack()
    
    # Position the box on the screen using the absolute X/Y coordinates
    # Forcing geometry to properly format signs for negative coordinate scaling
    x_str = f"+{int(x)}" if int(x) >= 0 else f"{int(x)}"
    y_str = f"+{int(y)}" if int(y) >= 0 else f"{int(y)}"
    root.geometry(f"{int(width)}x{int(height)}{x_str}{y_str}")
    
    # Tell the window to destroy itself after the duration expires
    root.after(duration, root.destroy)
    root.mainloop()

def draw_glass_box(x, y, width, height, duration=3000):
    """
    Draws a transparent red box on the screen to highlight the UI element.
    Uses daemon background threading to decouple the UI from blocking the controller.
    """
    print(f"Highlighting UI element at Coordinates: ({x}, {y})...")
    thread = threading.Thread(target=_draw_box_thread, args=(x, y, width, height, duration), daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    # TEST 1: Take a screenshot (bytes mode)
    img_bytes, _ = capture_screen(return_bytes=True)
    
    # TEST 2: Draw a Glass Box concurrently
    time.sleep(1)
    draw_glass_box(x=100, y=100, width=250, height=75, duration=3000)
    print("Module A Test Complete. You should see the box rendering asynchronously.")
    time.sleep(3.5)
