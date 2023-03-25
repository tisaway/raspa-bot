from json import dumps

# Возвращает кнопку с текстом text и цветом color в требуемом формате
def get_button(text, color):
    return {
        "action": {
            "type": "text",
            "payload": "{\"button\": \"" + "1" + "\"}",
            "label": f"{text}"
        },
        "color": f"{color}"
    }

KEYBOARD = {
    "one_time" : False,
    "buttons" : [
        [get_button('Сегодня', 'primary'), get_button('Завтра', 'primary')],
        [get_button('Эта неделя', 'primary'), get_button('Следующая неделя', 'primary')],
        [get_button('Изменить группу', 'secondary')]
    ]
}

#Возвращает клавиатуру в нужном формате
def get_keyboard():
    keyboard = dumps(KEYBOARD, ensure_ascii = False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard