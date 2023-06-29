import random, time, requests, json, html
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import browsercookie
import argparse

'''optional arguments:
  -h, --help            show this help message and exit
  -o ORIGIN, --origin ORIGIN
                        Origin IATA airport code.
  -d DATES, --dates DATES
                        Show flights for: Today: 1 Tommorrow: 2 Both: 3
  -c, --cjs             Use browser cookies.
  -r RESUME, --resume RESUME
                        Index of airport to resume from. Use index 21 to only
                        search for contiguous US destinations.'''
 
# Global Variables
destination_count = 0
destinations_avail = {}
roundtrip_avail = {}

all_destinations = {
    'ANU': 'Antigua and Barbuda', 
    'NAS': 'Bahamas', 
    'BZE': 'Belize', 
    'LIR': 'Costa Rica', 
    'SJO': 'San José', 
    'PUJ': 'Punta Cana, DR', 
    'SDQ': 'Santo Domingo, DR', 
    'SAL': 'El Salvador', 
    'GUA': 'Guatemala', 
    'KIN': 'Jamaica', 
    'MBJ': 'St. James', 
    'SJD': 'Los Cabos, MX', 
    'GDL': 'Guadalajara, MX', 
    'PVR': 'Puerto Vallarta, MX', 
    'MTY': 'Monetrrey, MX', 
    'CUN': 'Cancun, MX', 
    'CZM': 'Cozumel, MX',  
    'SXM': 'St. Maarten', 
    'BQN': 'Aguadilla, Puerto Rico', 
    'PSE': 'Ponce, Puerto Rico', 
    'SJU': 'San Juan, Puerto Rico',
    'PHX': 'Phoenix', 
    'XNA': 'Arkansas', 
    'LIT': 'Little Rock, AR', 
    'OAK': 'Oakland', 
    'ONT': 'Ontario', 
    'SNA': 'Orange County', 
    'SMF': 'Sacramento', 
    'SAN': 'San Diego', 
    'SFO': 'San Francisco', 
    'DEN': 'Colorado', 
    'BDL': 'Connecticut', 
    'FLL': 'Fort Lauderdale, FL', 
    'RSW': 'Fort Myers, FL', 
    'JAX': 'Jacksonville, FL', 
    'MIA': 'Miami, FL', 
    'MCO': 'Orlando, FL', 
    'PNS': 'Pensacola, FL', 
    'SRQ': 'Sarasota, FL', 
    'TPA': 'Tampa, FL', 
    'PBI': 'West Palm Beach, FL', 
    'ATL': 'Atlanta, Georgia', 
    'SAV': 'Savannah, Georgia', 
    'BMI': 'Illinois', 
    'MDW': 'Chicago', 
    'IND': 'Indiana', 
    'CID': 'Cedar rapids, Iowa', 
    'DSM': 'Des Moines, Iowa', 
    'CVG': 'Kentucky', 
    'MSY': 'Louisiana', 
    'PWM': 'Maine', 
    'BWI': 'Maryland', 
    'BOS': 'Massachusetts', 
    'DTW': 'Michigan', 
    'GRR': 'Grand Rapids, MI', 
    'MSP': 'Minnesota', 
    'MCI': 'Missouri', 
    'STL': 'St. Louis', 
    'MSO': 'Montana', 
    'OMA': 'Nebraska', 
    'LAS': 'Las Vegas', 
    'TTN': 'New Jersey', 
    'BUF': 'New York', 
    'ISP': 'Long Island/Islip', 
    'SWF': 'Newburgh', 
    'LGA': 'New York City', 
    'SYR': 'Syracuse', 
    'CLT': 'North Carolina', 
    'RDU': 'Raleigh, NC', 
    'FAR': 'North Dakota', 
    'CLE': 'Ohio', 
    'CMH': 'Columbus', 
    'OKC': 'Oklahoma', 
    'PDX': 'Oregon', 
    'MDT': 'Pennsylvania', 
    'PHL': 'Philadelphia', 
    'PIT': 'Pittsburgh', 
    'CHS': 'Charleston, South Carolina', 
    'MYR': 'Myrtle Beach, SC', 
    'TYS': 'Tennessee', 
    'MEM': 'Memphis', 
    'BNA': 'Nashville', 
    'AUS': 'Austin, Texas', 
    'DFW': 'Dallas/Fort Worth', 
    'ELP': 'El Paso', 
    'IAH': 'Houston', 
    'SAT': 'San Antonio', 
    'STT': 'U.S. Virgin Islands', 
    'SLC': 'Utah', 
    'DCA': 'Virginia', 
    'ORF': 'Norfolk', 
    'SEA': 'Washington', 
    'GRB': 'Wisconsin', 
    'MSN': 'Madison', 
    'MKE': 'Milwaukee'}
