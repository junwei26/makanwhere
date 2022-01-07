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
    welcome_text="""
Welcome to MakanWhere!\n 
To get started, click on one of the buttons below to add locations, set your budget, and add cuisines.\n
After one or more locations have been added, you may select "/getresults" for a list of our recommendations for where to makan.
    """
    if message.chat.id not in dict.keys():
        dict[message.chat.id] = BotData()
    botData = dict[message.chat.id]
    botData.isRunning = True
    bot.send_message(
        message.chat.id, welcome_text)
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
            elif call.data == "budget_cancel":
                bot.delete_message(
                    call.message.json['chat']['id'], call.message.json['message_id'])
                bot.send_message(
                    call.message.json['chat']['id'], "Okay budget remains the same.", reply_markup=None)
                return
            bot.delete_message(
                call.message.json['chat']['id'], call.message.json['message_id'])
            bot.send_message(
                call.message.json['chat']['id'], "Okay budget has been updated!", reply_markup=None)
        elif leader_word == "cuisine":
            cuisine = call.data.split("_", 1)[1]
            if cuisine == "cancel":
                bot.delete_message(
                    call.message.json['chat']['id'], call.message.json['message_id'])
                bot.send_message(
                    call.message.json['chat']['id'], "Okay no cuisine was removed.", reply_markup=None)
                return
            botData.cuisines.remove(cuisine)
            bot.delete_message(
                call.message.json['chat']['id'], call.message.json['message_id'])
            bot.send_message(call.message.json['chat']['id'], "Okay removed {0}".format(
                cuisine), reply_markup=None)
        elif leader_word == "location":
            location = call.data.split("_", 1)[1]
            if location == 'cancel':
                bot.delete_message(
                    call.message.json['chat']['id'], call.message.json['message_id'])
                bot.send_message(
                    call.message.json['chat']['id'], "Okay no location was removed.", reply_markup=None)
                return
            for i in botData.locations:
                if i[2] == location:
                    to_be_removed = i
            botData.locations.remove(to_be_removed)
            bot.delete_message(
                call.message.json['chat']['id'], call.message.json['message_id'])
            bot.send_message(call.message.json['chat']['id'], "Okay removed {0}".format(
                location), reply_markup=None)


@bot.message_handler(commands=['budget'], func=lambda message: True)
def budget(message):
    if dict.get(message.chat.id) is None:
        bot.send_message(message.chat.id, "Please use the /start command")
    else:
        botData = dict[message.chat.id]
        if botData.isRunning:
            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton('1', callback_data="budget_1")
            item2 = types.InlineKeyboardButton('2', callback_data="budget_2")
            item3 = types.InlineKeyboardButton('3', callback_data="budget_3")
            item4 = types.InlineKeyboardButton('4', callback_data="budget_4")
            item5 = types.InlineKeyboardButton(
                'cancel', callback_data="budget_cancel")
            markup.add(item1, item2, item3, item4, item5)
            bot.send_message(
                message.chat.id, "Choose a budget:", reply_markup=markup)


@bot.message_handler(commands=['showbudget'])
def show_budget(message):
    if dict.get(message.chat.id) is None:
        bot.send_message(message.chat.id, "Please use the /start command")
    else:
        botData = dict[message.chat.id]
        if botData.isRunning:
            bot.send_message(
                message.chat.id, "Your budget: {0}".format(botData.budget))
        else:
            bot.send_message(message.chat.id, "Please /start first")


@bot.message_handler(commands=['addcuisine'])
def add_cuisine(message):
    if dict.get(message.chat.id) is None:
        bot.send_message(message.chat.id, "Please use the /start command")
    else:
        botData = dict[message.chat.id]
        if botData.isRunning:
            markup = types.ForceReply(selective=True)
            sent = bot.send_message(message.chat.id, "@{0} What cuisine would you want to add?"
            .format(message.from_user.username), reply_markup=markup)
            bot.register_for_reply_by_message_id(
                sent.message_id, callback=add_cuisine_callback)
        else:
            bot.send_message(message.chat.id, "Please /start first")


@bot.callback_query_handler(func=lambda message: True)
def add_cuisine_callback(message):
    botData = dict[message.json['chat']['id']]
    botData.cuisines.append(message.json['text'])
    bot.send_message(message.json['chat']['id'], "Nice! Added {0} to the cuisines".format(
        message.json['text']))
    print("added cuisine: {0}".format(message.json['text']))


