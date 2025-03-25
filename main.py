import os

from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from db_handler.db_data import (
    save_favorite,
    get_favorites_from_db,
    save_user_state,
    load_user_state,
    ensure_user_exists
)

from keyboards.keyboards import preferences_kb, view_kb
from handlers.functions import (
    send_message, 
    send_messageEvAns, 
    find_candidates,
    send_current_candidate
)


# Конфигурация
group_id_ = os.getenv('GROUP_ID')
group_token = os.getenv('group_token')
placeholder = os.getenv('PLACEHOLDER')

# Авторизация VK
vk_gr_session = VkApi(token=group_token)
vk_gr = vk_gr_session.get_api()


# Инициализация LongPoll
longpoll = VkBotLongPoll(vk_gr_session, group_id=group_id_)

# Основной цикл бота
for event in longpoll.listen():
    if event.t == VkBotEventType.MESSAGE_NEW:
        user_name = vk_gr.users.get(user_id=event.obj['message']['from_id'])[0]['first_name']
        send_message(
            event.obj['message']['from_id'],
            f"Привет, {user_name}!\nДавайте поищем кандидатов для знакомства!",
            keyboard=preferences_kb()
        )
        break

for event in longpoll.listen():
    if event.t == VkBotEventType.MESSAGE_NEW:
        send_message(
            event.obj['message']['from_id'],
            "Я сегодня не в настроении. Пообщаться не получится.🥺\nДавайте, всё-таки, поищем кандидатов для знакомства!",
            keyboard=preferences_kb()
        )

    if event.t == VkBotEventType.MESSAGE_EVENT:
        user_id = event.obj['user_id']

        # Шаг 1: Убедиться, что пользователь существует
        ensure_user_exists(user_id)  # <-- Добавлено!

        # Загрузка состояния из базы данных
        current_state = load_user_state(user_id)
        if not current_state:
            # Инициализация нового состояния
            save_user_state(
                user_id=user_id,
                current_index=0,
                offset=0,
                candidates=[]
            )
            current_state = load_user_state(user_id)

        send_messageEvAns(
            event.obj.user_id,
            event.obj.peer_id,
            event.obj.event_id,
            event.obj.payload
        )

    if event.t == 'lead_forms_new':
        user_id = event.obj['user_id']
        send_message(user_id, 'Подбираем кандидатов', keyboard=view_kb())

        # Поиск кандидатов с учетом текущего offset
        current_state = load_user_state(user_id)
        candidates = find_candidates(event.obj, offset=current_state.get('offset', 0))

        # Сохранение кандидатов в базу данных
        save_user_state(
            user_id=user_id,
            current_index=0,
            offset=current_state.get('offset', 0),
            candidates=candidates
        )

        # Обновление локального состояния
        current_state = load_user_state(user_id)
        candidates_count = len(current_state['candidates'])

        # Отправка сообщения о количестве найденных кандидатов
        if str(candidates_count)[-1] == "1" and candidates_count != 11:
            send_message(user_id, f'Найден {candidates_count} кандидат!')
        elif candidates_count // 10 == 1 or str(candidates_count)[-1] in "567890":
            send_message(user_id, f'Найдено {candidates_count} кандидатов!')
        else:
            send_message(user_id, f'Найдено {candidates_count} кандидата!')

        # Вывод в чат первого кандидата
        send_current_candidate(user_id, 0)

        # Вложенный цикл для обработки действий
        for inner_event in longpoll.listen():
            current_state = load_user_state(user_id)

            if inner_event.t == VkBotEventType.MESSAGE_NEW:
                text = inner_event.obj['message']['text']

                # Навигация вперед
                if '👉' in text:
                    if current_state['current_index'] < len(current_state['candidates']) - 1:
                        new_index = current_state['current_index'] + 1
                        save_user_state(
                            user_id=user_id,
                            current_index=new_index,
                            offset=current_state['offset'],
                            candidates=current_state['candidates']
                        )
                        send_current_candidate(user_id, new_index)
                    else:
                        # Загрузка новых кандидатов
                        new_offset = current_state['offset'] + 1000
                        new_candidates = find_candidates(event.obj, offset=new_offset)
                        if new_candidates:
                            updated_candidates = current_state['candidates'] + new_candidates
                            save_user_state(
                                user_id=user_id,
                                current_index=0,
                                offset=new_offset,
                                candidates=updated_candidates
                            )
                            send_current_candidate(user_id, 0)
                        else:
                            send_message(user_id, 'Кандидаты закончились!')

                # Навигация назад
                elif '👈' in text:
                    if current_state['current_index'] == 0:
                        send_message(user_id, 'Это первый кандидат. Вы в начале списка')
                    else:
                        new_index = current_state['current_index'] - 1
                        save_user_state(
                            user_id=user_id,
                            current_index=new_index,
                            offset=current_state['offset'],
                            candidates=current_state['candidates']
                        )
                        send_current_candidate(user_id, new_index)

                # Добавление в избранное
                elif '🤪' in text:
                    current_candidate = send_current_candidate(
                        user_id,
                        current_state['current_index'],
                        True
                    )
                    if current_candidate:
                        save_favorite(
                            user_id=user_id,
                            first_name=current_candidate['first_name'],
                            last_name=current_candidate['last_name'],
                            vk_link=f"https://vk.com/id{current_candidate['id']}"
                        )
                        send_message(
                            user_id,
                            f"Кандидат {current_candidate['first_name']} {current_candidate['last_name']} добавлен в избранное!"
                        )

                # Просмотр избранного
                elif '😜' in text:
                    favorites = get_favorites_from_db(user_id)
                    if favorites:
                        favorites_list = "\n".join(
                            [f"{candidate['first_name']} {candidate['last_name']} - {candidate ['vk_link']}"
                             for candidate in favorites]
                        )
                        send_message(user_id, "Список избранных кандидатов:\n" + favorites_list)
                    else:
                        send_message(user_id, "Ваш список избранных кандидатов пуст.")

                # Удаление данных
                # elif '🤠' in text:
                #     send_message(user_id, 'Списки кандидатов и избранных кандидатов удалены!')

                # Дефолтный ответ
                else:
                    send_message(user_id, 'Список кандидатов просмотрен!')