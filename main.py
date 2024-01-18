import telebot
import sqlite3
import re
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import pandas as pd
import pytz
from datetime import datetime, timedelta
import time
from multiprocessing import *
from functools import wraps
import threading
import atexit

# def exit_handler():
#     # Код, который будет выполняться перед выходом из программы
#     bot.send_message(158079043, 'Программа завершила выполнение из-за ошибки или прерывания')
# atexit.register(exit_handler)


token = '6724776824:AAElnolJgOrq6IU8_c3vJc2aSBwMhwgElcM'
bot = telebot.TeleBot(token)
password = 'abakan2023'
registration_data = {}

bot.send_message(158079043, 'Бот включился')

"""СОЗДАНИЕ БАЗЫ ДАННЫХ"""
# Создание базы данных с участниками марафона
def database():
   db = sqlite3.connect('db.sql')
   cur = db.cursor()
   # Добавление таблицы участников в базу данных
   # id - номер участника [int auto_increment primary key]
   # name - имя и фамилия
   # link - ссылка на отзыв 
   cur.execute('''CREATE TABLE if NOT EXISTS users (id_user varchar(30), 
                                                    name varchar(50), 
                                                    company varchar(100), 
                                                    type varchar(100), 
                                                    link_1 varchar(256), 
                                                    link_2 varchar(256), 
                                                    reg_datetime varchar(50))''')
   db.execute(f'''CREATE table if not EXISTS Users_links (id_user, 
                                                          name, 
                                                          link, 
                                                          stream, 
                                                          wait, 
                                                          successfully)''')
   cur.execute('''CREATE TABLE IF NOT EXISTS ProcessingState (
               id INTEGER PRIMARY KEY,
               current_user_id TEXT
               )''')
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
"""СОЗДАНИЕ БАЗЫ ДАННЫХ"""



# Приветственное сообщение на команду /start
@bot.message_handler(commands=['start'])
def start(message):
  #markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  #button_1 = types.KeyboardButton("👋 Поздороваться")
  #markup.add(button_1)
  input_pass = bot.send_message(message.chat.id, '👋 Здравствуйте, '+ message.from_user.first_name +', я бот для проведения марафона отзывов.' + 
                   '\n\n' + 'Для доступа к боту в сообщении текстом отправьте мне пароль, который вы получили.')
  if message.chat.id == 158079043:
      bot.send_message(158079043, 'Привет, удачной работы :)')
  else:
      bot.register_next_step_handler(input_pass, verification)

# Обработка остальных команд и текста 
@bot.message_handler(content_types=['text'])
def func(message):
  if message.text == "👋 Поздороваться":
    # markup = types.ReplyKeyboardRemove()
    # input_pass = bot.send_message(message.chat.id, 'Для доступа к боту в сообщении текстом отправьте мне пароль, который вы получили для доступа к марафону.', reply_markup=markup)
    # bot.register_next_step_handler(input_pass, verification)
    pass
  elif message.text == "Зарегистрироваться":
    # registration(message)
    pass
  elif message.text == "/startmarathon":
    if message.from_user.id == 158079043:
      startmarathon()
    else:
      bot.send_message(message.chat.id, 'Это команда для администратора бота.')
  elif message.text == "/startspam":
    if message.from_user.id == 158079043:
      start_engine()
      bot.send_message(158079043, '<code>[Началась отправка собщений]</code>')
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
  elif message.text == "/first_cycle":
    if message.from_user.id == 158079043:
      first_cycle()
    else:
      bot.send_message(message.chat.id, 'Это команда для администратора бота.')
  else:
    bot.send_message(message.chat.id, 'Извините, я вас не понимаю :('
                     + "\n\n" + 'Если у вас есть вопросы или помощь по работе бота то напишите администратору @ahydrogen')



"""КОМАНДЫ ДЛЯ МЕНЯ"""
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

# Очистить БД
def cleardb():
  db = sqlite3.connect('db.sql')
  cur = db.cursor()
  cur.execute("DELETE FROM users")
  cur.execute("DELETE FROM Users_links")
  db.commit()
  db.close()
  bot.send_message(158079043, 'База данных очищена')

# Остановить спам
def stopspam():
  global stop_flag
  stop_flag = True
  bot.send_message(158079043, 'Рассылка остановлена.')

