#!/bin/bash

# Set the maximum number of concurrent containers
MAX_CONTAINERS=4

# Paths to the input, output, and log directories
INPUT_DIR="/home/hitesh/A/Data/email.scrapping/input"
OUTPUT_DIR="/home/hitesh/A/Data/email.scrapping/output"
LOG_DIR="/home/hitesh/A/Data/email.scrapping/logs"

# Docker image name
DOCKER_IMAGE="scrapping_img"

# Ensure the log directory exists
mkdir -p "$LOG_DIR"

# Function to run a Docker container
run_container() {
    local csv_file="$1"
    local container_name="email-scraper-container-$(basename "$csv_file" .csv)"
    local log_file="$LOG_DIR/$(basename "$csv_file" .csv).log"

    echo "Starting container: $container_name for CSV: $csv_file"

    docker run \
      --name "$container_name" \
      -v "$INPUT_DIR/$csv_file":/app/input/"$csv_file" \
      -v "$OUTPUT_DIR":/app/output \
      -e DISPLAY=:99 \
      -e CSV_PATH=/app/input/"$csv_file" \
      "$DOCKER_IMAGE" \
      python scrapping.py > "$log_file" 2>&1 &
}

# Function to monitor and restart container if necessary
monitor_container() {
    local container_name="$1"
    local log_file="$2"
    
    # Wait for 120 seconds to check the log file
    sleep 120

    if ! grep -q "Cookie acceptance button not found or already accepted." "$log_file"; then
        echo "Log message not found for container $container_name. Restarting container..."
        
        # Stop and remove the existing container
        docker stop "$container_name"
        docker rm "$container_name"

        # Re-run the container
        run_container "$csv_file"
    else
        echo "Log message found for container $container_name."
    fi
}

# Main loop to process all CSVs
while true; do
    # Get the list of CSV files in the input directory
    csv_files=($(ls "$INPUT_DIR"/*.csv 2>/dev/null))

    # If there are no more CSV files, exit the loop
    if [ ${#csv_files[@]} -eq 0 ]; then
        echo "All CSV files have been processed."
        break
    fi

    # Start new containers if the number of running containers is below the limit
    while [ $(docker ps -q | wc -l) -lt "$MAX_CONTAINERS" ] && [ ${#csv_files[@]} -gt 0 ]; do
        # Get the first CSV file from the list
        csv_file=$(basename "${csv_files[0]}")

        # Calculate a random delay between 10 and 200 seconds
        delay=$((RANDOM % 191 + 10))

        echo "Waiting for $delay seconds before starting the next container..."

        # Sleep for the random delay
        sleep "$delay"

        # Create a container name and log file path
        container_name="email-scraper-container-$(basename "$csv_file" .csv)"
        log_file="$LOG_DIR/$(basename "$csv_file" .csv).log"

        # Run the Docker container with the CSV file
        run_container "$csv_file"

        # Monitor the container's log file
        monitor_container "$container_name" "$log_file" &

        # Remove the CSV file from the list
        csv_files=("${csv_files[@]:1}")

        # Update the number of running containers
        running_containers=$(docker ps -q | wc -l)
    done

    # Wait for any container to stop before continuing
    wait
done
