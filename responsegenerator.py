import googlemaps
import os
import pprint
import json
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
    results_list.sort(key=lambda item : item['rating'], reverse=True)
    return results_list

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

pprint.pprint(generate_response(testdata))