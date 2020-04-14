from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from typing import Dict, List
import requests
import math

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Galimed Logs')
logger.setLevel(logging.INFO)
'''
fh = logging.FileHandler("bot_logs.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
'''
free_days = []
# ACCESS_TOKEN = "21df12be02decad1794736ccba47d0a87cac6c7decd0dd32910ffd4d5005aa7441a6042bd6ff2c47d26ee"
ACCESS_TOKEN = "f802f8143b2a5670d79a3afbcb4d8ee8a6f1dd96a7a40844bd87cb167bb077fa958c583d7d1da1900b3c8" # test_token
global_name = ''

class Day():
    def __init__(self,
                 month_name: str,
                 month_number: int,
                 month_short_name: str,
                 day_number: int,
                 day_ned: str,
                 is_saturday: bool,
                 times: List) -> None:

        self.month_name = month_name
        self.month_number = month_number
        self.month_short_name = month_short_name
        self.day_number = day_number
        self.day_ned = day_ned
        self.saturday = is_saturday
        self.times = times

    def get_ntimes(self, n):
        return self.times[:min(n, len(times))]

    def get_day_name(self):
        return "%s %s %s" % (self.month_name, self.day_number, self.day_ned)

    def __str__(self):
        return self.get_day_name()

class User():
    def __init__(self, user_id):
        self.user_id = user_id
        self.name = None
        self.telephone = None
        self.specialization = None
        self.doctor = None
        self.day = None
        self.offset = None

    def go_to_specialization(self):
        self.next_step = "doctor"
        self.offset =  0
        self.doctor = None
        self.specialization = None
        self.day = None
        self.full_day = None

    def save(self, url):
        self_data = self.__dict__

        data = {
            "day": self_data["full_day"].day_number,
            "first_name": self_data["name"].split()[0],
            "hour": int(self_data["time"].split(":")[0]),
            "id": self_data["doctor_id"],
            "last_name": self_data["name"].split()[1],
            "minute": int(self_data["time"].split(":")[1]),
            "month": self_data['full_day'].month_number,
            "phone": int(self_data['telephone'][1:])
        }

        logger.info("Данные отправлены: ")
        logger.info(data)
        requests.post(url, data)

    def display(self):
        for key in self.__dict__:
            print(key, self.__dict__[key])



