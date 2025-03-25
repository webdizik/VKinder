import os
import json

from vk_api.keyboard import VkKeyboard, VkKeyboardColor


group_id = os.getenv('GROUP_ID')

def preferences_kb() -> json:
    '''
    Создание клавиатуры, которая состоит из одной callback-кнопки.
    По нажатию на кнопку открывается анкета для заполнения параметров поиска.
    '''
    # Создание экземпляра класса VkKeyboard.
    # Клавиатура создается с указанием следующих параметров:
    # one_time=False - по нажатию на кнопку, клавиатура не пропадает,
    # inline=True - встроена в сообщение (по умолчанию False).
    keyboard = VkKeyboard(one_time=False, inline=True)
    # Создание кнопки с текстом "Перейти к заполнению анкеты". 
    # Кнопка открывает форму для заполнения анкеты.
    keyboard.add_callback_button(
        'Перейти к заполнению анкеты',
        color=VkKeyboardColor.POSITIVE,
        payload={
            "type": "open_app",
            "app_id": 6013442,
            "owner_id": group_id,
            "hash": "#form_id=1"
        }
    )

    return keyboard.get_keyboard()

def view_kb() -> json:
    '''
    Создание клавиатуры для взаимодействия с пользователем по реализации функциональности бота.
    '''
    keyboard = VkKeyboard(one_time=False)
    # Создание обычных кнопок для выполнения указанных на этих кнопках действий.
    keyboard.add_button('👈 Предыдущий кандидат', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Следующий кандидат👉', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('Посмотреть Избранное 😜', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сохранить в Избранное 🤪', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Заполнить анкету заново 🤠', color=VkKeyboardColor.NEGATIVE)
    
    return keyboard.get_keyboard()

def new_questionnaire_kb() -> json:
    '''
    Создание клавиатуры для уточнения намерений пользователя
    по выходу из текущей анкеты, и запуска поиска с новыми параметрами.
    '''
    keyboard = VkKeyboard(one_time=True)
    # Создание обычных кнопок для выполнения указанных на этих кнопках действий.
    keyboard.add_button('🚙  Вернуться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_button('Продолжить 🚀', color=VkKeyboardColor.POSITIVE)

    return keyboard.get_keyboard() 