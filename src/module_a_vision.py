import tkinter as tk
import mss
import time

def capture_screen(filename="current_screen.png"):
    """
    Takes a full screen capture using mss and saves it locally.
    This avoids the dependency issues associated with PyAutoGUI/Pillow on Python 3.14.
    """
    print("Capturing screen state using mss...")
    with mss.mss() as sct:
        # captures the primary monitor and saves to filename
        sct.shot(output=filename)
    
    print(f"Screenshot saved as {filename}")
    return filename

def draw_glass_box(x, y, width, height, duration=3000):
    """
    Draws a transparent red box on the screen to highlight the UI element.
    duration is in milliseconds (3000 = 3 seconds).
    """
    print(f"Highlighting UI element at Coordinates: ({x}, {y})...")
    
    # Initialize the transparent window
    root = tk.Tk()
    root.overrideredirect(True) # Removes the standard window borders/close buttons
    root.attributes("-alpha", 0.4) # Sets transparency (0.0 to 1.0)
    root.attributes("-topmost", True) # Forces the box to stay on top of all other windows
    
    # Create the red highlight box
    canvas = tk.Canvas(root, width=width, height=height, bg='red', highlightthickness=3, highlightbackground='darkred')
    canvas.pack()
    
    # Position the box on the screen using the X/Y coordinates
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Tell the window to destroy itself after the duration expires
    root.after(duration, root.destroy)
    root.mainloop()

if __name__ == "__main__":
    # TEST 1: Take a screenshot
    capture_screen()
    
    # TEST 2: Draw a Glass Box at coordinate (100, 100) for 3 seconds
    time.sleep(1) # Brief pause before drawing
    draw_glass_box(x=100, y=100, width=250, height=75, duration=3000)
    print("Module A Test Complete.")
