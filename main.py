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
    print("GOOGLE SHEETS OK")
except Exception as e:
    print("GOOGLE SHEETS FAILED:", repr(e))

WELCOME_IMAGE = "AgACAgIAAxkBAAPBaoTCHnyJJgPxSjI6BzRtqnAQD4IAAr0eaxtFxilIXzpkA6mpLd4BAAMCAAN5AAM9BA"

QUESTION_EMOJIS = ["🎯", "🤔", "🏖️", "💬", "📌", "📊", "👤", "💰"]

QUESTIONS = [
    {"text": "Вы понимаете, что должно измениться в вашем блоге за 2–3 месяца?", "answers": {"Да, понимаю, к какому результату веду блог": 3, "Есть цели, но чёткого плана нет": 2, "Веду блог по ситуации, без чёткого плана": 1, "Нет, главное — не забрасывать блог": 0}},
    {"text": "Когда приходит время делать контент, кто обычно решает, о чём вы будете говорить?", "answers": {"Этим занимается специалист. Я получаю готовые темы и понимаю, зачем они нужны.": 3, "Мы решаем вместе. Мне предлагают идеи, но я активно участвую в выборе тем.": 2, "В основном я. Кто-то может помогать со съёмкой или публикацией, но темы придумываю я.": 1, "Всё полностью на мне. Нет человека, который занимается контентом — сам(а) придумываю темы, снимаю, пишу и решаю, что публиковать.": 0, "Каждый раз по-разному. Иногда идеи есть заранее, иногда приходится срочно придумывать.": 0}},
    {"text": "Представьте, что на неделю вы выпали из ведения блога. Что произойдёт?", "answers": {"Ничего критичного. Есть план и контент, а помощник знает, что делать.": 3, "Что-то выйдет, но затормозит. Всё равно понадобятся мои решения.": 2, "Скорее всего, всё остановится без моего участия.": 1, "Если я занят(а) — контент ставится на паузу.": 0}},
    {"text": "Если вам помогают с контентом — часто приходится объяснять не только ЧТО, но и ЗАЧЕМ?", "answers": {"Почти никогда. Специалист понимает мои цели и аудиторию, сам предлагает, что делать.": 3, "Иногда. В целом понимаем друг друга, но кое-что приходится объяснять.": 2, "Часто. Приходится объяснять, что важно продвигать и почему.": 1, "Почти постоянно. Без моих объяснений результат получается не тем.": 0, "У меня пока нет специалиста, решения принимаю сам(а).": 1}},
    {"text": "Когда публикуете пост или Reels, понимаете, какую задачу он должен решить?", "answers": {"Да. Понимаю, какой контент привлекает, какой прогревает, а какой приводит к продажам.": 3, "Чаще да, но не у каждого материала есть конкретная задача.": 2, "Скорее нет. Публикую то, что кажется полезным, дальше смотрю, как зайдёт.": 1, "Нет. Главное, чтобы контент выходил.": 0}},
    {"text": "После публикации понимаете, что сработало и что изменить в следующий раз?", "answers": {"Да. Смотрю показатели, понимаю, какие темы и форматы работают.": 3, "Отчасти. Вижу разницу, но не всегда понимаю почему.": 2, "Скорее нет. Смотрю просмотры, но выводов почти не делаю.": 1, "Нет. После публикации не возвращаюсь к анализу, начинаю каждый раз с нуля.": 0, "Почти не смотрю аналитику.": 0}},
    {"text": "Если убрать возраст, пол и профессию — можете чётко описать человека, которого хотите привлечь?", "answers": {"Да. Понимаю его проблемы, запросы и почему ему нужны мои услуги.": 3, "В общих чертах. Примерно представляю, но глубоко не разбирал(а).": 2, "Скорее нет. Знаю общие характеристики, но не понимаю, что у них в голове.": 1, "Нет. Контент рассчитан на широкую аудиторию.": 0, "Особо не думал(а) об этом, надеюсь, нужные люди сами найдутся.": 0}},
    {"text": "Если убрать просмотры и лайки — блог реально помогает получать клиентов и зарабатывать?", "answers": {"Да. Регулярно приходят клиенты, вижу заявки и продажи.": 3, "Отчасти. Заявки бывают, но нестабильно, не понимаю систему.": 2, "Скорее нет. Просмотры есть, но в клиентах почти не отражается.": 1, "Нет. Вкладываю время и силы, но результата не вижу.": 0, "Блог стал ещё одной задачей без ощутимой отдачи.": 0}}
]

