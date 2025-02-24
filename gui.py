import PySimpleGUI as sg
import requests
import time
import os
import config

# File to store window position
POSITION_FILE = "window_position.txt"

def save_window_position(x, y):
    """Save current window position to a file"""
    with open(POSITION_FILE, "w") as f:
        f.write(f"{x},{y}")

def load_window_position():
    """Load saved window position from file, or return default if not available"""
    if os.path.exists(POSITION_FILE):
        with open(POSITION_FILE, "r") as f:
            try:
                x, y = map(int, f.read().strip().split(","))
                return x, y
            except Exception as e:
                print("Error loading position:", e)
    return 100, 100  # default

def sendHTTP(data):
    response = requests.get("http://172.16.32.112:8000/" + data)
    if response.status_code != 200:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
    return True

# Set Theme
sg.theme("DarkAmber")

# Load saved window position
start_x, start_y = load_window_position()

# Define the non-collapsing header
header = [[sg.Text("RF.Guru EpiCenter              Attenuator",
                    font=("Helvetica", 10), justification="center")]]

# Define dynamic content
switches = []
collapsible_layout = []
for i, val in enumerate(config.LoRaPorts):
    sw, att = config.LoRaPorts[val]
    switches.append(sw)
    buttonColor = "#83932F" if i == 0 else "#E0BC61"
    collapsible_layout.append([
        sg.Button(val, metadata=val, size=(18, 1), key="bt" + str(i), button_color=buttonColor),
        sg.Slider(orientation="horizontal", resolution=0.5, range=(0,31), size=(12,7),
                  expand_x=True, enable_events=False, disable_number_display=False,
                  default_value=att, key="sl" + str(i))
    ])

layout = header + collapsible_layout

# Create the Window at the saved position
windowTitle = "RF.Guru EpiCenter Switch"
window = sg.Window(windowTitle, layout, keep_on_top=True, grab_anywhere=True,
                   location=(start_x, start_y), finalize=True)

for i in range(len(config.LoRaPorts)):
    window["sl" + str(i)].bind("<ButtonRelease-1>", "")

# Variables for expand/collapse behavior
collapsed_height = 30       # Height when collapsed (header only)
expanded_height = 40 + (len(config.LoRaPorts) * 30)
safe_zone = 10              # Extra pixels for safe zone

# We'll track the position in our own variables
x, y = window.TKroot.winfo_x(), window.TKroot.winfo_y()
collapsed_y = y
expanded = False
dragging = False
last_hover_time = None

# Start in collapsed mode
window.TKroot.geometry(f"300x{collapsed_height}+{x}+{collapsed_y}")

while True:
    event, values = window.read(timeout=100)
    
    if event == sg.WIN_CLOSED:
        # Save the last known position (using our tracked x and y)
        save_window_position(x, y+expanded_height)
        break

    # Update current window position using TK methods
    new_x = window.TKroot.winfo_x()
    new_y = window.TKroot.winfo_y()
    if new_x != x or new_y != y:
        dragging = True
        x, y = new_x, new_y
        collapsed_y = y  # Update collapsed position
    else:
        dragging = False

    # Calculate the expanded window's top (expanding upward)
    expand_y = collapsed_y - (expanded_height - collapsed_height)
    
    # Get mouse position
    mouse_x = window.TKroot.winfo_pointerx()
    mouse_y = window.TKroot.winfo_pointery()
    win_x = window.TKroot.winfo_x()
    win_y = window.TKroot.winfo_y()
    win_width = window.TKroot.winfo_width()

    # Expand when mouse hovers over the header area (collapsed area)
    if (not dragging and 
        win_x <= mouse_x <= win_x + win_width and 
        win_y <= mouse_y <= win_y + collapsed_height):
        if not expanded:
            window.TKroot.geometry(f"300x{expanded_height}+{x}+{expand_y}")
            expanded = True
            last_hover_time = None

    # Collapse after 0.5 sec if mouse leaves the full expanded window (with safe zone)
    if (not dragging and expanded and 
        not (win_x <= mouse_x <= win_x + win_width and 
             win_y <= mouse_y <= win_y + expanded_height + safe_zone)):
        if last_hover_time is None:
            last_hover_time = time.time()
        if time.time() - last_hover_time > 0.5:
            # For collapse, we want to keep the header at the bottom of the window.
            collapsed_y = y + (expanded_height - collapsed_height)
            window.TKroot.geometry(f"300x{collapsed_height}+{x}+{collapsed_y}")
            expanded = False
            last_hover_time = None

window.close()
