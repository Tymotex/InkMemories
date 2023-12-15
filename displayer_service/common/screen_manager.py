#!/usr/bin/python3

import os
import logging
import time
import sys
import traceback
from logging import Logger
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
    logger: Logger
    display_config: DisplayConfig

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.initialise_display_config()
        self.configure_logger()

        self.initialise_eink_display()

    def initialise_eink_display(self) -> None:
        try:
            self.eink_display = auto(ask_user=True, verbose=True)
        except TypeError:
            logging.critical("You need to update the Inky library to >= v1.1.0")
            sys.exit(1)

        self.eink_display.set_border(self.eink_display.WHITE)
        self.logger("Initialised the eInk display.")

    def configure_logger(self):
        """Creates a custom (non-root) logger.

        Expects that the display config has already been populated.
        """
        formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
        file_handler = logging.FileHandler(self.display_config.config['logging']['log_file_path'])
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.info('Initialised custom logger.')

        # Custom exception hook to log unhandled exceptions.
        def custom_exception_hook(exc_type, exc_value, exc_traceback):
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
            self.logger.exception("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
            sys.exit(1)
        sys.excepthook = custom_exception_hook

    def initialise_display_config(self):
        self.display_config = DisplayConfig(self.logger, DISPLAY_CONFIG_FILE_PATH)

    def refresh_in_background(self) -> None:
        image_refresh_period_secs = self.display_config.config['display']['refresh_period_secs']
        while True:
            logging.info(f"Attempting to set a new random image.")
            self.set_random_image()
            logging.info(f"Waiting for {image_refresh_period_secs} seconds.")
            time.sleep(image_refresh_period_secs)

    def set_random_image(self):
        """Sets a new random image chosen from the images source.
        """
        img = image_retriever.get_random_image(self.display_config,
                                               CURRENT_IMAGE_PATH, self.logger)

        # Pre-process the image.
        width, height = self.eink_display.resolution
        img = image_processor.central_crop(img,  width / height)
        img = img.resize(self.eink_display.resolution)

        # Writing the image to the screen.
        self.eink_display.set_image(img)
        self.eink_display.show()

        logging.info("Done writing image.")

    def shutdown_pi(self):
        """
        """
        logging.info("Shutting down!")
        os.system('systemctl poweroff')
