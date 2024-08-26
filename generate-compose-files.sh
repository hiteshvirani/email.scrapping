#!/bin/bash

for i in $(seq 1 15); do
  cat > docker-compose.override.$i.yml <<EOF

services:
  email-scraper:
    environment:
      - CSV_PATH=/app/input/search.queries.$i.csv
    volumes:
      - /home/hitesh/A/Data/email.scrapping/input/search.queries.$i.csv:/app/input/search.queries.$i.csv
EOF
done
