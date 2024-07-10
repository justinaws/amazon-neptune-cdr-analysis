import csv
import random
import datetime
from faker import Faker
from collections import namedtuple
from geopy.geocoders import Nominatim
from citipy import citipy
from random import uniform # Draw samples from a uniform distribution

# Initialize the Nominatim geolocator
geolocator = Nominatim(user_agent="cdr_data_generator")
fake = Faker()
Faker.seed(0)

# Define a namedtuple to represent a CDR entry
CDREntry = namedtuple('CDREntry', ['record_id', 
                                   'record_type',
                                   'caller_num', 
                                   'callee_num', 
                                   'start_time', 
                                   'end_time', 
                                   'duration', 
                                   'caller_location', 
                                   'callee_location',
                                   'cost', 
                                   'service_provider_id',
                                   'billing_indicator',  
                                   'call_status',
                                   'rate_plan',
                                   'currency'])

CDREntryExt = namedtuple('CDREntryExt', [
                                   'caller_state',
                                   'callee_state'])

# Define some sample data for callers, callees, service provider IDs, and record sources
callers = ['1234567890', '0987654321', '5551234567', '7778889999']
callees = ['9876543210', '0123456789', '6785432109', '1112223333']
service_provider_ids = ['SP001', 'SP002', 'SP003', 'SP004']
call_statuses = ['Answered', 'Missed', 'Busy', 'Failed']
billing_indicators = ['Billable', 'Non-Billable']
rate_plans = ['Go5G', 'EssentialsSaver', 'Essentials','Go5GPlus','Go5GNext']
currencies = ['USD']
call_type = ['Voice','SMS']

# Function to generate a random phone number
def generate_random_phone_number():
    area_code_prefixes = ['201', '202', '203', '204', '205', '206', '207', '208', '209']
    area_code = random.choice(area_code_prefixes)
    prefix = str(random.randint(200, 203))
    line_number = str(random.randint(1000, 1030))
    phone_number = f"{area_code}{prefix}{line_number}"
    return phone_number

# Function to get a random location name based on coordinates
def get_random_location_faker():
    latitude = random.uniform(25.0, 50.0)
    longitude = random.uniform(-125.0, -65.0)
    lat_log = []
    lat_log = fake.local_latlng(country_code= 'US')
    city = citipy.nearest_city(float(lat_log[0]), float(lat_log[1]))
    city_name = city.city_name
    country_code = city.country_code
    #city = lat_log[2]
    if city is not None:
        city_name = city.city_name
        state_name = city.state_name
        return f"{city_name}, {state_name}, United States"
    else:
        return "Unknown Location, Unknown State, United States"

# Function to get a random location name based on coordinates within the USA
def get_random_location():
    while True:
        latitude = random.uniform(25.0, 50.0)
        longitude = random.uniform(-125.0, -65.0)
        city = citipy.nearest_city(latitude, longitude)
        if city is not None and city.country_code == 'US':
            city_name = city.city_name
            state_name = city.state_name
            return f"{city_name}, {state_name}, United States"

# Function to generate a random CDR entry
def generate_cdr_entry():
    caller = generate_random_phone_number()
    callee = generate_random_phone_number()
    start_time = datetime.datetime.now() - datetime.timedelta(minutes=random.randint(1, 60))
    duration = datetime.timedelta(seconds=random.randint(30, 3600))
    end_time = start_time + duration
    record_type = random.choice(call_type)
    record_id = random.randint(1000000, 9999999)
    #caller_location = get_random_location()
    city_data = read_city_data_from_csv('/Users/jusjohnp/Documents/myProjects_Code/cdr-data-generator-master/cdr-data-generator/python/major_us_cities.csv')
    caller_location, caller_city_data = random_pick_from_dict(city_data) #get_random_location_faker()
    callee_location, callee_city_data = random_pick_from_dict(city_data) #get_random_location_faker()
    cost = round(random.uniform(0.1, 5.0), 2)  # Random cost between $0.10 and $5.00
    call_status = random.choice(call_statuses)
    billing_indicator = random.choice(billing_indicators)
    rate_plan = random.choice(rate_plans)
    service_provider_id = random.choice(service_provider_ids)
    currency = random.choice(currencies)
    #record_source = random.choice(record_sources)
    return CDREntry(record_id,record_type,caller, callee, str(start_time), 
                    end_time, duration, caller_location, callee_location, cost,service_provider_id, billing_indicator, 
                    call_status, rate_plan,currency), CDREntryExt(caller_city_data['state'],callee_city_data['state'])

# Function to generate and write CDR data to a CSV file
def generate_cdr_data(num_entries, file_name):
    distinct_phone_numbers = {}
    with open(file_name, 'w', newline='') as csvfile:
         fieldnames = CDREntry._fields
         writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)

         writer.writeheader()
         for _ in range(num_entries):
            cdr_entry,cdr_entry_ext = generate_cdr_entry()
            writer.writerow(cdr_entry._asdict())
            distinct_phone_numbers[cdr_entry.caller_num] = {
                  'caller_location': cdr_entry.caller_location,
                  'state': cdr_entry_ext.caller_state,
                  'birthdate': datetime.date(random.randint(1970, 2000), random.randint(1, 12), random.randint(1, 28)),
                  'plan_start_date': datetime.date(random.randint(2015, 2023), random.randint(1, 12), random.randint(1, 28))
            }
            distinct_phone_numbers[cdr_entry.callee_num] = {
                  'caller_location': cdr_entry.callee_location,
                  'state': cdr_entry_ext.callee_state,
                  'birthdate': datetime.date(random.randint(1970, 2000), random.randint(1, 12), random.randint(1, 28)),
                  'plan_start_date': datetime.date(random.randint(2015, 2023), random.randint(1, 12), random.randint(1, 28))
            }
         
    # Write distinct phone numbers to a separate CSV file
    with open('distinct_phone_numbers.csv', 'w', newline='') as csvfile:
        #fieldnames = ['Phone Number', 'Caller Location', 'State', 'Country', 'Birthdate', 'Plan Start Date']
        fieldnames = ['~id','~label','city:string','state:string','country:string','birthdate:string','plan_start_dt:string']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for phone_number, details in distinct_phone_numbers.items():
            #city =  "" #location_parts[0]
            #state = "" #location_parts[1]
            # writer.writerow({
            #     'Phone Number': phone_number,
            #     'Caller Location': city,
            #     'State': details['state'],
            #     'Country': 'United States',
            #     'Birthdate': details['birthdate'],
            #     'Plan Start Date': details['plan_start_date']
            # }) ~id,~label,country:string,birthdate:string,state:string,city:string,act_date:string
            writer.writerow({
                '~id': phone_number,
                '~label': 'user',
                'city:string': details['caller_location'],
                'state:string': details['state'],
                'country:string': 'United States',
                'birthdate:string': details['birthdate'],
                'plan_start_dt:string': details['plan_start_date']
            })
def read_city_data_from_csv(file_path):
    city_data = {}

    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            city = row['City']
            state = row['State']
            population = int(row['Population'])
            latitude = float(row['lat'])
            longitude = float(row['lon'])

            city_data[city] = {
                'state': state,
                'population': population,
                'latitude': latitude,
                'longitude': longitude
            }

    return city_data         

# Function to randomly pick an item from a dictionary
def random_pick_from_dict(dictionary):
    keys = list(dictionary.keys())
    random_key = random.choice(keys)
    random_value = dictionary[random_key]
    return random_key, random_value

def main():

   # Generate and write 1000 CDR entries to a file
   generate_cdr_data(5000, 'cdr_data.csv')

if __name__ == "__main__":
    main()
