from time import sleep
from threading import Thread

from telegram import Message, Update, constants
from telegram.ext import Updater, CallbackContext, CommandHandler

import enum, json, logging

LANGUAGE = "be"
PREFERENSES = json.load(open("config.json"))
TOKEN = PREFERENSES["token"]
MESSAGE = PREFERENSES["messages"][LANGUAGE]

MAX_MENTION_COUNT = 5 # max count of mentions in one message

class sem(enum.Enum):
    lock = 0
    unlock = 1

lockedList: list[int] = []

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def all(update: Update, context: CallbackContext):
    if update.effective_chat.type == constants.CHAT_PRIVATE:
        context.bot.send_message(chat_id=update.effective_chat.id, text=MESSAGE["private"], parse_mode="Markdown")
        return

    if lock(update.effective_chat.id, sem.lock):
        Thread(target=try_call, args=(update, context)).start()

def help(update: Update, context: CallbackContext):
    if not lock(update.effective_chat.id, sem.lock):
        return

    context.bot.send_message(chat_id=update.effective_chat.id, text=MESSAGE["help"], parse_mode="Markdown")
    lock(update.effective_chat.id, sem.unlock)



def get_tag_messages(update: Update, custom_titles: str) -> list[str]:
    mentionMessages = [""]
    mentionCounter = 0

    for administrator in update.effective_chat.get_administrators():
        if administrator.user.is_bot or custom_titles and not has_coincidence(custom_titles, administrator.custom_title): ###
            continue

        mentionMessages[-1] += f"[⭐️](tg://user?id={administrator.user.id})"
        mentionCounter += 1
        if mentionCounter == MAX_MENTION_COUNT:
            mentionCounter = 0
            mentionMessages.append("")

    if "" in mentionMessages:
        mentionMessages.remove("")
    
    return mentionMessages


def try_call(update: Update, context: CallbackContext):
    messages: list[Message] = []
    custom_titles: str = None

    if context.args:
        custom_titles = ' '.join(context.args)

    tagMessages = get_tag_messages(update, custom_titles)

    try:
        for tags in tagMessages:
            messages.append(call_message(update, context, tags))
    except:
        delete_messages(messages)
        logging.error(MESSAGE["error"])

    message_context = {
            "chat_id":update.effective_chat.id, 
            "parse_mode":"Markdown"
            }

    if tagMessages:
        lock_message = context.bot.send_message(**message_context, text=MESSAGE["lock"])
        sleep(60)
        lock_message.delete()
    else:
        context.bot.send_message(**message_context, text=MESSAGE["none"])

    lock(update.effective_chat.id, sem.unlock)


def call_message(update: Update, context: CallbackContext, tags: str) -> Message:
    sleep(1)

    call_message_context = {
        "chat_id": update.effective_chat.id, 
        "text": f"{tags}\n\n{MESSAGE['call']}",
        "parse_mode": "Markdown", 
        "timeout": 30
        }
    
    return context.bot.send_message(**call_message_context)


def delete_messages(messages: list[Message]):
    for message in messages:
        message.delete()


def lock(chat_id: int, action: sem) -> bool:
    match action:
        case sem.lock:
            if chat_id not in lockedList:
                lockedList.append(chat_id)
                return True
        case sem.unlock:
            if chat_id in lockedList:
                lockedList.remove(chat_id)
                return True
    return False


def has_coincidence(tagsToSearch: str, userTags: str) -> bool:
    if not tagsToSearch:
        return False
    return [tag for tag in tagsToSearch.split(', ') if tag in userTags.split(', ')] != []


all_handler = CommandHandler('all', all)
help_handler = CommandHandler(['start', 'help'], help)

dispatcher.add_handler(all_handler)
dispatcher.add_handler(help_handler)

updater.start_polling()