import telebot
import sqlite3
import re
from telebot import types
import random
import pandas as pd
import pytz
from datetime import datetime
import time
from multiprocessing import *
from functools import wraps
import math


token = ''
bot = telebt.TeleBot(token)
password = '123'
sum_users = 0
url_pattern = r"https://\S+"

def save_stats_in_table():
  db =sqlite3.connect('db.sql')
  query = f'SELECT * FROM Users_links'
  df = pd.read_sql_query(query, db)
  db.close()
  output_excel_file = 'stats.xlsx'
  df.to_excel(output_excel_file, index=False, engine='openpyxl')

  file = open('stats.xlsx','rb')
  bot.send_document(158079043, file)

def save_users_in_table():
  db =sqlite3.connect('db.sql')
  query = f'SELECT * FROM users'
  df = pd.read_sql_query(query, db)
  db.close()
  output_excel_file = 'users.xlsx'
  df.to_excel(output_excel_file, index=False, engine='openpyxl')

  file = open('users.xlsx','rb')
  bot.send_document(158079043, file)


# Создание базы данных с участниками марафона
def database():
   db = sqlite3.connect('db.sql')
   cur = db.cursor()
   # Добавление таблицы участников в базу данных
   # id - номер участника [int auto_increment primary key]
   # name - имя и фамилия
   # link - ссылка на отзыв 
   cur.execute('CREATE TABLE if NOT EXISTS users(id_user varchar(30), name varchar(50), company varchar(100), type varchar(100), link varchar(256), reg_datetime varchar(50))')
   db.execute(f'CREATE table if not EXISTS Users_links (id_user, name, link, stream, wait, successfully)')
   db.commit()
   db.close()
database()

# Добавление участника в БД
def add_user(id_user, user):
  strip = user.strip()
  arr = strip.split(',')
  name_user = arr[0]
  company_user = arr[1]
  type_company_user = arr[2]
  link_user = arr[3]
  db = sqlite3.connect('db.sql')
  cur = db.cursor()
  krasnoyarsk_tz = pytz.timezone('Asia/Krasnoyarsk')
  current_time_krasnoyarsk = datetime.now(krasnoyarsk_tz)
  current_time_str = current_time_krasnoyarsk.strftime('%Y-%m-%d %H:%M:%S')
  cur.execute("INSERT INTO users(id_user, name, company, type, link, reg_datetime) VALUES (?, ?, ?, ?, ?, ?)", (id_user, name_user, company_user, type_company_user, link_user, current_time_str))
  db.commit()
  db.close()

def check_table():
  # db = sqlite3.connect('db.sql')
  # cur = db.cursor()
  # cur.execute("CREATE TABLE if NOT EXISTS check(id_user integer, name text, link text)")
  # cur.execute("INSERT into check (id_user, name, link) SELECT")
  pass

# Приветственное сообщение на команду /start
@bot.message_handler(commands=['start'])
def start(message):
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  button_1 = types.KeyboardButton("👋 Поздороваться")
  markup.add(button_1)
  bot.send_message(message.chat.id, '👋 Здравствуйте, '+ message.from_user.first_name +', я бот для проведения марафона отзывов.', reply_markup=markup)

