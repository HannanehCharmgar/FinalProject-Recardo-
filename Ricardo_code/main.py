import time
from datetime import datetime
from decouple import config

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import sql as db
import ai as AI
import todolist as ToDo
import reminder as Remind
import history
import ticket
import mail
from logger import main_log


TK = config("TOKEN_BOT_TELEGRAM")
robot_name = config("ROBOT_NAME")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # explanation of capabilities:
    #   1. reminder
    #   2. todo list
    #   3. sending email
    try:
        main_log.log("INFO", "send the start command")
        chat_id = update.effective_chat.id
        now_time = time.strftime("%H:%M:%S %Y/%m/%d")

        acc = db.Account()
        user = acc.find(chat_id)

        if len(user) == 0:
            fullname = update.effective_chat.full_name
            acc.insert(telegramId=chat_id, name=fullname)

            user = acc.find(chat_id)

            # add to history
            await history.set_history(
                userId=user[0]["id"],
                messageId=update.effective_message.id,
                messageText=update.effective_message.text,
                timeRequest=now_time,
                whoSent=1,
            )

            text = f"""سلام {fullname} عزیز
    به بات {robot_name} خوش آمدید.
    برای دیدن توضیحات بات، /help را ارسال کنید.
    """
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
            fullname = update.effective_chat.full_name

            if fullname != user[0]["name"]:
                acc.update(id=user[0]["id"], name=fullname, email=user[0]["email"])
                user = acc.find(telegramId=chat_id)

            # add to history
            await history.set_history(
                userId=user[0]["id"],
                messageId=update.effective_message.id,
                messageText=update.effective_message.text,
                timeRequest=now_time,
                whoSent=1,
            )

            text = f"""سلام مجدد {user[0]["name"]} عزیز
    به بات {robot_name} خوش آمدید.

    چه کاری برات انجام بدم؟
    در صورتی که نیاز داری توضیحات بات ارسال شود، /help را ارسال کن.
    """

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
        main_log.log("ERROR", f"start command: {err}")


