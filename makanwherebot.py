import os
import telebot
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


@bot.message_handler(commands=['start'], func=lambda message:True)
def start(message):
    welcome_text="""
Welcome to MakanWhere!\n 
To get started, click on one of the buttons below to add locations, set your budget, and add cuisines.\n
After one or more locations have been added, you may select "/getresults" for a list of our recommendations for where to makan.\n
*Another easy way to add a location is to simply share your location! :)
    """
    if message.chat.id not in dict.keys():
        dict[message.chat.id] = BotData()
    bot_data = dict[message.chat.id]
    bot_data.isRunning = True
    bot.send_message(
        message.chat.id, welcome_text)
    show_commands(message)

def show_commands(message):
    markup = types.InlineKeyboardMarkup()
    add_location_item = types.InlineKeyboardButton('add location', callback_data="command_addlocation")
    remove_location_item = types.InlineKeyboardButton('remove location', callback_data="command_removelocation")
    show_locations_item = types.InlineKeyboardButton('show locations', callback_data="command_showlocations")
    add_cuisine_item = types.InlineKeyboardButton('add cuisine', callback_data="command_addcuisine")
    remove_cuisine_item = types.InlineKeyboardButton('remove cuisine', callback_data="command_removecuisine")
    show_cuisines_item = types.InlineKeyboardButton('show cuisines', callback_data="command_showcuisines")
    set_budget_item = types.InlineKeyboardButton('set budget', callback_data="command_setbudget")
    show_budget_item = types.InlineKeyboardButton('show budget', callback_data="command_showbudget")
    get_results_item = types.InlineKeyboardButton('get results', callback_data="command_getresults")
    quit_item = types.InlineKeyboardButton('quit', callback_data="command_quit")
    markup.add(add_location_item, remove_location_item, show_locations_item, add_cuisine_item
    , remove_cuisine_item, show_cuisines_item, set_budget_item, show_budget_item, get_results_item, quit_item)
    bot.send_message(message.chat.id, "What command would you like to run?", reply_markup=markup)

def result_commands(message):
    markup = types.InlineKeyboardMarkup()
    more_results = types.InlineKeyboardButton('get more results', callback_data="command_moreresults")
    make_poll = types.InlineKeyboardButton('make poll', callback_data="command_makepoll")
    go_back = types.InlineKeyboardButton('go back', callback_data="command_goback")
    quit_item = types.InlineKeyboardButton('quit', callback_data="command_quit")
    markup.add(more_results, make_poll, go_back, quit_item)
    bot.send_message(message.chat.id, "What command would you like to run?", reply_markup=markup)


def quit(message):
    bot_data = dict[message.chat.id]
    bot.send_message(message.chat.id, "Goodbye!")
    dict[message.chat.id] = None


