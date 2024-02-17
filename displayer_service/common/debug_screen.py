#!/usr/bin/python3

"""Module for creating the debug screen."""

from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Image as ImageType

# At font size 20 and a screen size of 600x448, we can fit:
#  - 59 characters horizontally.
#  - 22 lines vertically.
CHARS_PER_LINE = 59
MAX_LINES = 22

# Font path relative to the root folder, `displayer_service`.
FONT_PATH = "fonts/Mono.ttf"
FONT_SIZE = 20


def transform_logs_to_image(logs_path: str) -> ImageType:
    """Returns a PIL Image of the debug screen.

    Writes the most recent few logs to an in-memory PIL image with readable font
    style and size.
    """
    # Create a blank white image
    debug_screen_img = Image.new('RGB', (600, 448), 'white')
    draw = ImageDraw.Draw(debug_screen_img)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    # Extract last MAX_LINES lines from the log file and reverse.
    lines = []
    with open(logs_path, "r", encoding='utf-8') as logs_file:
        lines = logs_file.read().splitlines()
    # Get only the last MAX_LINES items and reverse the list so most recent logs
    # are first.
    lines = lines[-MAX_LINES:]
    lines = lines[::-1]

    # Write out each line into a PIL image, accounting for text-wrapping. Stop
    # if we exceed the max number of lines permitted on the screen.
    line_index = 0
    lines_consumed = 0
    while lines_consumed < MAX_LINES and line_index < len(lines):
        curr_line = lines[line_index]
        # Truncate logs if they're beyond 3 lines, i.e. 67 * 3 characters.
        curr_line = (curr_line[:CHARS_PER_LINE * 3 - 3] +
                     "...") if len(curr_line) > CHARS_PER_LINE else curr_line
        while curr_line and lines_consumed < MAX_LINES:
            # Write out the first CHARS_PER_LINE characters, then slice it out.
            line_to_write = curr_line[:CHARS_PER_LINE].strip()
            draw.text((0, lines_consumed * FONT_SIZE), line_to_write,
                      font=font, fill=(0, 0, 0))
            curr_line = curr_line[CHARS_PER_LINE:]
            lines_consumed += 1
        line_index += 1

    return debug_screen_img
