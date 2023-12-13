#!/usr/bin/python3

import os
import random
from PIL import Image
from inky.auto import auto
from inky import Inky_Impressions_7
from pathlib import Path
import image_retriever
import shutil
import time
import image_processor


PATH = os.path.dirname(__file__)

# TODO: Add validation that such a path exists, otherwise create it.
IMAGE_SOURCE_PATH = "/home/pi/Pictures/InkMemories" # TODO: Ideally this should be parameterised in the config.

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png'] # TODO: Parameterisable?
CURRENT_IMAGE_PATH = 'current_image.png' # TODO: Cater for other extensions.

DISPLAY_WIDTH_PX = 600  # TODO: Parameterisable?
DISPLAY_HEIGHT_PX = 488


class ScreenManager:
    def __init__(self):
        self.initialise_eink_display()
        # TODO: Create instance of DisplayConfig.

    def initialise_eink_display(self):
        try:
            self.eink_display = auto(ask_user=True, verbose=True)
        except TypeError:
            raise TypeError("You need to update the Inky library to >= v1.1.0")
        try:
            self.eink_display.set_border(self.eink_display.WHITE)
        except NotImplementedError:
            pass

    def set_random_image(self):
        """Sets a new random image chosen from the images source.
        """
        # Fetch the paths of all the images.
        print("Fetching all images...")
        all_images = []
        for image_basename in os.listdir(IMAGE_SOURCE_PATH):
            _, file_extension = os.path.splitext(image_basename)
            image_path = os.path.join(IMAGE_SOURCE_PATH, image_basename)
            if file_extension.lower() in IMAGE_EXTENSIONS:
                print("Found an image: " + image_path)
                all_images.append(image_path)

        # Randomly pick an image from all the images.
        chosen_image_file_path = random.choice(all_images)
        print("Chose this image: " + chosen_image_file_path)

        shutil.copy(chosen_image_file_path, CURRENT_IMAGE_PATH)  
        img = Image.open(CURRENT_IMAGE_PATH)

        # Pre-process the image.
        width, height = self.eink_display.resolution
        img = image_processor.central_crop(img,  width / height)
        img = img.resize(self.eink_display.resolution)

        # Saving the output image.
        if not os.path.exists("./processed-images"):
            os.makedirs("./processed-images")
        # TODO: make this path more robust.
        # TODO: Let's stop saving processed-images, or limit the amount that's saved to save space.
        with open("./processed-images/" + os.path.basename(chosen_image_file_path), "wb") as processed_img:
            img.save(processed_img)

        # Writing the image to the screen.
        self.eink_display.set_image(img)
        self.eink_display.show()

    def shutdown_pi(self):
        """
        """
        # TODO:
        pass


if __name__ == "__main__":
    # Initialise the ScreenManager.
    screen_manager = ScreenManager()
    
    # Kick off a background thread that regularly 
    screen_manager.set_random_image()

# TODO: When main thread execution reaches here, if there are still running
#       threads, will the main thread be blocked on terminating the program?
