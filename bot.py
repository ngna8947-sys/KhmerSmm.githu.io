import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)

# ១. កំណត់ Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# ២. ព័ត៌មាន Bot & គណនី Bakong
BOT_TOKEN = "8730299395:AAFG-tX_lgvE_JeUInmRkNhMiT4snEbXsfc"
BAKONG_ID = "mon_samnang@bkrt"
ACCOUNT_NAME = "SAMNANG MÔN"

# ដាក់ Chat ID របស់អ្នក (ឆែកតាម Telegram @userinfobot) ដើម្បីឱ្យ Bot ផ្ញើ Slip ទៅប្រាប់
ADMIN_CHAT_ID = "YOUR_ADMIN_CHAT_ID" 

# ៣. ដំណាក់កាលដំណើរការ (States)
SELECT_GAME, SELECT_PACKAGE, ENTER_UID, UPLOAD_SLIP = range(4)

# ៤. បញ្ជីហ្គេម និងកញ្ចប់ពេជ្រ/ប្រចាំខែ
GAMES_DATA = {
    "freefire": {
        "title": "🔥 Free Fire",
        "input_hint": "Player ID (UID)",
        "packages": {
            "ff_100": {"name": "💎 100 Diamonds", "price": 0.99},
            "ff_310": {"name": "💎 310 Diamonds", "price": 2.90},
            "ff_520": {"name": "💎 520 Diamonds", "price": 4.80},
            "ff_1060": {"name": "💎 1,060 Diamonds", "price": 9.50},
            "ff_weekly": {"name": "🎟️ Weekly Membership", "price": 1.99},
            "ff_monthly": {"name": "👑 Monthly Membership (ពេជ្រប្រចាំខែ)", "price": 9.99},
        }
    },
    "mlbb": {
        "title": "⚔️ Mobile Legends (MLBB)",
        "input_hint": "User ID & Zone ID (ឧ. 12345678 (1234))",
        "packages": {
            "ml_86": {"name": "💎 86 Diamonds", "price": 1.40},
            "ml_172": {"name": "💎 172 Diamonds", "price": 2.75},
            "ml_257": {"name": "💎 257 Diamonds", "price": 4.10},
            "ml_706": {"name": "💎 706 Diamonds", "price": 10.50},
            "ml_weekly": {"name": "🎟️ Weekly Diamond Pass", "price": 1.90},
            "ml_monthly_starlight": {"name": "👑 Starlight Member (ប្រចាំខែ)", "price": 4.99},
        }
    },
    "pubg": {
        "title": "🎯 PUBG Mobile",
        "input_hint": "Character ID (UID)",
        "packages": {
            "pubg_60": {"name": "💵 60 UC", "price": 0.99},
            "pubg_325": {"name": "💵 325 UC", "price": 4.90},
            "pubg_660": {"name": "💵 660 UC", "price": 9.80},
            "pubg_1800": {"name": "💵 1,800 UC", "price": 24.50},
            "pubg_monthly_prime": {"name": "👑 Prime Plus (ប្រចាំខែ)", "price": 9.99},
        }
    },
    "roblox": {
        "title": "🧱 Roblox",
        "input_hint": "Roblox Username",
        "packages": {
            "rbx_80": {"name": "🪙 80 Robux", "price": 1.10},
            "rbx_400": {"name": "🪙 400 Robux", "price": 4.99},
            "rbx_800": {"name": "🪙 800 Robux", "price": 9.90},
            "rbx_1700": {"name": "🪙 1,700 Robux", "price": 19.80},
            "rbx_premium": {"name": "👑 Roblox Premium (ប្រចាំខែ)", "price": 4.99},
        }
    }
}

