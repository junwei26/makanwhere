import os
import googlemaps
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('GOOGLE_API')
gmaps = googlemaps.Client(API_KEY)

def generate_response(data):
    locations = data.locations
    cuisines = data.cuisines
    budget = data.budget
    search_radius = data.searchRadius
    result_display_length = data.resultDisplayLength

    if not data.cuisines:
        results_list = gmaps.places_nearby(location=find_average_pos(locations),radius=search_radius, min_price=0, max_price=budget, type='food')["results"]
    else:
        nested_results_list = [gmaps.places_nearby(location=find_average_pos(locations),radius=search_radius, keyword=cuisine, min_price=0, max_price=budget, type='food')["results"] for cuisine in cuisines]
        results_list = [item for result in nested_results_list for item in result]

    for result in results_list:
        #Not all results have a known price level
        if 'price_level' not in result.keys():
            result['price_level'] = "unknown"

    results_list.sort(key=lambda item : item['rating'], reverse=True)
    data.results = [result['name'] for result in results_list[:result_display_length]]
    return generate_results_message(results_list, result_display_length) 

def generate_results_message(results_list, limit):
    template = "{0}. <a href=\"https://www.google.com/maps/search/?api=1&query={2}&query_place_id={3}\">{1}</a> \n <b>Rating:</b> {4} \n <b>Price:</b> {5} \n"
    message = ""
    if len(results_list) == 0:
        message = "No results found! Please try /moreresults to increase your search radius or try adding more cuisines."
        
    else:
        for i in range(min(limit, len(results_list))):
            result = results_list[i]
            current_message = template.format(i + 1, result['name'], "_".join(result['name'].split()), result['place_id'], float(result['rating']), result['price_level'])
            message += current_message

    return message


def find_average_pos(locations):
    long_sum = sum([location[0] for location in locations])
    lat_sum = sum([location[1] for location in locations])
    count = len(locations)
    return (long_sum/count, lat_sum/count)

