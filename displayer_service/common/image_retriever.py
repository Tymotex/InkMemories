"""Provides utilities from fetching images from the image source."""
import random
import os
import shutil

from logging import Logger
from typing import List
from PIL import Image
from PIL.Image import Image as ImageType

from common.display_config import DisplayConfig


class ImageRetriever:
    """Handles the retrieval of images from the image source."""
    logger: Logger
    display_config: DisplayConfig

    def __init__(self, logger, display_config):
        self.logger = logger
        self.display_config = display_config

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
        # TODO(image retrieval error): throw(there are no images)

        # Randomly pick an image from all the images.
        chosen_image_file_path = random.choice(all_images)
        return Image.open(chosen_image_file_path)

    def get_random_images(self, num_images) -> List[ImageType]:
        """Retrieves `num_images` number of random images from the image source."""
        all_images = self.get_path_of_all_images()
        # TODO(image retrieval error): throw(there are no images)

        num_images = min(num_images, len(all_images))
        # Randomly pick an image from all the images.
        chosen_image_paths = random.sample(all_images, num_images)

        images = []
        for each_image_path in chosen_image_paths:
            new_path = f"./{os.path.basename(each_image_path)}"
            shutil.copy(each_image_path, new_path)
            images.append(Image.open(new_path))

        return images

    # TODO(image retrieval error): def get_error_image
