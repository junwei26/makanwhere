import sys
import os
import telebot
import pprint
from telebot import types
import googlemaps
from BotData import BotData
from dotenv import load_dotenv
import responsegenerator

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
    bot.send_message(
        message.chat.id, "Please share your locations or enter your address")
    print(botData)


@bot.message_handler(commands=['stop'])
def stop(message):
    if dict.get(message.chat.id) is None:
        bot.send_message(message.chat.id, "Please use the /start command")
    else:
        botData = dict[message.chat.id]
        botData.isRunning = False
        bot.send_message(message.chat.id, "{0} locations added!".format(
            len(botData.locations)))
        bot.send_message(
            message.chat.id, "the budget is {0}".format(botData.budget))
        botData.reset()


@bot.callback_query_handler(func=lambda call: True)
def callback_budget(call):
    if dict.get(call.message.json['chat']['id']) is None:
        bot.send_message(
            call.message.json['chat']['id'], "Please use the /start command")
    else:
        botData = dict[call.message.json['chat']['id']]
        leader_word = call.data.split("_", 1)[0]
        if leader_word == "budget":
            if call.data == "budget_1":
                botData.budget = 1
            elif call.data == "budget_2":
                botData.budget = 2
            elif call.data == "budget_3":
                botData.budget = 3
            elif call.data == "budget_4":
                botData.budget = 4
            bot.send_message(call.message.json['chat']['id'], "Okay budget has been updated!", reply_markup=None)
        elif leader_word == "cuisine":
            cuisine = call.data.split("_", 1)[1]
            botData.cuisines.remove(cuisine)
            bot.send_message(call.message.json['chat']['id'], "Okay removed {0}".format(cuisine), reply_markup=None)
        elif leader_word == "location":
            location = call.data.split("_", 1)[1]
            for i in botData.locations:
                if i[2] == location:
                    to_be_removed = i
            botData.locations.remove(to_be_removed)
            bot.send_message(call.message.json['chat']['id'], "Okay removed {0}".format(location), reply_markup=None)



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
            bot.send_message(
                message.chat.id, "Choose a budget:", reply_markup=markup)


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
                bot.send_message(
                    message.chat.id, "Please enter a cuisine following the /addcuisine command")
        else:
            bot.send_message(message.chat.id, "Please /start first")

@bot.message_handler(commands=['removecuisine'])
def remove_cuisine(message):
    if dict.get(message.chat.id) is None:
        bot.send_message(message.chat.id, "Please use the /start command")
    else:
        botData = dict[message.chat.id]
        if botData.isRunning:
           markup = types.InlineKeyboardMarkup()
           for i in botData.cuisines:
               markup.add(types.InlineKeyboardButton(i, callback_data="cuisine_"+i))
           bot.send_message(message.chat.id, "Which cuisine do you want to remove?:", reply_markup=markup)
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
                    botData.locations.append((lat, lng, address))
                    print(botData.locations)
                    bot.send_message(message.chat.id, "Location added!")
                except IndexError:
                    bot.send_message(message.chat.id, "Please enter a valid location.")
                    return
        else:
            bot.send_message(message.chat.id, "Please /start first")

@bot.message_handler(commands=['removelocation'])
def remove_location(message):
    if dict.get(message.chat.id) is None:
        bot.send_message(message.chat.id, "Please use the /start command")
    else:
        botData = dict[message.chat.id]
        if botData.isRunning:
           markup = types.InlineKeyboardMarkup()
           for i in botData.locations:
               markup.add(types.InlineKeyboardButton(i[2], callback_data="location_"+i[2]))
           bot.send_message(message.chat.id, "Which location do you want to remove?:", reply_markup=markup)
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
                botData.locations.append((message.location.latitude, message.location.longitude, "PLaceholder"))
                bot.send_message(message.chat.id, "Location added!")


@bot.message_handler(commands=['getresults'])
def get_results(message):
    data = dict[message.chat.id]
    print(responsegenerator.generate_response(data))
    bot.send_message(chat_id=message.chat.id, text=responsegenerator.generate_response(data), parse_mode='HTML')

@bot.message_handler(commands=['makepoll'])
def make_poll(message):
    if dict.get(message.chat.id) is None:
        bot.send_message(message.chat.id, "Please use the /start command")
    else:
        data = dict[message.chat.id]
        if data.results is None:
            bot.send_message(message.chat.id, "Do /getresults first!")
        #data.results is an array of result names
        bot.send_message(chat_id=message.chat.id, text='\n'.join(data.results)) #placeholder for poll

bot.polling()
