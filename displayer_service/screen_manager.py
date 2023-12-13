#!/usr/bin/python3

import os
import random
from PIL import Image
from inky.auto import auto
from inky import Inky_Impressions_7
from pathlib import Path
import image_retriever
import display_config
import shutil
import time
import image_processor


PATH = os.path.dirname(__file__)
CURRENT_IMAGE_PATH = 'current_image.png'
DISPLAY_CONFIG_FILE_PATH = './display_config.json'


class ScreenManager:
    display_config = None

    def __init__(self):
        self.initialise_eink_display()
        self.initialise_display_config()
    
    def initialise_display_config(self):
        print("Initialising Display Config.")
        self.display_config = display_config.DisplayConfig(DISPLAY_CONFIG_FILE_PATH)

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
        image_src_dir = self.display_config.config['display']['image_source_dir']
        for image_basename in os.listdir(image_src_dir):
            _, file_extension = os.path.splitext(image_basename)
            image_path = os.path.join(image_src_dir, image_basename)
            if file_extension.lower() in self.display_config.config['display']['allowed_image_extensions']:
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

# TODO: When main thread execution reaches here, if there are still running threads, will the main thread be blocked on terminating the program?
