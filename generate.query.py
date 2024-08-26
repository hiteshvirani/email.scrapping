import csv
import os

# Define your dynamic lists
sites = ["site:instagram.com", "site:linkedin.com"]
email_providers = ["@gmail.com"]

# Example list of cities (add more cities for all countries and states)
cities = ["Ahmedabad", "Rajkot", "Mumbai", "Delhi", "New York", "Los Angeles", "London", "Paris", "Tokyo"]

# Output CSV file name
csv_filename = 'search-queries.csv'

# Ensure the CSV file exists and load existing queries if any
existing_queries = set()
if os.path.exists(csv_filename):
    with open(csv_filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row and len(row) > 1:
                existing_queries.add(row[1])

# Function to generate queries
def generate_queries():
    queries = set()
    for site in sites:
        for city in cities:
            for email in email_providers:
                query = f'{site} "{city}" "{email}"'
                if query not in existing_queries:
                    queries.add(query)
    return queries

# Write new queries to the CSV
def write_to_csv(queries):
    with open(csv_filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        start_index = len(existing_queries) + 1
        for i, query in enumerate(queries, start=start_index):
            writer.writerow([i, query])

def main():
    new_queries = generate_queries()
    if new_queries:
        write_to_csv(new_queries)
        print(f'{len(new_queries)} new queries added to {csv_filename}')
    else:
        print('No new queries to add.')

if __name__ == "__main__":
    main()
