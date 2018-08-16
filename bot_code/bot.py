# -*- coding: utf-8 -*-

import collections
import logging
import os
import random
import string
from ast import literal_eval
from time import sleep
import configparser
from telegram import ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.parsemode import ParseMode
import datetime

import sys
sys.path.append(os.getcwd())

from bot_code.Chatbot import Chatbot

CONFPATH = "config.ini"
conf = configparser.ConfigParser()

if not os.path.exists('logs/'):
    os.makedirs('logs/')

if not os.path.exists(CONFPATH):
    print("Creating stub config...\n"
          "You need to replace STUB with your actual token in file {}".format(CONFPATH))
    conf["bot"] = {"TOKEN": "STUB", "CONTEXT_SIZE": 3, "REPLY_HIST_SIZE": 20, "LOGFILE": 'logs/log.txt'}
    with open(CONFPATH, 'wt') as configfile:
        conf.write(configfile)

conf.read(CONFPATH)

TOKEN = conf["bot"]["TOKEN"]
CONTEXT_SIZE = int(conf["bot"]["CONTEXT_SIZE"])
REPLY_HIST_SIZE = int(conf["bot"]["REPLY_HIST_SIZE"])

time = str(datetime.datetime.now())
LOGFILE = 'logs/log_' + time + '.txt'
print('LOGFILE = ' + LOGFILE)


# Enable logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler(LOGFILE)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

class Bot:
    def __init__(self):
        self.history = {}

        self.nTurn = 0
        self.end = False

        self.updater = Updater(TOKEN) # TOKEN is given from config.ini

        self.name = str(self).split(' ')[-1][:-1]

        self.dp = self.updater.dispatcher
        # Special functions (feel free to add)
        self.dp.add_handler(CommandHandler("start", start))  # function1 : /start
        self.dp.add_handler(CommandHandler("help", help))    # function2 : /help
        self.dp.add_handler(CommandHandler("end", end))      # function3 : /end : end conversation & rating
        #self.dp.add_handler(MessageHandler([Filters.text], echo))
        self.dp.add_handler(MessageHandler([], echo))
        self.dp.add_error_handler(error)

        # Define your chatbot
        self.Chatbot = Chatbot()
        logger.info('Initialization done. Start conversation by typing /start.')

    def power_on(self):
        # Start the Bot
        self.updater.start_polling()

        # Run the bot until the you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()


def mess2dict(mes):
    return literal_eval(str(mes))


def start(bot, update):
    ai.end = False
    md = mess2dict(update.message)
    sender_id = str(md['from']['id'])

    bot.sendMessage(update.message.chat_id, "Hello. I am qia2018 bot.")
    bot.sendMessage(update.message.chat_id, "We can talk about given image, or whatever you want.")
    bot.sendMessage(update.message.chat_id, 'You can type special commands such as /start, /help or /end')

    ai.history[sender_id] = {'context': collections.deque(maxlen=CONTEXT_SIZE),'replies': collections.deque(maxlen=REPLY_HIST_SIZE)}

def end(bot, update):
    bot.sendMessage(update.message.chat_id, 'Thanks for chatting with me. Please rate our conversation !')
    bot.sendMessage(update.message.chat_id, 'Appropriateness of response : How proper my reponse for your query? (1-3)')
    bot.sendMessage(update.message.chat_id, 'Multi-turn ability : How good am i remember what you said? (1-3)')
    bot.sendMessage(update.message.chat_id, 'You can type scores and feel free to leave :).  Bye !')
    ai.end = True

def help(bot, update):
    if not ai.end:
        md = mess2dict(update.message)
        sender_id = md['from']['id']
        try:
            sender_fname = md['from']['first_name']
            sender_lname = md['from']['last_name']
        except:
            sender_fname = sender_id
            sender_lname = ''
        help_msg = ("Hello, {} {}!").format(sender_fname, sender_lname)
        bot.sendMessage(update.message.chat_id, text=help_msg, parse_mode=ParseMode.MARKDOWN)
        bot.sendMessage(update.message.chat_id, 'Tell me anything about image or you can just chitchat with me')
        bot.sendMessage(update.message.chat_id, 'Or you can either type special commands such as /new, /help or /end')
    else:
        bot.sendMessage(update.message.chat_id, 'Currently, our conversation is over :) If you wanna start again, please type /start')


def echo(bot, update):
    # this function is executed when sending message in telegram
    if not ai.end:
        user_text = update.message.text
        md = mess2dict(update.message)
        ai.nTurn += 1
        try:
            sender_fname = md['from']['first_name']
            sender_lname = md['from']['last_name']
        except:
            sender_fname = str(md['from']['id'])
            sender_lname = ""
        logger.info("{} {} says: {}".format(sender_fname, sender_lname, user_text))
        sender_id = str(md['from']['id'])

        dialog_history = ai.history[sender_id]
        response = ai.Chatbot.get_response(user_text, dialog_history['context'], dialog_history['replies'])

        logger.info('bot replies: {}'.format(response))
        bot_send_message(bot, update, response)

        # History
        ai.history[sender_id]['context'].append(user_text)
        ai.history[sender_id]['replies'].append(response)
    else:
        text = update.message.text
        md = mess2dict(update.message)
        try:
            sender_fname = md['from']['first_name']
            sender_lname = md['from']['last_name']
        except:
            sender_fname = str(md['from']['id'])
            sender_lname = ""
        logger.info("{} {} says: {}".format(sender_fname, sender_lname, text))
        logger.info('bot replies: end of conversation')

def bot_send_message(bot, update, text):
    bot.sendChatAction(update.message.chat_id, action=ChatAction.TYPING)
    sleep(random.random() * 2 + 1.)
    bot.sendMessage(update.message.chat_id, text=text)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

exclude = set(string.punctuation)

if __name__ == "__main__":
    ai = Bot()
    ai.power_on()