@bot.callback_query_handler(func=lambda call: True)
def callback_budget(call):
    if dict.get(call.message.json['chat']['id']) is None:
        bot.send_message(
            call.message.json['chat']['id'], "Please use the /start command")
    else:
        bot_data = dict[call.message.json['chat']['id']]
        leader_word = call.data.split("_", 1)[0]
        if leader_word == "budget":
            if call.data == "budget_1":
                bot_data.budget = 1
            elif call.data == "budget_2":
                bot_data.budget = 2
            elif call.data == "budget_3":
                bot_data.budget = 3
            elif call.data == "budget_4":
                bot_data.budget = 4

            if call.data == "budget_cancel":
                bot.send_message(
                    call.message.json['chat']['id'], "Okay budget remains the same.", reply_markup=None)
            else:
                bot.send_message(
                    call.message.json['chat']['id'], "Okay budget has been updated!", reply_markup=None)
            bot.delete_message(
                call.message.json['chat']['id'], call.message.json['message_id'])
            show_commands(call.message)

        elif leader_word == "cuisine":
            cuisine = call.data.split("_", 1)[1]
            if cuisine == "cancel":
                bot.send_message(
                    call.message.json['chat']['id'], "Okay no cuisine was removed.", reply_markup=None)
            else:
                bot_data.cuisines.remove(cuisine)
                response = "Okay removed {0}.\n Your cuisines are:\n".format(cuisine)
                for i in range(len(bot_data.cuisines)):
                    response += "{0}: {1}\n".format(str(i + 1), bot_data.cuisines[i])
                bot.send_message(call.message.json['chat']['id'], response, reply_markup=None)
            bot.delete_message(
                call.message.json['chat']['id'], call.message.json['message_id'])
            show_commands(call.message)

        elif leader_word == "location":
            location = call.data.split("_", 1)[1]
            if location == 'cancel':
                bot.send_message(
                    call.message.json['chat']['id'], "Okay no location was removed.", reply_markup=None)
            else:
                for i in bot_data.locations:
                    if i[2] == location:
                        to_be_removed = i
                bot_data.locations.remove(to_be_removed)
                response = "Okay removed {0}.\nYour locations are:\n".format(location)
                for i in range(len(bot_data.locations)):
                    response += "{0}: {1}\n".format(str(i + 1), bot_data.locations[i][2])
                bot.send_message(call.message.json['chat']['id'], 
                    response, reply_markup=None)
            bot.delete_message(
                call.message.json['chat']['id'], call.message.json['message_id'])
            show_commands(call.message)


        elif leader_word == "command":
            command = call.data.split("_", 1)[1]
            if command == 'addlocation':
                add_location(call)
            elif command == 'removelocation':
                remove_location(call)
            elif command == 'showlocations':
                show_locations(call)
            elif command == 'addcuisine':
                add_cuisine(call)
            elif command == 'removecuisine':
                remove_cuisine(call)
            elif command == 'showcuisines':
                show_cuisines(call)
            elif command == 'setbudget':
                set_budget(call)
            elif command == 'showbudget':
                show_budget(call)
            elif command == 'getresults':
                get_results(call)
            elif command == 'makepoll':
                make_poll(call)
            elif command == 'moreresults':
                more_results(call)
            elif command == 'goback':
                show_commands(call.message)
            elif command == 'quit':
                quit(call.message)
            bot.delete_message(
                call.message.json['chat']['id'], call.message.json['message_id'])

def set_budget(call):
    print("set_budget call")
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('1', callback_data="budget_1")
    item2 = types.InlineKeyboardButton('2', callback_data="budget_2")
    item3 = types.InlineKeyboardButton('3', callback_data="budget_3")
    item4 = types.InlineKeyboardButton('4', callback_data="budget_4")
    item5 = types.InlineKeyboardButton(
        'cancel', callback_data="budget_cancel")
    markup.add(item1, item2, item3, item4, item5)
    bot.send_message(
        call.message.chat.id, "Choose a budget:", reply_markup=markup)


def show_budget(call):
    print("show_budget call")
    bot_data = dict[call.message.chat.id]
    bot.send_message(
        call.message.chat.id, "Your budget: {0}".format(bot_data.budget))
    show_commands(call.message)


def add_cuisine(call):
    print("add_cuisine call")
    markup = types.ForceReply(selective=True)
    sent = bot.send_message(call.message.chat.id, "@{0} What cuisine would you want to add?"
    .format(call.from_user.username), reply_markup=markup)
    bot.register_for_reply_by_message_id(
        sent.message_id, callback=add_cuisine_callback)


@bot.callback_query_handler(func=lambda message: True)
def add_cuisine_callback(message):
    bot_data = dict[message.json['chat']['id']]
    bot_data.cuisines.append(message.json['text'])
    response = "Nice! Added {0} to your cuisines!\n Your cuisines are:\n".format(message.json['text'])
    for i in range(len(bot_data.cuisines)):
        response += "{0}: {1}\n".format(str(i + 1), bot_data.cuisines[i])
    bot.send_message(message.json['chat']['id'], response)
    show_commands(message)
    print("added cuisine: {0}".format(message.json['text']))


def remove_cuisine(call):
    print("remove_cuisine call")
    bot_data = dict[call.message.chat.id]
    if not bot_data.cuisines:
        bot.send_message(
            call.message.chat.id, "There are no cuisines to remove!")
        show_commands(call.message)
    else:
        markup = types.InlineKeyboardMarkup()
        for i in bot_data.cuisines:
            markup.add(types.InlineKeyboardButton(
                i, callback_data="cuisine_"+i))
        markup.add(types.InlineKeyboardButton(
            "cancel", callback_data="cuisine_cancel"))
        bot.send_message(
            call.message.chat.id, "Which cuisine do you want to remove?:", reply_markup=markup)


