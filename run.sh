# #!/bin/bash

# # Directory paths
# logs_dir="/home/hitesh/A/Data/email.scrapping/logs"

# # Create the logs directory if it does not exist
# mkdir -p "$logs_dir"

# # Run Docker Compose with each override file
# for i in $(seq 1 15); do
#   docker-compose -f docker-compose.yml -f docker-compose.override.$i.yml up -d > "$logs_dir/compose-$i.log" 2>&1
# done

#!/bin/bash

# Directory paths
logs_dir="/home/hitesh/A/Data/email.scrapping/logs"

# Create the logs directory if it does not exist
mkdir -p "$logs_dir"

# Run Docker Compose with each override file
for i in $(seq 1 5); do
  echo "Starting container with override file: docker-compose.override.$i.yml"
  docker-compose -f docker-compose.yml -f docker-compose.override.$i.yml up -d > "$logs_dir/compose-$i.log" 2>&1
  # Check if the container started successfully
  if [ $? -eq 0 ]; then
    echo "Container $i started successfully."
  else
    echo "Failed to start container $i. Check log file: $logs_dir/compose-$i.log"
  fi
done
