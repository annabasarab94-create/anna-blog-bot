import os
import json
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiohttp import web

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

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
    (0, 5): ("❌ Блог на автопилоте", "Нет системы, нет стратегии. Начните отсюда."),
    (6, 11): ("🟡 Держится на вас", "Вы не делегировали - только исполнение."),
    (12, 15): ("🟢 Есть система", "Отточите аналитику."),
    (16, 19): ("✅ Хорошо", "Остались детали."),
    (20, 20): ("🏆 Отлично", "Готовы к масштабированию."),
}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_state = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Начни тест командой /test")

@dp.message(Command("test"))
async def test(message: types.Message):
    user_id = message.from_user.id
    user_state[user_id] = {"scores": [], "q": 0}
    await ask_question(message, user_id)

async def ask_question(message, user_id):
    q_num = user_state[user_id]["q"]
    if q_num >= len(QUESTIONS):
        await show_result(message, user_id)
        return
    
    question, answers = QUESTIONS[q_num]
    buttons = [[InlineKeyboardButton(text=ans, callback_data=f"q{q_num}_{ans}")] for ans in answers.keys()]
    
    await message.answer(
        f"Вопрос {q_num + 1}/10:\n\n{question}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@dp.callback_query(lambda c: c.data.startswith("q"))
async def answer(callback):
    user_id = callback.from_user.id
    parts = callback.data.split("_", 1)
    q_num = int(parts[0][1:])
    answer_text = parts[1]
    
    question, answers = QUESTIONS[q_num]
    score = answers[answer_text]
    user_state[user_id]["scores"].append(score)
    user_state[user_id]["q"] = q_num + 1
    
    if q_num + 1 < len(QUESTIONS):
        next_q, next_answers = QUESTIONS[q_num + 1]
        buttons = [[InlineKeyboardButton(text=ans, callback_data=f"q{q_num+1}_{ans}")] for ans in next_answers.keys()]
        await callback.message.edit_text(
            f"Вопрос {q_num + 2}/10:\n\n{next_q}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
    else:
        await show_result(callback.message, user_id)
    
    await callback.answer()

async def show_result(message, user_id):
    total = sum(user_state[user_id]["scores"])
    title, desc = None, None
    for (min_s, max_s), (t, d) in RESULTS.items():
        if min_s <= total <= max_s:
            title, desc = t, d
            break
    
    await message.edit_text(
        f"📊 Результат: {total}/20\n\n<b>{title}</b>\n\n{desc}\n\n"
        f"Напиши мне в Telegram: https://t.me/basarab_ani",
        parse_mode="HTML"
    )

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