async def process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        main_log.log("INFO", "Start the proccessing .... ")
        chat_id = update.effective_chat.id
        user_text = update.effective_message.text

        acc = db.Account()
        user = acc.find(telegramId=chat_id)

        now_time = time.strftime("%H:%M:%S %Y/%m/%d")
        # add to history
        await history.set_history(
            userId=user[0]["id"],
            messageId=update.effective_message.id,
            messageText=update.effective_message.text,
            timeRequest=now_time,
            whoSent=1,
        )

        static_text = f"""شما یک مدل پردازش زبان طبیعی هستید. وظیفه‌ی شما تحلیل یک متن است تا مشخص شود کاربر به چه چیزی اشاره دارد و نتیجه را در قالب یک JSON برگردانید.

    📌 نکات مهم:
    - تمام کلیدها و مقدارها در خروجی JSON باید رشته (string) باشند و داخل دابل کوتیشن `""` قرار گیرند، حتی اگر مقدار عدد یا زمان باشد.
    - خروجی فقط باید شامل همان JSON باشد، هیچ توضیح یا متن اضافی ننویسید.

    ---

    ## ساختار تصمیم‌گیری:

    ### 1. ابتدا مشخص کنید که موضوع متن زیر در کدام یک از سه دسته‌ی زیر قرار می‌گیرد و مقدار کلید "category" را برابر یکی از آن‌ها قرار دهید:
    - اگر مربوط به ایمیل بود → `"category": "email"`
    - اگر مربوط بلیط بود و درباره ی بلیطی میخواست → `"category": "ticket"`
    - اگر مربوط به کارهای روزمره و لیست کارها بود → `"category": "todolist"`
    - اگر مربوط به یادآوری کردن، یادآورها یا زمان‌بندی برای انجام کاری بود → `"category": "reminder"`

    ---

    ## ادامه‌ی ساختار بسته به مقدار "category":

    ### اگر `"category": "todolist"` بود:

    در این صورت باید سه کلید دیگر در خروجی وجود داشته باشد:

    - `"work"`: یکی از مقادیر زیر را بگذار:
    - `"add"` ← اگر کاربر خواست کاری به لیست اضافه کند
    - `"show todolist"` ← اگر خواست لیست را ببیند
    - `"doing today"` ← اگر خواست کاری را برای امروز انجام دهد
    - `"remove"` ← اگر خواست کاری را از لیست حذف کند یا انجام شده تلقی شود
    - `"not found"` ← اگر هیچ‌کدام قابل تشخیص نبودند

    - `"text"`: متن خلاصه‌ای از کاری که کاربر قصد انجام آن را دارد (در قالب رشته)

    ---

    ### اگر `"category": "reminder"` بود:

    در این صورت چهار کلید زیر را باید در خروجی قرار دهید:

    - `"work"`: یکی از مقادیر زیر را بگذار:
    - `"add"` ← اگر خواست چیزی بهش یادآوری شود
    - `"show reminders"` ← اگر خواست لیست یادآورها را ببیند
    - `"change time"` ← اگر خواست زمان یادآوری را تغییر دهد
    - `"remove"` ← اگر خواست یادآوری‌ای را حذف کند
    - `"not found"` ← اگر هیچ‌کدام قابل تشخیص نبودند

    - `"text"`: متن مربوط به چیزی که باید یادآوری شود (در قالب رشته)

    - `"type"`: اگر خواست در زمان خاصی یادآوری شود مقدار را `"in time"` بگذار  
    اگر گفت بعداً یا در چند دقیقه یا ساعت آینده یادآوری شود مقدار را `"later"` بگذار  
    اگر مشخص نبود مقدار را `"not found"` بگذار

    - `"time"`:  
    - اگر `"type"` برابر `"later"` بود، زمان یادآوری را به فرمت `"00:00:00 0000/00/00"` بده  
    - اگر `"type"` برابر `"in time"` بود، زمان درخواست‌شده را به همین فرمت بده  
    - اگر زمان قابل تشخیص نبود مقدار را `"not found"` قرار بده  
    - توجه: زمان فعلی سیستم برابر با `{now_time}` است

    ---

    ### اگر `"category": "email"` بود:

    در این صورت باید دو کلید زیر در خروجی قرار گیرد:

    - `"work"`: مقدار برابر باشد با:
    - `"send email"` ← اگر خواست ایمیلی ارسال شود
    - `"not found"` ← اگر قابل تشخیص نبود

    - `"subject"`: عنوان ایمیل را از متن استخراج کن و به صورت رشته بنویس ولی اگر قابل تشخیص نبود مقدار `"not found"` بذار

    - `"text"`: یک متن ایمیل تولید کن که شامل خواسته‌ی کاربر باشد و آن را با تگ‌های HTML مثل `<p>`, `<strong>`, `<br>` و ... فرمت‌دهی کن. سپس متن را به عنوان مقدار این کلید و داخل دابل کوتیشن قرار بده. اگر متن ایمیل گفته نشده بود و نبود مقدار `"not found"` بذار

    ---

    ### اگر `"category": "ticket"` بود:

    در این صورت باید دو کلید زیر در خروجی قرار گیرد:

    - `"target"`: مقدار برابر باشد با:
    - `"flight"` ← اگر مربوط به پروازها و هواپیماها بود
    - `"not found"` ← اگر قابل تشخیص نبود

    - `"work"`: مقدار برابر باشد با:
    - `"show tickets"` ← اگر خواست که بلیط ها رو ببینه
    - `"not found"` ← اگر قابل تشخیص نبود

    ---

    ## ⚠️ مهم:

    **فقط خروجی JSON تولید کن، بدون هیچ متن دیگر. تمام کلیدها و مقدارها داخل دابل کوتیشن `""` باشند.**

    ## مثال ورودی:
    متن: "یادآوری کن که ساعت ۷ شب به مامان زنگ بزنم"
    زمان فعلی: 12:30:00 2025/05/30


    ## مثال خروجی:

    ```json
    {{
    "category": "reminder",
    "work": "add",
    "text": "زنگ زدن به مامان",
    "type": "in time",
    "time": "19:00:00 2025/05/30"
    }}


    متن:{user_text}
    """

        temp_ai = AI.AIGemini()
        data = temp_ai.analysis(static_text)

        keys = list(data.keys())
        while not (("category" in keys)):
            data = temp_ai.analysis(static_text)

        data["timeRequest"] = now_time

        if data["category"] == "reminder":  # reminder
            if data["work"] == "add":
                if "not found" in list(data.values()):

                    text = """**لطفا درخواستتان رو واضح ارسال کنید.**

    موارد زیر در پیامتان قابل تشخیص باشد:
    چه چیزی یادآوری بشه؟
    چه زمانی (یا تاریخ و ساعت دقیق گفته شود یا اینکه بگید چقدر وقت دیگر) یادآوری انجام بشه؟
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
                        messageId=await history.get_last_message_id(
                            user_id=user[0]["id"]
                        )
                        + 1,
                        messageText=text,
                        timeRequest=now_time,
                        whoSent=0,
                    )
                else:
                    await Remind.add_new_reminder(
                        user, user_text, data, update, context
                    )
            elif data["work"] == "remove":
                await Remind.cancel_reminder(user, user_text, now_time, update, context)
                await Remind.show_remaining_reminder(user, now_time, update, context)
            elif data["work"] == "change time":
                await Remind.change_time_reminder(
                    user, user_text, now_time, data, update, context
                )
                await Remind.show_remaining_reminder(user, now_time, update, context)
            elif data["work"] == "show reminders":
                await Remind.show_remaining_reminder(user, now_time, update, context)
            elif data["work"] == "not found":
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

        elif data["category"] == "todolist":  # todolist
            if data["work"] == "add":
                await ToDo.add_work(user, user_text, data, now_time)
                await ToDo.show_todolist(user, update, context)
            elif data["work"] == "remove":
                await ToDo.remove_work(user, user_text, update, context)
                await ToDo.show_todolist(user, update, context)
            elif data["work"] == "doing today":
                await ToDo.choose_work_for_today(user, user_text, update, context)
                await ToDo.show_todolist(user, update, context)
            elif data["work"] == "show todolist":
                await ToDo.show_todolist(user, update, context)
            elif data["work"] == "not found":
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

        elif data["category"] == "email":  # email
            if (
                (data["work"] == "send email")
                and ("subject" in data.keys())
                and ("text" in data.keys())
                and not (data["subject"] == "not found")
                and not (data["text"] == "not found")
            ):
                await mail.send_email(user, data, update, context)
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

        elif data["category"] == "ticket":  # ticket
            if data["target"] == "flight":
                if data["work"] == "show tickets":
                    await ticket.show_ticket(user, user_text, update, context)
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

        elif data["category"] == "not found":
            text = f"""در حال حاضر خدماتی که ربات **{robot_name}** میتواند انجمام دهد به صورت زیر است"""

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
        main_log.log("ERROR", f"proccessing text: {err}")


async def set_job_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.effective_message.text[
        update.effective_message.text.find(" ") + 1 : :
    ]
    chat_id = update.effective_chat.id
    account = db.Account()

    user = account.find(telegramId=chat_id)

    now_time = time.strftime("%H:%M:%S %Y/%m/%d")
    # add to history
    await history.set_history(
        userId=user[0]["id"],
        messageId=update.effective_message.id,
        messageText=update.effective_message.text,
        timeRequest=now_time,
        whoSent=1,
    )

    text = ""
    if password == config("PASS_ADMIN"):
        remind = db.Reminder()
        reminders = remind.all()

        for item in reminders:
            if item["status"] == 0:
                dt = datetime.strptime(item["time"], "%H:%M:%S %Y/%m/%d")
                dateTime = dt - datetime.now()
                user_chat_id = account.findById(item["user_id"])[0]["telegramId"]

                context.job_queue.run_once(
                    Remind.send_reminder,
                    when=dateTime.total_seconds() + 30,
                    data={"chat_id": user_chat_id, "id_db_reminders": item["id"]},
                )

        text = "done"
        now_time = time.strftime("%H:%M:%S %Y/%m/%d")
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_to_message_id=update.effective_message.id,
        )
    else:
        text = "شما دسترسی ندارید."
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
        whoSent=0,
    )


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        main_log.log("INFO", "Help command ... ")
        chat_id = update.effective_chat.id
        acc = db.Account()
        user = acc.find(telegramId=chat_id)

        # add to history
        now_time = time.strftime("%H:%M:%S %Y/%m/%d")
        await history.set_history(
            userId=user[0]["id"],
            messageId=update.effective_message.id,
            messageText=update.effective_message.text,
            timeRequest=now_time,
            whoSent=1,
        )

        text_help = f"""
    *🎩 به ربات ریکاردو خوش اومدی\!*

    ریکاردو یک دستیار هوشمنده که کمک می‌کنه کارات رو راحت‌تر مدیریت کنی — از یادآوری و لیست کارها گرفته تا ارسال ایمیل و چک کردن قیمت بلیط هواپیما\!  
    در ادامه قابلیت‌هاش رو همراه با مثال برات توضیح دادیم 👇

    *🕒 یادآورها*  
    هیچ کاری رو فراموش نکن\! با ریکاردو می‌تونی:  
    • یادآور جدید ثبت کنی
    • لیست یادآورها رو ببینی  
    • زمان یادآورها رو تغییر بدی  
    • یادآور رو حذف کنی

    *🔹 مثال‌ها:*
    • `یادآوری کن فردا ساعت ۸ صبح برم باشگاه`
    • `یادآور بزار برای پنجشنبه ساعت ۱۴: جلسه با تیم`
    • `لیست یادآورها رو نشونم بده`
    • `یادآور جلسه با تیم رو حذف کن`
    • `زمان یادآور دکتر رو بزار برای ساعت ۱۰ صبح`

    *📝 لیست کارها \(To\-Do List\)*
    با لیست کارهای ریکاردو می‌تونی کارات رو سازمان‌دهی کنی:  
    • کار جدید اضافه کن  
    • لیست کارهات رو ببین  
    • کار انجام‌شده رو تیک بزن یا حذف کن  
    • مشخص کن کدوم کارها برای امروزن

    *🔹 مثال‌ها:*  
    • `کار جدید: خرید شیر و نان`
    • `لیست کارهام رو نشونم بده`
    • `کار خرید نان رو انجام شده علامت بزن`
    • `کار مطالعه برای امروز رو مشخص کن`

    *📧 ارسال ایمیل گروهی*  
    فقط متن و آدرس‌ها رو بده، ریکاردو خودش همه‌ی ایمیل‌ها رو ارسال می‌کنه\!

    *🔹 مثال:*
    ```
    به این ایمیلا: ali@gmail\.com, sara@yahoo\.com  
    بفرست: سلام، جلسه فردا ساعت ۱۰ برگزار میشه\.
    ```

    *✈️ استعلام قیمت بلیط هواپیما*
    بگو از کجا به کجا و برای چه تاریخی، تا ریکاردو بازه‌ی قیمت بلیط‌ها رو برات بفرسته\.

    *🔹 مثال‌ها:*
    • `قیمت بلیط از تهران به مشهد رو بگو`
    • `قیمت بلیط از شیراز به تبریز برای ۲۰ خرداد رو بفرست`

    *❓ راهنما خواستی؟*  
    هر موقع خواستی راهنمایی بگیری، فقط /help ارسال کن
    ریکاردو همیشه آماده‌ست 🤖

    """

        now_time = time.strftime("%H:%M:%S %Y/%m/%d")
        await context.bot.send_message(
            chat_id=chat_id,
            text=text_help,
            parse_mode="MarkdownV2",
        )

        # add to history
        await history.set_history(
            userId=user[0]["id"],
            messageId=await history.get_last_message_id(user_id=user[0]["id"]) + 1,
            messageText=text_help,
            timeRequest=now_time,
            whoSent=0,
        )
    except Exception as err:
        main_log.log("ERROR", f"help command: {err}")


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("test")
    te = "test"
    print(len(te))
    print(await ticket.price_formate("12345678900"))


def main():
    app = Application.builder().token(TK).build()
    try:

        app.add_handlers(
            [
                CommandHandler("test", test),
                CommandHandler("start", start),
                CommandHandler("set_job_queue", set_job_queue),
                CommandHandler("help", help),
                MessageHandler(filters.TEXT & (~filters.COMMAND), process),
            ]
        )

        app.run_polling()
    except:
        print("____+++++_____|there is a problem.|____+++++_____")


if __name__ == "__main__":
    main_log.log("INFO", "Start the bot ... ")
    main()
