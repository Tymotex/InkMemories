#!/usr/bin/python3

import os
import logging
import time
import sys
import traceback
import threading
import queue

from RPi import GPIO
from logging import Logger
from PIL import Image
from inky.auto import auto
from pathlib import Path
from typing import Union

from common import image_processor
from common.display_config import DisplayConfig
from common.image_retriever import ImageRetriever


PATH = os.path.dirname(__file__)
DISPLAY_CONFIG_FILE_PATH = './display_config.json'
INITIAL_QUEUE_SIZE = 10
LOG_FILE_PATH = './.ink-memories-log'
DEBUG_SCREEN_IMAGE_PATH = './debug-screen.png'


class ScreenManager:
    """Manages displaying new images to the e-ink display.
    """
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

    # Buffer of cached in-memory images.
    image_queue = queue.Queue()

    # Utility for retrieving images from the image source.
    image_retriever: ImageRetriever

    # Whether the user has turned on debug mode. In debug mode, all normal image
    # refreshing halts and a troubleshooting screen is displayed.
    # This is used to prevent the normal image refreshing thread from
    # pre-empting the troubleshooting screen.
    is_debug_mode = False

    def __init__(self):
        with self.screen_lock:
            self.logger = logging.getLogger(__name__)
            self.initialise_display_config()
            # TODO: make this self.display_config = self.configure_logger().
            self.configure_logger()

            self.initialise_eink_display()
            self.initialise_pi()

            self.image_retriever = ImageRetriever(
                self.logger, self.display_config)

            # Populate image buffer
            chosen_images = self.image_retriever.get_random_images(
                INITIAL_QUEUE_SIZE)
            for img in chosen_images:
                self.image_queue.put(img)

    def initialise_eink_display(self) -> None:
        """Initialises the e-ink display for usage."""
        try:
            self.eink_display = auto(ask_user=True, verbose=True)
        except TypeError:
            self.logger.critical(
                "You need to update the Inky library to >= v1.1.0")
            sys.exit(1)

        self.eink_display.set_border(self.eink_display.WHITE)
        self.logger.info("Initialised the eInk display.")

    def configure_logger(self):
        """Creates a custom (non-root) logger.

        Expects that the display config has already been populated.
        """
        formatter = logging.Formatter(
            '%(asctime)s : %(levelname)s : %(name)s : %(message)s')
        file_handler = logging.FileHandler(LOG_FILE_PATH)
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.info('Initialised custom logger.')

        # Tees the log output to stdout.
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(stream_handler)

        # Custom exception hook to log unhandled exceptions.
        def custom_exception_hook(exc_type, exc_value, exc_traceback):
            traceback.print_exception(
                exc_type, exc_value, exc_traceback, file=sys.stdout)
            self.logger.exception("Uncaught exception", exc_info=(
                exc_type, exc_value, exc_traceback))
            sys.exit(1)
        sys.excepthook = custom_exception_hook

    def initialise_display_config(self):
        """Initialises the display config."""
        self.display_config = DisplayConfig(
            self.logger, DISPLAY_CONFIG_FILE_PATH)

    def initialise_pi(self):
        """Initialises the Pi's hardware settings."""
        # Set up RPi.GPIO with the "BCM" numbering scheme. This is necessary
        # to map number GPIO pins to each screen button.
        GPIO.setmode(GPIO.BCM)

        # Buttons connect to ground when pressed, so we should set them up
        # with a "PULL UP", which weakly pulls the input signal to 3.3V.
        GPIO.setup(list(self.pins_to_buttons.keys()),
                   GPIO.IN, pull_up_down=GPIO.PUD_UP)

        for each_pin_num in self.pins_to_buttons.keys():
            GPIO.add_event_detect(each_pin_num, GPIO.FALLING,
                                  self.handle_button_press, bouncetime=250)

    def refresh_in_background(self) -> None:
        """Periodically displays a new image."""
        image_refresh_period_secs = self.display_config.config['display']['refresh_period_secs']
        while True:
            self.logger.info("Attempting to set a new random image.")

            self.output_and_queue_image()

            self.logger.info("Waiting for %s seconds.",
                             image_refresh_period_secs)

            time.sleep(image_refresh_period_secs)

    def queue_image(self):
        """Adds a random image to image buffer"""
        self.image_queue.put(self.image_retriever.get_random_image())

    def output_and_queue_image(self):
        """Displays the next image in the image queue, and adds a new image to the queue."""
        if self.is_debug_mode:
            self.logger.info("In debug mode. Skipping image refresh.")
            return

        self.logger.info(
            "Image queue size is %s.", self.image_queue.qsize())

        with self.screen_lock:
            next_image = self.image_queue.get()
            self.set_image(next_image)
        self.image_retriever.clean_up_image(next_image)

        # Queue image in a separate thread to make consecutive A presses
        # produce an instant response.
        enqueue_thread = threading.Thread(target=self.queue_image)
        enqueue_thread.start()

    def set_image(self, img):
        """Sets a new random image chosen from the images source.
        """
        # TODO: Catch and handle image fetch failure (probably due to network failure, invalid API credentials).

        # Pre-process the image.
        width, height = self.eink_display.resolution
        img = image_processor.central_crop(img,  width / height)
        img = img.resize(self.eink_display.resolution)

        # Writing the image to the screen.
        self.eink_display.set_image(img)
        self.eink_display.show()

        self.logger.info("Done writing image.")

    def show_troubleshooting_screen(self):
        """Displays the debug mode screen.

        When the user presses B, debug mode will be flipped on and the
        troubleshooting screen will show.
        This screen shows some of the most recent logs.

        Flipping on debug mode will not pre-empt any in-progress screen
        refreshes.
        """
        if self.screen_lock.locked():
            self.logger.info(
                "Attempted to enter debug mode while screen was busy. Skipping.")
            return

        with self.screen_lock:
            # Ensuring the image fits into the eink display's resolution.
            debug_screen_img = Image.open(DEBUG_SCREEN_IMAGE_PATH)
            debug_screen_img = debug_screen_img.resize(
                self.eink_display.resolution)

            self.set_image(debug_screen_img)

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
            if self.screen_lock.locked():
                self.logger.info(
                    "Skipping image refresh because refresh is already underway.")
                return
            self.output_and_queue_image()
        elif label == 'B':
            self.is_debug_mode = not self.is_debug_mode
            self.logger.info("Toggling debug screen %s.",
                             'on' if self.is_debug_mode else 'off')
            if self.is_debug_mode:
                self.show_troubleshooting_screen()
        elif label == 'C':
            if self.is_debug_mode:
                self.logger.info("Refreshing the debug screen.")
                self.show_troubleshooting_screen()
            else:
                self.logger.info(
                    "Attempted to refresh image while not in debug mode. Skipping.")
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
            self.logger.error(
                "Failed to shut down because this process is not executing with root privileges.")
        else:
            os.system('systemctl poweroff')
