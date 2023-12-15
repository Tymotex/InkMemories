import os
import random
import shutil
from typing import List
from PIL import Image
from PIL.Image import Image as ImageType


def get_path_of_all_images(display_config) -> List[str]:
    # Fetch the paths of all the images.
    all_images = []
    image_src_dir = display_config.config['display']['image_source_dir']
    print(f"Fetching all images in {image_src_dir}.")

    images_found = 0
    for image_basename in os.listdir(image_src_dir):
        _, file_extension = os.path.splitext(image_basename)
        image_path = os.path.join(image_src_dir, image_basename)
        if file_extension.lower() in display_config.config['display']['allowed_image_extensions']:
            images_found += 1
            all_images.append(image_path)
    print(f"Found {images_found} images.")
    return all_images

def get_random_image(display_config, current_image_path) -> ImageType:
    all_images = get_path_of_all_images(display_config)
    
    # Randomly pick an image from all the images.
    chosen_image_file_path = random.choice(all_images)
    print("Chose this image: " + chosen_image_file_path)
    
    shutil.copy(chosen_image_file_path, current_image_path)
    return Image.open(current_image_path)
