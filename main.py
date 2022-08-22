import telebot
import configparser
import emoji
import re
from telebot import types
import datetime

config = configparser.ConfigParser()
config.read("settings.ini")
token = str(config["bot"]["token"])
#print(token)
bot = telebot.TeleBot(token)
NOK = "❌"
OK = "✅"

def get_list_of_tasks(user_list):
	splited_list = user_list.split("\n")
	for task in splited_list:
		match = bool(re.match(r'\d.\s*', task))
		if match == True:
			pass
		else: return("Syntax Error")
	tasks_only = []

	for task in splited_list:
		splited_task = task.split(" ", 1)[1]
		tasks_only.append(splited_task)
	nums = list(range(1,len(tasks_only)+1))

	full_list_of_tasks = dict(zip(nums, tasks_only))
	#print(full_list_of_tasks)


	return(full_list_of_tasks)


@bot.message_handler(commands = ["start"])

def start(message):
	start_message = f"""Hey, {message.from_user.first_name}!
I can help you to be productive today \U0001F913
To create a new to-do list use this commands:
/create
"""

	bot.send_message(message.chat.id, start_message, parse_mode = None)

@bot.message_handler(commands = ["create"])

def create(message):
	create_message = f"""Ok, I see you wanna create a new to-do list.
Please send it to me in such format:
1. Task1
2. Task2
3. Task3
	..."""
	bot.send_message(message.chat.id, create_message, parse_mode = "html")

@bot.message_handler(content_types = ["text"])
def get_user_list(message):
	user_tasks = message.text
	user_tasks_list = get_list_of_tasks(user_tasks)
	if user_tasks_list == "Syntax Error":
		error_message = """Please, check your list and send me again. It should be in such format:
1. Task1
2. Task2
3. Task3
	...""" 
		bot.send_message(message.chat.id, error_message, parse_mode = "html")
	else:

		e = datetime.datetime.now()
		today = f"{e.day}.{e.month:02d}.{e.year}"
		markup = types.InlineKeyboardMarkup()
		for i in range(0, len(list(user_tasks_list.values()))):
			button = types.InlineKeyboardButton(text=NOK + ' ' + list(user_tasks_list.values())[i],
				callback_data=str(i+1))
			markup.add(button)
		bot.send_message(message.chat.id, text = f"Plan for today ({today})", reply_markup = markup)

@bot.callback_query_handler(lambda query:True)
def inline(query):
	global keyb
	keyb = query.message.reply_markup
	d = int(query.data)
	if d > 0:
		button = types.InlineKeyboardButton(text=NOK, callback_data=str(-1*d))
	else:
		button = types.InlineKeyboardButton(text=OK, callback_data=str(-1*d))
	n = len(keyb.keyboard)
	for i in range(n):
		if keyb.keyboard[i][0].callback_data == str(d):
			t = keyb.keyboard[i][0].text[2:]
			#print(t)
			if d > 0:
				button = types.InlineKeyboardButton(text=OK + ' ' + t, callback_data=str(-1*d))
			else:
				button = types.InlineKeyboardButton(text=NOK + ' ' + t, callback_data=str(-1*d))
			keyb.keyboard[i][0] = button
	bot.edit_message_reply_markup(chat_id=query.message.chat.id,
        message_id=query.message.message_id, reply_markup=keyb)

bot.polling(none_stop = True)