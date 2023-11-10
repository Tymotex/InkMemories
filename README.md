# InkMemories

## Usage


Beware: disconnecting the Raspberry Pi directly from power can corrupt the SD card. Always click the top left button to perform a graceful shutdown before unplugging from power.

## Setup Instructions
These instructions assume that you have set up Raspbian OS.
- In `raspi-config`, enable I2C and SPI. This is necessary for getting the e-ink display to work.
- Set a hostname that you'd like with `cat $NEW_HOSTNAME >> /etc/hostname`.
- In your router's configuration either disable DHCP or reserve a static IP for the Raspberry Pi.

## Components


## How it works


## Troubleshooting



## Potential Features




