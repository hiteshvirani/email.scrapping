import csv
import os

sites = ["site:instagram.com", "site:linkedin.com", "site:x.com"]
email_providers = ["@gmail.com"]
cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville", "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Indianapolis", "Seattle", "Denver", "Washington", "Boston", "El Paso", "Nashville", "Detroit", "Oklahoma City", "Portland", "Las Vegas", "Memphis", "Louisville", "Baltimore", "Milwaukee", "Albuquerque", "Tucson", "Fresno", "Mesa", "Sacramento", "Atlanta", "Kansas City", "Colorado Springs", "Miami", "Raleigh", "Omaha", "Long Beach", "Virginia Beach", "Oakland", "Minneapolis", "Tulsa", "Arlington", "Tampa", "New Orleans", "Wichita", "Cleveland", "Bakersfield", "Aurora", "Anaheim", "Honolulu", "Santa Ana", "Riverside", "Corpus Christi", "Lexington", "Stockton", "St. Louis", "Saint Paul", "Henderson", "Pittsburgh", "Cincinnati", "Anchorage", "Greensboro", "Plano", "Newark", "Lincoln", "Orlando", "Irvine", "Toledo", "Jersey City", "Chula Vista", "Durham", "Fort Wayne", "St. Petersburg", "Laredo", "Buffalo", "Madison", "Lubbock", "Chandler", "Scottsdale", "Reno", "Glendale", "Gilbert", "Winston-Salem", "North Las Vegas", "Norfolk", "Chesapeake", "Garland", "Irving", "Hialeah", "Fremont", "Boise", "Richmond", "Baton Rouge", "Spokane", "Des Moines", "Tacoma", "San Bernardino", "Modesto", "Fontana", "Santa Clarita", "Birmingham", "Oxnard", "Fayetteville", "Moreno Valley", "Rochester", "Glendale", "Huntington Beach", "Salt Lake City", "Grand Rapids", "Amarillo", "Yonkers", "Aurora", "Montgomery", "Akron", "Little Rock", "Huntsville", "Augusta", "Port St. Lucie", "Grand Prairie", "Columbus", "Tallahassee", "Overland Park", "Tempe", "McKinney", "Mobile", "Cape Coral", "Shreveport", "Frisco", "Knoxville", "Worcester", "Brownsville", "Vancouver", "Fort Lauderdale", "Sioux Falls", "Ontario", "Chattanooga", "Providence", "Newport News", "Rancho Cucamonga", "Santa Rosa", "Oceanside", "Salem", "Elk Grove", "Garden Grove", "Pembroke Pines", "Peoria", "Eugene", "Corona", "Cary", "Springfield", "Fort Collins", "Jackson", "Alexandria", "Hayward", "Lancaster", "Lakewood", "Clarksville", "Palmdale", "Salinas", "Springfield", "Hollywood", "Pasadena", "Sunnyvale", "Macon", "Pomona", "Escondido", "Killeen", "Naperville", "Joliet", "Bellevue", "Rockford", "Savannah", "Paterson", "Torrance", "Bridgeport", "McAllen", "Mesquite", "Syracuse", "Midland", "Murfreesboro", "Miramar", "Dayton", "Fullerton", "Olathe", "Orange", "Thornton", "Roseville", "Denton", "Waco", "Surprise", "Carrollton", "West Valley City", "Charleston", "Warren", "Hampton", "Gainesville", "Visalia", "Coral Springs", "Columbia", "Cedar Rapids", "Sterling Heights", "New Haven", "Stamford", "Concord", "Kent", "Santa Clara", "Elizabeth", "Round Rock", "Thousand Oaks", "Lafayette", "Athens", "Topeka", "Simi Valley", "Fargo", "Norman", "Abilene", "Wilmington", "Hartford", "Victorville", "Pearland", "Vallejo", "Ann Arbor", "Berkeley", "Allentown", "Richardson", "Odessa", "Arvada", "Cambridge", "Sugar Land", "Beaumont", "Lansing", "Evansville", "Rochester", "Independence", "Fairfield", "Provo", "Clearwater", "College Station", "West Jordan", "Carlsbad", "El Monte", "Murrieta", "Temecula", "Palm Bay", "Costa Mesa", "Westminster", "North Charleston", "Miami Gardens", "Manchester", "High Point", "Downey", "Clovis", "Pompano Beach", "Pueblo", "Elgin", "Lowell", "Antioch", "West Palm Beach", "Everett", "Ventura", "Centennial", "Lakeland", "Gresham", "Richmond", "Billings", "Inglewood", "Broken Arrow", "Sandy Springs", "Jurupa Valley", "Hillsboro", "Waterbury", "Santa Maria", "Boulder", "Greeley", "Daly City", "Meridian", "Lewisville", "Davie", "West Covina", "League City", "Tyler", "Norwalk", "San Mateo", "Green Bay", "Wichita Falls", "Sparks", "Lakewood", "Burbank", "Rialto", "Allen", "El Cajon", "Las Cruces", "Renton", "Davenport", "South Bend", "Vista", "Tuscaloosa", "Clinton", "Edison", "Woodbridge", "San Angelo", "Kenosha", "Vacaville", "Lawrence", "Santa Monica", "Tracy", "Beaverton", "South Gate", "Mission", "Edinburg", "San Buenaventura", "Bellingham", "Lake Charles", "San Marcos", "Albany", "Bend", "Upland", "Folsom", "Camden", "Brockton", "Palm Coast", "Merced", "Lauderhill", "Missoula", "Fort Smith", "San Leandro", "Boynton Beach", "Gary", "Mount Pleasant", "Longview", "Canton", "Livermore", "Lawton", "Boca Raton", "Redwood City", "Alhambra", "Conroe", "Mission Viejo", "Brooklyn Park", "Fall River", "Newton", "Schenectady", "Dearborn", "Greenville", "Yuma", "Santa Barbara", "Chino", "Dothan", "Florissant", "Rogers", "North Little Rock", "Reading", "Farmington Hills", "Portsmouth", "Florence", "Warner Robins", "Union City", "St. Charles", "Lynn", "Yakima", "Tamarac", "Southfield", "Nampa", "Portland", "Bossier City", "Rochester Hills", "South San Francisco", "Bryan", "Lodi", "Livonia", "Pharr", "Vista", "Miami Beach", "West Allis", "Delray Beach", "Oshkosh", "Hesperia", "Compton", "Nashua", "Missouri City", "Layton", "Carmel", "Janesville", "Gastonia"]