@bot.message_handler(commands=['removecuisine'])
def remove_cuisine(message):
    if dict.get(message.chat.id) is None:
        bot.send_message(message.chat.id, "Please use the /start command")
    else:
        botData = dict[message.chat.id]
        if botData.isRunning:
           markup = types.InlineKeyboardMarkup()
           for i in botData.cuisines:
               markup.add(types.InlineKeyboardButton(
                   i, callback_data="cuisine_"+i))
           markup.add(types.InlineKeyboardButton(
               "cancel", callback_data="cuisine_cancel"))
           bot.send_message(
               message.chat.id, "Which cuisine do you want to remove?:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Please /start first")


@bot.message_handler(commands=['showcuisines'])
def show_cuisine(message):
    if dict.get(message.chat.id) is None:
        bot.send_message(message.chat.id, "Please use the /start command")
    else:
        botData = dict[message.chat.id]
        if botData.isRunning:
            all_cuisines = "Cuisines added so far:\n"
            for i in range(len(botData.cuisines)):
                all_cuisines += "{0}. {1}\n".format(i + 1, botData.cuisines[i])
            bot.send_message(message.chat.id, all_cuisines)
        else:
            bot.send_message(message.chat.id, "Please /start first")


@bot.message_handler(commands=['addlocation'])
def add_location(message):
    if dict.get(message.chat.id) is None:
        bot.send_message(message.chat.id, "Please use the /start command")
    else:
        botData = dict[message.chat.id]
        if botData.isRunning:
            markup = types.ForceReply(selective=True)
            sent = bot.send_message(message.chat.id, "@{0} What location would you want to add?"
            .format(message.from_user.username), reply_markup=markup)
            bot.register_for_reply_by_message_id(
                sent.message_id, callback=add_location_callback)
        else:
            bot.send_message(message.chat.id, "Please /start first")


@bot.callback_query_handler(func=lambda message: True)
def add_location_callback(message):
    botData = dict[message.json['chat']['id']]
    try:
        address = message.json['text']
        code = gmaps.geocode(address)
    except IndexError:
        bot.send_message(
            message.chat.id, "Please enter a location following the /addlocation command")
        return
    try:
        lat = code[0]['geometry']['location']['lat']
        lng = code[0]['geometry']['location']['lng']
        botData.locations.append((lat, lng, address))
        print(botData.locations)
        bot.send_message(message.json['chat']['id'], "Location added!")
    except IndexError:
        bot.send_message(
            message.json['chat']['id'], "Please enter a valid location.")
        return
    

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
            markup.add(types.InlineKeyboardButton("cancel", callback_data="location_cancel"))
            bot.send_message(message.chat.id, "Which location do you want to remove?:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Please /start first")

@bot.message_handler(commands=['showlocations'])
def show_locations(message):
    if dict.get(message.chat.id) is None:
        bot.send_message(message.chat.id, "Please use the /start command")
    else:
        botData = dict[message.chat.id]
        if botData.isRunning:
            all_locations="Locations added so far:\n"
            for i in range(len(botData.locations)):
                all_locations += "{0}. {1}\n".format(i + 1, botData.locations[i][2])
            bot.send_message(message.chat.id, all_locations)
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
                location_name = gmaps.reverse_geocode(( message.location.latitude, message.location.longitude))[0]['formatted_address'].split(",", -1)[0]
                botData.locations.append((message.location.latitude, message.location.longitude, location_name))
                bot.send_message(message.chat.id, "Location added!")


@bot.message_handler(commands=['getresults'])
def get_results(message):
    data = dict[message.chat.id]
    bot.send_message(chat_id=message.chat.id, text=responsegenerator.generate_response(data), parse_mode='HTML')

@bot.message_handler(commands=['moreresults'])
def more_results(message):
    data = dict[message.chat.id]
    data.searchRadius += 500
    data.resultDisplayLength += 5
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
        #bot.send_message(chat_id=message.chat.id, text='\n'.join(data.results)) #placeholder for poll
        bot.send_poll(message.chat.id, "Vote for which one you want", data.results, is_anonymous=False, allows_multiple_answers=True)

bot.polling()
