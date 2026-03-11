import telebot
from telebot import types
from telebot.types import ChatPermissions
import json
import os

TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"
bot = telebot.TeleBot(TOKEN)

FORCE_CHANNELS = ["@sshah8115", "@sshah_811"]

user_lang = {}
warnings = {}
media_db = {"videos": {}, "files": {}}
waiting_video = {}
waiting_file = {}

MEDIA_FILE = "media_db.json"

def save_media(data):
    with open(MEDIA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_media():
    if os.path.exists(MEDIA_FILE):
        with open(MEDIA_FILE, "r") as f:
            return json.load(f)
    save_media(media_db)
    return media_db

media_db = load_media()

# اللغات
LANG = {
    "ar": """👑 أنا روبوت لإدارة قناتك ومجموعتك
تم تطويري من قبل 𓆩˹𝚈𝙴𝙼 القياده شاهر 🇾🇪˼𓆪

الأوامر:
/حظر
/الغاء_حظر
/كتم
/الغاء_كتم
/تحذير
/مسح_التحذيرات
""",
    "en": """👑 I am a bot for managing your channel and group
Developed by 𓆩˹𝚈𝙴𝙼 Leader Shaher 🇾🇪˼𓆪
""",
    "ru": """👑 Я бот для управления вашей группой и каналом
Разработано 𓆩˹𝚈𝙴𝙼 Лидер Shaher 🇾🇪˼𓆪
""",
    "vi": """👑 Tôi là bot quản lý nhóm và kênh của bạn
Được phát triển bởi 𓆩˹𝚈𝙴𝙼 Leader Shaher 🇾🇪˼𓆪
"""
}

MENU = {
    "ar": ["📂 رفع فيديو","📁 رفع ملف","📊 الاحصائيات","⚙️ الاعدادات"],
    "en": ["📂 Upload Video","📁 Upload File","📊 Statistics","⚙️ Settings"],
    "ru": ["📂 Видео","📁 Файл","📊 Статистика","⚙️ Настройки"],
    "vi": ["📂 Video","📁 Tệp","📊 Thống kê","⚙️ Cài đặt"]
}

def main_menu(lang):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add(MENU[lang][0], MENU[lang][1])
    m.add(MENU[lang][2], MENU[lang][3])
    return m

# التحقق من الاشتراك
def check_sub(user_id):
    try:
        for ch in FORCE_CHANNELS:
            member = bot.get_chat_member(ch, user_id)
            if member.status not in ["member","administrator","creator"]:
                return False
        return True
    except:
        return False

# بدء البوت
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if not check_sub(user_id):
        text = "🚫 يجب الاشتراك في القنوات أولاً\n\n"
        for ch in FORCE_CHANNELS:
            text += ch + "\n"
        bot.send_message(message.chat.id,text)
        return

    mk = types.InlineKeyboardMarkup()
    mk.add(
        types.InlineKeyboardButton("العربية 🇾🇪", callback_data="ar"),
        types.InlineKeyboardButton("English 🇺🇸", callback_data="en")
    )
    mk.add(
        types.InlineKeyboardButton("Русский 🇷🇺", callback_data="ru"),
        types.InlineKeyboardButton("Vietnamese 🇻🇳", callback_data="vi")
    )

    bot.send_message(message.chat.id,"اختر لغتك",reply_markup=mk)

@bot.callback_query_handler(func=lambda call: call.data in ["ar","en","ru","vi"])
def set_language(call):
    user_lang[call.from_user.id] = call.data
    lang = call.data
    bot.send_message(call.message.chat.id, LANG[lang], reply_markup=main_menu(lang))

# ترحيب عضو جديد
@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for user in message.new_chat_members:
        bot.send_message(message.chat.id,f"👋 أهلاً بك {user.first_name} في المجموعة")

# رفع فيديو
@bot.message_handler(func=lambda m: "رفع فيديو" in str(m.text))
def ask_video_name(message):
    msg = bot.send_message(message.chat.id,"اكتب اسم الفيديو")
    bot.register_next_step_handler(msg, save_video_name)

def save_video_name(message):
    waiting_video[message.from_user.id] = message.text
    bot.send_message(message.chat.id,"ارسل الفيديو")

@bot.message_handler(content_types=['video'])
def save_video(message):
    uid = message.from_user.id
    if uid not in waiting_video:
        return

    name = waiting_video[uid]
    media_db["videos"][name] = message.video.file_id
    save_media(media_db)

    bot.send_message(message.chat.id,"✅ تم حفظ الفيديو")
    del waiting_video[uid]

# رفع ملف
@bot.message_handler(func=lambda m: "رفع ملف" in str(m.text))
def ask_file_name(message):
    msg = bot.send_message(message.chat.id,"اكتب اسم الملف")
    bot.register_next_step_handler(msg, save_file_name)

def save_file_name(message):
    waiting_file[message.from_user.id] = message.text
    bot.send_message(message.chat.id,"ارسل الملف")

@bot.message_handler(content_types=['document'])
def save_file(message):
    uid = message.from_user.id
    if uid not in waiting_file:
        return

    name = waiting_file[uid]
    media_db["files"][name] = message.document.file_id
    save_media(media_db)

    bot.send_message(message.chat.id,"✅ تم حفظ الملف")
    del waiting_file[uid]

# ارسال الوسائط المحفوظة
@bot.message_handler(func=lambda message: True)
def send_saved_media(message):
    if not message.text:
        return

    text = message.text.strip()

    if text in media_db["videos"]:
        bot.send_video(message.chat.id, media_db["videos"][text])
        return

    if text in media_db["files"]:
        bot.send_document(message.chat.id, media_db["files"][text])
        return

# التحقق هل المستخدم مشرف
def is_admin(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except:
        return False


# تحذير
@bot.message_handler(commands=['تحذير'])
def warn_user(message):
    try:
        print("تم استدعاء امر تحذير")

        if message.chat.type == "private":
            return

        if not is_admin(message.chat.id, message.from_user.id):
            bot.reply_to(message,"❌ هذا الامر للمشرفين فقط")
            return

        if not message.reply_to_message:
            bot.reply_to(message,"⚠️ يجب الرد على رسالة العضو")
            return

        user_id = message.reply_to_message.from_user.id
        warnings[user_id] = warnings.get(user_id,0)+1

        bot.send_message(message.chat.id,f"⚠️ تحذير {warnings[user_id]}/3")

        if warnings[user_id] >= 3:
            bot.ban_chat_member(message.chat.id,user_id)
            bot.send_message(message.chat.id,"🚫 تم حظر العضو بسبب 3 تحذيرات")

    except Exception as e:
        print(e)
        bot.send_message(message.chat.id,f"خطأ: {e}")


# حظر
@bot.message_handler(commands=['حظر'])
def ban_user(message):
    try:
        print("تم استدعاء امر حظر")

        if message.chat.type == "private":
            return

        if not is_admin(message.chat.id, message.from_user.id):
            bot.reply_to(message,"❌ هذا الامر للمشرفين فقط")
            return

        if not message.reply_to_message:
            bot.reply_to(message,"⚠️ يجب الرد على رسالة العضو")
            return

        user_id = message.reply_to_message.from_user.id
        bot.ban_chat_member(message.chat.id,user_id)

        bot.send_message(message.chat.id,"🚫 تم حظر العضو")

    except Exception as e:
        print(e)
        bot.send_message(message.chat.id,f"خطأ: {e}")


# الغاء الحظر
@bot.message_handler(commands=['الغاء_حظر'])
def unban_user(message):
    try:
        print("تم استدعاء امر الغاء حظر")

        if message.chat.type == "private":
            return

        if not is_admin(message.chat.id, message.from_user.id):
            bot.reply_to(message,"❌ هذا الامر للمشرفين فقط")
            return

        if not message.reply_to_message:
            bot.reply_to(message,"⚠️ يجب الرد على رسالة العضو")
            return

        user_id = message.reply_to_message.from_user.id
        bot.unban_chat_member(message.chat.id,user_id)

        bot.send_message(message.chat.id,"✅ تم الغاء الحظر")

    except Exception as e:
        print(e)
        bot.send_message(message.chat.id,f"خطأ: {e}")


# كتم
@bot.message_handler(commands=['كتم'])
def mute_user(message):
    try:
        print("تم استدعاء امر كتم")

        if message.chat.type == "private":
            return

        if not is_admin(message.chat.id, message.from_user.id):
            bot.reply_to(message,"❌ هذا الامر للمشرفين فقط")
            return

        if not message.reply_to_message:
            bot.reply_to(message,"⚠️ يجب الرد على رسالة العضو")
            return

        user_id = message.reply_to_message.from_user.id

        bot.restrict_chat_member(
            message.chat.id,
            user_id,
            ChatPermissions(can_send_messages=False)
        )

        bot.send_message(message.chat.id,"🔇 تم كتم العضو")

    except Exception as e:
        print(e)
        bot.send_message(message.chat.id,f"خطأ: {e}")


# الغاء الكتم
@bot.message_handler(commands=['الغاء_كتم'])
def unmute_user(message):
    try:
        print("تم استدعاء امر الغاء كتم")

        if message.chat.type == "private":
            return

        if not is_admin(message.chat.id, message.from_user.id):
            bot.reply_to(message,"❌ هذا الامر للمشرفين فقط")
            return

        if not message.reply_to_message:
            bot.reply_to(message,"⚠️ يجب الرد على رسالة العضو")
            return

        user_id = message.reply_to_message.from_user.id

        bot.restrict_chat_member(
            message.chat.id,
            user_id,
            ChatPermissions(can_send_messages=True)
        )

        bot.send_message(message.chat.id,"🔊 تم الغاء الكتم")

    except Exception as e:
        print(e)
        bot.send_message(message.chat.id,f"خطأ: {e}")
   
print("Shaher Bot Running")
bot.infinity_polling()
        
