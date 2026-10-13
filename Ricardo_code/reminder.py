import time
from datetime import datetime

import jdatetime

from telegram import Update
from telegram.ext import ContextTypes

import sql as db
import ai as AI
import history
from logger import reminder_log


async def time_convert(time: str):
    gregorian_date = datetime.strptime(time[9::], "%Y/%m/%d").date()

    jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)

    temp = jalali_date.strftime("%Y-%m-%d")
    result = ""

    result += temp[8::] + " / " + temp[5:7:] + " / " + temp[:4:]
    result = time[:8:] + " " + result
    return result


async def send_reminder(context: ContextTypes.DEFAULT_TYPE):

    job = context.job
    remind = db.Reminder()
    my_reminder = remind.find(job.data["id_db_reminders"])

    if my_reminder[0]["status"] == 0:
        text = f"⏰ یادآوری: \n{my_reminder[0]["text"]}"

        now_time = time.strftime("%H:%M:%S %Y/%m/%d")
        await context.bot.send_message(
            chat_id=job.data["chat_id"],
            text=text,
        )

        # add to history
        await history.set_history(
            userId=my_reminder[0]["user_id"],
            messageId=await history.get_last_message_id(
                user_id=my_reminder[0]["user_id"]
            )
            + 1,
            messageText=text,
            timeRequest=now_time,
            whoSent=0,
        )


async def add_new_reminder(
    user, user_text, data, update: Update, context: ContextTypes.DEFAULT_TYPE
):
    try:
        reminder_log.log("INFO", "add new reminder")
        chat_id = update.effective_chat.id
        remind = db.Reminder()
        remind.insert(userId=user[0]["id"], orgText=user_text, data=data)

        reminders = remind.viewRemainder(user[0]["id"], data["timeRequest"])

        dt = datetime.strptime(data["time"], "%H:%M:%S %Y/%m/%d")
        dateTime = dt - datetime.now()

        if dateTime.total_seconds() > 0:
            context.job_queue.run_once(
                send_reminder,
                when=dateTime.total_seconds(),
                data={"chat_id": chat_id, "id_db_reminders": reminders[-1]["id"]},
            )

            text = f"در تاریخ و ساعت {await time_convert(data["time"])} به شما متن زیر برای یادآوری ارسال می‌شود.\n\n{data["text"]}"

            now_time = time.strftime("%H:%M:%S %Y/%m/%d")
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
            )

            # add to history
            await history.set_history(
                userId=user[0]["id"],
                messageId=await history.get_last_message_id(user_id=user[0]["id"]) + 1,
                messageText=text,
                timeRequest=now_time,
                whoSent=0,
            )
        else:
            text = "زمانی که خواستید گذشته است."

            now_time = time.strftime("%H:%M:%S %Y/%m/%d")
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
            )

            # add to history
            await history.set_history(
                userId=user[0]["id"],
                messageId=await history.get_last_message_id(user_id=user[0]["id"]) + 1,
                messageText=text,
                timeRequest=now_time,
                whoSent=0,
            )
    except Exception as err:
        reminder_log.log("ERROR", f"add new reminder: {err}")


async def show_remaining_reminder(
    user, now_time, update: Update, context: ContextTypes.DEFAULT_TYPE
):
    try:
        reminder_log.log("INFO", "show remaining reminder")
        chat_id = update.effective_chat.id
        remind = db.Reminder()
        reminders = remind.viewRemainder(user[0]["id"], now_time)

        if len(reminders) == 0:
            text = "شما در حال حاضر در لیست یادآوری هایتان موردی ندارید."

            now_time = time.strftime("%H:%M:%S %Y/%m/%d")
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_to_message_id=update.effective_message.id,
            )

            # add to history
            await history.set_history(
                userId=user[0]["id"],
                messageId=await history.get_last_message_id(user_id=user[0]["id"]) + 1,
                messageText=text,
                timeRequest=now_time,
                whoSent=0,
            )

        else:
            out_str = "لیست یادآوری های شما : \n\n"

            i = 1
            for r in reminders:
                out_str += (
                    f"{i}. {r["text"]} - زمان : {await time_convert(r["time"])}\n"
                )
                i += 1

            now_time = time.strftime("%H:%M:%S %Y/%m/%d")
            await context.bot.send_message(
                chat_id=chat_id,
                text=out_str,
                reply_to_message_id=update.effective_message.id,
            )

            # add to history
            await history.set_history(
                userId=user[0]["id"],
                messageId=await history.get_last_message_id(user_id=user[0]["id"]) + 1,
                messageText=out_str,
                timeRequest=now_time,
                whoSent=0,
            )
    except Exception as err:
        reminder_log.log("ERROR", f"show remaining reminder: {err}")


