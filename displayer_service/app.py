import common.screen_manager
import logging
import threading


if __name__ == "__main__":
    # Initialise the ScreenManager.
    display = common.screen_manager.ScreenManager()

    # Create a thread for the set_random_image function
    # Note: daemon threads automatically terminate when the program does.
    thread = threading.Thread(
        target=display.refresh_in_background, daemon=True)
    thread.start()

    # Block the main thread until the user interrupts the program
    try:
        thread.join()
    except KeyboardInterrupt:
        logging.info("Exiting program...")