# ៥. មុខងារចាប់ផ្តើម /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("🔥 Free Fire", callback_data="game_freefire")],
        [InlineKeyboardButton("⚔️ Mobile Legends", callback_data="game_mlbb")],
        [InlineKeyboardButton("🎯 PUBG Mobile", callback_data="game_pubg")],
        [InlineKeyboardButton("🧱 Roblox", callback_data="game_roblox")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 **សូមស្វាគមន៍មកកាន់សេវាបញ្ចូលហ្គេមស្វ័យប្រវត្ត!**\n\n"
        "🎮 សូមជ្រើសរើសប្រភេទហ្គេមដែលអ្នកចង់បញ្ចូល៖",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return SELECT_GAME

# ៦. មុខងារជ្រើសរើសហ្គេម
async def select_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    game_key = query.data.replace("game_", "")
    context.user_data["game_key"] = game_key
    game_info = GAMES_DATA[game_key]

    # បង្កើតប៊ូតុងកញ្ចប់ពេជ្រ
    keyboard = []
    for pkg_id, pkg in game_info["packages"].items():
        keyboard.append([InlineKeyboardButton(f"{pkg['name']} (${pkg['price']})", callback_data=pkg_id)])
    
    keyboard.append([InlineKeyboardButton("🔙 ត្រឡប់ក្រោយ", callback_data="back_to_games")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"🎮 ហ្គេមដែលបានរើស៖ **{game_info['title']}**\n\n"
        "👉 សូមជ្រើសរើសកញ្ចប់ដែលអ្នកចង់ទិញ៖",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return SELECT_PACKAGE

# ៧. មុខងារជ្រើសរើសកញ្ចប់ពេជ្រ
async def select_package(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    # ប៊ូតុង Back
    if query.data == "back_to_games":
        keyboard = [
            [InlineKeyboardButton("🔥 Free Fire", callback_data="game_freefire")],
            [InlineKeyboardButton("⚔️ Mobile Legends", callback_data="game_mlbb")],
            [InlineKeyboardButton("🎯 PUBG Mobile", callback_data="game_pubg")],
            [InlineKeyboardButton("🧱 Roblox", callback_data="game_roblox")],
        ]
        await query.edit_message_text(
            "🎮 សូមជ្រើសរើសប្រភេទហ្គេមដែលអ្នកចង់បញ្ចូល៖",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return SELECT_GAME

    game_key = context.user_data["game_key"]
    pkg_key = query.data
    game_info = GAMES_DATA[game_key]
    selected_pkg = game_info["packages"][pkg_key]

    context.user_data["package"] = selected_pkg

    await query.edit_message_text(
        f"🎮 ហ្គេម៖ **{game_info['title']}**\n"
        f"📦 កញ្ចប់៖ **{selected_pkg['name']}** (តម្លៃ: **${selected_pkg['price']}**)\n\n"
        f"👉 **សូមផ្ញើ {game_info['input_hint']} របស់អ្នកមកកាន់ Bot:**",
        parse_mode="Markdown"
    )
    return ENTER_UID

# ៨. មុខងារទទួល UID និងបង្ហាញព័ត៌មាន Bakong
async def enter_uid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    uid = update.message.text
    context.user_data["uid"] = uid
    pkg = context.user_data["package"]
    game_key = context.user_data["game_key"]
    game_info = GAMES_DATA[game_key]

    payment_info = (
        f"📝 **ព័ត៌មានការកុម្ម៉ង់៖**\n"
        f"• ហ្គេម៖ **{game_info['title']}**\n"
        f"• ព័ត៌មាន ID៖ `{uid}`\n"
        f"• កញ្ចប់៖ **{pkg['name']}**\n"
        f"• តម្លៃត្រូវបង់៖ **${pkg['price']}**\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🏦 **ព័ត៌មានទូទាត់ប្រាក់ (Bakong / KHQR)**\n"
        f"• ឈ្មោះគណនី៖ **{ACCOUNT_NAME}**\n"
        f"• Bakong ID៖ `{BAKONG_ID}`\n"
        f"• ចំនួនទឹកប្រាក់៖ **${pkg['price']}**\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"👉 **សូមធ្វើការផ្ទេរប្រាក់ រួចផ្ញើរូបភាពវិក្កយបត្រ (Slip) ចូលទីនេះដើម្បីបញ្ជាក់ការបញ្ជាទិញ។**"
    )

    await update.message.reply_text(payment_info, parse_mode="Markdown")
    return UPLOAD_SLIP

# ៩. មុខងារទទួលរូបភាពវិក្កយបត្រ (Slip)
async def upload_slip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    pkg = context.user_data.get("package")
    uid = context.user_data.get("uid")
    game_key = context.user_data.get("game_key")
    game_info = GAMES_DATA.get(game_key, {"title": "Unknown"})
    photo = update.message.photo[-1]

    # បញ្ជាក់ទៅអតិថិជន
    await update.message.reply_text(
        "✅ **យើងបានទទួលវិក្កយបត្ររបស់អ្នកហើយ!**\n"
        "Admin កំពុងត្រួតពិនិត្យ និងបញ្ចូលជូនក្នុងរយៈពេល 1-5 នាទី។ សូមអរគុណ!",
        parse_mode="Markdown"
    )

    # បាញ់ដំណឹងទៅកាន់ Admin
    if ADMIN_CHAT_ID != "YOUR_ADMIN_CHAT_ID":
        admin_text = (
            f"🔔 **មានការកុម្ម៉ង់ថ្មី!**\n"
            f"🎮 ហ្គេម: {game_info['title']}\n"
            f"👤 អតិថិជន: @{user.username} (ID: `{user.id}`)\n"
            f"🆔 Game ID: `{uid}`\n"
            f"📦 កញ្ចប់: {pkg['name']} (${pkg['price']})\n"
        )
        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=photo.file_id,
            caption=admin_text,
            parse_mode="Markdown"
        )

    return ConversationHandler.END

# ១០. មុខងារបោះបង់ /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ ការបញ្ជាទិញត្រូវបានបោះបង់។ វាយ /start ដើម្បីចាប់ផ្តើមឡើងវិញ។")
    return ConversationHandler.END

# Main Loop
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_GAME: [CallbackQueryHandler(select_game)],
            SELECT_PACKAGE: [CallbackQueryHandler(select_package)],
            ENTER_UID: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_uid)],
            UPLOAD_SLIP: [MessageHandler(filters.PHOTO, upload_slip)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("🚀 Top-Up Bot កំពុងដំណើរការ...")
    app.run_polling()

if __name__ == "__main__":
    main()
