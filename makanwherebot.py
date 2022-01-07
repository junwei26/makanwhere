import sys
import os
import telebot
import googlemaps
from BotData import BotData
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('GOOGLE_API')
BOT_TOKEN = os.getenv('BOT_TOKEN')
locations = []
state = True
bot = telebot.TeleBot(BOT_TOKEN)
gmaps = googlemaps.Client(API_KEY)

hashmap = {}

@bot.message_handler(commands=['address'])
def address(message):
    input = message.text.split(" ", 1)
    if len(input) == 2:
        address = input[1]
        code = gmaps.geocode(address)
        lat = code[0]['geometry']['location']['lat']
        lng = code[0]['geometry']['location']['lng']
        bot.send_message(message.chat.id, "Here is the lat and lng: " + str(lat) + " " + str(lng))
    else:
        bot.send_message(message.chat.id, "Please input an address")


@bot.message_handler(commands=['start'])
def start(message):
    global state
    state = True
    bot.send_message(message.chat.id, "Please share your locations or enter your address")

@bot.message_handler(commands=['stop'])
def stop(message):
    global state
    state = False
    bot.send_message(message.chat.id, "{0} locations added!".format(len(locations)))

@bot.message_handler(commands=['addlocation'])
def add_location(message):
    if state:
        if message.content_type == "text":
            code = gmaps.geocode(message.text)
            lat = code[0]['geometry']['location']['lat']
            lng = code[0]['geometry']['location']['lng']
            locations.append((lat, lng))
            bot.send_message(message.chat.id, "Location added!")
    else:
        bot.send_message(message.chat.id, "Please /start first")

@bot.message_handler(content_types=['location'])
def handle_responses(message):
    if state:
        if message.content_type == 'location':
            print(message.location)
            locations.append((message.location.longitude, message.location.latitude))
            bot.send_message(message.chat.id, "Location added!")



bot.polling()
