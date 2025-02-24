import PySimpleGUI as sg
import requests
import time
import config

def sendHTTP(data):
    response = requests.get("http://172.16.32.112:8000/" + data)
    if response.status_code != 200:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
    return True

# Set Theme
Theme = "DarkAmber"
sg.theme(Theme)

# Define the non-collapsing header
header = [[sg.Text("RF.Guru EpiCenter              Attenuator", font=("Helvetica", 10), justification="center")]]

# Define the dynamic content that collapses
switches = []
collapsible_layout = []
for i, val in enumerate(config.LoRaPorts):
    sw, att = config.LoRaPorts[val]
    switches.append(sw)
    buttonColor = "#E0BC61"
    if i == 0:
        buttonColor = "#83932F"
    collapsible_layout.append([
        sg.Button(
            val, metadata=val, size=(18, 1), key="bt" + str(i), button_color=buttonColor
        ),
        sg.Slider(
            orientation="horizontal",
            resolution=0.5,
            range=(0, 31),
            size=(12, 7),
            expand_x=True,
            enable_events=False,
            disable_number_display=False,
            default_value=att,
            key="sl" + str(i),
        ),
    ])

# Merge layouts
layout = header + collapsible_layout

# Create the Window
windowTitle = "RF.Guru EpiCenter Switch"
window = sg.Window(
    windowTitle,
    layout,
    keep_on_top=True,
    grab_anywhere=True,
    finalize=True,
)

for i in range(len(config.LoRaPorts)):
    window["sl" + str(i)].bind("<ButtonRelease-1>", "")

# Window expansion/collapse variables
x, y = window.current_location()
collapsed_height = 30  # Only the RF.Guru EpiCenter header is visible
expanded_height = 30 + (len(config.LoRaPorts) * 30)  # Adjust height based on number of buttons
safe_zone = 10  # Extra 10px safe zone to prevent flickering

collapsed_y = y  # Start with the window at its current position
expanded = False  # Track expansion state
dragging = False  # Track if the window is being moved
last_hover_time = None  # Timer for collapse delay

# Event Loop to process "events" and handle expand/collapse
while True:
    event, values = window.read(timeout=100)

    if event == sg.WIN_CLOSED:
        break

    # **Detect dragging and update collapsed position**
    new_x, new_y = window.current_location()
    if new_x != x or new_y != y:
        dragging = True
        x, y = new_x, new_y
        collapsed_y = y  # Store new collapsed position dynamically

    # Ensure expansion happens upwards from the correct position
    expand_y = collapsed_y - (expanded_height - collapsed_height)

    # **Expand when hovered over the RF.Guru EpiCenter area**
    mouse_x = window.TKroot.winfo_pointerx()
    mouse_y = window.TKroot.winfo_pointery()
    win_x = window.TKroot.winfo_x()
    win_y = window.TKroot.winfo_y()
    win_width = window.TKroot.winfo_width()
    win_height = window.TKroot.winfo_height()

    # Adjust hover detection so it includes the full expanded height
    if not dragging and win_x <= mouse_x <= win_x + win_width and win_y <= mouse_y <= win_y + expanded_height:
        if not expanded:
            window.TKroot.geometry(f"300x{expanded_height}+{x}+{expand_y}")  # Expand upwards
            expanded = True
            last_hover_time = None  # Reset collapse timer

    # **Collapse downwards after 0.5 sec if mouse leaves the FULL expanded window (with safe zone)**
    if expanded and not (win_x <= mouse_x <= win_x + win_width and win_y <= mouse_y <= win_y + expanded_height + safe_zone):
        if last_hover_time is None:
            last_hover_time = time.time()  # Start collapse timer

        if time.time() - last_hover_time > 0.5:
            window.TKroot.geometry(f"300x{collapsed_height}+{x}+{collapsed_y + (expanded_height - collapsed_height)}")  # Collapse downward
            expanded = False
            last_hover_time = None  # Reset timer

    # **Reset dragging state after movement**
    dragging = False

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
