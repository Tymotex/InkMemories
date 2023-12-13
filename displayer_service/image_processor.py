#!/usr/bin/python3

import os
from PIL import Image
from pathlib import Path


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
    print("ASPECT RATIO: " + str(aspect_ratio))
    image_width_px, image_height_px = image.size
    crop_coordinates = determine_central_crop_coordinates(image_width_px, image_height_px, aspect_ratio)
    return image.crop(crop_coordinates)