# Уведомление всем об окончании марафона
def stopmarathon():
  db = sqlite3.connect('db.sql')
  cur = db.cursor()
  cur.execute('SELECT id_user FROM users')
  arr = cur.fetchall()
  db.close()
  for i in range(len(arr)):
    bot.send_message(int(arr[i][0]), 'Марафон закончен, всем спасибо за участие!')

# Вывод таблицы users
def save_stats_in_table():
  db = sqlite3.connect('db.sql')
  query = f'SELECT * FROM Users_links'
  df = pd.read_sql_query(query, db)
  db.close()
  
  output_excel_file = 'stats.xlsx'
  df.to_excel(output_excel_file, index=False, engine='openpyxl')

  file = open('stats.xlsx','rb')
  bot.send_document(158079043, file)
  file = open('db.sql','rb')
  bot.send_document(158079043, file)

# Вывод таблицы Users_links
def save_users_in_table():
  db = sqlite3.connect('db.sql')
  query = f'SELECT * FROM users'
  df = pd.read_sql_query(query, db)
  db.close()
  
  output_excel_file = 'users.xlsx'
  df.to_excel(output_excel_file, index=False, engine='openpyxl')

  file = open('users.xlsx','rb')
  bot.send_document(158079043, file)
"""КОМАНДЫ ДЛЯ МЕНЯ"""



"""РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ"""
# Валидация пароля
def verification(message):
  if message.text == password:
      markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
      button_2 = types.KeyboardButton("Зарегистрироваться")
      markup.add(button_2)
      bot.send_message(message.chat.id, '✅ Отлично! Пароль введен верно. Теперь давайте зарегистрируемся 😃', reply_markup=markup)
      registration(message)
  else:
      wrong_pass = bot.send_message(message.chat.id, '❌ Неверный пароль')
      bot.register_next_step_handler(wrong_pass, verification)

# Регистрация
def registration(message):
    markup = types.ReplyKeyboardRemove()
    chat_id = message.chat.id
    bot.send_message(chat_id, "Для начала, пожалуйста, напишите мне свое имя:", reply_markup=markup)
    bot.register_next_step_handler(message, ask_name)

