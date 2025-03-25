import os
import json
from heapq import nlargest

from vk_api import VkApi
from vk_api.utils import get_random_id


vk_gr_session = VkApi(token=os.getenv('GROUP_TOKEN'))
vk_gr = vk_gr_session.get_api()
vk_us_session = VkApi(token=os.getenv('USER_TOKEN'))
vk_us = vk_us_session.get_api()

def send_message(user_id, message, attachment=None, keyboard=None):
    """
    Функция для отправки от имени бота сообщений в чат.
    На вход принимает сообщение - message.
    При необходимости можно передать медиа - attachment или клавиатуру - keyboard.
    """
    vk_gr.messages.send(
        user_id=user_id,
        message=message,
        attachment=attachment,
        keyboard=keyboard,
        random_id=get_random_id()
    )
   
def send_messageEvAns(user_id, peer_id, event_id, action):
    """
    Функция для генерации события, как реакции на нажатие на callback-кнопку.
    Выполняемое событие передаётся на вход в виде словаря в параметре action.
    """
    vk_gr.messages.sendMessageEventAnswer(
        user_id=user_id,
        peer_id=peer_id,
        event_id=event_id,
        event_data=json.dumps(action)
    )

def find_candidates(preferences, offset=0):
    """
    Функция для поиска кандидатов по заданным параметрам - preferences.
    Поиск кандидатов осуществляется от 0 до 1000 по параметру count=1000.
    Параметр offset задаёт смещение для поиска кандидатов от 1000 до 2000, от 2000 до 3000 и т.д
    """    
    response = vk_us.users.search(
        sex = 1 if preferences.answers[0]['answer'] == 'Девушку' else 2,
        age_from = preferences.answers[1]['answer'].split()[1],
        age_to = preferences.answers[1]['answer'].split()[3],
        hometown = preferences.answers[2]['answer'],
        has_photo=True,
        status=6,
        fields={
            'music': preferences.answers[3]['answer'],
            'movies': preferences.answers[4]['answer']
        },
        offset=offset,
        count=1000,
        is_closed=False
    )

    return response['items']

def get_popular_photos(id):
    """
    Функция для получения наиболее популярных фотографий кандидата.
    На вход принимает id пользователя.
    Фотографии получаются из профиля и со стены кандидата.
    Популярность определяется по количеству лайков.
    """     
    response = vk_us.photos.get(owner_id=id, album_id='profile', extended=1)
    if response['count'] == 0:
        top_3_photos_profile = []
    else:
        photos = response['items']
        top_3_photos_profile = nlargest(3, photos, key=lambda x: x['likes']['count'])

    response = vk_us.photos.get(owner_id=id, album_id='wall', extended=1)
    if response['count'] == 0:
        top_3_photos_wall = []
    else:
        photos = response['items']
        top_3_photos_wall = nlargest(3, photos, key=lambda x: x['likes']['count'])
    
    return top_3_photos_profile, top_3_photos_wall

def send_current_candidate(user_id, current_index, user_state={}, favorites=False):
    """
    Функция для отправки в чат имени, фамилии, ссылки на профиль,
    а также популярных фотографий кандидата.
    На вход принимает id пользователя и его текущий индекс в списке полученных кандидатов.
    Если передан флаг favorites=True, то возвращается текущий кандидат.
    """ 
    # Текущий кандидат извлекается из словаря с состояниями пользователей по его user_id.
    current_candidate = user_state[user_id]['candidates'][current_index]
    
    # Имя и фамилия кандидата:
    name = f"{current_candidate['first_name']} {current_candidate['last_name']}"
    # Ссылка на профиль кандидата:
    profile_link = f"https://vk.com/id{current_candidate['id']}"
    
    # Получение популярных фотографий кандидата:
    photos = get_popular_photos(current_candidate['id'])
    
    # Получение популярных фотографий кандидата из профиля:
    if photos[0] == []:
        # Если фотографий в профиле нет, то отправляется конкретная установленная фотография:
        attachment_profile = f'photo282701707_457239053_{group_token}'
    else:
        attachment_profile = ",".join([f'photo{photo['owner_id']}_{photo['id']}_{group_token}'
                                       for photo in photos[0]])

    # Получение популярных фотографий кандидата со стены:
    if photos[1] == []:
        # Если фотографий на стене нет, то отправляется конкретная установленная фотография:
        attachment_wall = f'photo282701707_457239053_{group_token}'
    else:
        attachment_wall = ",".join([f'photo{photo['owner_id']}_{photo['id']}_{group_token}' 
                                    for photo in photos[1]])
    
    # Если передан флаг favorites=False,
    if favorites is False:
        # то в чат отправляются имя и фамилия кандидата, ссылка на профиль, а так же
        # популярные фото профиля и со стены.
        return send_message(user_id, f"{name}\n{profile_link}"),\
               send_message(user_id, 'Наиболее популярные фото профиля ☝️', 
                    attachment=attachment_profile),\
               send_message(user_id, 'Наиболее популярные фото со стены ☝️',
                    attachment=attachment_wall)
    # А если передан флаг favorites=True,
    else:
        # то возвращается только текущий кандидат из словаря.
        return current_candidate
