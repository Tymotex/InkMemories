#!/usr/bin/python3

import os
import logging
import time
import sys
import traceback
import threading

from RPi import GPIO
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
    pins_to_buttons = {
        5: 'A',
        6: 'B',
        16: 'C',
        24: 'D'
    }
    
    # Protects multi-threaded access to the screen.
    screen_lock = threading.Lock()

    def __init__(self):
        with self.screen_lock:
            self.logger = logging.getLogger(__name__)
            self.initialise_display_config()
            self.configure_logger()

            self.initialise_eink_display()
            self.initialise_pi()

    def initialise_eink_display(self) -> None:
        """Initialises the e-ink display for usage."""
        try:
            self.eink_display = auto(ask_user=True, verbose=True)
        except TypeError:
            self.logger.critical("You need to update the Inky library to >= v1.1.0")
            sys.exit(1)

        self.eink_display.set_border(self.eink_display.WHITE)
        self.logger.info("Initialised the eInk display.")

    def configure_logger(self):
        """Creates a custom (non-root) logger.

        Expects that the display config has already been populated.
        """
        formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
        file_handler = logging.FileHandler(self.display_config.config['logging']['log_file_path'])
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.info('Initialised custom logger.')

        # Tees the log output to stdout.
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(stream_handler)

        # Custom exception hook to log unhandled exceptions.
        def custom_exception_hook(exc_type, exc_value, exc_traceback):
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
            self.logger.exception("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
            sys.exit(1)
        sys.excepthook = custom_exception_hook

    def initialise_display_config(self):
        """Initialises the display config."""
        self.display_config = DisplayConfig(self.logger, DISPLAY_CONFIG_FILE_PATH)
    
    def initialise_pi(self):
        """Initialises the Pi's hardware settings."""
        # Set up RPi.GPIO with the "BCM" numbering scheme. This is necessary
        # to map number GPIO pins to each screen button.
        GPIO.setmode(GPIO.BCM)

        # Buttons connect to ground when pressed, so we should set them up
        # with a "PULL UP", which weakly pulls the input signal to 3.3V.
        GPIO.setup(list(self.pins_to_buttons.keys()), GPIO.IN, pull_up_down=GPIO.PUD_UP)

        for each_pin_num in self.pins_to_buttons.keys():
            GPIO.add_event_detect(each_pin_num, GPIO.FALLING, self.handle_button_press, bouncetime=250)

    def refresh_in_background(self) -> None:
        image_refresh_period_secs = self.display_config.config['display']['refresh_period_secs']
        while True:
            self.logger.info(f"Attempting to set a new random image.")
            with self.screen_lock:
                self.set_random_image()
            self.logger.info(f"Waiting for {image_refresh_period_secs} seconds.")
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

        self.logger.info("Done writing image.")

    def handle_button_press(self, pressed_pin):
        """Executes specific actions on button presses.

        Labels and their GPIO pins:
        A --> 5
        B --> 6
        C --> 16
        D --> 24
        """
        label = self.pins_to_buttons[pressed_pin]
        if label == 'A':
            self.logger.info("User pressed A. Forcing refresh image.")
            with self.screen_lock:
                self.set_random_image()
        elif label == 'B':
            self.logger.info("User pressed B. Nothing is implemented for this button.")
        elif label == 'C':
            self.logger.info("User pressed C. Nothing is implemented for this button.")
        elif label == 'D':
            self.logger.info("User pressed D. Shutting down the Pi.")
            
            # Only commence shutdown after the image finishes refreshing, 
            # if it is currently refreshing.
            with self.screen_lock:
                self.shutdown_pi()

    def shutdown_pi(self):
        """Gracefully shuts down the host system.

        Note that when the power is reconnected, the Pi boots up and the daemons
        will start up automatically.
        """
        self.logger.info("Shutting down!")
        if os.geteuid() != 0:
            self.logger.error("Failed to shut down because this process is not executing with root privileges.")
        else:
            os.system('systemctl poweroff')
