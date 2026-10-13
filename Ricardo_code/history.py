from logger import history_log
import sql as db


async def set_history(userId, messageId, messageText, timeRequest, whoSent):
    history_log.log("INFO", "Add message in the history ")
    message = db.History()
    messages_with_messageId = message.viewByMessageId(messageId=messageId)
    if len(messages_with_messageId) == 0:
        message.insert(
            userId=userId,
            messageId=messageId,
            messageText=messageText,
            timeReq=timeRequest,
            whoSent=whoSent,
        )


async def get_last_message_id(user_id: int):
    history_log.log("INFO", "Get last message of the history ")
    history = db.History()
    messages = history.all()
    for item in messages[::-1]:
        if item["user_id"] == user_id:
            return item["message_id"]


