#!/usr/bin/python3

import os
from PIL import Image, ImageDraw, ExifTags, ImageFont
from pathlib import Path
from datetime import datetime


# Font path relative to the root folder, `displayer_service`.
FONT_PATH = "fonts/Mono.ttf"
FONT_SIZE = 20

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


def burn_date_into_image(img):
    """Writes the date the image was taken into the image itself.

    If no date is found, then this function has no effect.

    See https://en.wikipedia.org/wiki/Exif.
    In the EXIF standard, 306 is the identifier for the 'DateTime' field, which
    tells you when the photo was taken.
    """
    exif_data = img.getexif()
    if not exif_data:
        return img

    creation_time = exif_data.get(306)
    if not creation_time:
        return img

    # Format the creation date.
    creation_time = datetime.strptime(creation_time, "%Y:%m:%d %H:%M:%S")
    formatted_time = creation_time.strftime(
        "%d %b, %Y, %I:%M%p").replace(" 0", " ")

    # Burn the text to the bottom right of the image with a small padding.
    image_draw = ImageDraw.Draw(img)
    img_width, img_height = img.size
    anchor_position = (img_width - 10, img_height - 10)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    image_draw.text(anchor_position, formatted_time, fill=(0, 0, 0),
                    font=font, anchor="rs", stroke_fill=(255, 255, 255), stroke_width=2)
    return img


def central_crop(image, aspect_ratio):
    """Returns the central cropped image of the given image.
    """
    image_width_px, image_height_px = image.size
    crop_coordinates = determine_central_crop_coordinates(
        image_width_px, image_height_px, aspect_ratio)
    return image.crop(crop_coordinates)
