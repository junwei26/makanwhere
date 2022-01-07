import sys
import os
import telebot
import pprint
from telebot import types
import googlemaps
from BotData import BotData
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('GOOGLE_API')
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
gmaps = googlemaps.Client(API_KEY)

dict = dict()

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id not in dict.keys():
        dict[message.chat.id] = BotData()
    botData = dict[message.chat.id]
    botData.isRunning = True
    bot.send_message(message.chat.id, "Please share your locations or enter your address")
    print(botData)

@bot.message_handler(commands=['stop'])
def stop(message):
    if dict.get(message.chat.id) is None:
        bot.send_message(message.chat.id, "Please use the /start command")
    else:
        botData = dict[message.chat.id]
        botData.isRunning = False
        bot.send_message(message.chat.id, "{0} locations added!".format(len(botData.locations)))
        bot.send_message(message.chat.id, "the budget is {0}".format(botData.budget))
        botData.reset()

@bot.callback_query_handler(func=lambda call: True)
def callback_budget(call):
    if dict.get(call.message.json['chat']['id']) is None:
        bot.send_message(call.message.json['chat']['id'], "Please use the /start command")    
    else:
        botData = dict[call.message.json['chat']['id']]
        if call.data == "budget_1":
            botData.budget = 1
        elif call.data == "budget_2":
            botData.budget = 2
        elif call.data == "budget_3":
            botData.budget = 3
        elif call.data == "budget_4":
            botData.budget = 4
        print(botData.budget)

@bot.message_handler(commands=['budget'], func=lambda message: True)
def budget(message):
    if dict.get(message.chat.id) is None:
        bot.send_message(message.chat.id, "Please use the /start command")
    else:
        botData = dict[message.chat.id]
        print(message.chat.id)
        if botData.isRunning:
            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton('1', callback_data="budget_1")
            item2 = types.InlineKeyboardButton('2', callback_data="budget_2")
            item3 = types.InlineKeyboardButton('3', callback_data="budget_3")
            item4 = types.InlineKeyboardButton('4', callback_data="budget_4")
            markup.add(item1, item2, item3, item4)
            bot.send_message(message.chat.id, "Choose a budget:", reply_markup=markup)



@bot.message_handler(commands=['addcuisine'])
def add_cuisine(message):
    if dict.get(message.chat.id) is None:
        bot.send_message(message.chat.id, "Please use the /start command")
    else:
        botData = dict[message.chat.id]
        if botData.isRunning:
            try:
                cuisine = message.text.split(" ", 1)[1]
                botData.cuisines.append(cuisine)
            except IndexError:
                bot.send_message(message.chat.id, "Please enter a cuisine following the /addcuisine command")
        else:
            bot.send_message(message.chat.id, "Please /start first")
            

@bot.message_handler(commands=['addlocation'])
def add_location(message):
    if dict.get(message.chat.id) is None:
        bot.send_message(message.chat.id, "Please use the /start command")
    else:
        botData = dict[message.chat.id]
        if botData.isRunning:
            if message.content_type == "text":
                try:
                    address = message.text.split(" ", 1)[1]
                    code = gmaps.geocode(address)
                except IndexError:
                    bot.send_message(message.chat.id, "Please enter a location following the /addlocation command")
                    return
                try:
                    lat = code[0]['geometry']['location']['lat']
                    lng = code[0]['geometry']['location']['lng']
                    botData.locations.append((lat, lng))
                    print(botData.locations)
                    bot.send_message(message.chat.id, "Location added!")
                except IndexError:
                    bot.send_message(message.chat.id, "Please enter a valid location.")
                    return
        else:
            bot.send_message(message.chat.id, "Please /start first")

@bot.message_handler(content_types=['location'])
def handle_responses(message):
    if dict.get(message.chat.id) is None:
        bot.send_message(message.chat.id, "Please use the /start command")
    else:
        botData = dict[message.chat.id]
        if botData.isRunning:
            if message.content_type == 'location':
                botData.locations.append((message.location.longitude, message.location.latitude))
                bot.send_message(message.chat.id, "Location added!")



bot.polling()
