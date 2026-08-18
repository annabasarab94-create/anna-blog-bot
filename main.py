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
    creds = Credentials.from_service_account_info(creds_dict, scopes=['https://www.googleapis.com/auth/spreadsheets'])
    gc = gspread.authorize(creds)
    worksheet = gc.open_by_key(GOOGLE_SHEET_ID).sheet1
except:
    pass

QUESTIONS = [
    {"text": "Если я спрошу вас, что должно измениться в вашем блоге за ближайшие 2–3 месяца, вы сможете ответить конкретно?", "answers": {"Да. Я понимаю, к какому результату веду блог": 3, "Примерно. Есть цели и идеи": 2, "Не особо. Веду блог по ситуации": 1, "Если честно, нет": 0}},
    {"text": "Когда приходит время делать контент, кто обычно решает, о чём вы будете говорить?", "answers": {"Этим занимается специалист": 3, "Мы решаем вместе": 2, "В основном я": 1, "Всё полностью на мне": 0, "Каждый раз по-разному": 0}},
    {"text": "Представьте, что на неделю вы полностью выпали из ведения блога. Что с ним произойдёт?", "answers": {"Ничего критичного": 3, "Что-то продолжит выходить, но процесс начнёт тормозить": 2, "Скорее всего, всё остановится": 1, "Блог и так полностью на мне": 0}},
    {"text": "Если вам кто-то помогает с контентом, насколько часто приходится объяснять не только ЧТО сделать, но и ЗАЧЕМ?", "answers": {"Почти никогда": 3, "Иногда": 2, "Часто": 1, "Почти постоянно": 0, "У меня пока нет специалиста": 1}},
    {"text": "Когда вы публикуете пост или Reels, вы обычно понимаете, какую задачу он должен решить?", "answers": {"Да. Я понимаю, какой контент должен привлекать": 3, "Чаще да. Обычно понимаю общую цель": 2, "Скорее нет. Публикую то, что кажется полезным": 1, "Нет. Главное, чтобы контент выходил": 0}},
    {"text": "После публикации вы понимаете, что в контенте сработало и что стоит изменить?", "answers": {"Да. Я смотрю результаты и понимаю": 3, "Отчасти. Вижу, что один контент заходит лучше": 2, "Скорее нет. Обычно смотрю просмотры, но выводов не делаю": 1, "Нет. Опубликовал и пошёл дальше": 0, "Я почти не смотрю аналитику": 0}},
    {"text": "Если убрать возраст, пол и профессию, вы можете чётко описать человека, которого хотите привлечь?", "answers": {"Да. Я понимаю, что это за человек": 3, "В общих чертах. Примерно представляю": 2, "Скорее нет. Могу назвать характеристики": 1, "Нет. Контент рассчитан на широкую аудиторию": 0, "Я об этом особо не думал": 0}},
    {"text": "Если убрать просмотры, лайки и подписчиков, блог реально помогает вам получать клиентов?", "answers": {"Да. Из блога регулярно приходят клиенты": 3, "Отчасти. Заявки бывают, но нестабильно": 2, "Скорее нет. Контент выходит, но в клиентах не отражается": 1, "Нет. Я вкладываю много, но результата не вижу": 0, "Сейчас блог скорее стал ещё одной задачей": 0}}
]

