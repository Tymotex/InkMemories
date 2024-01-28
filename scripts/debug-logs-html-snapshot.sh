#!/bin/sh

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <logs_file_path>"
    exit 1
fi

debug_logs_file_path=$1

# Check if the argument is a file.
if [ ! -f "$debug_logs_file_path" ]; then
    echo "Error: '$debug_logs_file_path' is not a valid file."
    exit 1
fi

# Create an empty log file if it does not exist.
if [ ! -e "$debug_logs_file_path" ]; then
    touch "$debug_logs_file_path"
fi

output_dir=$(dirname "$debug_logs_file_path")
output_debug_screen_html_file_path="${output_dir}/debug-screen.html"
output_debug_screen_image_name="debug-screen.png"

while true; do
    # Capture the most recent several lines and format it into an HTML file.
    # Note: The HTML file is very barebones currently but can be customised with
    #       better styling and formatting with CSS.
    echo "Grabbing recent logs and creating an HTML file."
    logs=$(tail -50 "$debug_logs_file_path" | tac)

    # Reset the HTML file's contents and write formatted HTML logs to it.
    echo "" > "$output_debug_screen_html_file_path"
    echo "$logs" | while IFS= read -r line; do
        # Wrap each line in <p>...</p> and dump to HTML file.
        echo "<p>${line}</p>" >> "$output_debug_screen_html_file_path"
    done

    # Take a screenshot of the HTML file to produce an image file.
    # Note: What if the HTML file contains too many lines - wouldn't that not
    #       fit into the output image? Yup - it gets truncated. This is
    #       acceptable because we usually only care about the most recent logs.
    output_screenshot_path="${output_dir}/${output_debug_screen_image_name}"
    echo "Taking screenshot at path: $output_screenshot_path"
    chromium \
        --headless \
        --screenshot="$output_screenshot_path" \
        --window-size=600,448 \
        "$output_debug_screen_html_file_path"
    sleep 5s
done