def show_cuisines(call):
    print("show_cuisine call")
    bot_data = dict[call.message.chat.id]
    all_cuisines = "Cuisines added so far:\n"
    for i in range(len(bot_data.cuisines)):
        all_cuisines += "{0}. {1}\n".format(i + 1, bot_data.cuisines[i])
    bot.send_message(call.message.chat.id, all_cuisines)
    show_commands(call.message)


def add_location(call):  
    print("add_location call")
    markup = types.ForceReply(selective=True)
    sent = bot.send_message(call.message.chat.id, "@{0} What location would you want to add?"
    .format(call.from_user.username), reply_markup=markup)
    bot.register_for_reply_by_message_id(
        sent.message_id, callback=add_location_callback)


@bot.callback_query_handler(func=lambda message: True)
def add_location_callback(message):
    bot_data = dict[message.json['chat']['id']]
    address = message.json['text']
    code = gmaps.geocode(address)
    try:
        lat = code[0]['geometry']['location']['lat']
        lng = code[0]['geometry']['location']['lng']
        bot_data.locations.append((lat, lng, address))
        print(bot_data.locations)
        response = "{0} has been added to the locations!\nYour locations are:\n".format(address)
        for i in range(len(bot_data.locations)):
            response += "{0}: {1}\n".format(str(i+1), bot_data.locations[i][2])
        bot.send_message(message.json['chat']['id'], response)
        show_commands(message)
    except IndexError:
        bot.send_message(
            message.json['chat']['id'], "Please enter a valid location.")
        show_commands(message)
        return
    

def remove_location(call):
    print("remove_location call")
    bot_data = dict[call.message.chat.id]
    if not bot_data.locations:
        bot.send_message(call.message.chat.id, "There are no locations to remove!")
        show_commands(call.message)
    else:
        markup = types.InlineKeyboardMarkup()
        for i in bot_data.locations:
            markup.add(types.InlineKeyboardButton(i[2], callback_data="location_"+i[2]))
        markup.add(types.InlineKeyboardButton("cancel", callback_data="location_cancel"))
        bot.send_message(call.message.chat.id, "Which location do you want to remove?", reply_markup=markup)

def show_locations(call):
    print("show_locations call")
    bot_data = dict[call.message.chat.id]
    all_locations="Locations added so far:\n"
    for i in range(len(bot_data.locations)):
        all_locations += "{0}. {1}\n".format(i + 1, bot_data.locations[i][2])
    bot.send_message(call.message.chat.id, all_locations)
    show_commands(call.message)

@bot.message_handler(content_types=['location'])
def handle_responses(message):
    if dict.get(message.chat.id) is None:
        bot.send_message(message.chat.id, "Please use the /start command")
    else:
        bot_data = dict[message.chat.id]
        if bot_data.isRunning:
            if message.content_type == 'location':
                location_name = gmaps.reverse_geocode(( message.location.latitude, message.location.longitude))[0]['formatted_address'].split(",", -1)[0]
                bot_data.locations.append((message.location.latitude, message.location.longitude, location_name))
                bot.send_message(message.chat.id, "Location added!")


def get_results(call):
    print("get_results call")
    data = dict[call.message.chat.id]
    if not data.locations:
        bot.send_message(chat_id=call.message.chat.id, text="Please enter at least 1 location")
        show_commands(call.message)
    else:
        response = responsegenerator.generate_response(data)
        bot.send_message(chat_id=call.message.chat.id, text=response, parse_mode='HTML')
        if response == "No results found! Please try /moreresults to increase your search radius or try adding more cuisines.":
            show_commands(call.message)
        else:
            result_commands(call.message)


def more_results(call):
    print("more_results call")
    data = dict[call.message.chat.id]
    data.searchRadius += 500
    data.resultDisplayLength += 5
    bot.send_message(chat_id=call.message.chat.id, text=responsegenerator.generate_response(data), parse_mode='HTML')
    result_commands(call.message)


def make_poll(call):
    print("make_poll call")
    data = dict[call.message.chat.id]
    if data.results is None:
        bot.send_message(call.message.chat.id, "Do /getresults first!")
    max_poll_size = 10
    splitted_results = [data.results[i:i+max_poll_size] for i in range(0, len(data.results), max_poll_size)]
    for result in splitted_results:
        bot.send_poll(call.message.chat.id, "Vote for where you want to eat!", result, is_anonymous=False, allows_multiple_answers=True)
    result_commands(call.message)

bot.infinity_polling()
