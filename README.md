# InkMemories

## Usage

TODO.

Beware: disconnecting the Raspberry Pi directly from power can corrupt the SD card. Always click the top left button to perform a graceful shutdown before unplugging from power.

## Setup Instructions
These instructions assume that you have set up Raspbian OS.
- In `raspi-config`, enable I2C and SPI. This is necessary for getting the e-ink display to work.
- Set a hostname that you'd like with `cat $NEW_HOSTNAME >> /etc/hostname`.
- In your router's configuration either disable DHCP or reserve a static IP for the Raspberry Pi.

## Components
- Raspberry Pi Zero W and its power supply.
- Inky Impression 5.7" 600x448p (7 colour eInk HAT). [Source](https://shop.pimoroni.com/products/inky-impression-5-7?variant=32298701324371).
- Optional 3D printed stand.

## How it works

### Google Photos API
The photos are sourced from a shared Google Photos album.

As of 2023, the free tier permits 10000 requests per day for operations such as uploading images, and 75000 requests per day for reading images. In other words, it's surely enough for this project.

#### Retrieving a shared album's images
Note: In my situation, the album I wanted to display was shared with me.
1. `GET https://photoslibrary.googleapis.com/v1/sharedAlbums` should return the shared albums you have. In the response, you'll be able to find the albumId.
2. `POST https://photoslibrary.googleapis.com/v1/mediaItems:search` specifying the albumId should return a paginated list of all URLs for all photos in the album.

### PIL Image Manipulation
The display used in this project is 600x448p. Ideally, images should have their
aspect ratio preserved while resized to fit into the display.

The solution chosen in this project is to crop the center.

![center crop demonstration](./assets/crop.png)

## Troubleshooting


## Potential Features