# Обработка остальных команд и текста 
@bot.message_handler(content_types=['text'])
def func(message):
  if message.text == "👋 Поздороваться":
    markup = types.ReplyKeyboardRemove()
    input_pass = bot.send_message(message.chat.id, 'Теперь в сообщении текстом отправьте мне пароль, который вы получили для доступа к марафону.', reply_markup=markup)
    bot.register_next_step_handler(input_pass, verification)
  elif message.text == "Зарегистрироваться":
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, '❗️ Пожалуйста включите уведомления и звук от бота если они не включены. В специальное время от бота будет приходить сообщение с ссылкой на сервис, на который необходимо будет оставить отзыв.'
                     + "\n\n" + 'Для регистрации в марафоне отправьте сообщение в следующем формате: Имя,Название организации,Вид_деятельности,[ссылка на карточку организации]'
                     + "\n" + 'Перечисление обязательно через запятую и без пробела после запятой❗️'
                     + "\n\n" + 'Примеры сообщения:')
    reg = bot.send_message(message.chat.id, 'Иван,Яндекс,Реклама и IT услуги,https://yandex.ru/profile/93247744409'
                           + "\n" + 'или'
                           + "\n" + 'Александр,Перцы,Деятельность по предоставлению продуктов питания и напитков,https://go.2gis.com/mqrfv', reply_markup=markup)
    bot.register_next_step_handler(reg, validation_form)
  elif message.text == "/startmarathon":
    if message.from_user.id == 158079043:
      startmarathon()
    else:
      bot.send_message(message.chat.id, 'Это команда для администратора бота.')
  elif message.text == "/startspam":
    if message.from_user.id == 158079043:
      start_engine()
      bot.send_message(158079043, 'Началась отправка собщений')
    else:
      bot.send_message(message.chat.id, 'Это команда для администратора бота.')
  elif message.text == "/cleardb":
    if message.from_user.id == 158079043:
      cleardb()
    else:
      bot.send_message(message.chat.id, 'Это команда для администратора бота.')
  elif message.text == "/checkstats":
    if message.from_user.id == 158079043:
      save_stats_in_table() 
    else:
      bot.send_message(message.chat.id, 'Это команда для администратора бота.')
  elif message.text == "/stopspam":
    if message.from_user.id == 158079043:
      stopspam()
    else:
      bot.send_message(message.chat.id, 'Это команда для администратора бота.')
  elif message.text == "/givemeusers":
    if message.from_user.id == 158079043:
      save_users_in_table()
    else:
      bot.send_message(message.chat.id, 'Это команда для администратора бота.')
  elif re.search(url_pattern, message.text):
    delete_from_wait(message.chat.id, message.text)
  else:
    bot.send_message(message.chat.id, 'Извините, я вас не понимаю :('
                     + "\n\n" + 'Если у вас есть вопросы или помощь по работе бота то напишите администратору @ahydrogen')

def delete_from_wait(id_user,url_del):
  db = sqlite3.connect('db.sql')
  cur = db.cursor()
  cur.execute("SELECT wait FROM Users_links WHERE id_user = ?", (id_user,))
  wait_str = cur.fetchone()[0]
  new_wait_str = wait_str.replace(url_del+'|', '')
  cur.execute("UPDATE Users_links SET wait = ? WHERE id_user = ?", (new_wait_str, id_user))

  krasnoyarsk_tz = pytz.timezone('Asia/Krasnoyarsk')
  current_time_krasnoyarsk = datetime.now(krasnoyarsk_tz)
  current_time_str = current_time_krasnoyarsk.strftime('%Y-%m-%d %H:%M:%S')
  cur.execute("SELECT successfully FROM Users_links WHERE id_user = ?", (id_user,))
  successfully_str = cur.fetchone()[0]
  successfully_str = successfully_str+str(url_del)+' '+'['+current_time_str+']'+'|'
  cur.execute("UPDATE Users_links SET successfully = ? WHERE id_user = ?", (successfully_str, id_user))
  db.commit()
  db.close()
  bot.send_message(id_user, 'Спасибо за участие в марафоне! Ожидайте следующего сообщения с ссылкой 😉')

def stopspam():
  global stop_flag
  stop_flag = True
  bot.send_message(158079043, 'Рассылка остановлена.')

def stopmarathon():
  pass #написать рассылку всем об окончании марафона
  
# Валидация пароля
def verification(message):
  if message.text == password:
      markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
      button_2 = types.KeyboardButton("Зарегистрироваться")
      markup.add(button_2)
      bot.send_message(message.chat.id, '✅ Отлично! Пароль введен верно. Теперь необходимо зарегистрироваться, для этого нажмите на кнопку ниже.', reply_markup=markup)
  else:
      wrong_pass = bot.send_message(message.chat.id, '❌ Неверный пароль')
      bot.register_next_step_handler(wrong_pass, verification)