# Output CSV file prefix
csv_prefix = 'input/search.queries'
max_lines_per_file = 1

# Ensure the CSV files exist and load existing queries if any
existing_queries = set()
file_index = 1

def get_existing_queries():
    global existing_queries
    global file_index
    for file_index in range(1, 1000):  # Assuming a maximum of 1000 files
        file_name = f'{csv_prefix}.{file_index}.csv'
        if os.path.exists(file_name):
            with open(file_name, 'r') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row and len(row) > 1:
                        existing_queries.add(row[1])
        else:
            break

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

# Write new queries to the CSV files
def write_to_csv(queries):
    global file_index
    queries_list = list(queries)
    while queries_list:
        file_name = f'{csv_prefix}.{file_index}.csv'
        with open(file_name, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            start_index = len(existing_queries) + 1
            for i in range(min(max_lines_per_file, len(queries_list))):
                writer.writerow([start_index + i, queries_list[i]])
        existing_queries.update(queries_list[:max_lines_per_file])
        queries_list = queries_list[max_lines_per_file:]
        file_index += 1

def main():
    get_existing_queries()
    new_queries = generate_queries()
    if new_queries:
        write_to_csv(new_queries)
        print(f'{len(new_queries)} new queries added across {file_index-1} files.')
    else:
        print('No new queries to add.')

if __name__ == "__main__":
    main()