def generate_user_agent():
    platform = random.choice(['Windows NT 10.0', 'Macintosh; Intel Mac OS X 10_15_7'])
    webkit_version = random.choice(['537.36', '605.1.15'])
    chrome_version = f"{random.randint(80, 91)}.0.{random.randint(1000, 9999)}.{random.randint(100, 999)}"
    firefox_version = f"{random.randint(80, 89)}.0"
    
    return f"Mozilla/5.0 ({platform}) AppleWebKit/{webkit_version} (KHTML, like Gecko) Chrome/{chrome_version} Safari/{webkit_version}"

def get_flight_html(origin, date, session, cjs, roundtrip, start_index=0, destinations = all_destinations):

    date_str = date.strftime("%b-%d,-%Y").replace("-", "%20")
    #f = open("destinations.txt", "a")
    #f.write("Origin: " + origin + "\n")
    destination_keys = list(destinations.keys()) # Retrieve a list of destination keys
    for i in range(start_index, len(destination_keys)):
        dest = destination_keys[i]

        if dest == origin:
            print('cannot search between identical origin and destination')
            continue

        # Choose a random User-Agent header
        header = {
            "User-Agent": generate_user_agent(),
        }
        cj = browsercookie.chrome() if cjs else None
        time.sleep(random.uniform(0.5,1.5))
        #time.sleep(random.uniform(0.5,1.5))
        # Get schedule data for the route
        schedule_url = f"https://booking.flyfrontier.com/Flight/RetrieveSchedule?calendarSelectableDays.Origin={origin}&calendarSelectableDays.Destination={dest}"
        schedule_response = requests.Session().get(schedule_url, headers=header, cookies=cj) if cjs else requests.Session().get(schedule_url, headers=header)
            
        if schedule_response.status_code == 200:
            schedule_data = schedule_response.json()
            disabled_dates = schedule_data['calendarSelectableDays']['disabledDates']
            last_available_date = schedule_data['calendarSelectableDays']['lastAvailableDate']

            # Convert the input date to the same format as the disabled dates list
            formatted_date = date.strftime('%m/%d/%Y')

            # Check if the date is in the list of disabled dates
            if formatted_date in disabled_dates or last_available_date == '0001-01-01 00:00:00':
                print(f"{i}. No flights available on {formatted_date} from {origin} to {dest}. Date skipped.")
                continue
        else:
            print(f"{i}. Problem accessing URL: code {schedule_response.status_code}\n url = " + schedule_url)

        
        # Mimic human-like behavior by adding delays between requests
        #delay = random.uniform(2, 5)  # Random delay between 2 to 5 seconds
        #time.sleep(delay)
        time.sleep(random.uniform(0.5,1.5))
        url = f"https://booking.flyfrontier.com/Flight/InternalSelect?o1={origin}&d1={dest}&dd1={date_str}&ADT=1&mon=true&promo="
        response = session.get(url, headers=header, cookies=cj) if cjs else session.get(url, headers=header)
        if (response.status_code == 200):
            decoded_data = extract_html(response)
            if (decoded_data != 'NoneType'):
                orgin_success = extract_json(decoded_data, origin, dest, date, roundtrip)
                if(roundtrip == 1 & orgin_success):
                    new_dest = {origin: all_destinations[origin]}
                    # 1 = trigger roundtrip
                    # 0 = no roundtrip
                    # -1 = in roundtrip recurssion 
                    get_flight_html(dest, (date+timedelta(days=1)), session, cjs, -1, 0, new_dest)
                    roundtrip = 1 # reset var for the next dest
                #f.write(dest + ",")
        else:
            print(f"{i}. Problem accessing URL: code {response.status_code}\n url = " + url)
            break
    #f.close()

