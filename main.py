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

# Google Sheets
try:
    creds = Credentials.from_service_account_info(
        json.loads(GOOGLE_CREDENTIALS_JSON),
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    gc = gspread.authorize(creds)
    worksheet = gc.open_by_key(GOOGLE_SHEET_ID).sheet1
except:
    worksheet = None

QUESTIONS = [
    ("Есть ли у вашего блога четкая стратегия на 2-3 месяца?", 
     {"Да": 2, "Отчасти": 1, "Нет": 0}),
    ("Вы уже делегировали выбор тем кому-то?", 
     {"Да": 2, "Отчасти": 1, "Нет": 0}),
    ("Работает ли ваш помощник по системе?", 
     {"Да": 2, "Отчасти": 1, "Нет": 0}),
    ("Часто ли вы объясняете подрядчику, почему?", 
     {"Нет": 2, "Иногда": 1, "Да": 0}),
    ("Вы знаете, чего ожидать от каждого поста?", 
     {"Да": 2, "Отчасти": 1, "Нет": 0}),
    ("Понимаете ли вы, почему один пост работает, а другой нет?", 
     {"Да": 2, "Отчасти": 1, "Нет": 0}),
    ("Можете четко описать, для кого ваш блог?", 
     {"Да": 2, "Отчасти": 1, "Нет": 0}),
    ("Как вас видит ваша аудитория - четко позиционированы?", 
     {"Да": 2, "Отчасти": 1, "Нет": 0}),
    ("Вы смотрите на качество лидов и продажи из блога?", 
     {"Да": 2, "Отчасти": 1, "Нет": 0}),
    ("Блог - это работающая система или обуза?", 
     {"Система": 2, "Задача": 1, "Обуза": 0}),
]

RESULTS = {
    (0, 5): ("❌ Блог на автопилоте", "Нет системы, нет стратегии, нет делегирования. Это можно переделать в первую очередь."),
    (6, 11): ("🟡 Держится на вас", "Вы не делегировали - только исполнение. Это съедает энергию."),
    (12, 15): ("🟢 Есть система", "Стратегия есть. Нужна аналитика и регулярный разбор."),
    (16, 19): ("✅ Хорошо", "Система работает. Остались детали и возможности роста."),
    (20, 20): ("🏆 Отлично", "Вы знаете свой блог лучше всех. Готовы к масштабированию."),
}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_state = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("👋 Привет! Начни тест командой /test")

@dp.message(Command("test"))
async def test(message: types.Message):
    user_id = message.from_user.id
    user_state[user_id] = {"scores": [], "q": 0}
    
    q_num = 0
    question, answers = QUESTIONS[q_num]
    buttons = [[InlineKeyboardButton(text=ans, callback_data=f"q{q_num}_{ans}")] for ans in answers.keys()]
    
    await message.answer(
        f"Вопрос 1/10:\n\n{question}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@dp.callback_query(lambda c: c.data.startswith("q"))
async def answer(callback):
    user_id = callback.from_user.id
    
    if user_id not in user_state:
        await callback.answer("Начни тест заново: /test")
        return
    
    parts = callback.data.split("_", 1)
    q_num = int(parts[0][1:])
    answer_text = parts[1]
    
    question, answers = QUESTIONS[q_num]
    score = answers[answer_text]
    user_state[user_id]["scores"].append(score)
    
    if q_num + 1
