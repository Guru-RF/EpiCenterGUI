import PySimpleGUI as sg
import requests

import config


def sendHTTP(data):
    response = requests.get("http://172.16.132.174:8000/" + data)

    # Check if the request was successful (status code 200)
    if response.status_code != 200:
        print(f"Failed to retrieve data. Status code: {response.status_code}")

    return True


Theme = "DarkAmber"  # [‘Black’, ‘BlueMono’, ‘BluePurple’, ‘BrightColors’, ‘BrownBlue’, ‘Dark’, ‘Dark2’, ‘DarkAmber’, ‘DarkBlack’, ‘DarkBlack1’, ‘DarkBlue’, ‘DarkBlue1’, ‘DarkBlue10’, ‘DarkBlue11’, ‘DarkBlue12’, ‘DarkBlue13’, ‘DarkBlue14’, ‘DarkBlue15’, ‘DarkBlue16’, ‘DarkBlue17’, ‘DarkBlue2’, ‘DarkBlue3’, ‘DarkBlue4’, ‘DarkBlue5’, ‘DarkBlue6’, ‘DarkBlue7’, ‘DarkBlue8’, ‘DarkBlue9’, ‘DarkBrown’, ‘DarkBrown1’, ‘DarkBrown2’, ‘DarkBrown3’, ‘DarkBrown4’, ‘DarkBrown5’, ‘DarkBrown6’, ‘DarkGreen’, ‘DarkGreen1’, ‘DarkGreen2’, ‘DarkGreen3’, ‘DarkGreen4’, ‘DarkGreen5’, ‘DarkGreen6’, ‘DarkGrey’, ‘DarkGrey1’, ‘DarkGrey2’, ‘DarkGrey3’, ‘DarkGrey4’, ‘DarkGrey5’, ‘DarkGrey6’, ‘DarkGrey7’, ‘DarkPurple’, ‘DarkPurple1’, ‘DarkPurple2’, ‘DarkPurple3’, ‘DarkPurple4’, ‘DarkPurple5’, ‘DarkPurple6’, ‘DarkRed’, ‘DarkRed1’, ‘DarkRed2’, ‘DarkTanBlue’, ‘DarkTeal’, ‘DarkTeal1’, ‘DarkTeal10’, ‘DarkTeal11’, ‘DarkTeal12’, ‘DarkTeal2’, ‘DarkTeal3’, ‘DarkTeal4’, ‘DarkTeal5’, ‘DarkTeal6’, ‘DarkTeal7’, ‘DarkTeal8’, ‘DarkTeal9’, ‘Default’, ‘Default1’, ‘DefaultNoMoreNagging’, ‘Green’, ‘GreenMono’, ‘GreenTan’, ‘HotDogStand’, ‘Kayak’, ‘LightBlue’, ‘LightBlue1’, ‘LightBlue2’, ‘LightBlue3’, ‘LightBlue4’, ‘LightBlue5’, ‘LightBlue6’, ‘LightBlue7’, ‘LightBrown’, ‘LightBrown1’, ‘LightBrown10’, ‘LightBrown11’, ‘LightBrown12’, ‘LightBrown13’, ‘LightBrown2’, ‘LightBrown3’, ‘LightBrown4’, ‘LightBrown5’, ‘LightBrown6’, ‘LightBrown7’, ‘LightBrown8’, ‘LightBrown9’, ‘LightGray1’, ‘LightGreen’, ‘LightGreen1’, ‘LightGreen10’, ‘LightGreen2’, ‘LightGreen3’, ‘LightGreen4’, ‘LightGreen5’, ‘LightGreen6’, ‘LightGreen7’, ‘LightGreen8’, ‘LightGreen9’, ‘LightGrey’, ‘LightGrey1’, ‘LightGrey2’, ‘LightGrey3’, ‘LightGrey4’, ‘LightGrey5’, ‘LightGrey6’, ‘LightPurple’, ‘LightTeal’, ‘LightYellow’, ‘Material1’, ‘Material2’, ‘NeutralBlue’, ‘Purple’, ‘Reddit’, ‘Reds’, ‘SandyBeach’, ‘SystemDefault’, ‘SystemDefault1’, ‘SystemDefaultForReal’, ‘Tan’, ‘TanBlue’, ‘TealMono’, ‘Topanga’]
sg.theme(Theme)  # Add a touch of color

layout = []

arr = [sg.Text("RF.Guru EpiCenter              Attenuator")]
layout.append(arr)

switches = []

for i, val in enumerate(config.LoRaPorts):
    sw, att = config.LoRaPorts[val]
    switches.append(sw)
    buttonColor = "#E0BC61"
    if i == 0:
        buttonColor = "#83932F"
    arr = [
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
    ]
    layout.append(arr)


# Create the Window
windowTitle = "RF.Guru EpiCenter Switch"
window = sg.Window(
    windowTitle, layout, keep_on_top=True, grab_anywhere=True, finalize=True
)

for i in range(len(config.LoRaPorts)):
    window["sl" + str(i)].bind("<ButtonRelease-1>", "")

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    print(event)
    if event == sg.WIN_CLOSED:
        break
    elif event.startswith("bt"):
        str_pos = event.removeprefix("bt")
        pos = int(str_pos)
        switch = switches[pos]
        att = values["sl" + str_pos]
        for i in range(len(config.LoRaPorts)):
            if i != pos:
                window["bt" + str(i)].update(button_color=("#E0BC61"))
            else:
                window["bt" + str(i)].update(button_color=("#83932F"))
        httpREQ = switch + "/" + str(att)
        print(httpREQ)
        sendHTTP(httpREQ)
    elif event.startswith("sl"):
        if sg.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED:
            str_pos = event.removeprefix("sl")
            pos = int(str_pos)
            switch = switches[pos]
            att = values["sl" + str_pos]
            for i in range(len(config.LoRaPorts)):
                if i != pos:
                    window["bt" + str(i)].update(button_color=("#E0BC61"))
                else:
                    window["bt" + str(i)].update(button_color=("#83932F"))
            httpREQ = switch + "/" + str(att)
            print(httpREQ)
            sendHTTP(httpREQ)

window.close()
