import csv
import os

# Configuration
INPUT_DIR = 'input'
CSV_PREFIX = os.path.join(INPUT_DIR, 'search.queries')
MAX_LINES_PER_FILE = 10000

# Search parameters
SITES = ["site:instagram.com", "site:linkedin.com", "site:x.com"]
EMAIL_PROVIDERS = ["@gmail.com"]
CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", 
    "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville", 
    "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Indianapolis", 
    "Seattle", "Denver", "Washington", "Boston", "El Paso", "Nashville", 
    "Detroit", "Oklahoma City", "Portland", "Las Vegas", "Memphis", "Louisville", 
    "Baltimore", "Milwaukee", "Albuquerque", "Tucson", "Fresno", "Mesa", 
    "Sacramento", "Atlanta", "Kansas City", "Colorado Springs", "Miami", 
    "Raleigh", "Omaha", "Long Beach", "Virginia Beach", "Oakland", "Minneapolis", 
    "Tulsa", "Arlington", "Tampa", "New Orleans", "Wichita", "Cleveland", 
    "Bakersfield", "Aurora", "Anaheim", "Honolulu", "Santa Ana", "Riverside", 
    "Corpus Christi", "Lexington", "Stockton", "St. Louis", "Saint Paul", 
    "Henderson", "Pittsburgh", "Cincinnati", "Anchorage", "Greensboro", "Plano", 
    "Newark", "Lincoln", "Orlando", "Irvine", "Toledo", "Jersey City", 
    "Chula Vista", "Durham", "Fort Wayne", "St. Petersburg", "Laredo", "Buffalo", 
    "Madison", "Lubbock", "Chandler", "Scottsdale", "Reno", "Glendale", "Gilbert", 
    "Winston-Salem", "North Las Vegas", "Norfolk", "Chesapeake", "Garland", 
    "Irving", "Hialeah", "Fremont", "Boise", "Richmond", "Baton Rouge", 
    "Spokane", "Des Moines", "Tacoma", "San Bernardino", "Modesto", "Fontana", 
    "Santa Clarita", "Birmingham", "Oxnard", "Fayetteville", "Moreno Valley", 
    "Rochester", "Glendale", "Huntington Beach", "Salt Lake City", "Grand Rapids", 
    "Amarillo", "Yonkers", "Aurora", "Montgomery", "Akron", "Little Rock", 
    "Huntsville", "Augusta", "Port St. Lucie", "Grand Prairie", "Columbus", 
    "Tallahassee", "Overland Park", "Tempe", "McKinney", "Mobile", "Cape Coral", 
    "Shreveport", "Frisco", "Knoxville", "Worcester", "Brownsville", "Vancouver", 
    "Fort Lauderdale", "Sioux Falls", "Ontario", "Chattanooga", "Providence", 
    "Newport News", "Rancho Cucamonga", "Santa Rosa", "Oceanside", "Salem", 
    "Elk Grove", "Garden Grove", "Pembroke Pines", "Peoria", "Eugene", "Corona", 
    "Cary", "Springfield", "Fort Collins", "Jackson", "Alexandria", "Hayward", 
    "Lancaster", "Lakewood", "Clarksville", "Palmdale", "Salinas", "Springfield", 
    "Hollywood", "Pasadena", "Sunnyvale", "Macon", "Pomona", "Escondido", 
    "Killeen", "Naperville", "Joliet", "Bellevue", "Rockford", "Savannah", 
    "Paterson", "Torrance", "Bridgeport", "McAllen", "Mesquite", "Syracuse", 
    "Midland", "Murfreesboro", "Miramar", "Dayton", "Fullerton", "Olathe", 
    "Orange", "Thornton", "Roseville", "Denton", "Waco", "Surprise", "Carrollton", 
    "West Valley City", "Charleston", "Warren", "Hampton", "Gainesville", 
    "Visalia", "Coral Springs", "Columbia", "Cedar Rapids", "Sterling Heights", 
    "New Haven", "Stamford", "Concord", "Kent", "Santa Clara", "Elizabeth", 
    "Round Rock", "Thousand Oaks", "Lafayette", "Athens", "Topeka", "Simi Valley", 
    "Fargo", "Norman", "Abilene", "Wilmington", "Hartford", "Victorville", 
    "Pearland", "Vallejo", "Ann Arbor", "Berkeley", "Allentown", "Richardson", 
    "Odessa", "Arvada", "Cambridge", "Sugar Land", "Beaumont", "Lansing", 
    "Evansville", "Rochester", "Independence", "Fairfield", "Provo", "Clearwater", 
    "College Station", "West Jordan", "Carlsbad", "El Monte", "Murrieta", 
    "Temecula", "Palm Bay", "Costa Mesa", "Westminster", "North Charleston", 
    "Miami Gardens", "Manchester", "High Point", "Downey", "Clovis", "Pompano Beach", 
    "Pueblo", "Elgin", "Lowell", "Antioch", "West Palm Beach", "Everett", "Ventura", 
    "Centennial", "Lakeland", "Gresham", "Richmond", "Billings", "Inglewood", 
    "Broken Arrow", "Sandy Springs", "Jurupa Valley", "Hillsboro", "Waterbury", 
    "Santa Maria", "Boulder", "Greeley", "Daly City", "Meridian", "Lewisville", 
    "Davie", "West Covina", "League City", "Tyler", "Norwalk", "San Mateo", 
    "Green Bay", "Wichita Falls", "Sparks", "Lakewood", "Burbank", "Rialto", 
    "Allen", "El Cajon", "Las Cruces", "Renton", "Davenport", "South Bend", 
    "Vista", "Tuscaloosa", "Clinton", "Edison", "Woodbridge", "San Angelo", 
    "Kenosha", "Vacaville", "Lawrence", "Santa Monica", "Tracy", "Beaverton", 
    "South Gate", "Mission", "Edinburg", "San Buenaventura", "Bellingham", 
    "Lake Charles", "San Marcos", "Albany", "Bend", "Upland", "Folsom", 
    "Camden", "Brockton", "Palm Coast", "Merced", "Lauderhill", "Missoula", 
    "Fort Smith", "San Leandro", "Boynton Beach", "Gary", "Mount Pleasant", 
    "Longview", "Canton", "Livermore", "Lawton", "Boca Raton", "Redwood City", 
    "Alhambra", "Conroe", "Mission Viejo", "Brooklyn Park", "Fall River", 
    "Newton", "Schenectady", "Dearborn", "Greenville", "Yuma", "Santa Barbara", 
    "Chino", "Dothan", "Florissant", "Rogers", "North Little Rock", "Reading", 
    "Farmington Hills", "Portsmouth", "Florence", "Warner Robins", "Union City", 
    "St. Charles", "Lynn", "Yakima", "Tamarac", "Southfield", "Nampa", 
    "Portland", "Bossier City", "Rochester Hills", "South San Francisco", 
    "Bryan", "Lodi", "Livonia", "Pharr", "Vista", "Miami Beach", "West Allis", 
    "Delray Beach", "Oshkosh", "Hesperia", "Compton", "Nashua", "Missouri City", 
    "Layton", "Carmel", "Janesville", "Gastonia"
]

