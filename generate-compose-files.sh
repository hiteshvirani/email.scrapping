# #!/bin/bash

# for i in $(seq 1 5); do
#   cat > docker-compose.override.$i.yml <<EOF

# services:
#   email-scraper:
#     environment:
#       - CSV_PATH=/app/input/search.queries.$i.csv
#     volumes:
#       - /home/hitesh/A/Data/email.scrapping/input/search.queries.$i.csv:/app/input/search.queries.$i.csv
# EOF
# done


#!/bin/bash

# Directory paths
input_dir="/home/hitesh/A/Data/email.scrapping/input"
output_dir="/home/hitesh/A/Data/email.scrapping/output"

# Number of overrides to create
num_overrides=5

# Create Docker Compose override files
for i in $(seq 1 $num_overrides); do
  cat > docker-compose.override.$i.yml <<EOF

services:
  email-scraper-$i:
    image: scrapping_img
    environment:
      - CSV_PATH=/app/input/search.queries.$i.csv
    volumes:
      - type: bind
        source: $input_dir/search.queries.$i.csv
        target: /app/input/search.queries.$i.csv
      - type: bind
        source: $output_dir
        target: /app/output
    command: python scrapping.py
EOF
done
