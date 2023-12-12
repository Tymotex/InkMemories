#!/usr/bin/python3

import os
import sys
from PIL import Image
from inky.auto import auto
import crop_and_resize_image


PATH = os.path.dirname(__file__)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("USage: python display_image.py $IMAGE_FILE_PATH")
        sys.exit(1)

    image_file_path = sys.argv[1]
    if not os.path.exists(image_file_path):
        print(f"Error: File '{image_file_path}' does not exist.")
        sys.exit(1)

    # Initialising the eInk display.
    try:
        inky_display = auto(ask_user=True, verbose=True)
    except TypeError:
        raise TypeError("You need to update the Inky library to >= v1.1.0")
    try:
        inky_display.set_border(inky_display.WHITE)
    except NotImplementedError:
        pass

    # Image processing.
    filename = sys.argv[1]
    img = Image.open(os.path.join(PATH, filename))
    width, height = inky_display.resolution
    img = crop_and_resize_image.central_crop(img, width / height)
    img = img.resize(inky_display.resolution)

    # Display the logo image
    inky_display.set_image(img)
    inky_display.show()
