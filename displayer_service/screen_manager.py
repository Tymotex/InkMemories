#!/usr/bin/python3

import os
import random
import display_config
import shutil
import time
import image_processor
from PIL import Image
from inky.auto import auto
from inky import Inky_Impressions_7
from pathlib import Path


import threading


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
        self.display_config = display_config.DisplayConfig(
            DISPLAY_CONFIG_FILE_PATH)

    def initialise_eink_display(self):
        try:
            self.eink_display = auto(ask_user=True, verbose=True)
        except TypeError:
            raise TypeError("You need to update the Inky library to >= v1.1.0")
        try:
            self.eink_display.set_border(self.eink_display.WHITE)
        except NotImplementedError:
            pass

    def refresh_in_background(self):
        image_refresh_period_secs = self.display_config.config['display']['refresh_period_secs']
        while True:
            print(f"Attempting to set a new random image.")
            self.set_random_image()
            print(f"Waiting for {image_refresh_period_secs} seconds.")
            time.sleep(image_refresh_period_secs)

    def set_random_image(self):
        """Sets a new random image chosen from the images source.
        """
        # Fetch the paths of all the images.
        all_images = []
        image_src_dir = self.display_config.config['display']['image_source_dir']
        print(f"Fetching all images in {image_src_dir}.")

        images_found = 0
        for image_basename in os.listdir(image_src_dir):
            _, file_extension = os.path.splitext(image_basename)
            image_path = os.path.join(image_src_dir, image_basename)
            if file_extension.lower() in self.display_config.config['display']['allowed_image_extensions']:
                images_found += 1
                all_images.append(image_path)
        print(f"Found {images_found} images.")

        # Randomly pick an image from all the images.
        chosen_image_file_path = random.choice(all_images)
        print("Chose this image: " + chosen_image_file_path)

        shutil.copy(chosen_image_file_path, CURRENT_IMAGE_PATH)
        img = Image.open(CURRENT_IMAGE_PATH)

        # Pre-process the image.
        width, height = self.eink_display.resolution
        img = image_processor.central_crop(img,  width / height)
        img = img.resize(self.eink_display.resolution)

        # Writing the image to the screen.
        self.eink_display.set_image(img)
        self.eink_display.show()

        print(f"Done writing image {chosen_image_file_path}.")

    def shutdown_pi(self):
        """
        """
        # print("SHUTTING DOWN!")
        # os.system('systemctl poweroff')


if __name__ == "__main__":
    # Initialise the ScreenManager.
    screen_manager = ScreenManager()

    # Create a thread for the set_random_image function
    # Note: daemon threads automatically terminate when the program does.
    thread = threading.Thread(
        target=screen_manager.refresh_in_background, daemon=True)
    thread.start()

    # Block the main thread until the user interrupts the program
    try:
        thread.join()
    except KeyboardInterrupt:
        print("Exiting program...")


# TODO: When main thread execution reaches here, if there are still running threads, will the main thread be blocked on terminating the program?
