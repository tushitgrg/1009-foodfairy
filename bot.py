import requests
import telebot

import openai

from telebot import types


openai.api_key = "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"
API_KEY = "16af4ee752174c5d8556899af9a643db"
Token = "6461048124:AAHlFGlnV8vpDzrVehFbu_NbgXAvMtuXu_8"
bot = telebot.TeleBot(Token)


def getdetails(pname):
  prompt = "Give me Short Description of " + pname + "Also Write Farming methods, or precautions to take while growing this"
  response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                          messages=[
                                            {
                                              "role": "user",
                                              "content": prompt
                                            },
                                          ])
  details = response.choices[0].message.content
  return details


@bot.message_handler(['start'])
def start(message):
  bot.send_message(
    message.chat.id,
    "Hi I am Food Fairy, a Prototype made by Tushit Garg.\n Send Me any Photo of the Plant to Get details like its name, its farming mathods etc. \n Use /askme to Ask me anything! \n Use /preserveme Get Tips for preservation! \n Join Our Exclusive Community at /community "
  )


@bot.message_handler(content_types=['photo'])
def photo(message):
  global name
  name = message.from_user.id
  global chatid
  chatid = message.chat.id
  fileID = message.photo[-1].file_id
  file = bot.get_file(fileID)
  global filepath
  filepath = file.file_path.replace("/", "%2F")

  options = ["leaf", "flower", "fruit", "bark"]

  keyboard = types.InlineKeyboardMarkup(row_width=2)
  for index, option in enumerate(options):
    callback_button = types.InlineKeyboardButton(text=option,
                                                 callback_data=str(index + 1))
    keyboard.add(callback_button)

  bot.reply_to(message,
               "Which Part of the Plant the Picture Represents?",
               reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.isdigit())
def handle_callback(call):

  try:
    option = int(call.data)
    if option == 1:
      organ = "leaf"
    elif option == 2:
      organ = "flower"
    elif option == 3:
      organ = "fruit"
    elif option == 4:
      organ = "bark"
    bot.edit_message_reply_markup(call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=None)
  except:
    pass

  try:
    url = f"https://my-api.plantnet.org/v2/identify/all?images=https%3A%2F%2Fapi.telegram.org%2Ffile%2Fbot{Token}%2F{filepath}&organs={organ}&include-related-images=true&no-reject=false&lang=en&api-key=2b10HbhnHDd56iPFf8aoXcv3e"
    response5 = requests.get(url)
    data5 = response5.json()
    results = data5.get('results')
    score = results[0]['score']
    accuracy = int(score * 100)
    species = results[0]['species']
    img = results[0]['images']
    img2 = img[0]['url']
    global pname
    pname = species.get('scientificNameWithoutAuthor')

    bot.reply_to(call.message,
                 f"Your Plant is {pname} with {accuracy}% Accuracy! ")
    bot.reply_to(call.message, "Now Searching Farming Details")
  except Exception as e:
    print(e)
    pass
  details = getdetails(pname)
  print(details)

  bot.reply_to(call.message, details)


@bot.message_handler(['askme'])
def askme(message):
  bot.reply_tp(
    message, "Hey! Ask me anything related to Farming and I will answer it!")
  bot.register_next_step_handler(message, answerquery)


def answerquery(message):
  prompt = f"Answer this Question as Food Fairy Bot, '{message.text}'"
  bot.reply_to(message, "Answering Your Question......")
  response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                          messages=[
                                            {
                                              "role": "user",
                                              "content": prompt
                                            },
                                          ])
  answer = response.choices[0].message.content
  bot.reply_to(message, answer)


@bot.message_handler(['preserveme'])
def preserveme(message):
  bot.reply_to(message, "What Do You want to Preserve?")
  bot.register_next_step_handler(message, preserveanswer)


def preserveanswer(message):
  prompt = f"Answer this Question as Food Fairy Bot, 'How to Preserve {message.text}?'"
  bot.reply_to(message, "Answering Your Question......")
  response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                          messages=[
                                            {
                                              "role": "user",
                                              "content": prompt
                                            },
                                          ])
  answer = response.choices[0].message.content
  bot.reply_to(message, answer)


@bot.message_handler(['community'])
def community(message):
  bot.send_message(
    message.chat.id,
    "Join the Exclusive Farmer Community Here! https://t.me/+hgYATCwyK3E3ZWNl")


bot.polling(None)
