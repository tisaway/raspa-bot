import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from pendulum import today
from pendulum.constants import MONDAY
from re import sub

from keyboard import get_keyboard
from schedule import get_schedule, get_groups
from db import *
from constants import *

vk_session = vk_api.VkApi(token=TOKEN)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

class MyVkLongPoll(VkLongPoll):
    def listen(self):
        while True:
            try: 
                for event in self.check():
                    yield event
            except Exception as e:
                print('ERROR WITH LONGPOLL: ', e)

# Добавляет название групп и их id в бд
def update_groups():
    groups = get_groups()
    for group_name in groups:
        group_id = groups[group_name] 
        group_name = sub(r'\s', '', group_name).upper()
        insert_new_group(group_name, group_id)
    print('Groups updated successfully.')

#Отправляет сообщение с текстом text пользователю с user_id
def write_msg(user_id, text):
    vk_session.method('messages.send', {'user_id': user_id, 'message': text, 'random_id' : 0, 'keyboard' : get_keyboard()})

# Отправляет расписание на день
# Получает id пользователя и дату, на которое нужно расписание
def send_day(user_id, date):
    group = db_get_user_group_id(user_id)
    schedule = get_schedule(date, group)
    write_msg(user_id, schedule)

# Отправляет расписание на неделю
# Получает id пользователя и понедельник, с которого нужно начинать отправлять 
def send_week(user_id, monday):
    date = monday
    for i in range(6):
        send_day(user_id, date)
        date = date.add(days=1)
    # В редких случаях может быть занятие в воскресенье и об этом нужно сказать
    schedule = get_schedule(date, db_get_user_group_id(user_id))
    if schedule.find('нет занятий') == -1:
        write_msg(user_id, schedule)

# Обработчик сообщений
def handler(user_id, message):

    # Если пользователя нет в бд, значит мы не знаем его группу
    if not db_user_exist(user_id):
        message = sub(r'\s', '', message).upper()
        # Если сообщение - это номер группы, значит нужно записать ее в бд как группу пользователя
        if db_group_exist(message):
            db_insert_new_user(user_id, message)
            text = 'Ты можешь получить расписание, написав нужный день:\nсегодня/завтра/понедельник/пн и др.' 
            write_msg(user_id, 'Группа добавлена. '+ text)
        else:
            write_msg(user_id, 'Не знаю такой группы😬\nВведи номер группы, например: 121. Убедись, что используешь полное название: 103-ПИвЭ, а не 103. Если всё ещё не получается, значит, твоей группы нет в расписании на сайте вуза и мне негде его взять. Подожди :)')

    # Если мы знаем группу пользователя
    else:
        message = message.lower()
        date = today('Europe/Moscow')

        # Если пользователь запросил расписание на текущую неделю
        # Отправляем расписание, начиная с этого понедельника
        if message == 'эта неделя':
            send_week(user_id, date.start_of('week'))
        # Если пользователь запросил расписание на следующую неделю
        # Отправляем расписание, начиная с этого понедельника
        elif message == 'следующая неделя':
            send_week(user_id, date.next(MONDAY))

        elif message == "изменить группу":
            db_delete_user(user_id)
            write_msg(user_id, 'Какая группа?')

        # В любом другом случае нужно отправить распиание на один день
        else:
            #Обрабатываем сообщения по типу "завтра"/"вчера"/"пн", меняя дату в соответсвии
            if message == 'завтра':
                date = date.add(days=1)
            elif message == 'вчера':
                date = date.add(days=-1)
            elif message in days_of_week:
                date = date.next(days_of_week[message])
            
            send_day(user_id, date)

update_groups()
print("Bot is running.")

# Обработчик событий longpoll
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me: 
        try:
            handler(event.user_id, event.text)
        except Exception as e:
            write_msg(event.user_id, 'Что-то не так. Попробуй ещё раз позже.')
            print("ERROR: " + str(e))