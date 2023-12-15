#!/usr/bin/python3

import os
import time
from PIL import Image
from inky.auto import auto
from pathlib import Path
from typing import Union

from common import image_processor
from common import image_retriever
from common.display_config import DisplayConfig


PATH = os.path.dirname(__file__)
CURRENT_IMAGE_PATH = 'current_image.png'
DISPLAY_CONFIG_FILE_PATH = './display_config.json'


class ScreenManager:
    display_config: Union[None, DisplayConfig] = None

    def __init__(self):
        self.initialise_eink_display()
        self.initialise_display_config()

    def initialise_display_config(self) -> None:
        print("Initialising Display Config.")
        self.display_config = DisplayConfig(DISPLAY_CONFIG_FILE_PATH)

    def initialise_eink_display(self) -> None:
        try:
            self.eink_display = auto(ask_user=True, verbose=True)
        except TypeError:
            raise TypeError("You need to update the Inky library to >= v1.1.0")
        try:
            self.eink_display.set_border(self.eink_display.WHITE)
        except NotImplementedError:
            pass

    def refresh_in_background(self) -> None:
        image_refresh_period_secs = self.display_config.config['display']['refresh_period_secs']
        while True:
            print(f"Attempting to set a new random image.")
            self.set_random_image()
            print(f"Waiting for {image_refresh_period_secs} seconds.")
            time.sleep(image_refresh_period_secs)

    def set_random_image(self):
        """Sets a new random image chosen from the images source.
        """
        img = image_retriever.get_random_image(self.display_config, CURRENT_IMAGE_PATH)

        # Pre-process the image.
        width, height = self.eink_display.resolution
        img = image_processor.central_crop(img,  width / height)
        img = img.resize(self.eink_display.resolution)

        # Writing the image to the screen.
        self.eink_display.set_image(img)
        self.eink_display.show()

        print("Done writing image.")

    def shutdown_pi(self):
        """
        """
        # print("SHUTTING DOWN!")
        # os.system('systemctl poweroff')