RESULTS = {
    1: {"title": "📈 Блог уже работает как система", "text": "У вас уже есть понимание, зачем вы ведёте блог. Вы знаете, кого привлекать и какой контент должен давать результат.\n\nНо блог работает, а расти быстрее не получается. Где-то контент не приводит к нужному действию, теряются клиенты.\n\n✨ Вам не нужно перестраивать всё. Найти слабые места, убрать лишнее и масштабировать то, что работает.\n\nНапишите мне ДИАГНОСТИКА @anya_basarab"},
    2: {"title": "🔄 Блог работает, но слишком многое держится на вас", "text": "Вы понимаете, что блог должен приводить клиентов. Но слишком многое зависит лично от вас.\n\nТемы, идеи, согласования. Пока вы включены, всё движется. Стоит переключиться, и блог тормозит.\n\n✨ Это можно исправить. Выстроить работу так, чтобы блог не зависел от вашего постоянного участия.\n\nНапишите мне ДИАГНОСТИКА @anya_basarab"},
    3: {"title": "🧩 Контент есть, системы пока нет", "text": "Вы ведёте блог, тратите время на идеи. Иногда что-то заходит, иногда нет. Стабильности нет.\n\nСегодня просмотры, завтра тишина. Снова придумываете контент, не понимая, что сработало.\n\n✨ Контент можно выстроить так, чтобы была система и результаты подсказывали, что делать дальше.\n\nНапишите мне ДИАГНОСТИКА @anya_basarab"},
    4: {"title": "😵‍💫 Блог забирает больше, чем даёт", "text": "Блог ощущается как ещё одна работа. Придумать, снять, написать, выложить.\n\nВсё висит в голове. Клиентов либо мало, либо приходят нестабильно.\n\nВы всё время что-то делаете, а блог почти ничего не даёт.\n\n✨ Блог можно выстроить так, чтобы вы понимали, что публиковать и как контент приводит к заявкам.\n\nНапишите мне ДИАГНОСТИКА @anya_basarab"}
}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_state = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("👋 Привет! Начни тест: /test")

@dp.message(Command("test"))
async def test(message: types.Message):
    user_id = message.from_user.id
    user_state[user_id] = {"scores": [], "q": 0}
    
    txt = "Насколько ваш блог действительно работает на вас?\n\nЗа 8 вопросов вы поймёте результат и где теряются клиенты.\n\nТест покажет:\n🔎 есть ли система\n📈 что работает\n🧩 где проседает\n\nПриступим?"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="👍 Да!", callback_data="start"), InlineKeyboardButton(text="🚀 Поехали!", callback_data="start")]])
    await message.answer(txt, reply_markup=kb)

@dp.callback_query(lambda c: c.data == "start")
async def start_test(callback):
    user_id = callback.from_user.id
    if user_id not in user_state:
        return
    
    q = QUESTIONS[0]
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=ans, callback_data=f"a0_{ans[:15]}")] for ans in q["answers"]])
    await callback.message.answer(f"<b>Вопрос 1/8</b>\n\n{q['text']}", reply_markup=kb, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("a"))
async def answer(callback):
    user_id = callback.from_user.id
    if user_id not in user_state:
        return
    
    parts = callback.data.split("_", 1)
    q_num = int(parts[0][1:])
    ans_prefix = parts[1]
    
    if q_num < len(user_state[user_id]["scores"]):
        await callback.answer("Ответ уже принят")
        return
    
    q = QUESTIONS[q_num]
    score = None
    for ans, pts in q["answers"].items():
        if ans.startswith(ans_prefix):
            score = pts
            break
    
    if score is None:
        return
    
    user_state[user_id]["scores"].append(score)
    await callback.message.edit_text(f"<b>Вопрос {q_num + 1}/8</b>\n\n{q['text']}\n\n✓", parse_mode="HTML", reply_markup=None)
    
    if q_num + 1 < 8:
        nq = QUESTIONS[q_num + 1]
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=ans, callback_data=f"a{q_num+1}_{ans[:15]}")] for ans in nq["answers"]])
        await callback.message.answer(f"<b>Вопрос {q_num + 2}/8</b>\n\n{nq['text']}", reply_markup=kb, parse_mode="HTML")
    else:
        total = sum(user_state[user_id]["scores"])
        q1, q5, q6, q8 = user_state[user_id]["scores"][0], user_state[user_id]["scores"][4], user_state[user_id]["scores"][5], user_state[user_id]["scores"][7]
        
        if total >= 19 and q1 >= 2 and q5 >= 2 and q6 >= 2 and q8 >= 2:
            res = RESULTS[1]
        elif total >= 13:
            res = RESULTS[2]
        elif total >= 7:
            res = RESULTS[3]
        else:
            res = RESULTS[4]
        
        txt = f"<b>{res['title']}</b>\n\n{res['text']}"
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Написать диагностику", url="https://t.me/anya_basarab?text=ДИАГНОСТИКА")]])
        await callback.message.answer(txt, reply_markup=kb, parse_mode="HTML")
        
        if worksheet:
            try:
                worksheet.append_row([callback.from_user.id, callback.from_user.first_name or "User", total, res['title']])
            except:
                pass
    
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
