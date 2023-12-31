import os
import random
import shutil
from logging import Logger
from typing import List
from PIL import Image
from PIL.Image import Image as ImageType

# TODO potentially wrap in class and make into variables the logger and display_config


def get_path_of_all_images(display_config, logger: Logger) -> List[str]:
    """Returns a list of the paths of all the available images from image source."""
    # Fetch the paths of all the images.
    all_images = []
    image_src_dir = display_config.config['display']['image_source_dir']
    logger.info(f"Fetching all images in {image_src_dir}.")

    if not os.path.exists(image_src_dir):
        logger.error(f"Directory '{image_src_dir}' does not exist.")
        # TODO(image retrieval error): return empty for error handling

    images_found = 0
    for image_basename in os.listdir(image_src_dir):
        _, file_extension = os.path.splitext(image_basename)
        image_path = os.path.join(image_src_dir, image_basename)
        if file_extension.lower() in display_config.config['display']['allowed_image_extensions']:
            images_found += 1
            all_images.append(image_path)

    if images_found <= 0:
        logger.warning(f"No images found in {image_src_dir}.")
    else:
        logger.info(f"Found {images_found} images.")

    return all_images


def get_random_image(display_config, current_image_path, logger: Logger) -> ImageType:
    """Retrieves one random image from the image source."""
    all_images = get_path_of_all_images(display_config, logger)
    # TODO(image retrieval error): throw(there are no images)

    # Randomly pick an image from all the images.
    chosen_image_file_path = random.choice(all_images)
    logger.info(f"Chose this image: {chosen_image_file_path}")

    # TODO verify whether current_image_path is necessary
    shutil.copy(chosen_image_file_path, current_image_path)
    logger.info(f"Saved as {current_image_path}")

    return Image.open(current_image_path)


def get_random_images(num_images, display_config, logger: Logger) -> List[ImageType]:
    """Retrieves `num_images` number of random images from the image source."""
    all_images = get_path_of_all_images(display_config, logger)
    # TODO(image retrieval error): throw(there are no images)

    num_images = min(num_images, len(all_images))
    # Randomly pick an image from all the images.
    chosen_image_paths = random.sample(all_images, num_images)

    return [Image.open(img) for img in chosen_image_paths]

# TODO(image retrieval error): def get_error_image
