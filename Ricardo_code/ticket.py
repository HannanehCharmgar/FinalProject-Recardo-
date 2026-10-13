import requests
import jdatetime
import time
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

import sql as db
import ai as AI
import history
from logger import ticket_log


class Ticket:
    cities = {
        "Tehran": "THR",
        "Mashhad": "MHD",
        "Shiraz": "SYZ",
        "Isfahan": "IFN",
        "Tabriz": "TBZ",
        "Ahvaz": "AWZ",
        "Bandar Abbas": "BND",
        "Kish": "KIH",
        "Qeshm": "GSM",
        "Rasht": "RAS",
        "Sari": "SRY",
        "Ardabil": "ADU",
        "Zahedan": "ZAH",
        "Abadan": "ABD",
        "Birjand": "XBJ",
        "Bojnord": "BJB",
        "Bushehr": "BUZ",
        "Gorgan": "GBT",
        "Hamadan": "HMD",
        "Ilam": "IIL",
        "Kerman": "KER",
        "Kermanshah": "KSH",
        "Lar": "LRR",
        "Mahshahr": "MRX",
        "Ramsar": "RZR",
        "Sanandaj": "SDG",
        "Shahrekord": "CQD",
        "Sirjan": "SYJ",
        "Tabas": "TCX",
        "Urmia": "OMH",
        "Yazd": "AZD",
        "Zanjan": "JWN",
    }

    def __init__(self):
        pass

    def flight(self, mabda, maghsad, date=""):
        try:
            ticket_log.log("INFO", "start the request for get flight ticket")
            response = requests.get(
                f"https://safarmarket.com/api/flight/v3/calendar?org={self.cities[mabda]}&orgCity=true&dst={self.cities[maghsad]}&dstCity=true&dom=true"
            )

            res = response.json()
            if "cal" in res.keys():
                if date == "":
                    data = res["cal"]
                    return data, True
                else:
                    if date in res["cal"].keys():
                        data = res["cal"][date]
                        return data, True
                    else:
                        return {}, True
            else:
                return {}, True
        except Exception as err:
            ticket_log.log("ERROR", f"get flight ticket by api: {err}")
            return {}, False


async def time_convert(miladi_date):
    try:
        ticket_log.log("INFO", "time converting ... ")
        gregorian_date = datetime.strptime(miladi_date, "%Y-%m-%d").date()

        jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)

        temp = jalali_date.strftime("%Y-%m-%d")
        result = ""

        result += temp[8::] + " / " + temp[5:7:] + " / " + temp[:4:]
        return result
    except Exception as err:
        ticket_log.log("ERROR", f"time converting: {err}")
        return ""


async def price_formate(price):
    try:
        ticket_log.log("INFO", "price formate")
        price_str = str(price)

        i = len(price_str) % 3
        if i == 0:
            i = 3
        while i < len(price_str):
            price_str = price_str[:i:] + "," + price_str[i::]
            i += 4

        return price_str
    except Exception as err:
        ticket_log.log("ERROR", f"price formate: {err}")