# Регистрация Имя Фамилия ссылка
def validation_form(message):
  pattern = r'^[А-ЯЁа-яёa-zA-Z]+,[А-ЯЁа-яёa-zA-Z0-9]+,[^,]+,(https?://[^\s,]+)$'
  if re.match(pattern, message.text):
    bot.send_message(message.chat.id, 'Регистрация прошла успешно! Когда все участники зарегистрируются вам придёт сообщение о старте марафона.')
    add_user(message.from_user.id, message.text)
  else:
    wrong_reg = bot.send_message(message.chat.id, 'Неверный формат сообщения, проверьте соответсвие шаблону.')
    bot.register_next_step_handler(wrong_reg, validation_form)

# Команда для начала марафона
def startmarathon():
  db = sqlite3.connect('db.sql')
  cur = db.cursor()
  cur.execute('SELECT id_user FROM users')
  arr = cur.fetchall()
  matrix()
  for i in range(len(arr)):
    bot.send_message(int(arr[i][0]), 'Марафон начался!')
  db.close()
  

# Создание матрицы участников
def matrix():
  db = sqlite3.connect('db.sql')
  cur = db.cursor()
  cur.execute('SELECT link FROM users')
  link = cur.fetchall()
  links = []

  
  for i in range(len(link)):
     links.append(link[i][0])
  links.reverse()
  
  cur.execute('SELECT * FROM users') 
  users = cur.fetchall()

  matrixx = pd.DataFrame(columns=['id_user', 'name', 'company', 'type', 'link', 'stream', 'wait', 'successfully'])
  for i in range(len(users)):
      
      random.shuffle(links)
      stream = ' '.join(links)
      stream = str(stream)
      #print(stream)
      stream = stream.replace(users[i][4], " ")

      

      
      if stream[-1] == ' ':
        stream_inp = stream[:-1]
        list = [users[i][0], users[i][1], users[i][2], users[i][3], users[i][4], stream_inp, "|", "|"]
        matrixx.loc[len(matrixx)] = list
      else:
        list = [users[i][0], users[i][1], users[i][2], users[i][3], users[i][4], stream, "|", "|"]
        matrixx.loc[len(matrixx)] = list
      # print('-------------')
      # print(stream)
  db.execute(f'CREATE table if not EXISTS Users_links (id_user, name, company, type, link, stream, wait, successfully)')
  matrixx.to_sql('Users_links', db, if_exists='replace')
  db.commit()
  #print(matrix)
  
  db.close()


def spam():
  
  db = sqlite3.connect('db.sql')
  cur = db.cursor()
  cur.execute('SELECT id_user FROM users')
  ids = cur.fetchall()
  id_arr = []
  for i in range(len(ids)):
     id_arr.append(ids[i][0])

  for id in id_arr:

    db = sqlite3.connect('db.sql')
    cur = db.cursor()
    query = "SELECT stream FROM Users_links WHERE id_user = ?"
    cur.execute(query, (id,))
    result = cur.fetchone()

    result = result[0].split(" ")
    
    try:
      while True:
        result.remove("")
    except ValueError:
        pass  
          
    if len(result) > 0:
      bot.send_message(id, '📣 Ссылка для отзыва: ' + result[-1])

      # krasnoyarsk_tz = pytz.timezone('Asia/Krasnoyarsk')
      # current_time_krasnoyarsk = datetime.now(krasnoyarsk_tz)
      # current_time_str = current_time_krasnoyarsk.strftime('%Y-%m-%d %H:%M:%S')

      query = "SELECT wait from Users_links WHERE id_user = ?"
      cur.execute(query, (id,))
      wait_queue = cur.fetchone()
      wait_queue = wait_queue[0]+str(result[-1])+'|'
      
      cur.execute("UPDATE Users_links SET wait = ? WHERE id_user = ?", (wait_queue, id))

      bot.send_message(id, '❗️ Обязательно после того как оставите отзыв скопируйте ссылку и отправьте её в ответ боту чтобы подтвердить своё участие в марафоне.')
      
      result.pop(-1)
      out = ' '.join(result)
      # out загрузить заместо этого stream
      query = "UPDATE Users_links SET stream = ? WHERE id_user = ?"
      cur.execute(query, (out, id))
      db.commit()
      db.close()
      time.sleep(round(math.random(32400,43200)/len(id_arr)))
    else:
      bot.send_message(158079043, 'Марафон закончен, выключи его')
      time.sleep(10) 
    db.close()
