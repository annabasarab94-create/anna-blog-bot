import os
import json
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiohttp import web
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GOOGLE_CREDENTIALS_JSON = os.getenv('GOOGLE_CREDENTIALS_JSON')

try:
    creds = Credentials.from_service_account_info(
        json.loads(GOOGLE_CREDENTIALS_JSON),
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    gc = gspread.authorize(creds)
    worksheet = gc.open_by_key(GOOGLE_SHEET_ID).sheet1
except:
    worksheet = None

QUESTIONS = {
    1: ("Есть ли у вашего блога четкая стратегия?", {"yes": 2, "partially": 1, "no": 0}),
    2: ("Кто принимает решение о том, что постить?", {"yes": 2, "partially": 1, "no": 0}),
    3: ("Если у вас есть помощник, то он работает по системе?", {"yes": 2, "partially": 1, "no": 0}),
    4: ("Как часто вы объясняете подрядчику, почему?", {"yes": 2, "partially": 1, "no": 0}),
    5: ("Вы знаете, чего ожидать от каждого поста?", {"yes": 2, "partially": 1, "no": 0}),
    6: ("Понимаете ли вы, почему один пост работает, а другой нет?", {"yes": 2, "partially": 1, "no": 0}),
    7: ("Можете чётко описать, для кого ваш блог?", {"yes": 2, "partially": 1, "no": 0}),
    8: ("Как вас видит ваша аудитория?", {"yes": 2, "partially": 1, "no": 0}),
    9: ("На что вы смотрите в отчётах о блоге?", {"yes": 2, "partially": 1, "no": 0}),
    10: ("Блог для вас сейчас...", {"yes": 2, "partially": 1, "no": 0}),
}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_data = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {"scores": [], "question": 0}
    await message.answer("Привет! Начнём тест? /test")

@dp.message(Command("test"))
async def test(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {"scores": [], "question": 1}
    q_text, _ = QUESTIONS[1]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="ans_1_yes")],
        [InlineKeyboardButton(text="Отчасти", callback_data="ans_1_partially")],
        [InlineKeyboardButton(text="Нет", callback_data="ans_1_no")],
    ])
    await message.answer(f"Вопрос 1/10: {q_text}", reply_markup=kb)

@dp.callback_query(lambda c: c.data.startswith("ans_"))
async def answer(callback):
    user_id = callback.from_user.id
    parts = callback.data.split("_")
    question_num = int(parts[1])
    answer_type = parts[2]
    
    q_text, scores = QUESTIONS[question_num]
    score = scores[answer_type]
    user_data[user_id]["scores"].append(score)
    
    if question_num < 10:
        next_q = question_num + 1
        next_text, _ = QUESTIONS[next_q]
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data=f"ans_{next_q}_yes")],
            [InlineKeyboardButton(text="Отчасти", callback_data=f"ans_{next_q}_partially")],
            [InlineKeyboardButton(text="Нет", callback_data=f"ans_{next_q}_no")],
        ])
        await callback.message.edit_text(f"Вопрос {next_q}/10: {next_text}", reply_markup=kb)
    else:
        total = sum(user_data[user_id]["scores"])
        result = f"📊 Ваш результат: {total}/20"
        if worksheet:
            try:
                worksheet.append_row([user_id, callback.from_user.first_name or "User", total])
            except:
                pass
        await callback.message.edit_text(result)
    
    await callback.answer()

async def health_check(request):
    return web.Response(text="OK")

async def main():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
