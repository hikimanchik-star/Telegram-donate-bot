import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

WELCOME_TEXT = """Здравствуйте! Вас приветствует проводник в сеть каналов Сеймей. Что вы хотели?

Переходник @SeimeiAdapters"""

DONATION_AMOUNTS = {
    "50": 50,
    "100": 100,
    "250": 250,
    "500": 500,
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💫 Поддержать проект", callback_data="donate")],
        [
            InlineKeyboardButton(
                "📡 Каналы Сеймей",
                url="https://t.me/SeimeiAdapters"
            )
        ],
        [
            InlineKeyboardButton(
                "📞 Связаться",
                url="https://t.me/SeimeiAdapters"
            )
        ],
    ]

    await update.message.reply_text(
        WELCOME_TEXT,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "donate":
        keyboard = [
            [
                InlineKeyboardButton("⭐ 50", callback_data="50"),
                InlineKeyboardButton("⭐ 100", callback_data="100"),
            ],
            [
                InlineKeyboardButton("⭐ 250", callback_data="250"),
                InlineKeyboardButton("⭐ 500", callback_data="500"),
            ],
        ]

        await query.message.reply_text(
            "Выберите сумму поддержки ⭐",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return

    if query.data in DONATION_AMOUNTS:
        amount = DONATION_AMOUNTS[query.data]

        await context.bot.send_invoice(
            chat_id=query.message.chat_id,
            title="Поддержка Сеймей",
            description=f"Добровольная поддержка проекта — {amount} ⭐",
            payload=f"donation_{amount}",
            currency="XTR",
            prices=[
                LabeledPrice(
                    label=f"Поддержка проекта — {amount} ⭐",
                    amount=amount
                )
            ],
        )


async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stars = update.message.successful_payment.total_amount

    await update.message.reply_text(
        f"Спасибо за поддержку! ❤️\n\n"
        f"Получено: ⭐ {stars}\n\n"
        "Ваша поддержка помогает проекту развиваться."
    )


async def other_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Используйте /start, чтобы открыть меню."
    )


def main():
    token = os.getenv("BOT_TOKEN")

    if not token:
        raise RuntimeError("BOT_TOKEN не установлен")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(PreCheckoutQueryHandler(precheckout))

    app.add_handler(
        MessageHandler(
            filters.SUCCESSFUL_PAYMENT,
            successful_payment
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            other_message
        )
    )

    print("Бот запущен!")

    app.run_polling()


if __name__ == "__main__":
    main()
