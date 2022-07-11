from telegram import Update, constants
from telegram.ext import Updater, CallbackContext, CommandHandler

TOKEN="PASTE_YOUR_TOKEN_HERE"

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def all(update: Update, context: CallbackContext):
    if update.effective_chat.type == constants.CHAT_PRIVATE:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Ну і каго мне тэгаць у асабоўцы?\nДадай мяне ў суполку!")
        return

    call = " ".join(context.args)
    tagMessages = [""]
    tagsCounter = 0

    for administrator in update.effective_chat.get_administrators():
        if administrator.user.is_bot:
            continue
        tagMessages[-1] += "Паклікаў " + administrator.user.mention_markdown() + "\n"
        tagsCounter += 1
        if tagsCounter == 5:
            tagsCounter = 0
            tagMessages[-1] += "\nБіп-буп, паведамленне яшчэ не знікла?\nПадаецца хтосьці схапіў бан за флуд, \nпачакай некалькі хвілін і спрабуй яшчэ раз 🤖"
            tagMessages.append("")

    if "" in tagMessages:
        tagMessages.remove("")
    
    for tags in tagMessages:
        try:
            message = context.bot.send_message(chat_id=update.effective_chat.id, text=tags, parse_mode="Markdown", timeout=60)
            message.edit_text(f"🔔 {update.effective_user.mention_markdown()} кліча усіх {call}", parse_mode="Markdown", timeout=60)
        except:
            print("Біп-буп, занадта шмат выклікаў, я зламаўся 🤖")

    try:
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id)
    except:
        None

def help(update: Update, context: CallbackContext):
    help_text = "Вітанкі! 👋\n\n\
Я дапамагу табе паклікаць усіх, хто знаходзіцца разам з табой у суполцы.\n\n\
Але перад тым як я гэта зраблю *дадай мяне ў гэтую суполку* каб я мог рэагаваць на паведамленні, а таксама *прызнач кіраўнікамі ўсіх, каго хочаш тэгаць*. \
Не абавязкова выдаваць паўнамоцтвы кіраўнікам, галоўнае каб яны мелі статус. Таксама звяртаю ўвагу на тое, што тэлеграм дазваляе мець толькі 50 кіраўнікоў \
у адной суполцы, таму ў больш вялікіх суполках табе прыйдзецца добра падумаць каго па выніку я патурбую\n\n\
Калі прыйдзе час проста напішы /all у суполцы і я ўсіх паклічу. Апцыянальна можаш пасля /all дадаць свой заклік, напрыклад: `/all шатаць рэжым`"

    context.bot.send_message(chat_id=update.effective_chat.id, text=help_text, parse_mode="Markdown")
    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id)

all_handler = CommandHandler('all', all)
start_handler = CommandHandler('start', help)
help_handler = CommandHandler('help', help)


dispatcher.add_handler(all_handler)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(help_handler)

updater.start_polling()