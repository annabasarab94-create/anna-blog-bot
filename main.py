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

worksheet = None

try:
    creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    gc = gspread.authorize(creds)
    worksheet = gc.open_by_key(GOOGLE_SHEET_ID).sheet1
    print("✓ Google Sheets connected")
except Exception as e:
    print(f"❌ Google Sheets error: {e}")

QUESTIONS = [
    {
        "text": "Если я спрошу вас, что должно измениться в вашем блоге за ближайшие 2–3 месяца, вы сможете ответить конкретно?",
        "answers": {
            "Да. Я понимаю, к какому результату веду блог": 3,
            "Примерно. Есть цели и идеи": 2,
            "Не особо. Веду блог по ситуации": 1,
            "Если честно, нет": 0
        }
    },
    {
        "text": "Когда приходит время делать контент, кто обычно решает, о чём вы будете говорить?",
        "answers": {
            "Этим занимается специалист": 3,
            "Мы решаем вместе": 2,
            "В основном я": 1,
            "Всё полностью на мне": 0,
            "Каждый раз по-разному": 0
        }
    },
    {
        "text": "Представьте, что на неделю вы полностью выпали из ведения блога. Что с ним произойдёт?",
        "answers": {
            "Ничего критичного": 3,
            "Что-то продолжит выходить, но процесс начнёт тормозить": 2,
            "Скорее всего, всё остановится": 1,
            "Блог и так полностью на мне": 0
        }
    },
    {
        "text": "Если вам кто-то помогает с контентом, насколько часто приходится объяснять не только ЧТО сделать, но и ЗАЧЕМ это вообще нужно?",
        "answers": {
            "Почти никогда": 3,
            "Иногда": 2,
            "Часто": 1,
            "Почти постоянно": 0,
            "У меня пока нет специалиста": 1
        }
    },
    {
        "text": "Когда вы публикуете пост или Reels, вы обычно понимаете, какую задачу он должен решить?",
        "answers": {
            "Да. Я понимаю, какой контент должен привлекать новых людей": 3,
            "Чаще да. Обычно понимаю общую цель": 2,
            "Скорее нет. Публикую то, что кажется полезным": 1,
            "Нет. Главное, чтобы контент выходил": 0
        }
    },
    {
        "text": "После публикации вы понимаете, что в контенте сработало и что стоит изменить в следующий раз?",
        "answers": {
            "Да. Я смотрю результаты и понимаю, какие темы работают": 3,
            "Отчасти. Вижу, что один контент заходит лучше другого": 2,
            "Скорее нет. Обычно смотрю просмотры, но выводов не делаю": 1,
            "Нет. Опубликовал(а) и пошёл(ла) дальше": 0,
            "Я почти не смотрю аналитику": 0
        }
    },
    {
        "text": "Если убрать возраст, пол и профессию, вы можете чётко описать человека, которого хотите привлечь своим блогом?",
        "answers": {
            "Да. Я понимаю, что это за человек, с какими проблемами": 3,
            "В общих чертах. Примерно представляю свою аудиторию": 2,
            "Скорее нет. Могу назвать характеристики, но не понимаю запросы": 1,
            "Нет. Контент рассчитан на широкую аудиторию": 0,
            "Я об этом особо не думал(а)": 0
        }
    },
    {
        "text": "Если убрать просмотры, лайки и количество подписчиков, блог сейчас реально помогает вам получать клиентов и зарабатывать?",
        "answers": {
            "Да. Из блога регулярно приходят клиенты и продажи": 3,
            "Отчасти. Заявки бывают, но нестабильно": 2,
            "Скорее нет. Контент выходит, но в клиентах не отражается": 1,
            "Нет. Я вкладываю много, но результата не вижу": 0,
            "Сейчас блог скорее стал ещё одной задачей": 0
        }
    }
]