def extract_json(flight_data, origin, dest, date, roundtrip):
    # Extract the flights with isGoWildFareEnabled as true
    try:
        flights = flight_data['journeys'][0]['flights']
    except (TypeError, KeyError):
        return 0
    if (flights == None):
        return 0
    go_wild_count = 0

    for flight in flights:
        if flight["isGoWildFareEnabled"]:
            if (go_wild_count == 0):
                print(f"\n{'{} to {}: {}'.format(origin, dest, all_destinations[dest]) if roundtrip != -1 else '**Return flight'} available:")
                #print(f"\n{'{origin} to {dest}: {all_destinations[dest]}' if roundtrip!=-1 else 'Return flight'} available:")
            go_wild_count+=1
            info = flight['legs'][0]
            print(f"flight {go_wild_count}. {flight['stopsText']}")
            print(f"\tDate: {info['departureDate'][5:10]}")
            print(f"\tDepart: {info['departureDateFormatted']}")
            print(f"\tTotal flight time: {flight['duration']}")
            print(f"Price: ${flight['goWildFare']}")
            # if go wild seats value is provided
            if flight['goWildFareSeatsRemaining'] is not None:
                print(f"Go Wild: {flight['goWildFareSeatsRemaining']}\n")
    
    if (go_wild_count == 0):
        print(f"No {'next day return ' if roundtrip==-1 else ''}flights from {origin} to {dest}")
        return 0
    else:
        if(roundtrip==-1):
            roundtrip_avail[origin] = all_destinations.get(origin)
        else:
            destinations_avail[dest] = all_destinations.get(dest)
        print(f"{origin} to {dest}: {go_wild_count} GoWild {'return ' if roundtrip==-1 else''}flights available for {date.strftime('%A, %m-%d-%y')}")
    return 1

def extract_html(response):
    # Parse the HTML source using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all <script> tags with type="text/javascript" and extract their contents
    scripts = soup.find("script", type="text/javascript")
    decoded_data = html.unescape(scripts.text)
    decoded_data = decoded_data[decoded_data.index('{'):decoded_data.index(';')-1]
    return json.loads(decoded_data)

def print_dests(origin):
    print(f"\n{len(destinations_avail)} destinations found from {origin}:")
    for dest, name in destinations_avail.items():
        print(f"{'**' if dest in roundtrip_avail else ''}{dest}: {name}")
    print("** = next day return flight available")
def main():
    global all_destinations

    parser = argparse.ArgumentParser(description='Check flight availability.')
    parser.add_argument('-o', '--origin', type=str, required=True, help='Origin IATA airport code.')
    parser.add_argument('-d', '--dates', type=str, required=True, help='Show flights for:\n\tToday: 1\n\tTommorrow: 2\n\tBoth: 3')
    # ??? Unsure how to offer feature right now
    #parser.add_argument('-t', '--roundtrip', type=bool, default=False, help='Search for a roundtrip/return flights for tomorrow. \'True\' for yes, defualt is no')
    parser.add_argument('-c', '--cjs', action='store_true', help='Use browser cookies.')
    parser.add_argument('-r', '--resume', type=int, default=0, help='Index of airport to resume from. Use index 21 to only search for contiguous US destinations.')

    args = parser.parse_args()
    origin = args.origin.upper()
    input_dates = args.dates
    #roundtrip = args.roundtrip()
    cjs = args.cjs
    today = datetime.today()
    # test during blackout period
    #today = datetime(2023,7,6)    
    session = requests.Session()
    resume = args.resume

    if input_dates in ['1','3']:
        roundtrip = 1 # DEFAULT for now
        # Todays date in URL format
        print("\nFlights for today:")
#(origin, date, session, cjs, roundtrip, start_index=0, destinations = all_destinations):
        get_flight_html(origin, today, session, cjs, roundtrip, resume)
        print_dests(origin)

    if input_dates in ['2','3']:
        roundtrip = 0 # DEFAULT for now
        # Tomorrows date in URL
        tmrw = today + timedelta(days=1)
        travel_tmrw = tmrw.strftime("%b-%d,-%Y").replace("-", "%20")
        print("\nFlights for tommorrow:")
        get_flight_html(origin, tmrw, session, cjs, roundtrip, resume)
        print_dests(origin)        

if __name__ == "__main__":
    main()