async def cancel_reminder(
    user, user_text, now_time, update: Update, context: ContextTypes.DEFAULT_TYPE
):
    try:
        reminder_log.log("INFO", "cancel reminder")
        chat_id = update.effective_chat.id
        remind = db.Reminder()
        reminders = remind.viewRemainder(user[0]["id"], now_time)

        out_str = ""
        i = 1
        for r in reminders:
            out_str += f"{i}. {r["text"]} - زمان : {r["time"]}\n"
            i += 1

        static_text = f"""شما یک مدل پردازش زبان طبیعی هستید. ورودی شما دو پارامتر است:
    1. text: یک رشته متن که کاربر نوشته.
    2. options: یک لیست از جملات که هر کدام با شمارهٔ ترتیبی (از 1 به بعد) مشخص شده‌اند.

    وظیفهٔ شما این است که:
    - بررسی کنید متنِ ورودی (text) به کدام یک از گزینه‌های موجود در لیست options اشاره یا مرتبط است.
    - عدد آن گزینه را به صورت یک رشته در فیلد "op" خروجی JSON قرار دهید.

    اگر متن صریحاً گفته باشد «مورد اول»، «اول»، «شماره یک» و …، عدد «1» را انتخاب کنید.  
    اگر به صورت ضمنی اشاره داشته باشد، بر اساس بیشترین شباهت معنایی تصمیم بگیرید.

    **خروجی باید دقیقاً به شکل زیر باشد (بدون توضیحات اضافی):**
    ```json
    {{
    "op": "X"
    }}

    text: {user_text}
    options:
    {out_str}

    """

        temp_ai = AI.AIGemini()
        data = temp_ai.analysis(f"{static_text}")

        option = int(data["op"])

        if option - 1 < len(reminders):
            remind.update(reminders[option - 1]["id"], "status")
        else:
            text = """یادآوری‌ای که می‌خواهید لغو شود یا در لیست یادآوری‌هایتان نیست یا قابل تشخیص نبود.
    لطفا مورد مدنظرتان را واضح‌تر بگید.
    لیست یادآوری‌های شما به صورت زیر است.
    """

            now_time = time.strftime("%H:%M:%S %Y/%m/%d")
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_to_message_id=update.effective_message.id,
            )

            # add to history
            await history.set_history(
                userId=user[0]["id"],
                messageId=await history.get_last_message_id(user_id=user[0]["id"]) + 1,
                messageText=text,
                timeRequest=now_time,
                whoSent=0,
            )
    except Exception as err:
        reminder_log.log("ERROR", f"cancel reminder: {err}")


async def change_time_reminder(
    user, user_text, now_time, data, update: Update, context: ContextTypes.DEFAULT_TYPE
):
    try:
        reminder_log.log("INFO", "change time reminder")
        chat_id = update.effective_chat.id
        remind = db.Reminder()
        reminders = remind.viewRemainder(user[0]["id"], now_time)

        out_str = ""
        i = 1
        for r in reminders:
            out_str += f"{i}. {r["text"]} - زمان : {r["time"]}\n"
            i += 1

        static_text = f"""شما یک مدل پردازش زبان طبیعی هستید. ورودی شما دو پارامتر است:
    1. text: یک رشته متن که کاربر نوشته.
    2. options: یک لیست از جملات که هر کدام با شمارهٔ ترتیبی (از 1 به بعد) مشخص شده‌اند.

    وظیفهٔ شما این است که:
    - بررسی کنید متنِ ورودی (text) به کدام یک از گزینه‌های موجود در لیست options اشاره یا مرتبط است.
    - عدد آن گزینه را به صورت یک رشته در فیلد "op" خروجی JSON قرار دهید.

    اگر متن صریحاً گفته باشد «مورد اول»، «اول»، «شماره یک» و …، عدد «1» را انتخاب کنید.  
    اگر به صورت ضمنی اشاره داشته باشد، بر اساس بیشترین شباهت معنایی تصمیم بگیرید.

    **خروجی باید دقیقاً به شکل زیر باشد (بدون توضیحات اضافی):**
    ```json
    {{
    "op": "X"
    }}

    text: {user_text}
    options:
    {out_str}

    """

        temp_ai = AI.AIGemini()
        data_op = temp_ai.analysis(f"{static_text}")

        option = int(data_op["op"])

        if option - 1 < len(reminders):
            data["text"] = reminders[option - 1]["text"]
            remind.update(reminders[option - 1]["id"], "status")
            await add_new_reminder(user, user_text, data, update, context)
        else:
            text = """یادآوری‌ای که می‌خواهید زمانش را تغییر دهید، یا در لیست یادآوری‌هایتان نیست یا قابل تشخیص نبود.
    لطفا موردی که مدنظرتان است را واضح‌تر بگید.
    لیست یادآوری‌های شما به صورت زیر است.
    """

            now_time = time.strftime("%H:%M:%S %Y/%m/%d")
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_to_message_id=update.effective_message.id,
            )

            # add to history
            await history.set_history(
                userId=user[0]["id"],
                messageId=await history.get_last_message_id(user_id=user[0]["id"]) + 1,
                messageText=text,
                timeRequest=now_time,
                whoSent=0,
            )
    except Exception as err:
        reminder_log.log("ERROR", f"change time reminder: {err}")