RESULTS = {
    1: {
        "title": "📈 Блог уже работает как система",
        "text": "У вас уже есть то, чего нет у многих: вы понимаете, зачем ведёте блог, кого хотите привлекать и какой контент должен давать результат.\n\nНо, скорее всего, вы уже упёрлись в другую точку: блог работает, а расти быстрее не получается. Где-то контент не приводит к нужному действию, где-то теряются потенциальные клиенты.\n\n✨ Хорошая новость: вам не нужно перестраивать всё с нуля. Здесь задача уже другая — найти слабые места, убрать лишнее и масштабировать то, что действительно приносит результат.",
        "image": "https://imgur.com/R08Ipm3.png"
    },
    2: {
        "title": "🔄 Блог работает, но слишком многое держится на вас",
        "text": "У вас уже есть понимание, что блог должен приводить клиентов. Но слишком многое до сих пор зависит лично от вас.\n\nТемы, идеи, согласования, решения. Пока вы включены, всё движется. Стоит переключиться, и блог начинает тормозить.\n\nВместо того, чтобы помогать вам расти, он становится ещё одной задачей.\n\n✨ Хорошая новость: это можно исправить. Нужно просто выстроить работу так, чтобы блог не зависел от вашего постоянного участия.",
        "image": "https://imgur.com/BY8zBe6.png"
    },
    3: {
        "title": "🧩 Контент есть, системы пока нет",
        "text": "Вы ведёте блог, тратите время на идеи, съёмки, тексты. Иногда что-то хорошо заходит, иногда приходят заявки. Но стабильности в этом нет.\n\nСегодня ролик набрал просмотры, завтра почти никто не увидел. И вы снова садитесь придумывать новый контент, не до конца понимая, что из предыдущего вообще сработало.\n\n✨ Это можно изменить. Контент можно выстроить так, чтобы у вас была понятная стратегия и результаты прошлых публикаций подсказывали, что делать дальше.",
        "image": "https://imgur.com/kIdLQQP.png"
    },
    4: {
        "title": "😵‍💫 Блог забирает больше, чем даёт",
        "text": "Сейчас блог ощущается как ещё одна работа поверх основной.\n\nНужно придумать тему, снять, написать, выложить, посмотреть охваты. И всё это постоянно висит в голове. При этом клиентов из блога либо мало, либо они приходят настолько нестабильно.\n\nВы всё время что-то делаете для блога, а он почти ничего не даёт взамен.\n\n✨ Это можно изменить. Блог можно выстроить так, чтобы вы понимали, что публиковать и как контент должен приводить к заявкам, а не просто занимать часы вашей недели.",
        "image": "https://imgur.com/Ml5QfL7.png"
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
    user_state[user_id] = {"scores": [], "q": 0, "started": False}
    
    welcome_text = """Насколько ваш блог действительно работает на вас?

За 8 вопросов вы поймёте, почему блог даёт именно такой результат сейчас и где теряются клиенты, время и силы.

Тест покажет:

🔎 есть ли у вас понятная система или контент выходит скорее по ситуации;
📈 что уже работает и что можно усилить;
🧩 где именно блог проседает и что мешает получать больше заявок.

В конце вы получите свой результат с расшифровкой и пониманием, что стоит менять в первую очередь.

Займёт около 3 минут.

Приступим?"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👍 Да!", callback_data="start_yes")],
        [InlineKeyboardButton(text="✅ Конечно", callback_data="start_yes")],
        [InlineKeyboardButton(text="🚀 Поехали!", callback_data="start_yes")],
    ])
    
    await message.answer_photo(
        photo="https://imgur.com/bZSzS7z.png",
        caption=welcome_text,
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data.startswith("start_"))
async def start_questions(callback):
    user_id = callback.from_user.id
    
    if user_id not in user_state:
        await callback.answer("Начни тест: /test")
        return
    
    user_state[user_id]["started"] = True
    
    question_data = QUESTIONS[0]
    buttons = []
    for answer_text in question_data["answers"].keys():
        buttons.append([InlineKeyboardButton(text=answer_text, callback_data=f"q0_{answer_text[:20]}")])
    
    await callback.message.answer(
        f"<b>Вопрос 1/8</b>\n\n{question_data['text']}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )
    
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("q"))
async def answer(callback):
    user_id = callback.from_user.id
    
    if user_id not in user_state:
        await callback.answer("Начни тест: /test")
        return
    
    parts = callback.data.split("_", 1)
    q_num = int(parts[0][1:])
    answer_prefix = parts[1]
    
    if q_num < len(user_state[user_id]["scores"]):
        await callback.answer("Ответ уже принят")
        return
    
    question_data = QUESTIONS[q_num]
    answer_text = None
    score = None
    
    for ans, pts in question_data["answers"].items():
        if ans.startswith(answer_prefix):
            answer_text = ans
            score = pts
            break
    
    if score is None:
        await callback.answer("Ошибка")
        return
    
    user_state[user_id]["scores"].append(score)
    
    await callback.message.edit_text(
        f"<b>Вопрос {q_num + 1}/8</b>\n\n{question_data['text']}\n\n✓ Ответ принят",
        parse_mode="HTML",
        reply_markup=None
    )
    
    if q_num + 1 < len(QUESTIONS):
        next_q = q_num + 1
        next_question = QUESTIONS[next_q]
        buttons = []
        for answer_text in next_question["answers"].keys():
            buttons.append([InlineKeyboardButton(text=answer_text, callback_data=f"q{next_q}_{answer_text[:20]}")])
        
        await callback.message.answer(
            f"<b>Вопрос {next_q + 1}/8</b>\n\n{next_question['text']}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
            parse_mode="HTML"
        )
    else:
        await show_result(callback.message, user_id)
    
    await callback.answer()

async def show_result(message, user_id):
    scores = user_state[user_id]["scores"]
    total = sum(scores)
    
    q1_score = scores[0]
    q5_score = scores[4]
    q6_score = scores[5]
    q8_score = scores[7]
    
    if total >= 19 and q1_score >= 2 and q5_score >= 2 and q6_score >= 2 and q8_score >= 2:
        result_key = 1
    elif total >= 13:
        result_key = 2
    elif total >= 7:
        result_key = 3
    else:
        result_key = 4
    
    result = RESULTS[result_key]
    
    result_text = f"<b>{result['title']}</b>\n\n{result['text']}\n\n<b>Что дальше?</b>\nНапишите мне слово <b>ДИАГНОСТИКА</b> @anya_basarab ✉️"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="📞 Написать диагностику", url="https://t.me/anya_basarab?text=ДИАГНОСТИКА")
    ]])
    
    if worksheet:
        try:
            user_name = message.chat.first_name or "User"
            user_username = message.chat.username or "No username"
            worksheet.append_row([
                message.chat.id,
                user_name,
                user_username,
                total,
                result['title'],
                "pending"
            ])
            print(f"✓ Saved: {message.chat.id}, {total}/24, {result['title']}")
        except Exception as e:
            print(f"❌ Error saving: {e}")
    
    await message.answer_photo(
        photo=result["image"],
        caption=result_text,
        reply_markup=keyboard,
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