class MedBot():
    def __init__(self):
        self.vk_session = vk_api.VkApi(token=ACCESS_TOKEN)
        self.json_url = "http://galimed.ru/test_vk.php"
        self.colors = ["positive", "positive"]
        self.clients = {}

        self.n_days_view = 5

        self.refresh_bot()

    def refresh_bot(self):
        self.specializations = self.get_specializations()

        self.welcome = requests.get(self.json_url).json()["welcome"]
        self.fine = requests.get(self.json_url).json()["fine"]
        self.spesialization_msg = requests.get(self.json_url).json()["welcom2"]
        self.doctor_msg = requests.get(self.json_url).json()["welcom3"]
        self.date_msg = requests.get(self.json_url).json()["welcom4"]
        self.time_msg = requests.get(self.json_url).json()["welcom5"]
        self.last_msg = requests.get(self.json_url).json()["welcom6"]
        self.retry_msg = requests.get(self.json_url).json()["welcom7"]
        self.errorss = requests.get(self.json_url).json()["errorss"]
        self.retry_always = requests.get(self.json_url).json()["nachat"]
    def run(self):
        longpoll = VkLongPoll(self.vk_session)
        vk = self.vk_session.get_api()
        self.refresh_bot()

        logger.info("Бот запущен")

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                if event.text == "/start" or event.text == self.retry_msg or event.text == "Начать":
                    self.clients[event.user_id] = User(event.user_id)
                    logger.info(str(event.user_id) + " начал сессию")
                    vk.messages.send(
                        user_id=event.user_id,
                        message=self.welcome,
                        random_id=get_random_id(),
                    )

                    self.clients[event.user_id].next_step = "specialization"
                elif event.text == 's' + self.retry_always:
                    global next_step
                    next_step = "specialization"
                    self.clients[event.user_id].name = global_name
                elif event.user_id in self.clients or event.text == self.retry_always:

                    client = self.clients[event.user_id]
                    client.display()

                    next_step = client.next_step
                    if event.text == self.retry_always:
                        client = self.clients[event.user_id]
                        next_step = "specialization"
                        client.next_step = 'specialization'
                        self.clients[event.user_id].next_step = 'specialization'
                        self.clients[event.user_id].doctor = None
                        self.clients[event.user_id].doctor_id = None
                        self.clients[event.user_id].day = None
                        self.clients[event.user_id].full_day = None

                    if next_step == "specialization":
                        if len(event.text.split()) == 2:
                            #global global_name
                            if event.text == self.retry_always:
                                self.clients[event.user_id].name = global_name
                            else:
                                global_name = event.text
                                self.clients[event.user_id].name = event.text
                            #if self.clients[event.user_id].name == None:

                             #   global_name = event.text
                              #  self.clients[event.user_id].name = event.text
                            keyboard = self.get_specializations_keyboard().get_keyboard()
                            self.clients[event.user_id].next_step = "doctor"

                            message = self.spesialization_msg
                        else:
                            keyboard = VkKeyboard(one_time=True)
                            keyboard = self.add_retry_button(keyboard)
                            keyboard = keyboard.get_keyboard()
                            message = "Введите, пожалуйста, имя и фамилию через пробел"

                    if next_step == "doctor":
                        # CHOICE DOCTOR
                        if self.clients[event.user_id].specialization is None:
                            print(event.text)
                            self.clients[event.user_id].specialization = event.text

                        try:
                            keyboard = self.get_doctors_keyboard(self.clients[event.user_id].specialization).get_keyboard()
                            self.clients[event.user_id].next_step =  "day"
                            self.clients[event.user_id].offset =  0

                            message = self.doctor_msg

                        except:
                            message = "К сожалению, к %s больше нет свободных мест" % client.doctor
                            keyboard = self.get_doctors_keyboard(self.clients[event.user_id].specialization).get_keyboard()

                            self.clients[event.user_id].next_step = "day"
                            self.clients[event.user_id].doctor = None

                    if next_step == "day":
                        # CHOICE DAY
                        if (event.text != "Еще даты" and event.text != "Назад" and not client.doctor is None):
                            self.clients[event.user_id].day = event.text
                            self.clients[event.user_id].full_day = event.text
                            self.clients[event.user_id].next_step = "time"
                            message = self.time_msg
                        else:
                            if client.doctor is None:
                                client.doctor = event.text
                                client.doctor_id = self.get_doctor_id_by_name(client, client.doctor)

                            if event.text == "Еще даты":
                                self.clients[event.user_id].offset += self.n_days_view
                            elif event.text == "Назад":
                                self.clients[event.user_id].offset -= self.n_days_view

                            try:
                                keyboard = self.get_free_days_keyboard(self.clients[event.user_id].specialization, self.clients[event.user_id].doctor, self.n_days_view, self.clients[event.user_id].offset).get_keyboard()
                                message = self.date_msg
                            except:
                                message = "К сожалению, к %s больше нет свободных мест" % self.clients[event.user_id].doctor
                                keyboard = self.get_specializations_keyboard().get_keyboard()
                                self.clients[event.user_id].go_to_specialization()

                    if self.clients[event.user_id].next_step == "time":
                        #CHOICE TIME

                        try:
                            day = self.get_day_by_name(self.clients[event.user_id], self.clients[event.user_id].day)
                            self.clients[event.user_id].full_day = day
                            times = day.times
                            keyboard = self.fill_keyboard(times, 3).get_keyboard()

                            self.clients[event.user_id].next_step = "telephone"
                        except:
                            message = "К сожалению, в %s к %s больше нет свободных мест" % (self.clients[event.user_id].day, self.clients[event.user_id].doctor)
                            keyboard = self.get_specializations_keyboard().get_keyboard()
                            self.clients[event.user_id].go_to_specialization()

                    if next_step == "telephone":
                        keyboard = VkKeyboard(one_time=True)
                        keyboard = self.add_retry_button(keyboard)
                        keyboard = keyboard.get_keyboard()

                        client.time = event.text
                        message = self.last_msg
                        client.next_step = "save"

                    if next_step == "save":
                        if len(event.text) != 11 or not event.text.isdigit():
                            message = "Пожалуйста, введите номер телефона без лишних пробелов и символов, вы нам очень поможете!\nНапример: 79992135134"
                            keyboard = VkKeyboard(one_time=True)
                            keyboard = self.add_retry_button(keyboard)
                            keyboard = keyboard.get_keyboard()
                        else:
                            keyboard = VkKeyboard(one_time = True)
                            keyboard.add_button(self.retry_msg, color='positive', payload=[])
                            keyboard = keyboard.get_keyboard()

                            client.telephone = event.text

                            client.save(self.json_url)

                            message = self.fine % client.name.split()[0]

                            logger.info('Client delited')
                            del client


                    try:
                        vk.messages.send(
                            user_id=event.user_id,
                            message=message,
                            keyboard=keyboard,
                            random_id=get_random_id(),
                        )
                    except:
                        if next_step == "day":
                            message = "К сожалению, к %s больше нет свободных мест" % client.doctor
                            keyboard = self.get_specializations_keyboard().get_keyboard()
                            self.clients[event.user_id].go_to_specialization()

                        vk.messages.send(
                            user_id=event.user_id,
                            message=message,
                            keyboard=keyboard,
                            random_id=get_random_id(),
                        )

                else:
                    keyboard = VkKeyboard(one_time = True)
                    keyboard.add_button("Начать", color='primary', payload=[])
                    keyboard = keyboard.get_keyboard()

                    vk.messages.send(
                        user_id=event.user_id,
                        message=self.errorss,
                        keyboard=keyboard,
                        random_id=get_random_id(),
                    )

    def get_specializations_keyboard(self):
        specializations = self.get_specializations()
        keyboard = self.fill_keyboard(specializations, 1)

        return keyboard

    def get_doctors_keyboard(self, specialization):
        doctors  = self.get_doctors_by_specialization(specialization)
        for doctor in doctors:
            if len(self.get_free_days_by_doctor(specialization, doctor[0], n=5, offset=0)) == 0:
                doctors.remove(doctor)

        keyboard = self.fill_keyboard([doctor[0] for doctor in doctors], 1)

        return keyboard

    def get_free_days_keyboard(self, specialization, doctor, n=5, offset=0):
        days = self.get_free_days_by_doctor(specialization, doctor, n, offset)

        keyboard = self.fill_keyboard(["%s" % (day.get_day_name()) for day in days], 2)

        if(offset != 0 or len(days) >= n): keyboard.add_line()
        if offset != 0: keyboard.add_button("Назад", color='default', payload=[])
        if len(days) >= n: keyboard.add_button("Еще даты", color='default', payload=[])
        return keyboard

    def fill_keyboard(self, items: List, row_len: int=3) -> VkKeyboard:
        keyboard = VkKeyboard(one_time=True)

        for line_num in range(math.ceil(len(items)/row_len)):

            if line_num != 0: keyboard.add_line()

            for _ in range(min(row_len, len(items))):
                keyboard.add_button(items[0], color=self.colors[line_num % 2], payload=[])
                del items[0]

        keyboard = self.add_retry_button(keyboard, new_line=True)

        return keyboard

    def add_retry_button(self, keyboard, new_line=False):
        if new_line: keyboard.add_line()

        keyboard.add_button(self.retry_always, color='primary', payload=[])

        return keyboard

    def get_specializations(self):
        data = requests.get(self.json_url).json()
        groups = [group["name"] for group in data["groups"]]

        return groups

    def get_group_by_name(self, name):
        data = requests.get(self.json_url).json()

        for group in data["groups"]:
            if group["name"] == name:
                return group

    def get_doctors_by_specialization(self, specialization):
        group = self.get_group_by_name(specialization)
        doctors = [(list["name"], list["id"]) for list in group["list"]]

        return doctors

    def get_shedule_by_doctor_id(self, group, doctor_name):
        for item in group["list"]:
            if item['name'] == doctor_name:
                return item

    def get_day_by_name(self, client, day_name) -> Day:
        days = self.get_free_days_by_doctor(client.specialization, client.doctor, n=5, offset=0)
        for day in days:
            print(day.get_day_name())
            if day.get_day_name() == day_name:
                return day

    def get_doctor_id_by_name(self, client, doctor_name):
        doctors = self.get_doctors_by_specialization(client.specialization)

        for doctor in doctors:
            if doctor[0] == doctor_name:
                return doctor[1]

    def get_free_days_by_doctor(self, specialization, doctor_id, n=5, offset=1):
        group   = self.get_group_by_name(specialization)
        shedule = self.get_shedule_by_doctor_id(group, doctor_id)
        days_list = []

        for days in shedule['calendar']:
            month_name = days['name']
            month_short_name = days['names']
            month_number = days['month']
            for day in days['days']:
                day_number = day['day']
                day_ned = day['day_ned']
                is_saturday = day['saturday']
                times = day['time']
                print(times)
                days_list.append(Day(month_name, month_number, month_short_name,
                                 day_number, day_ned, is_saturday, times))

        return days_list[offset: offset+n]


while True:
    try:
        bot = MedBot()
        logger.info("Бот загружен")
        logger.info("Запуск...")

        bot.run()
    except Exception as e:
        logger.error(str(e))
        print("Перезапуск...")
