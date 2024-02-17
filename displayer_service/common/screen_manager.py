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

from common import image_processor, debug_screen
from common.display_config import DisplayConfig
from common.image_retriever import ImageRetriever


PATH = os.path.dirname(__file__)
DISPLAY_CONFIG_FILE_PATH = './display_config.json'
INITIAL_QUEUE_SIZE = 10
LOG_FILE_PATH = './.ink-memories-log'


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

    # Whether the user is currently in debugging mode.
    # The user can enter debugging mode by pressing the 'B' button.
    # Debugging mode can be exited via a force image refresh ('A' button).
    is_debugging = False

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

            # Populate the image buffer with some intiial images.
            # Keep trying until it is populated.
            chosen_images = None
            while chosen_images is None:
                try:
                    chosen_images = self.image_retriever.get_random_images(
                        INITIAL_QUEUE_SIZE)
                except Exception as e:
                    self.logger.error(e)
                    self.logger.info(
                        "Initial population of images has failed. Trying again in 300 seconds.")
                    time.sleep(300)

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
            '[%(asctime)s] %(message)s', datefmt="%Y-%m-%d %H:%M")
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
            self.logger.info("Automatic image refresh requested.")

            if self.is_debugging:
                self.logger.info(
                    "Debugging mode is ON. Skipping image refresh."
                )
            else:
                self.output_and_queue_image()

            self.logger.info("Waiting for %s seconds.",
                             image_refresh_period_secs)
            time.sleep(image_refresh_period_secs)

    def queue_image(self):
        """Adds a random image to image buffer"""
        try:
            self.image_queue.put(self.image_retriever.get_random_image())
        except Exception as e:
            self.logger.error(e)
            self.logger.info(
                "Failed to queue image. Size of queue: %s", self.image_queue.qsize())

    def output_and_queue_image(self):
        """Displays the next image in the image queue, and adds a new image to the queue."""
        self.logger.info("Image queue size is %s.", self.image_queue.qsize())

        try:
            next_image = self.image_queue.get()
        except queue.Empty:
            self.logger.error(
                "Tried to set the next image, but queue was empty.")

            self.logger.info("Repopulating the image buffer.")
            chosen_images = self.image_retriever.get_random_images(
                INITIAL_QUEUE_SIZE)
            for img in chosen_images:
                self.image_queue.put(img)

            next_image = self.image_queue.get()

        with self.screen_lock:
            self.set_image(next_image)
        self.image_retriever.clean_up_image(next_image)

        # Run as thread to make consecutive A presses instant response.
        enqueue_thread = threading.Thread(target=self.queue_image)
        enqueue_thread.start()

    def set_image(self, img):
        """Sets a new random image chosen from the images source.
        """
        # Pre-process the image.
        width, height = self.eink_display.resolution
        img = image_processor.central_crop(img,  width / height)
        img = img.resize(self.eink_display.resolution)

        # Writing the image to the screen.
        self.eink_display.set_image(img)
        self.eink_display.show()

        self.logger.info("Done writing image.")

    def push_debugger_update(self):
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

        self.logger.info("Already in debug mode. Fetching latest debug logs." if self.is_debugging else "Entering debug mode.")
        self.is_debugging = True

        with self.screen_lock:
            # Ensure the image fits into the eink display's resolution.
            debug_screen_img = debug_screen.transform_logs_to_image(LOG_FILE_PATH)
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
            self.is_debugging = False
            self.output_and_queue_image()
        elif label == 'B':
            self.logger.info("User pressed B. Displaying the debug screen.")
            self.push_debugger_update()
        elif label == 'C':
            self.logger.info(
                "User pressed C. Nothing is implemented for this button.")
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
