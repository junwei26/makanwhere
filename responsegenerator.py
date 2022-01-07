import googlemaps
import os
from BotData import BotData 
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('GOOGLE_API')
gmaps = googlemaps.Client(API_KEY)

def generate_response(data):
    locations = data.locations
    cuisines = data.cuisines
    budget = data.budget
    nested_results_list = [gmaps.places_nearby(find_average_pos(locations),1000, cuisine,'food')["results"] for cuisine in cuisines]
    results_list = [item for result in nested_results_list for item in result]
    for result in results_list:
        if 'price_level' not in result.keys():
            result['price_level'] = "unknown"
    results_list.sort(key=lambda item : item['rating'], reverse=True)
    return generate_results_message(results_list)

def generate_results_message(results_list, limit=10):
    template = "{0}. [{1}](https://www.google.com/maps/search/?api=1&query={2}&query_place_id={3}) \n Rating: {4} \n Price: {5} \n"
    message = ""
    for i in range(limit):
        result = results_list[i]
        current_message = template.format(i, result['name'], "_".join(result['name'].split()), result['place_id'], result['rating'], result['price_level'])
        message += current_message

    return message


def find_average_pos(locations):
    long_sum = sum([location[0] for location in locations])
    lat_sum = sum([location[1] for location in locations])
    count = len(locations)
    return (long_sum/count, lat_sum/count)

junweihouse = (1.2907344996919183, 103.82238516757782)
ninejlnmembina = (1.2847037525600302, 103.82769396757784)
testlocation = find_average_pos([junweihouse,ninejlnmembina])
testdata = BotData()
testdata.locations=[testlocation]
testdata.cuisines=["indian", "chinese"]
testdata.budget=""

print(generate_response(testdata))