async def show_ticket(
    user, user_text, update: Update, context: ContextTypes.DEFAULT_TYPE
):
    try:
        ticket_log.log("INFO", "show ticket")
        chat_id = update.effective_chat.id

        cities = [
            "Tehran",
            "Mashhad",
            "Shiraz",
            "Isfahan",
            "Tabriz",
            "Ahvaz",
            "Bandar Abbas",
            "Kish",
            "Qeshm",
            "Rasht",
            "Sari",
            "Ardabil",
            "Zahedan",
            "Abadan",
            "Birjand",
            "Bojnord",
            "Bushehr",
            "Gorgan",
            "Hamadan",
            "Ilam",
            "Kerman",
            "Kermanshah",
            "Lar",
            "Mahshahr",
            "Ramsar",
            "Sanandaj",
            "Shahrekord",
            "Sirjan",
            "Tabas",
            "Urmia",
            "Yazd",
            "Zanjan",
        ]

        cities_persian = {
            "Tehran": "تهران",
            "Mashhad": "مشهد",
            "Shiraz": "شیراز",
            "Isfahan": "اصفهان",
            "Tabriz": "تبریز",
            "Ahvaz": "اهواز",
            "Bandar Abbas": "بندرعباس",
            "Kish": "کیش",
            "Qeshm": "قشم",
            "Rasht": "رشت",
            "Sari": "ساری",
            "Ardabil": "اردبیل",
            "Zahedan": "زاهدان",
            "Abadan": "آبادان",
            "Birjand": "بیرجند",
            "Bojnord": "بجنورد",
            "Bushehr": "بوشهر",
            "Gorgan": "گرگان",
            "Hamadan": "همدان",
            "Ilam": "ایلام",
            "Kerman": "کرمان",
            "Kermanshah": "کرمانشاه",
            "Lar": "لار",
            "Mahshahr": "ماهشهر",
            "Ramsar": "رامسر",
            "Sanandaj": "سنندج",
            "Shahrekord": "شهرکرد",
            "Sirjan": "سیرجان",
            "Tabas": "طبس",
            "Urmia": "ارومیه",
            "Yazd": "یزد",
            "Zanjan": "زنجان",
        }

        now_time = time.strftime("%H:%M:%S %Y/%m/%d")

        text = f"""متنی که بهت دادم رو پردازش کن و ببین که برای بلیط هواپیما از چه شهری به چه شهری را برای چه زمانی را میخواد و در آخر به من یک فرمت json بده که شامل کلید و مقدار های زیر است :
    کلید "org" : مقدار این کلید را برابر شهر مبدا بذار و فقط قبلش توی لیست شهرهای زیر که گذاشتم ببین که هست یا نه و اگر بود همون طوری که در لیست شهرها بود برای مقدار این کلید بذار و اگر قابل تشخیص نبود مقدارش را "not found" بذار.
    لیست شهر ها به صورت رو به رو است: {str(cities)}

    کلید "dst" : مقدار این کلید را برابر شهر مقصد بذار و فقط قبلش توی لیست شهرهای زیر که گذاشتم ببین که هست یا نه و اگر بود همون طوری که در لیست شهرها بود برای مقدار این کلید بذار و اگر قابل تشخیص نبود مقدارش را "not found" بذار.
    لیست شهر ها به صورت رو به رو است: {str(cities)}

    کلید "date" : تاریخی که برای بلیط میخواد رو برای این کلید بذار و فقط اینکه اولا به صورت رشته یعنی داخل دابل کوتیشن بذار و به فرمت "yyyy-mm-dd" که به میلادی است بذار. اگر برای مثال گفته بود فردا، تاریخ آن را محاسبه کن و قرار بده و اگر تاریخ عجیبی گفت باز هم محاسبه کن و قرار بده. اگر قابل تشخیص نبود مقدارش را "not found" بذار. زمان حال {now_time} است.

    متن : '{user_text}'
    """
        ai = AI.AIGemini()
        data = ai.analysis(text)
        ti = Ticket()

        while not (
            "org" in data.keys() or "dst" in data.keys() or "date" in data.keys()
        ):
            data = ai.analysis(text)

        if data["org"] != "not found" and data["dst"] != "not found":
            if data["date"] == "not found":
                result_tickets, status = ti.flight(data["org"], data["dst"])

                if status == True:
                    text = f"بلیط های هواپیما موجود از {cities_persian[data["org"]]} به {cities_persian[data["dst"]]} به صورت زیر است: \n"
                    i = 1
                    for key in result_tickets.keys():
                        if i == 11:
                            break
                        i += 1
                        text += f"- تاریخ {await time_convert(key)} :\n\t"
                        if (
                            result_tickets[key]["minPrice"] == None
                            or result_tickets[key]["maxPrice"] == None
                        ):
                            text += "-- بلیطی برای این تاریخ وچود ندارد.\n"
                        else:
                            text += f"-- کمترین قیمت: {await price_formate(result_tickets[key]["minPrice"])} ریال\n\t-- بیشترین قیمت: {await price_formate(result_tickets[key]["maxPrice"])} ریال\n\t"

                    now_time = time.strftime("%H:%M:%S %Y/%m/%d")
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=text,
                    )

                    # add to history
                    await history.set_history(
                        userId=user[0]["id"],
                        messageId=await history.get_last_message_id(
                            user_id=user[0]["id"]
                        )
                        + 1,
                        messageText=text,
                        timeRequest=now_time,
                        whoSent=0,
                    )

                else:
                    text = f"بلیط هواپیما از {cities_persian[data["org"]]} به {cities_persian[data["dst"]]} وجود ندارد."

                    now_time = time.strftime("%H:%M:%S %Y/%m/%d")
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=text,
                    )

                    # add to history
                    await history.set_history(
                        userId=user[0]["id"],
                        messageId=await history.get_last_message_id(
                            user_id=user[0]["id"]
                        )
                        + 1,
                        messageText=text,
                        timeRequest=now_time,
                        whoSent=0,
                    )
            else:
                result_ticket, status = ti.flight(
                    data["org"], data["dst"], data["date"]
                )

                if (
                    status == True
                    and result_ticket["minPrice"] != None
                    and result_ticket["maxPrice"] != None
                ):
                    text = f"بلیط هوایپیما از {cities_persian[data["org"]]} به {cities_persian[data["dst"]]} در تاریخ {await time_convert(data["date"])} به صورت زیر است: \n\t- کمترین قیمت: {await price_formate(result_ticket["minPrice"])} ریال\n\t- بیشترین قیمت: {await price_formate(result_ticket["maxPrice"])} ریال"

                    now_time = time.strftime("%H:%M:%S %Y/%m/%d")
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=text,
                    )

                    # add to history
                    await history.set_history(
                        userId=user[0]["id"],
                        messageId=await history.get_last_message_id(
                            user_id=user[0]["id"]
                        )
                        + 1,
                        messageText=text,
                        timeRequest=now_time,
                        whoSent=0,
                    )
                else:
                    text = f"بلیطی برای از {cities_persian[data["org"]]} به {cities_persian[data["dst"]]} در تاریخ {await time_convert(data["date"])} وجود ندارد."

                    now_time = time.strftime("%H:%M:%S %Y/%m/%d")
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=text,
                    )

                    # add to history
                    await history.set_history(
                        userId=user[0]["id"],
                        messageId=await history.get_last_message_id(
                            user_id=user[0]["id"]
                        )
                        + 1,
                        messageText=text,
                        timeRequest=now_time,
                        whoSent=0,
                    )
        else:
            text = """این ربات در حال حاضر درخواست شما را نمی‌تواند انجام دهد یا درخواستتان واضح گفته نشده است.
    متن زیر قابلیت‌هایی است که ربات می‌تواند انجام دهد.
    لطفا طبق این قابلیت‌ها درخواست کنید.
    """
            now_time = time.strftime("%H:%M:%S %Y/%m/%d")
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
            )

            # add to history
            await history.set_history(
                userId=user[0]["id"],
                messageId=await history.get_last_message_id(user[0]["id"]) + 1,
                messageText=text,
                timeRequest=now_time,
                whoSent=0,
            )

            await help(update, context)
    except Exception as err:
        ticket_log.log("ERROR", f"show ticket: {err}")
