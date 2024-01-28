"""Provides utilities from fetching images from the image source."""
import random
import os
import shutil

from logging import Logger
from typing import List
from pathlib import Path
from PIL import Image
from PIL.Image import Image as ImageType

from common.display_config import DisplayConfig


IMAGE_QUEUE_DIR = "tmp-images"


class ImageRetriever:
    """Handles the retrieval of images from the image source."""
    logger: Logger
    display_config: DisplayConfig

    def __init__(self, logger, display_config):
        self.logger = logger
        self.display_config = display_config

        # Temporary directory to store local copies of the images in the image
        # buffer.
        Path(f"./{IMAGE_QUEUE_DIR}").mkdir(parents=True, exist_ok=True)

    def __del__(self):
        shutil.rmtree(f"./{IMAGE_QUEUE_DIR}", ignore_errors=True)

    def get_path_of_all_images(self) -> List[str]:
        """Returns a list of the paths of all the available images from image source."""
        # Fetch the paths of all the images.
        all_images = []
        image_src_dir = self.display_config.config['display']['image_source_dir']
        self.logger.info(f"Fetching all images in {image_src_dir}.")

        if not os.path.exists(image_src_dir):
            self.logger.error(f"Directory '{image_src_dir}' does not exist.")
            # TODO(image retrieval error): return empty for error handling

        images_found = 0
        for image_basename in os.listdir(image_src_dir):
            _, file_extension = os.path.splitext(image_basename)
            image_path = os.path.join(image_src_dir, image_basename)
            if file_extension.lower() in self.display_config.config['display']['allowed_image_extensions']:
                images_found += 1
                all_images.append(image_path)

        if images_found <= 0:
            self.logger.warning(f"No images found in {image_src_dir}.")
        else:
            self.logger.info(f"Found {images_found} images.")

        return all_images

    def get_random_image(self) -> ImageType:
        """Retrieves one random image from the image source."""
        all_images = self.get_path_of_all_images()
        if not all_images: 
            raise Exception("No images were found in fetch, in an attempt to get a random image.")

        # Randomly pick an image from all the images.
        chosen_image_file_path = random.choice(all_images)

        local_image_copy_path = self.create_local_image_copy(
            chosen_image_file_path)

        return Image.open(local_image_copy_path)

    def get_random_images(self, num_images) -> List[ImageType]:
        """Retrieves `num_images` number of random images from the image source."""
        all_images = self.get_path_of_all_images()
        if not all_images: 
            raise Exception(f"No images were found in fetch, in an attempt to get {num_images} random images. ")


        num_images = min(num_images, len(all_images))
        # Randomly pick an image from all the images.
        chosen_image_paths = random.sample(all_images, num_images)

        images = []
        for each_image_path in chosen_image_paths:
            local_image_copy_path = self.create_local_image_copy(
                each_image_path)
            images.append(Image.open(local_image_copy_path))

        return images

    def create_local_image_copy(self, image_path) -> str:
        """Locally clone the image from the image source (Google Photos).

        This is necessary because PIL fails to load the image directly from the
        image files in the rclone mounted directory.
        """
        local_image_copy_path = f"./{IMAGE_QUEUE_DIR}/{os.path.basename(image_path)}"
        shutil.copy(image_path, local_image_copy_path)

        return local_image_copy_path

    def clean_up_image(self, img: ImageType):
        """Cleans up temporary local copy of the given image."""
        if not img:
            return
        if not os.path.exists(img.filename):
            return
        os.remove(img.filename)

    # TODO(image retrieval error): def get_error_image
