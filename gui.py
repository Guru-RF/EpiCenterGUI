import PySimpleGUI as sg
import requests
import time
import os
import config

# --- Functions to save and load window position ---
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
    return 100, 100  # default position

def sendHTTP(data):
    response = requests.get("http://172.16.32.112:8000/" + data)
    if response.status_code != 200:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
    return True

# Set Theme
sg.theme("DarkAmber")

# --- Load saved position ---
start_x, start_y = load_window_position()

# --- Define layout ---
header = [[sg.Text("RF.Guru EpiCenter              Attenuator",
                    font=("Helvetica", 10), justification="center")]]
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

# --- Create window at saved position ---
windowTitle = "RF.Guru EpiCenter Switch"
window = sg.Window(windowTitle, layout, keep_on_top=True, grab_anywhere=True,
                   location=(start_x, start_y), finalize=True)

for i in range(len(config.LoRaPorts)):
    window["sl" + str(i)].bind("<ButtonRelease-1>", "")

# --- Variables for expand/collapse behavior ---
# collapsed_height: only header visible; expanded_height: full window when expanded
collapsed_height = 30
expanded_height = 40 + (len(config.LoRaPorts) * 30)
safe_zone = 10

# We'll track position using TK's winfo methods
x, y = window.TKroot.winfo_x(), window.TKroot.winfo_y()
collapsed_y = y  # When collapsed, the window's y is as-is.
expanded = False  # Initially, start in collapsed mode
dragging = False
last_hover_time = None

# Start in collapsed mode
window.TKroot.geometry(f"300x{collapsed_height}+{x}+{collapsed_y}")

# --- Main Event Loop ---
while True:
    event, values = window.read(timeout=100)
    
    if event == sg.WIN_CLOSED:
        save_window_position(final_x, final_y+expanded_height)
        break
        
    # Save the current window position using our tracked x,y
    final_x = window.TKroot.winfo_x()
    final_y = window.TKroot.winfo_y()

    # Detect dragging: update our tracked x,y if the window moves
    new_x, new_y = window.current_location()
    if new_x != x or new_y != y:
        dragging = True
        x, y = new_x, new_y
        collapsed_y = y  # update collapsed position
    else:
        dragging = False

    # Calculate the top position when expanded so that the header remains in place
    expand_y = collapsed_y - (expanded_height - collapsed_height)
    
    # Get mouse and window geometry
    mouse_x = window.TKroot.winfo_pointerx()
    mouse_y = window.TKroot.winfo_pointery()
    win_x = window.TKroot.winfo_x()
    win_y = window.TKroot.winfo_y()
    win_width = window.TKroot.winfo_width()

    # Expand when mouse hovers over the header (collapsed area)
    if (not dragging and
        win_x <= mouse_x <= win_x + win_width and
        win_y <= mouse_y <= win_y + collapsed_height):
        if not expanded:
            window.TKroot.geometry(f"300x{expanded_height}+{x}+{expand_y}")
            expanded = True
            last_hover_time = None

    # Collapse after 0.5 seconds if mouse leaves the full expanded window (with safe zone)
    if (not dragging and expanded and
        not (win_x <= mouse_x <= win_x + win_width and
             win_y <= mouse_y <= win_y + expanded_height + safe_zone)):
        if last_hover_time is None:
            last_hover_time = time.time()
        if time.time() - last_hover_time > 0.5:
            # When collapsing, position the window so that its header remains at the bottom.
            collapsed_y = y + (expanded_height - collapsed_height)
            window.TKroot.geometry(f"300x{collapsed_height}+{x}+{collapsed_y}")
            expanded = False
            last_hover_time = None

    # Process button clicks
    if event.startswith("bt"):
        str_pos = event.removeprefix("bt")
        pos = int(str_pos)
        switch = switches[pos]
        att = values["sl" + str_pos]
        for i in range(len(config.LoRaPorts)):
            window["bt" + str(i)].update(button_color=("#83932F" if i == pos else "#E0BC61"))
        sendHTTP(f"{switch}/{att}")

    elif event.startswith("sl"):
        if sg.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED:
            str_pos = event.removeprefix("sl")
            pos = int(str_pos)
            switch = switches[pos]
            att = values["sl" + str_pos]
            for i in range(len(config.LoRaPorts)):
                window["bt" + str(i)].update(button_color=("#83932F" if i == pos else "#E0BC61"))
            sendHTTP(f"{switch}/{att}")

window.close()