# bot_messages = {}
# def spam():
#     db = sqlite3.connect('db.sql')
#     cur = db.cursor()
#     cur.execute('SELECT id_user FROM users')
#     ids = cur.fetchall()
#     id_arr = [row[0] for row in ids]

#     for id in id_arr:
#         db = sqlite3.connect('db.sql')
#         cur = db.cursor()
#         query = "SELECT stream FROM Users_links WHERE id_user = ?"
#         cur.execute(query, (id,))
#         result = cur.fetchone()

#         result = result[0].split(" ")

#         try:
#             while True:
#                 result.remove("")
#         except ValueError:
#             pass

#         if len(result) > 0:
#             link_message = '📣 Ссылка для отзыва: ' + result[-1]
#             bot.send_message(id, link_message)

#             krasnoyarsk_tz = pytz.timezone('Asia/Krasnoyarsk')
#             current_time_krasnoyarsk = datetime.now(krasnoyarsk_tz)
#             current_time_str = current_time_krasnoyarsk.strftime('%Y-%m-%d %H:%M:%S')

#             query = "SELECT wait from Users_links WHERE id_user = ?"
#             cur.execute(query, (id,))
#             wait_queue = cur.fetchone()
#             wait_queue = wait_queue[0] + str(result[-1]) + '[' + current_time_str + ']' + '|'

#             cur.execute("UPDATE Users_links SET wait = ? WHERE id_user = ?", (wait_queue, id))

#             # Сохраняем сообщение бота для пользователя в словаре
#             bot_messages[id] = '❗️ Обязательно после того как оставите отзыв нажмите на кнопку подтверждения ниже.'

#             # Создание кнопки подтверждения
#             inline_keyboard = types.InlineKeyboardMarkup()
#             button = types.InlineKeyboardButton('Подтвердите то, что оставили отзыв по ссылке выше', callback_data=str(id))
#             inline_keyboard.add(button)
#             bot.send_message(id, bot_messages[id], reply_markup=inline_keyboard)

#             result.pop(-1)
#             out = ' '.join(result)
#             # out загрузить заместо этого stream
#             query = "UPDATE Users_links SET stream = ? WHERE id_user = ?"
#             cur.execute(query, (out, id))
#             db.commit()
#             db.close()
#             time.sleep(30/len(id_arr))
#         else:
#             bot.send_message(158079043, 'Марафон закончен')
#             time.sleep(10)
#         db.close()

# @bot.callback_query_handler(func=lambda call: call.data.isdigit())
# def handle_button_click(call):
#     user_id = int(call.data)
#     if user_id in bot_messages:
#         bot.send_message(user_id, "Вы нажали кнопку!")
#         print("Пользователь с ID {} нажал кнопку с сообщением бота: {}".format(user_id, bot_messages[user_id]))
#         del bot_messages[user_id]  # Удаляем сохраненное сообщение бота


# Многопоточность для регистрации времени
def mult_threading(func):
  # Декоратор для запуска функции в отдельном потоке
  @wraps(func)
  def wrapper(*args_, **kwargs_):
    import threading
    func_thread = threading.Thread(target=func,
                                   args=tuple(args_),
                                   kwargs=kwargs_)
    func_thread.start()
    return func_thread
  return wrapper

@mult_threading
def start_engine():
  global stop_flag
  stop_flag = False
  # db = sqlite3.connect('db.sql')
  # cur = db.cursor()
  # cur.execute('SELECT id_user FROM users')
  # ids = cur.fetchall()
  # id_arr = []
  # for i in range(len(ids)):
  #    id_arr.append(ids[i][0])
  # counter = len(id_arr)

  while not stop_flag:
    tz = pytz.timezone('Asia/Krasnoyarsk')
    Krasnoyarsk_hour = datetime.now(tz).hour

    if (Krasnoyarsk_hour >= 8) and (Krasnoyarsk_hour <= 20):
        spam()
    else:
      time.sleep(60)

def cleardb():
  db = sqlite3.connect('db.sql')
  cur = db.cursor()
  cur.execute("DELETE FROM users")
  cur.execute("DELETE FROM Users_links")
  db.commit()
  db.close()
  bot.send_message(158079043, 'База данных почищена')

if __name__ == '__main__':
  bot.polling(none_stop=True)