import os
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
# =========================
# НАСТРОЙКИ БОТА
# =========================
WELCOME_TEXT = """Здравствуйте! Вас приветствует проводник в сеть каналов Сеймей. Что вы хотели?
Переходник @SeimeiAdapters"""
# Здесь позже можно менять названия кнопок
BUTTON_DONATE = "💫 Поддержать проект"
BUTTON_CHANNELS = "📡 Каналы Сеймей"
BUTTON_CONTACT = "📞 Связаться"
# Суммы донатов в Telegram Stars
DONATION_AMOUNTS = {
    "donate_50": 50,
    "donate_100": 100,
    "donate_250": 250,
    "donate_500": 500,
}
# =========================
# КОМАНДА /start
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(BUTTON_DONATE, callback_data="donate")],
        [InlineKeyboardButton(BUTTON_CHANNELS, url="https://t.me/SeimeiAdapters")],
        [InlineKeyboardButton(BUTTON_CONTACT, callback_data="contact")],
    ]
    await update.message.reply_text(
        WELCOME_TEXT,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
# =========================
# КНОПКИ
# =========================
async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()
    if query.data == "donate":
        keyboard = [
            [
                InlineKeyboardButton("⭐ 50", callback_data="donate_50"),
                InlineKeyboardButton("⭐ 100", callback_data="donate_100"),
            ],
            [
                InlineKeyboardButton("⭐ 250", callback_data="donate_250"),
                InlineKeyboardButton("⭐ 500", callback_data="donate_500"),
            ],
        ]
        await query.message.reply_text(
            "Выберите сумму поддержки ⭐",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    elif query.data == "contact":
        await query.message.reply_text(
            "По вопросам связи: @SeimeiAdapters"
        )
    elif query.data in DONATION_AMOUNTS:
        amount = DONATION_AMOUNTS[query.data]
        prices = [
            LabeledPrice(
                label=f"Поддержка проекта — {amount} ⭐",
                amount=amount,
            )
        ]
        await context.bot.send_invoice(
            chat_id=query.message.chat_id,
            title="Поддержка проекта",
            description=f"Донат на {amount} Telegram Stars ⭐",
            payload=f"donation_{amount}",
            currency="XTR",
            prices=prices,
        )
# =========================
# ПРОВЕРКА ПЕРЕД ОПЛАТОЙ
# =========================
async def precheckout_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.pre_checkout_query
    await query.answer(ok=True)
# =========================
# УСПЕШНАЯ ОПЛАТА
# =========================
async def successful_payment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    payment = update.message.successful_payment
    await update.message.reply_text(
        "Спасибо огромное за поддержку! ❤️\n\n"
        f"Получено: ⭐ {payment.total_amount}\n\n"
        "Ваша поддержка помогает проекту развиваться."
    )
# =========================
# ОБЫЧНЫЕ СООБЩЕНИЯ
# =========================
async def unknown_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "Я пока не понял ваш запрос. Используйте /start, чтобы открыть меню."
    )
# =========================
# ЗАПУСК
# =========================
def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Переменная BOT_TOKEN не установлена.")
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(
        MessageHandler(
            filters.SUCCESSFUL_PAYMENT,
            successful_payment,
        )
    )
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            unknown_message,
        )
    )
    print("Бот запущен!")
    application.run_polling()
if __name__ == "__main__":
    main()
