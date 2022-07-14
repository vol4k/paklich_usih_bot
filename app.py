
from time import sleep
from threading import Thread

from telegram import Message, Update, constants
from telegram.ext import Updater, CallbackContext, CommandHandler

TOKEN="PASTE_YOUR_TOKEN_HERE"

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

lockedList: list[int] = []

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def all(update: Update, context: CallbackContext):
    if update.effective_chat.type == constants.CHAT_PRIVATE:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Ну і каго мне тэгаць у асабоўцы?\nДадай мяне ў суполку!")
        return

    delete_message(update, context)

    if lock(update.effective_chat.id):
        Thread(target=call_all, args=(update, context)).start()


def help(update: Update, context: CallbackContext):
    delete_message(update, context)

    if not lock(update.effective_chat.id):
        return

    help_text = "Вітанкі! 👋\n\n\
Я дапамагу табе паклікаць усіх, хто знаходзіцца разам з табой у суполцы.\n\n\
Але перад тым як я гэта зраблю *дадай мяне ў гэтую суполку* каб я мог рэагаваць на паведамленні, а таксама *прызнач кіраўнікамі ўсіх, каго хочаш тэгаць*. \
Не абавязкова выдаваць паўнамоцтвы кіраўнікам, галоўнае каб яны мелі статус.\n\
А вось мне можаш даць *паўнамоцтвы на выдаленне паведамленняў*, калі хочаш, каб я выдаляў звароты да мяне.\n\
Таксама звяртаю ўвагу на тое, што тэлеграм дазваляе мець толькі 50 кіраўнікоў \
у адной суполцы, таму ў больш вялікіх суполках табе прыйдзецца добра падумаць каго па выніку мне давядзецца турбаваць\n\n\
Калі прыйдзе час проста напішы /all у суполцы і я ўсіх паклічу. Апцыянальна можаш пасля /all дадаць свой заклік, напрыклад: `/all шатаць рэжым`"

    context.bot.send_message(chat_id=update.effective_chat.id, text=help_text, parse_mode="Markdown")

    unlock(update.effective_chat.id)


def get_tag_messages(update: Update) -> list[str]:
    tagMessages = [""]
    tagsCounter = 0

    for administrator in update.effective_chat.get_administrators():
        if administrator.user.is_bot:
            continue
        tagMessages[-1] += "Паклікаў " + administrator.user.mention_markdown() + "\n"
        tagsCounter += 1
        if tagsCounter == 5:
            tagsCounter = 0
            tagMessages.append("")

    if "" in tagMessages:
        tagMessages.remove("")
    
    return tagMessages


def call_all(update: Update, context: CallbackContext):
    call = " ".join(context.args)
    messages: list[Message] = []

    tagMessages = get_tag_messages(update)

    try:
        for tags in tagMessages:
            messages.append(message_call(update, context, tags, call))
    except:
        delete_messages(messages)
        logging.error("Біп-буп, занадта шмат выклікаў, я зламаўся 🤖")

    message = context.bot.send_message(chat_id=update.effective_chat.id, text=f"*🤖 Біп-буп, праца зроблена.*\n\n_Адыйшоў за гарбаткай ☕️\nПраз хвіліну вярнуся, не сумуйце без мяне 😊_", parse_mode="Markdown")

    sleep(60)
    message.delete()
    unlock(update.effective_chat.id)


def message_call(update: Update, context: CallbackContext, tags: str, call: str) -> Message:
    sleep(2.5)

    message = context.bot.send_message(chat_id=update.effective_chat.id, text=tags, parse_mode="Markdown", timeout=60)
    message.edit_text(f"🔔 {update.effective_user.mention_markdown()} кліча усіх {call}", parse_mode="Markdown", timeout=60)

    return message


def delete_messages(messages: list[Message]):
    for message in messages:
        sleep(1)
        message.delete()


def delete_message(update: Update, context: CallbackContext):
    try:
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id)
    except:
        None

def lock(chat_id: int) -> bool:
    if chat_id not in lockedList:
        lockedList.append(chat_id)
        return True
    else:
        return False

def unlock(chat_id: int) -> bool:
    if chat_id in lockedList:
        lockedList.remove(chat_id)
        return True
    else:
        return False


all_handler = CommandHandler('all', all)
start_handler = CommandHandler('start', help)
help_handler = CommandHandler('help', help)


dispatcher.add_handler(all_handler)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(help_handler)

updater.start_polling()