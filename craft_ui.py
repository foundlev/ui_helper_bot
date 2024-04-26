import json
import os

import logging

import aiogram.types
from aiogram import Bot, Dispatcher, types


# Telegram Bot Token
BOT_TOKEN: str = ""


# Set up logging
logging.basicConfig(level=logging.INFO)

# Create bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


def get_reply_markup(message: aiogram.types.Message):
    content = load(message.chat.id)

    keyboard = content.get('keyboard')
    inline = content.get('inline')
    rpl = keyboard

    if keyboard:
        kb = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True)

        for row in keyboard:
            row_buttons = []
            for button_name in row:
                row_buttons.append(aiogram.types.KeyboardButton(text=button_name))

            kb.add(*row_buttons)
        rpl = kb

    elif inline:
        kb = aiogram.types.InlineKeyboardMarkup()

        for row in inline:
            row_buttons = []
            for button_name in row:
                if ":url" in button_name:
                    button_name = button_name.replace(":url", "").strip()
                    row_buttons.append(aiogram.types.InlineKeyboardButton(text=button_name, url='https://t.me/'))
                else:
                    row_buttons.append(aiogram.types.InlineKeyboardButton(text=button_name, callback_data='_'))

            kb.add(*row_buttons)
        rpl = kb

    else:
        rpl = None

    return rpl


def load(user_id: int) -> dict:
    try:
        with open(f"settings_{user_id}.json", "rt", encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}


def save(user_id: int, key: str, value):
    try:
        content = load(user_id)
        content[key] = value

        with open(f"settings_{user_id}.json", "wt", encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
    except:
        ...


# Handler for text messages
@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def echo_message(message: types.Message):
    user_id = message.chat.id

    try:

        if message.text.startswith("/start"):
            text = """
👋 <b>Добро пожаловать. Используй команды бота.</b>

<u>Установить параметры сообщения</u>
Текст: [текст]
Картинку: просто отправь картинку
Инлайн-кнопки: /set_inline (кнопка 1) (кнопка 2) _ (кнопка 3)
Клавиатурные-кнопки: /set_keyboard (кнопка 1) (кнопка 2) _ (кнопка 3)

Удалить кнопки: /reset_buttons
Удалить картинку: /reset_img

Символ "_" - перенос строки
:url в тексте инлайн кнопки - кнопка будет ссылкой
                """
            await message.answer(text, parse_mode='html')

        elif message.text.startswith("/set_inline "):
            buttons = []
            text: str = message.text.replace("\n", " ")

            for row in text.split("_"):
                row_buttons = []
                for button in row.split("(")[1:]:
                    button = button.split(")")[0].strip()
                    row_buttons.append(button)
                buttons.append(row_buttons)

            save(user_id, 'inline', buttons)
            save(user_id, 'keyboard', [])

            await message.answer("✅ Кнопки обновлены")

        elif message.text.startswith("/set_keyboard "):
            buttons = []
            text: str = message.text.replace("\n", " ")

            for row in text.split(" _ "):
                row_buttons = []
                for button in row.split("(")[1:]:
                    button = button.split(")")[0].strip()
                    row_buttons.append(button)
                buttons.append(row_buttons)

            save(user_id, 'keyboard', buttons)
            save(user_id, 'inline', [])

            await message.answer("✅ Кнопки обновлены")

        elif message.text.startswith("/reset_buttons"):

            save(user_id, 'keyboard', [])
            save(user_id, 'inline', [])

            await message.answer("✅ Кнопки удалены")

        else:
            await message.send_copy(message.chat.id, reply_markup=get_reply_markup(message),
                                    disable_web_page_preview=True)

    except Exception as e:
        text = f"❌ Ошибка: {e}"
        await message.answer(text)


# Handler for photo messages
@dp.message_handler(content_types=types.ContentTypes.PHOTO)
async def save_photo(message: types.Message):
    await message.send_copy(message.chat.id, reply_markup=get_reply_markup(message))


# Start the bot
if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)