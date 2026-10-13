import time

from telegram import Update
from telegram.ext import ContextTypes

import sql as db
import history
import ai as AI
from logger import todolist_log


async def add_work(user, user_text, data, now_time):
    try:
        todolist_log.log("INFO", "add work")
        todo = db.ToDoList()
        todo.insert(
            userId=user[0]["id"],
            orgText=user_text,
            text=data["text"],
            timeReq=now_time,
        )
    except Exception as err:
        todolist_log.log("ERROR", f"add work: {err}")


async def remove_work(
    user, user_text, update: Update, context: ContextTypes.DEFAULT_TYPE
):
    try:
        todolist_log.log("INFO", "remove work")
        chat_id = update.effective_chat.id
        todo = db.ToDoList()
        works = todo.viewRemainder(user[0]["id"])

        out_str = ""

        i = 1
        for work in works:
            out_str += f"{i}. {work["text"]}\n"
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

        if option - 1 < len(works):
            todo.update(works[option - 1]["id"], "status")
        else:
            text = """موردی که می‌خواهید از لیست کارهایتان حذف کنید، یا در لیست کارهایتان نیست یا قابل تشخیص نبود.
    لطفا موردی که مدنظرتان است را واضح‌تر بگید.
    لیست کارهای شما به صورت زیر است.
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
        todolist_log.log("ERROR", f"remove work: {err}")


async def choose_work_for_today(
    user, user_text, update: Update, context: ContextTypes.DEFAULT_TYPE
):
    try:
        todolist_log.log("INFO", "choose work for today")
        chat_id = update.effective_chat.id
        todo = db.ToDoList()
        works = todo.viewRemainder(user[0]["id"])

        out_str = ""

        i = 1
        for work in works:
            out_str += f"{i}. {work["text"]}\n"
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
        if option - 1 < len(works):
            todo.update(works[option - 1]["id"], "today")
        else:
            text = """مموردی که می‌خواهید از لیست کارهایتان برای امروز علامت بزنید و انجام دهید، یا در لیست کارهایتان نیست یا قابل تشخیص نبود.
    لطفا موردی که مدنظرتان است را واضح‌تر بگید.
    لیست کارهای شما به صورت زیر است.
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
        todolist_log.log("ERROR", f"choose work for today: {err}")


async def show_todolist(user, update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        todolist_log.log("INFO", "show todolist")
        chat_id = update.effective_chat.id
        todo = db.ToDoList()
        works = todo.viewRemainder(user[0]["id"])

        out_str = ""

        if len(works) == 0:
            text = "شما در حال حاضر در لیست کارهایتان موردی وجود ندارد."

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
            works_list = "لیست کارهای شما : \n\n"
            works_doing_today = "کارهایی که امروز میخواهید انجام دهید: \n"

            i = 1
            j = 1
            for work in works:
                works_list += f"{i}. {work["text"]}\n"
                i += 1
                if work["today"] == 1:
                    works_doing_today += f"{j}. {work["text"]}\n"
                    j += 1

            out_str = works_list + "\n------------------------\n" + works_doing_today

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
        todolist_log.log("ERROR", f"show todolist: {err}")
