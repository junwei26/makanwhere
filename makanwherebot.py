import sys
import os
import telebot
import googlemaps
from BotData import BotData
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('GOOGLE_API')
BOT_TOKEN = os.getenv('BOT_TOKEN')

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

bot.polling()