def load_existing_queries():
    """Load already generated queries to avoid duplicates"""
    existing = set()
    
    # Ensure input directory exists
    os.makedirs(INPUT_DIR, exist_ok=True)
    
    # Scan for existing query files
    index = 1
    while True:
        file_path = f'{CSV_PREFIX}.{index}.csv'
        if not os.path.exists(file_path):
            break
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and len(row) > 1:
                        existing.add(row[1])
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
        
        index += 1
        
    return existing, index

def generate_queries(existing_queries):
    """Generate new unique queries"""
    new_queries = set()
    for site in SITES:
        for city in CITIES:
            for email in EMAIL_PROVIDERS:
                query = f'{site} "{city}" "{email}"'
                if query not in existing_queries:
                    new_queries.add(query)
    return new_queries

def write_queries(new_queries, start_file_index, existing_count):
    """Write new queries to CSV files"""
    queries_list = list(new_queries)
    file_index = start_file_index
    current_count = existing_count
    
    while queries_list:
        chunk = queries_list[:MAX_LINES_PER_FILE]
        queries_list = queries_list[MAX_LINES_PER_FILE:]
        
        file_path = f'{CSV_PREFIX}.{file_index}.csv'
        print(f"Writing {len(chunk)} queries to {file_path}...")
        
        try:
            with open(file_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for i, query in enumerate(chunk):
                    writer.writerow([current_count + 1, query])
                    current_count += 1
        except IOError as e:
            print(f"Error writing to {file_path}: {e}")
            return
            
        file_index += 1
        
    print(f"Successfully added {len(new_queries)} new queries.")

def main():
    print("Generating search queries...")
    existing_queries, next_file_index = load_existing_queries()
    print(f"Found {len(existing_queries)} existing queries.")
    
    new_queries = generate_queries(existing_queries)
    
    if new_queries:
        print(f"Found {len(new_queries)} new unique queries to add.")
        write_queries(new_queries, next_file_index, len(existing_queries))
    else:
        print("No new queries to generate.")

if __name__ == "__main__":
    main()