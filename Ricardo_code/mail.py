import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from decouple import config

from telegram import Update
from telegram.ext import ContextTypes

import history

import re
import time

from logger import mail_log


class Mail:
    sender_email = None
    password = None
    mail_host = None
    mail_port = None

    def __init__(self):
        mail_log.log("INFO", "Mail configuration ... ")
        self.sender_email = config("EMAIL_SENDER")
        self.password = config("EMAIL_PASSWORD")
        self.mail_host = config("EMAIL_HOST")
        self.mail_port = config("EMAIL_PORT")

    def sending_emails(self, receivers_email: list, subject: str, body: str):
        try:
            mail_log.log("INFO", "Mail connection .... ")
            server = smtplib.SMTP(self.mail_host, self.mail_port)
            server.starttls()
            server.login(self.sender_email, self.password)

            mail_log.log("INFO", "send emails ")
            for re_email in receivers_email:
                msg = MIMEMultipart()
                msg["From"] = self.sender_email
                msg["To"] = re_email
                msg["Subject"] = subject

                msg.attach(MIMEText(body, "html"))

                server.sendmail(self.sender_email, re_email, msg.as_string())

            server.quit()
        except Exception as err:
            mail_log.log("ERROR", f"sending email: {err}")


async def send_email(user, data, update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.effective_message.text

    mail_log.log("INFO", "Extracting the email of the user text")
    emails_address = re.findall(
        pattern=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        string=user_text,
        flags=re.MULTILINE,
    )

    set_mail = Mail()

    body = data["text"]

    set_mail.sending_emails(
        receivers_email=emails_address, subject=data["subject"], body=body
    )

    text = "ایمیل ها ارسال شد."
    now_time = time.strftime("%H:%M:%S %Y/%m/%d")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
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
