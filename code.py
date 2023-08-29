import time
import board
from adafruit_pyportal import PyPortal
from terminalio import FONT

import neopixel
pixel = neopixel.NeoPixel(board.NEOPIXEL,1)
pixel.fill(0)

# Set up where we'll be fetching data from
DATA_SOURCE_CSV = "http://192.168.1.66/presently-backup.csv"
LINE_SEPARATION = "\n"
FIELD_SEPARATION = "," # the "c" in csv ?

pyportal = PyPortal()
pyportal.preload_font()
char_width = FONT.get_bounding_box()[0]

message_label = pyportal.add_text(
    text_scale=2,
    text_position=(20, pyportal.display.height // 2 - 32),
    text_anchor_point=(0, 0.5),
    text_wrap=pyportal.display.width // char_width // 2,
    text="Wait for the goodshit to appear...",
    text_color=0x008080,
)
date_label = pyportal.add_text(
    text_scale=2,
    text_position=(pyportal.display.width - 10, pyportal.display.height - 10),
    text_anchor_point=(1, 1),
    text_wrap=pyportal.display.width // char_width,
    text="1984/12/18",
    text_color=0x8080FF,
)
#     text_color=0, , text_maxlen=0, text_transform=None, text_scale=1, line_spacing=1.25, text_anchor_point=(0, 0.5), is_data=True, text=None)¶

while True:
    try:
        # blue means we are retrieving data
        pixel.fill(0x0000FF)
        with pyportal.network.fetch(DATA_SOURCE_CSV) as response:
            if response.status_code != 200:
                pixel.fill(0xFF0000)
                raise ConnectionError(f"Network error: {response.status_code}")
            else:
                data = response.text

        pixel.fill(0)
        # here we have the csv.
        for line in data.split(LINE_SEPARATION):
            fields = line.strip().split(FIELD_SEPARATION)

            ignore_list = ['entryDate', 'entryContent']
            if fields != ignore_list:
                if len(fields) > 1:
                    date = fields[0]
                    message = fields[1]
                    pyportal.set_text(message, message_label)
                    pyportal.set_text(date, date_label)
                    time.sleep(5)

    except (ValueError, RuntimeError) as e:
        print("Some error occured, retrying! -", e)
        time.sleep(10)