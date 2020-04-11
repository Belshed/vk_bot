from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from typing import Dict, List

import traceback

import requests

import math

# = "21df12be02decad1794736ccba47d0a87cac6c7decd0dd32910ffd4d5005aa7441a6042bd6ff2c47d26ee"
ACCESS_TOKEN = "f802f8143b2a5670d79a3afbcb4d8ee8a6f1dd96a7a40844bd87cb167bb077fa958c583d7d1da1900b3c8"

vk_session = vk_api.VkApi(token=ACCESS_TOKEN)

while True:
    try:
        longPoll = VkLongPoll(vk_session)
        vk = vk_session.get_api()
        for event in longPoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                print(event.text)
                vk.messages.send(
                    user_id=event.user_id,
                    message=event.text,
                    random_id=get_random_id(),
                )
    except Exception as e:
        print("Error:", e)
        print("Перезапуск...")
