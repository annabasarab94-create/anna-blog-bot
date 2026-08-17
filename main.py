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
    (0, 5): {
        "title": "❌ Блог на автопилоте",
        "text": "Вот что я вижу: у вас есть блог, но это не система. Периодические посты, которые откладываются, непонятная аудитория, непредсказуемые результаты.\n\nНет стратегии. Нет делегирования. Нет анализа.\n\nЭто ровно то, что можно переделать в первую очередь — не добавлять контент, а сделать систему, которая работает без вашего постоянного управления."
    },
    (6, 11): {
        "title": "🟡 Держится на вас",
        "text": "Вы понимаете, что блог нужен, и пытаетесь его вести. Может быть, есть помощник. Но всё крутится вокруг вас. Вы выбираете темы, объясняете, смотрите результаты.\n\nВы не делегировали продвижение — вы делегировали только исполнение. Это съедает энергию и не масштабируется.\n\nНужна система, которая работает без вашего ежедневного управления."
    },
    (12, 15): {
        "title": "🟢 Есть основа",
        "text": "Хорошо: стратегия есть, вы понимаете аудиторию, делегирование частично работает.\n\nНо вот беда: вы не всегда видите закономерности. Почему один рилс зашёл, другой нет? Что работает?\n\nБез аналитики и регулярного разбора система становится случайной. Нужна не перестройка, а настройка."
    },
    (16, 19): {
        "title": "✅ Хорошо",
        "text": "Вы знаете, что делаете, для кого и зачем. Система работает. Делегирование на месте. Результаты понятны.\n\nОсталось убедиться, что не теряете возможности роста, которые не видите со стороны.\n\nМожет быть, есть канал или формат, который вы не используете. Или способ сэкономить ваше время через ещё большее делегирование."
    },
    (20, 20): {
        "title": "🏆 Отлично",
        "text": "Вы знаете свой блог лучше всех. Система работает, результаты видны, управление делегировано.\n\nТеперь интересное: масштабирование. Новые платформы, новые форматы, полное делегирование управления.\n\nГотовы к следующему уровню."
    }
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
    
    question, answers = QUESTIONS[0]
    buttons = [[InlineKeyboardButton(text=ans, callback_data=f"q0_{ans}")] for ans in answers.keys()]
    
    await message.answer(
        f"<b>Вопрос 1/10</b>\n\n{question}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )

@dp.callback_query(lambda c: c.data.startswith("q"))
async def answer(callback):
    user_id = callback.from_user.id
    
    if user_id not in user_state:
        await callback.answer("Начни тест: /test")
        return
    
    parts = callback.data.split("_", 1)
    q_num = int(parts[0][1:])
    answer_text = parts[1]
    
    question, answers = QUESTIONS[q_num]
    score = answers[answer_text]
    user_state[user_id]["scores"].append(score)
    
    if q_num + 1 < len(QUESTIONS):
        next_q = q_num + 1
        next_question, next_answers = QUESTIONS[next_q]
        buttons = [[InlineKeyboardButton(text=ans, callback_data=f"q{next_q}_{ans}")] for ans in next_answers.keys()]
        
        await callback.message.answer(
            f"<b>Вопрос {next_q + 1}/10</b>\n\n{next_question}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
            parse_mode="HTML"
        )
    else:
        total = sum(user_state[user_id]["scores"])
        result = None
        
        for (min_s, max_s), r in RESULTS.items():
            if min_s <= total <= max_s:
                result = r
                break
        
        result_text = f"📊 <b>Ваш результат: {total}/20</b>\n\n<b>{result['title']}</b>\n\n{result['text']}\n\n<b>Что дальше?</b>\nЕсли хотите разобраться, как это переделать — напишите мне. Ссылка в профиле."
        
        if worksheet:
            try:
                user_name = callback.from_user.first_name or "User"
                user_username = callback.from_user.username or "No username"
                worksheet.append_row([
                    user_id,
                    user_name,
                    user_username,
                    total,
                    result['title'],
                    "pending"
                ])
            except:
                pass
        
        await callback.message.answer(
            result_text,
            parse_mode="HTML"
        )
    
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
