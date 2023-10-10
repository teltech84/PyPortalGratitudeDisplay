import time
import board
from adafruit_pyportal import PyPortal
from terminalio import FONT
import microcontroller

import neopixel
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel.fill(0)

DATA_SOURCE_CSV = "http://192.168.1.69/presently-backup.csv"
LINE_SEPARATION = b"\n"  # Use bytes for better memory efficiency
FIELD_SEPARATION = b","  # Use bytes for better memory efficiency

pyportal = PyPortal()
pyportal.preload_font()
char_width = FONT.get_bounding_box()[0]

# Set up text configurations outside the loop
message_label = pyportal.add_text(
    text_scale=2,
    text_position=(20, pyportal.display.height // 2 - 32),
    text_anchor_point=(0, 0.5),
    text_wrap=pyportal.display.width // char_width // 2,
    text_color=0x008080,
)
date_label = pyportal.add_text(
    text_scale=2,
    text_position=(pyportal.display.width - 10, pyportal.display.height - 10),
    text_anchor_point=(1, 1),
    text_wrap=pyportal.display.width // char_width,
    text_color=0x8080FF,
)

first_line_processed = False  # Flag to track if the first line has been processed

while True:
    try:
        # Blue means we are retrieving data
        pixel.fill(0x0000FF)

        with pyportal.network.fetch(DATA_SOURCE_CSV) as response:
            if response.status_code != 200:
                pixel.fill(0xFF0000)
                raise ConnectionError(f"Network error: {response.status_code}")

            # Process data as it becomes available
            data = b""
            for chunk in response.iter_content(chunk_size=128):
                data += chunk
                lines = data.split(LINE_SEPARATION)

                # Process only the first line if it hasn't been processed yet
                if not first_line_processed and len(lines) > 1:
                    first_line = lines[0].strip()
                    fields = first_line.split(FIELD_SEPARATION)

                    # Check if line should be ignored
                    ignore_list = [b'entryDate', b'entryContent']
                    if fields not in ignore_list and len(fields) > 1:
                        date = fields[0].decode("utf-8")  # Convert bytes to str
                        message = fields[1].decode("utf-8")  # Convert bytes to str
                        pyportal.set_text(message, message_label)
                        pyportal.set_text(date, date_label)
                        first_line_processed = True

                    # Keep the rest of the data for future processing
                    data = LINE_SEPARATION.join(lines[1:])

                # Process subsequent lines
                for line in lines[1:]:
                    fields = line.strip().split(FIELD_SEPARATION)

                    # Check if line should be ignored
                    ignore_list = [b'entryDate', b'entryContent']
                    if fields not in ignore_list and len(fields) > 1:
                        date = fields[0].decode("utf-8")  # Convert bytes to str
                        message = fields[1].decode("utf-8")  # Convert bytes to str
                        pyportal.set_text(message, message_label)
                        pyportal.set_text(date, date_label)
                        time.sleep(5)  # Delay of 5 seconds after displaying each entry

            # Clear memory
            data = None

        # Delay of 5 seconds after displaying all entries
        if first_line_processed:
            time.sleep(5)
            first_line_processed = False  # Reset the flag to start from the beginning

    except (ValueError, RuntimeError) as e:
        print("Some error occurred, retrying! -", e)
        time.sleep(10)
        microcontroller.reset()
