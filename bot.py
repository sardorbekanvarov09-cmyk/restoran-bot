from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = "8942898982:AAHrCveD4tMQv-iFP5bznP5oRBQyFSqqqWA"
ADMIN_ID = 7463200311
RESTORAN_NOMI = "Osh Markazi"
TELEFON = "+998 90 123 45 67"
MANZIL = "Toshkent, Chilonzor 5-mavze"

MENYU = {
    "Birinchi taomlar": {"Mastava": 15000, "Lagman": 18000, "Shurva": 12000},
    "Ikkinchi taomlar": {"Osh (plov)": 25000, "Manti": 20000, "Shashlik (6 ta)": 35000, "Norin": 22000},
    "Salatlar": {"Achchiq-chuchuk": 8000, "Toshkent salati": 10000, "Achichuk": 7000},
    "Ichimliklar": {"Choy (domlama)": 5000, "Kompot": 6000, "Kola/Fanta": 8000}
}

def format_cart(cart):
    if not cart:
        return "Savatcha bosh"
    lines = []
    total = 0
    for item, qty in cart.items():
        price = None
        for cat in MENYU.values():
            if item in cat:
                price = cat[item]
                break
        if price:
            subtotal = price * qty
            total += subtotal
            lines.append("- " + item + " x" + str(qty) + " = " + str(subtotal) + " som")
    lines.append("\nJami: " + str(total) + " som")
    return "\n".join(lines)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    buttons = [["Buyurtma berish", "Menyuni korish"], ["Savatcham", "Boglanish"]]
    markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text("Assalomu alaykum! " + RESTORAN_NOMI + " ga xush kelibsiz!\n\nBuyurtma berish uchun tugmani bosing.", reply_markup=markup)

async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[InlineKeyboardButton(cat, callback_data="cat:" + cat)] for cat in MENYU.keys()]
    await update.message.reply_text("Kategoriyani tanlang:", reply_markup=InlineKeyboardMarkup(buttons))

async def show_menu_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = RESTORAN_NOMI + " Menyusi:\n\n"
    for cat, items in MENYU.items():
        text += cat + ":\n"
        for name, price in items.items():
            text += "  - " + name + " - " + str(price) + " som\n"
        text += "\n"
    await update.message.reply_text(text)

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart = context.user_data.get("cart", {})
    text = "Sizning savatchangiz:\n\n" + format_cart(cart)
    if cart:
        buttons = [[InlineKeyboardButton("Buyurtmani tasdiqlash", callback_data="confirm")], [InlineKeyboardButton("Tozalash", callback_data="clear_cart")]]
        markup = InlineKeyboardMarkup(buttons)
    else:
        markup = None
    await update.message.reply_text(text, reply_markup=markup)

async def show_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Boglanish:\n\nTelefon: " + TELEFON + "\nManzil: " + MANZIL + "\n\nIsh vaqti: 08:00 - 22:00")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Buyurtma berish":
        await show_categories(update, context)
    elif text == "Menyuni korish":
        await show_menu_text(update, context)
    elif text == "Savatcham":
        await show_cart(update, context)
    elif text == "Boglanish":
        await show_contacts(update, context)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("cat:"):
        cat = data[4:]
        items = MENYU.get(cat, {})
        buttons = [[InlineKeyboardButton(name + " - " + str(price) + " som", callback_data="add:" + name)] for name, price in items.items()]
        buttons.append([InlineKeyboardButton("Orqaga", callback_data="back")])
        await query.edit_message_text(cat + ":", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("add:"):
        item = data[4:]
        cart = context.user_data.get("cart", {})
        cart[item] = cart.get(item, 0) + 1
        context.user_data["cart"] = cart
        buttons = [[InlineKeyboardButton("Yana qoshish", callback_data="back_to_cats")], [InlineKeyboardButton("Buyurtmani tasdiqlash", callback_data="confirm")]]
        await query.edit_message_text(item + " savatga qoshildi!\n\n" + format_cart(cart), reply_markup=InlineKeyboardMarkup(buttons))

    elif data in ("back", "back_to_cats"):
        buttons = [[InlineKeyboardButton(cat, callback_data="cat:" + cat)] for cat in MENYU.keys()]
        await query.edit_message_text("Kategoriyani tanlang:", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "clear_cart":
        context.user_data["cart"] = {}
        await query.edit_message_text("Savatcha tozalandi!")

    elif data == "confirm":
        cart = context.user_data.get("cart", {})
        if not cart:
            await query.edit_message_text("Savatcha bosh!")
            return
        user = query.from_user
        order_text = format_cart(cart)
        await query.edit_message_text("Buyurtmangiz qabul qilindi!\n\n" + order_text + "\n\nTez orada boglanamiz!\n" + TELEFON)
        admin_msg = "YANGI BUYURTMA!\n\nMijoz: " + str(user.full_name) + "\nID: " + str(user.id) + "\n\n" + order_text
        try:
            await context.bot.send_message(ADMIN_ID, admin_msg)
        except Exception as e:
            print("Admin xabari yuborilmadi: " + str(e))
        context.user_data["cart"] = {}

if __name__ == "__main__":
    print("Bot ishga tushdi!")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()