def ask_name(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    name = message.text
    registration_data[user_id] = {'name': name}
    bot.send_message(chat_id, "Отлично, теперь напишите название организации:")
    bot.register_next_step_handler(message, ask_company_name)

def ask_company_name(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    company_name = message.text
    registration_data[user_id]['company_name'] = company_name
    bot.send_message(chat_id, "Хорошо, теперь укажите сферу вашей организации:")
    bot.register_next_step_handler(message, ask_company_field)

def ask_company_field(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    company_field = message.text
    registration_data[user_id]['company_field'] = company_field
    bot.send_message(chat_id, "Отлично, теперь отправьте только ссылку на карточку вашей организации без лишнего текста, например:"+
                     "\n" + 'https://yandex.ru/profile/239139382678')
    bot.register_next_step_handler(message, ask_first_company_link)

def ask_first_company_link(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    company_link = message.text
    registration_data[user_id]['company_link'] = company_link

    # Устанавливаем флаг, чтобы помнить, что первая ссылка уже получена
    registration_data[user_id]['first_link_received'] = True

    bot.send_message(chat_id, "Записали первую ссылку. Теперь отправьте мне вторую ссылку.")
    bot.register_next_step_handler(message, ask_second_company_link)

def ask_second_company_link(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if 'first_link_received' in registration_data[user_id] and registration_data[user_id]['first_link_received']:
        company_link_optional = message.text

        if company_link_optional.lower() == "отсутствует":
            company_link_optional = None

        registration_data[user_id]['company_link_optional'] = company_link_optional

        krasnoyarsk_tz = pytz.timezone('Asia/Krasnoyarsk')
        current_time_krasnoyarsk = datetime.now(krasnoyarsk_tz)
        current_time_str = current_time_krasnoyarsk.strftime('%Y-%m-%d %H:%M:%S')

        user_data = registration_data[user_id]
        db = sqlite3.connect('db.sql')
        cur = db.cursor()
        cur.execute("INSERT INTO users (id_user, name, company, type, link_1, link_2, reg_datetime) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (user_id, user_data['name'], user_data['company_name'], user_data['company_field'], user_data['company_link'], user_data.get('company_link_optional', None), current_time_str))
        db.commit()

        bot.send_message(chat_id, "Спасибо за регистрацию! Ваши данные сохранены. Когда все участники зарегистрируются вам придёт сообщение о старте марафона.")
        del registration_data[user_id]
    else:
        bot.send_message(chat_id, "Пожалуйста, сначала отправьте первую ссылку.")
"""РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ"""  



"""НАЧАЛО МАРАФОНА"""
# Создание матрицы участников
def matrix():
  db = sqlite3.connect('db.sql')
  cur = db.cursor()
  cur.execute("PRAGMA table_info(users)")
  columns = [column[1] for column in cur.fetchall()]
  if 'link_conc' not in columns:
      # Если столбец не существует, добавить его
      cur.execute('ALTER TABLE users ADD COLUMN link_conc TEXT')
  cur.execute("UPDATE users SET link_conc = '|' || link_1 || ' ' || link_2 || '|'")
  if 'stream' not in columns:
    cur.execute('ALTER TABLE users ADD COLUMN stream varchar(256)')
  cur.execute('UPDATE users SET stream = NULL')
  cur.execute('DELETE FROM Users_links')


  cur.execute('SELECT id_user FROM users')
  user_ids = [row[0] for row in cur.fetchall()]

  for user_id in user_ids:
      # Получить список всех пользователей, кроме текущего пользователя
      other_user_ids = [uid for uid in user_ids if uid != user_id]
      
      # Получите значения link_conc для других пользователей и объедините их в строку
      stream_values = []
      for other_user_id in other_user_ids:
          cur.execute('SELECT link_conc FROM users WHERE id_user = ?', (other_user_id,))
          link_conc_value = cur.fetchone()[0]
          stream_values.append(link_conc_value)
      
      # Создать строку stream для текущего пользователя, объединяя значения других пользователей
      stream = '|'.join(stream_values)

      stream = stream.replace('|||', '|')
      
      # Обновить значение stream для текущего пользователя в таблице
      cur.execute('UPDATE users SET stream = ? WHERE id_user = ?', (stream, user_id))

  db.commit()
  db.close()
  randomize()
  perenos()

def randomize():
  import sqlite3

  def shift_elements_forward(stream_value, shift):
      stream_value = stream_value.strip('|')
      elements = stream_value.split('|')

      # Сдвигаем элементы на указанное количество позиций вперед
      shifted_elements = [elements[(i + shift) % len(elements)] for i in range(len(elements))]

      new_stream_value = '|'.join(shifted_elements)
      return new_stream_value

  db = sqlite3.connect('db.sql')
  cur = db.cursor()
  cur.execute("SELECT id_user, stream FROM users")
  user_streams = cur.fetchall()

  shift = 0 

  for user_id, stream_value in user_streams:
      new_stream_value = shift_elements_forward(stream_value, shift)

      # Обновляем значение столбца stream для текущего пользователя
      cur.execute("UPDATE users SET stream = ? WHERE id_user = ?", (new_stream_value, user_id))
      db.commit()

      shift += 1

  db.close()

def perenos():
  import sqlite3


  db = sqlite3.connect('db.sql')
  cur = db.cursor()

  try:
      cur.execute("SELECT id_user, name, link_conc, stream FROM users")
      data_to_insert = cur.fetchall()

      for row in data_to_insert:
          id_user, name, link_conc, stream = row
          cur.execute("INSERT INTO Users_links (id_user, name, link, stream, wait, successfully) VALUES (?, ?, ?, ?, ?, ?)",
                      (id_user, name, link_conc, stream, "", ""))

      db.commit()
      print("Данные успешно перенесены из таблицы 'users' в таблицу 'Users_links'.")

  except sqlite3.Error as e:
      print(f"Произошла ошибка при переносе данных: {e}")

  finally:
      db.close()
"""НАЧАЛО МАРАФОНА"""



"""ПЕРВЫЙ ЦИКЛ СПАМА"""
def first_cycle():
    db = sqlite3.connect('db.sql')
    cur = db.cursor()
    cur.execute('SELECT id_user FROM users')
    ids = cur.fetchall()
    db.close()
    id_arr = [str(id[0]) for id in ids]
    # # Получить id текущего пользователя из таблицы состояния
    # db = sqlite3.connect('db.sql')
    # cur = db.cursor()
    # cur.execute("SELECT current_user_id FROM ProcessingState")
    # current_user_id = cur.fetchone()
    # db.close()

    # # Найти индекс текущего пользователя в списке id_arr
    # if current_user_id:
    #     current_user_id = current_user_id[0]
    #     current_user_index = id_arr.index(current_user_id)
    # else:
    #     current_user_index = 0

    random.shuffle(id_arr)
    #print(id_arr)
    count = 0
    for id in id_arr:
        count += 1
        bot.send_message(158079043,'✅ ' + str(count) + 'й Получил сообщение '+'id['+str(id)+']')

        db = sqlite3.connect('db.sql')
        cur = db.cursor()
        cur.execute("SELECT wait FROM Users_links WHERE id_user = ?", (id,))
        wait = cur.fetchone()

        if wait and not wait[0]:
            cur.execute("SELECT stream FROM Users_links WHERE id_user = ?", (id,))
            result = cur.fetchone()

            if result and result[0] != "":
                result = result[0].split("|")
                # print(result)
                out = result[-1].split(" ")

                if len(result) > 0:
                    keyboard = types.InlineKeyboardMarkup()
                    button = types.InlineKeyboardButton('ОТЗЫВЫ ОСТАВЛЕНЫ', callback_data=f"button_pressed_{id}")
                    keyboard.add(button)
                    # print(out)
                    bot.send_message(id, '📣📣📣📣📣📣📣📣📣' + '\n' + 'Новые ссылки для отзыва: ' + '\n\n' + out[0] + '\n\n' + out[1] + '\n\n' + 
                                     'Нажмите на кнопку снизу только после того как оставите оба отзыва.', reply_markup=keyboard)
                    
                    cur.execute("SELECT wait from Users_links WHERE id_user = ?", (id,))
                    wait_queue = cur.fetchone()
                    wait_queue = wait_queue[0] + str(out[0])+' '+str(out[1])
                    cur.execute("UPDATE Users_links SET wait = ? WHERE id_user = ?", (wait_queue, id))

                    # bot.send_message(id, '⬆️⬆️⬆️ ')
                    
                    
                    
                    
                    result.pop(-1)
                    
                        
                    result = '|'.join(result)

                    cur.execute("UPDATE Users_links SET stream = ? WHERE id_user = ?", (result, id))
                    db.commit()
                    time.sleep(5)
                else:
                    pass
                    # bot.send_message(id, 'Вы завершили марафон, поздравляем! Чтобы эти сообщения больше не приходили заблокируйте бота сверху в настройках :)')
            else:
                bot.send_message(158079043, '❕ ' + str(count) + 'й уже закончил марафон '+'id['+str(id)+']')
                time.sleep(5)
                #pass
            db.close()
        else:
            bot.send_message(id, 'Вы проспустили или не подтвердили предыдущий отзыв отправленный вам выше ⬆️⬆️⬆️, напишите отзыв и подтвердите его нажатием на кнопку пожалуйста.')
            time.sleep(5)
    bot.send_message(158079043, '✅ Первый цикл спама окончен')

"""ПЕРВЫЙ ЦИКЛ СПАМА"""



"""СПАМ ФУНКЦИЯ"""
def spam():
    db = sqlite3.connect('db.sql')
    cur = db.cursor()
    cur.execute('SELECT id_user FROM users')
    ids = cur.fetchall()
    db.close()
    id_arr = [str(id[0]) for id in ids]

    current_time = datetime.now()
    target_time = current_time.replace(hour=20, minute=0, second=0, microsecond=0)
    if current_time >= target_time:
        target_time += timedelta(days=1)
    time_difference = target_time - current_time
    seconds_until_9pm = int(time_difference.total_seconds())

    # # Получить id текущего пользователя из таблицы состояния
    # db = sqlite3.connect('db.sql')
    # cur = db.cursor()
    # cur.execute("SELECT current_user_id FROM ProcessingState")
    # current_user_id = cur.fetchone()
    # db.close()

    # # Найти индекс текущего пользователя в списке id_arr
    # if current_user_id:
    #     current_user_id = current_user_id[0]
    #     current_user_index = id_arr.index(current_user_id)
    # else:
    #     current_user_index = 0
    
    random.shuffle(id_arr)
    #print(id_arr)
    count = 0
    for id in id_arr:
        count += 1
        bot.send_message(158079043, '✅ ' + str(count) + 'й Получил сообщение '+'id['+str(id)+']')

        db = sqlite3.connect('db.sql')
        cur = db.cursor()
        cur.execute("SELECT wait FROM Users_links WHERE id_user = ?", (id,))
        wait = cur.fetchone()

        if wait and not wait[0]:
            cur.execute("SELECT stream FROM Users_links WHERE id_user = ?", (id,))
            result = cur.fetchone()

            if result and result[0] != "":
                result = result[0].split("|")
                out = result[-1].split(" ")

                if len(result) > 0:
                    keyboard = types.InlineKeyboardMarkup()
                    button = types.InlineKeyboardButton('ОТЗЫВЫ ОСТАВЛЕНЫ', callback_data=f"button_pressed_{id}")
                    keyboard.add(button)
                    bot.send_message(id, '📣📣📣📣📣📣📣📣📣' + '\n' + 'Новые ссылки для отзыва: ' + '\n\n' + out[0] + '\n\n' + out[1] + '\n\n' + 
                                     'Нажмите на кнопку снизу только после того как оставите оба отзыва.', reply_markup=keyboard)

                    cur.execute("SELECT wait from Users_links WHERE id_user = ?", (id,))
                    wait_queue = cur.fetchone()
                    wait_queue = wait_queue[0] + str(out[0])+' '+str(out[1])
                    cur.execute("UPDATE Users_links SET wait = ? WHERE id_user = ?", (wait_queue, id))

                    # bot.send_message(id, '⬆️⬆️⬆️ Нажмите на эту кнопку только после того как оставите оба отзыва.')
                    


                    result.pop(-1)
                    result = '|'.join(result)

                    cur.execute("UPDATE Users_links SET stream = ? WHERE id_user = ?", (result, id))
                    db.commit()

                    # Добавляем задержку перед отправкой следующего сообщения
                    ft = int((seconds_until_9pm - (seconds_until_9pm / 8)) / len(id_arr))
                    st = int(seconds_until_9pm / len(id_arr))
                    waiting = random.randint(ft, st)
                    bot.send_message(158079043, '🕘 ' + str(count+1) + 'й пользователь получит сообщение'+' через ' + str("{:0>8}".format(str(timedelta(seconds=waiting)))))
                    time.sleep(waiting)
                else:
                    bot.send_message(id, 'Вы завершили марафон, поздравляем!!! Чтобы эти сообщения больше не приходили заблокируйте бота сверху в настройках :)')
            else:
                bot.send_message(158079043, '❕ ' + str(count) + 'Уже закончил марафон '+'id['+str(id)+']')
            db.close()
        else:
            bot.send_message(id, 'Вы проспустили или не подтвердили предыдущий отзыв отправленный вам выше ⬆️⬆️⬆️, напишите отзыв и подтвердите его нажатием на кнопку пожалуйста.')
            #time.sleep(5)
            # current_time = datetime.now()
            # target_time = current_time.replace(hour=20, minute=0, second=0, microsecond=0)
            # if current_time >= target_time:
            #   target_time += timedelta(days=1)
            # time_difference = target_time - current_time
            # seconds_until_9pm = int(time_difference.total_seconds())
            #print(seconds_until_9pm)
            
            ft = int((seconds_until_9pm - (seconds_until_9pm / 8))/len(id_arr))
            st = int(seconds_until_9pm / len(id_arr))
            waiting = (random.randint(ft, st))
            bot.send_message(158079043, '🕘 ' + str(count+1) + 'й пользователь получит сообщение'+' через ' +  str("{:0>8}".format(str(timedelta(seconds=waiting)))))
            time.sleep(waiting)
      

# Обработка нажатий кнопки подтверждения  
@bot.callback_query_handler(func=lambda call: True)
def confirmation(call):
  id = call.from_user.id
  id = str(id)
  db = sqlite3.connect('db.sql')
  cur = db.cursor()
  cur.execute("SELECT wait FROM Users_links WHERE id_user = ?", (id,))
  wait = cur.fetchone()[0]

  krasnoyarsk_tz = pytz.timezone('Asia/Krasnoyarsk')
  current_time_krasnoyarsk = datetime.now(krasnoyarsk_tz)
  current_time_str = current_time_krasnoyarsk.strftime('%Y-%m-%d %H:%M:%S')
  cur.execute("SELECT successfully FROM Users_links WHERE id_user = ?", (id,))
  successfully_str = cur.fetchone()[0]
  successfully_str = successfully_str+' '+str(wait)+' '+'['+current_time_str+']'+' '+'|'
  cur.execute("UPDATE Users_links SET successfully = ? WHERE id_user = ?", (successfully_str, id))
  wait = ""
  cur.execute("UPDATE Users_links SET wait = ? WHERE id_user = ?", (wait, id))
  db.commit()
  
  cur.execute("SELECT stream FROM Users_links WHERE id_user = ?", (id,))
  result = cur.fetchone()
  result = result[0].split(" ")
      
  try:
    while True:
      result.remove("")
  except ValueError:
    pass

  if len(result)>0:
    bot.send_message(id, '👍 Вы подтвердили отзывы, спасибо за участие в марафоне! Ожидайте следующего сообщения с ссылками.')
  else:
    bot.send_message(id, '🎉🎉 Это была последняя ссылка марафона, спасибо за участие!')
  db.close()

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


last_spam_time = None
lock = threading.Lock()


@mult_threading
def start_engine():
  global stop_flag
  stop_flag = False
  while not stop_flag:
    # Получить текущее время в Красноярске и извлечь текущий час
    tz = pytz.timezone('Asia/Krasnoyarsk')
    Krasnoyarsk_hour = datetime.now(tz).hour

    if 8 <= Krasnoyarsk_hour <= 19:
        bot.send_message(158079043, '❗️ Спам сегодня запущен')
 
        spam()
        bot.send_message(158079043, '❗️ Спам сегодня закончен')

        # Получить текущее время в Красноярске
        current_time_krasnoyarsk = datetime.now(tz)

        # Вычислить дату и время для завершения ожидания
        next_day = current_time_krasnoyarsk.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
        sleep_time = next_day.strftime("%H:%M, %d %B")

        # сообщение о том, что бот отправляется спать до указанного времени и даты
        bot.send_message(158079043, '🕘 ' + f'Бот отправляется спать до {sleep_time}')

        # Вычислить время ожидания до следующего события
        time_to_wait = (next_day - current_time_krasnoyarsk).total_seconds()

        # Подождать до указанного времени
        time.sleep(round(time_to_wait))
    else:
        if 0 <= Krasnoyarsk_hour < 8:
            # Вычислить время ожидания до 9:00 утра текущего дня
            current_time_krasnoyarsk = datetime.now(tz)
            next_day = current_time_krasnoyarsk.replace(hour=9, minute=0, second=0, microsecond=0)
            sleep_time = next_day.strftime("%H:%M, %d %B")
            time_to_wait = (next_day - current_time_krasnoyarsk).total_seconds()

            # Если текущее время уже больше или равно 9:00 утра, то ждать не нужно
            if time_to_wait > 0:
                # Ожидаем до 9:00 утра текущего дня
                bot.send_message(158079043, '🕘 ' + f'Бот отправляется спать до {sleep_time}')
                time.sleep(round(time_to_wait))
            # spam()
            
            
        else:
            current_time_krasnoyarsk = datetime.now(tz)
            next_day = current_time_krasnoyarsk.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
            sleep_time = next_day.strftime("%H:%M, %d %B")

            # сообщение о том, что бот отправляется спать до указанного времени и даты
            bot.send_message(158079043, '🕘 ' + f'Бот отправляется спать до {sleep_time}')

            time_to_wait = (next_day - current_time_krasnoyarsk).total_seconds()
            time.sleep(round(time_to_wait))

"""СПАМ ФУНКЦИЯ"""





if __name__ == '__main__':
  # bot.polling(none_stop=True, timeout=60)
  bot.infinity_polling(True)
