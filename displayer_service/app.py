import common.screen_manager
import logging
import threading


if __name__ == "__main__":
    # Initialise the ScreenManager.
    display = common.screen_manager.ScreenManager()

    # Create a thread for the regularly refreshing the image.
    # Note: daemon threads automatically terminate when the program does.
    image_refresh_thread = threading.Thread(
        target=display.refresh_in_background, daemon=True)
    image_refresh_thread.start()

    # Create a thread for handling button presses at any time.

    # Block the main thread until the user interrupts the program
    try:
        image_refresh_thread.join()
    except KeyboardInterrupt:
        logging.info("Exiting program...")
