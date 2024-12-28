#!/usr/bin/bash

if [ "$EUID" -ne 0 ]; then
    echo "This script must be run with sudo."
    exit 1
fi

#===========================================================================
#                            Configuring rclone.
#===========================================================================
echo "Configuring RClone."

# Installing RClone.
sudo -v ; curl https://rclone.org/install.sh | sudo bash
sudo apt install -y fuse3 python-pip

# Setting up RClone's connection to Google Photos.
rclone config

#===========================================================================
#                            Setting up dependencies
#===========================================================================
echo "Installing dependencies."

sudo pip install -r displayer_service/requirements.txt

# Inky throws an error, 'libopenblas.so.0: cannot open shared object file: No such file or directory'.
# Installing this fixes it.
sudo apt-get install libopenblas-dev 

#===========================================================================
#                  Configuring Ink Memories to run as a daemon
#===========================================================================
echo "Configuring Ink Memories to run as a daemon."

# Interpolate in user-supplied variables into the .service files under
# /etc/systemd/system.
read -p "Enter image source directory path (where the image files to display are located at): " image_src_dir
read -p "Enter the directory of the InkMemories root repository: " ink_memories_root
read -p "Enter the name of the shared Google Photos album: " shared_album_name

mkdir -p "${image_src_dir}" 2>&1

for service_file_basename in ink-memories-image-source.service ink-memories-displayer.service; do
    echo "Making service file, $service_file_basename"
    sed -e "s|{{IMAGE_SRC_DIR}}|${image_src_dir}|g" \
        -e "s|{{INK_MEMORIES_ROOT}}|${ink_memories_root}|g" \
        -e "s|{{SHARED_ALBUM_NAME}}|${shared_album_name}|g" \
        -e "s|{{HOME_DIR}}|${HOME}|g" \
        "./service_files/${service_file_basename}" > /etc/systemd/system/${service_file_basename}
    
    sudo systemctl daemon-reload
    sudo systemctl enable $service_file_basename
    sudo systemctl start $service_file_basename
done