RESULTS = {
    1: {
        "title": "📈 Блог уже работает как система",
        "text": "У вас уже есть то, чего нет у многих: вы понимаете, <b>зачем ведёте блог, кого хотите привлекать и какой контент должен давать результат.</b>\n\nНо, скорее всего, вы уже упёрлись в другую точку: блог работает, <b>а расти быстрее не получается</b>. Где-то контент не приводит к нужному действию, где-то теряются потенциальные клиенты, а какие-то действия продолжают забирать ресурсы, хотя почти ничего не дают.\n\n✨ Хорошая новость: вам не нужно перестраивать всё с нуля. Здесь задача уже другая — <b>найти слабые места, убрать лишнее и масштабировать то, что действительно приносит результат.</b>\n\nЕсли хотите понять, <b>где именно сейчас находится ваша точка роста</b>, напишите мне слово «ДИАГНОСТИКА» @anya_basarab ✉️",
        "image": "AgACAgIAAxkBAAPDaoTC9j1zD-DtdE7CWamWzfz0n1gAAsMeaxtFxilIK1hqebOdsSQBAAMCAAN5AAM9BA"
    },
    2: {
        "title": "🔄 Блог работает, но слишком многое держится на вас",
        "text": "У вас уже есть понимание, что блог должен приводить клиентов, а не просто собирать просмотры. Но слишком многое до сих пор <b>зависит лично от вас.</b>\n\nТемы, идеи, согласования, решения, что продвигать и что менять. Пока вы включены, всё движется. Стоит переключиться на работу, клиентов или обычную жизнь, и блог начинает тормозить.\n\nВ итоге вместо того, чтобы помогать вам расти, он становится <b>ещё одной задачей, которую нужно постоянно держать в голове.</b>\n\n✨ Хорошая новость: это можно исправить. Нужно просто выстроить работу так, чтобы блог <b>не зависел от вашего постоянного участия.</b>\n\nЕсли хотите понять, <b>что именно можно снять с вас и как сделать блог более самостоятельным</b>, напишите мне слово «ДИАГНОСТИКА» @anya_basarab ✉️",
        "image": "AgACAgIAAxkBAAPFaoTDUZ6qCSxZ0BxX2J_YaqYfes0AAsUeaxtFxilIlBUPIZTfudsBAAMCAAN5AAM9BA"
    },
    3: {
        "title": "🧩 Контент есть, системы пока нет",
        "text": "Вы ведёте блог, тратите время на идеи, съёмки, тексты, Reels. Иногда что-то хорошо заходит, иногда приходят заявки. Но <b>стабильности в этом нет.</b>\n\nСегодня ролик набрал просмотры, завтра почти никто не увидел. Один месяц из блога приходят клиенты, в другой — тишина. И вы снова садитесь придумывать новый контент, не до конца понимая, <b>что из предыдущего вообще сработало.</b>\n\nВ итоге блог требует постоянного внимания, а вы всё равно не можете уверенно сказать: <b>что именно приводит вам клиентов и что нужно делать, чтобы получать этот результат чаще.</b>\n\n✨ Это можно изменить. Контент можно выстроить так, чтобы у вас была понятная стратегия, темы не приходилось каждый раз высасывать из пальца, а результаты прошлых публикаций подсказывали, что делать дальше.\n\nЕсли хотите понять, <b>где именно сейчас у вас разваливается эта система</b>, напишите мне слово «ДИАГНОСТИКА» @anya_basarab ✉️",
        "image": "AgACAgIAAxkBAAPHaoTDoxSRvefV-Nn_zzt4AZteFf0AAsceaxtFxilIM8pw6w-x_GkBAAMCAAN5AAM9BA"
    },
    4: {
        "title": "😵‍💫 Блог забирает больше, чем даёт",
        "text": "Сейчас блог, скорее всего, ощущается как <b>ещё одна работа поверх основной работы.</b>\n\nНужно придумать тему, снять, написать, выложить, не пропасть из сторис, посмотреть охваты. И всё это постоянно висит в голове. При этом клиентов из блога либо мало, либо они приходят настолько нестабильно, что сложно понять, <b>зачем вы вообще тратите на это столько сил.</b>\n\nВ какой-то момент появляется ощущение:\n<b>«Я всё время что-то делаю для блога, а он почти ничего не даёт мне взамен».</b>\n\nИменно поэтому хочется то резко взяться за контент, то вообще всё бросить.\n\n✨ Это можно изменить. Блог можно выстроить так, чтобы вы понимали, <b>что публиковать, зачем это делать и как контент должен приводить к заявкам</b>, а не просто занимать ещё несколько часов вашей недели.\n\nЕсли хотите понять, <b>с чего начать и что сейчас сильнее всего тормозит ваш блог</b>, напишите мне слово «ДИАГНОСТИКА» @anya_basarab ✉️",
        "image": "AgACAgIAAxkBAAPJaoTEBQ4ZaPCMLKXhQypyt1zs3DQAAsgeaxtFxilImq-gvdN02SIBAAMCAAN5AAM9BA"
    }
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
    user_state[user_id] = {"scores": [], "q": 0, "answers": []}
    txt = "Тест покажет:\n🔎 есть ли у вас система или контент по ситуации;\n📈 что работает и что можно усилить;\n🧩 где именно блог проседает и что мешает получать больше заявок.\n\n<b>8 вопросов — 3 минуты</b>. Узнаете, <b>где теряются клиенты, время и силы</b>.\n\nПриступим?"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="👍 Да!", callback_data="start"), InlineKeyboardButton(text="🚀 Поехали!", callback_data="start")]])
    await message.answer_photo(photo=WELCOME_IMAGE, caption=txt, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(lambda c: c.data == "start")
async def start_test(callback):
    user_id = callback.from_user.id
    if user_id not in user_state:
        return
    q = QUESTIONS[0]
    ans_list = list(q["answers"].keys())
    txt = "<b>" + QUESTION_EMOJIS[0] + " Вопрос 1/8</b>\n\n<b>" + q["text"] + "</b>\n\n"
    for i, a in enumerate(ans_list):
        txt += str(i+1) + "️⃣ " + a + "\n\n"
    buttons = [[InlineKeyboardButton(text=str(i+1)+"️⃣", callback_data=f"a0_{i}")] for i in range(len(ans_list))]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.answer(txt, reply_markup=kb, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("a"))
async def answer(callback):
    user_id = callback.from_user.id
    if user_id not in user_state:
        return
    parts = callback.data.split("_")
    q_num = int(parts[0][1:])
    ans_idx = int(parts[1])
    if q_num < len(user_state[user_id]["scores"]):
        await callback.answer("Ответ уже принят")
        return
    q = QUESTIONS[q_num]
    ans_items = list(q["answers"].items())
    ans_text, score = ans_items[ans_idx]
    user_state[user_id]["scores"].append(score)
    user_state[user_id]["answers"].append(ans_text)
    await callback.message.edit_text("<b>" + QUESTION_EMOJIS[q_num] + " Вопрос "+str(q_num+1)+"/8</b>\n\n<b>"+q["text"]+"</b>\n\n✓ Ваш ответ: "+ans_text, reply_markup=None, parse_mode="HTML")
    if q_num + 1 < 8:
        nq = QUESTIONS[q_num+1]
        ans_list = list(nq["answers"].keys())
        txt = "<b>" + QUESTION_EMOJIS[q_num+1] + " Вопрос "+str(q_num+2)+"/8</b>\n\n<b>" + nq["text"] + "</b>\n\n"
        for i, a in enumerate(ans_list):
            txt += str(i+1) + "️⃣ " + a + "\n\n"
        buttons = [[InlineKeyboardButton(text=str(i+1)+"️⃣", callback_data=f"a{q_num+1}_{i}")] for i in range(len(ans_list))]
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.answer(txt, reply_markup=kb, parse_mode="HTML")
    else:
        await callback.message.answer("⏳ Минуточку, подготавливаю результаты теста для вас...")
        await asyncio.sleep(5)
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
        txt = "<b>" + res["title"] + "</b>\n\n" + res["text"]
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ХОЧУ ДИАГНОСТИКУ", url="https://t.me/anya_basarab?text=ДИАГНОСТИКА")]])
        await callback.message.answer_photo(photo=res["image"], caption=txt, reply_markup=kb, parse_mode="HTML")
        if worksheet:
            try:
                username = callback.from_user.username
                username_display = "@" + username if username else "нет username"
                worksheet.append_row([callback.from_user.id, callback.from_user.first_name or "User", username_display, total, res["title"]])
                print("SAVED TO SHEETS OK")
            except Exception as e:
                print("SAVE TO SHEETS FAILED:", repr(e))
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
