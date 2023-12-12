#!/usr/bin/python3

import os
from PIL import Image
from pathlib import Path


PATH = os.path.dirname(__file__)
DISPLAY_WIDTH_PX = 600
DISPLAY_HEIGHT_PX = 488

# TODO: This is good to unit test.
def determine_central_crop_coordinates(image_width_px, image_height_px, crop_aspect_ratio):
    """Determine cropping box coordinates.
    
    Returns a 4-tuple for the upper left corner (x1, y1) and lower right corner
    (x2, y2).
    """
    # Either:
    # 1. Image dims already match aspect ratio. Return immediately.
    # 2. Image is wider than aspect ratio (meaning image_aspect_ratio > crop_aspect_ratio).
    #    In this case, we should bound the crop height to the image height.
    # 3. Image is taller than aspect ratio (meaning image_aspect_ratio < crop_aspect_ratio).
    #    In this case, we should bound the crop width to the image width.
    image_aspect_ratio = image_width_px / image_height_px
    if image_aspect_ratio == crop_aspect_ratio:
        return (0, 0, image_width_px, image_height_px)
    elif image_aspect_ratio > crop_aspect_ratio:
        crop_width_px = image_height_px * crop_aspect_ratio
        crop_height_px = image_height_px
        return ((image_width_px - crop_width_px) / 2, 0, (image_width_px + crop_width_px) / 2, image_height_px)
    else:
        crop_width_px = image_width_px
        crop_height_px = image_width_px / crop_aspect_ratio
        return (0, (image_height_px - crop_height_px) / 2, image_width_px, (image_height_px + crop_height_px) / 2)


def central_crop(image, aspect_ratio):
    """Returns the central cropped image of the given image.
    """
    image_width_px, image_height_px = image.size
    crop_coordinates = determine_central_crop_coordinates(image_width_px, image_height_px, aspect_ratio)
    return image.crop(crop_coordinates)


def resize_to_resolution(image, width_px, height_px):
    """Resizes the given photo to the display's resolution.

    Resizing may mess up the aspect ratio. Crop the image according to the eInk
    display's aspect ratio before resizing the image.
    """
    size = (width_px, height_px)
    return image.resize(size)

if __name__ == "__main__":
    image_path = input('Please enter an image file path: ')

    # Proessing the image.
    img = Image.open(os.path.join(PATH, image_path))
    cropped_img = central_crop(img, DISPLAY_WIDTH_PX / DISPLAY_HEIGHT_PX)
    resized_img = resize_to_resolution(cropped_img, DISPLAY_WIDTH_PX, DISPLAY_HEIGHT_PX)

    # Saving the output image.
    Path("./processed-images").mkdir(parents=True, exist_ok=True)
    output_image_path = f"./processed-images/{os.path.basename(image_path)}"
    with open(f"./processed-images/{os.path.basename(image_path)}", "wb") as processed_img:
        resized_img.save(processed_img)

    print(f"Wrote: '{output_image_path}'")
