#!/usr/bin/bash

# Check if filename is provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <output_file_path> <url> [<submodule_1>, ...]"
    exit 1
fi

output_file="$1"
webpage="webpage.html.tmp"

# Download webpage
curl -Ls "$2" > "$webpage"
# Check if curl was successful
if [ $? -ne 0 ]; then
    echo "Failed to download webpage."
    rm "$webpage"  # Clean up temporary file
    exit 1
fi

# Clear output file
> "$output_file"

# If no additional search terms are provided, search only for "<span class="pre">"
if [ $# -eq 2 ]; then
    grep_pattern="<span class=\"pre\">"
    grep -oP "${grep_pattern}\K[^<]*" "$webpage" | sed 's/[*()]//g' >> "$output_file"
else
    # Loop over each search term
    for term in "${@:3}"; do
        if [ -n "$term" ]; then
            grep_pattern="<span class=\"pre\">${term}\."
            grep -oP "${grep_pattern}\K[^<]*" "$webpage" | sed 's/[*()]//g' >> "$output_file"
        fi
    done
fi

rm "$webpage"  # Clean up temporary file
echo "Output saved to $output_file"
