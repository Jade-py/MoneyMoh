import requests
import os
from datetime import datetime
import calendar
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import BadRequest
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes, \
    CallbackQueryHandler
from environs import Env

env = Env()
env.read_env()

# Replace with your actual API endpoint
API_ENDPOINT = "http://127.0.0.1:8000"

# Replace with your Telegram Bot Token
TOKEN = os.environ["BOT_TOKEN"]

# Define conversation states
CHOOSING, SELECT_LIST_TYPE, SELECT_DATE, EVENT, PRICE = range(5)


def create_calendar(year, month):
    keyboard = []
    # Add month and year at the top
    keyboard.append([InlineKeyboardButton(f"{calendar.month_name[month]} {year}", callback_data="ignore")])

    # Add days of the week as the second row
    week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    keyboard.append([InlineKeyboardButton(day, callback_data="ignore") for day in week_days])

    # Add the calendar dates
    month_calendar = calendar.monthcalendar(year, month)
    for week in month_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(" ", callback_data="ignore"))
            else:
                row.append(InlineKeyboardButton(str(day), callback_data=f"date_{year}-{month:02d}-{day:02d}"))
        keyboard.append(row)

    # Add navigation buttons
    keyboard.append([
        InlineKeyboardButton("<<", callback_data=f"prev_{year}_{month}"),
        InlineKeyboardButton("Done", callback_data="done"),
        InlineKeyboardButton(">>", callback_data=f"next_{year}_{month}"),
        InlineKeyboardButton("Cancel", callback_data="cancel")
    ])

    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("Add Expense", callback_data='add'),
         InlineKeyboardButton("List Expenses", callback_data='list'),
         ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! Please choose an option:", reply_markup=reply_markup)
    return CHOOSING


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [[InlineKeyboardButton("Cancel", callback_data='cancel')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    await query.answer()

    if query.data == 'add':
        await query.edit_message_text("Great! What's the event name?", reply_markup=reply_markup)
        return EVENT
    elif query.data == 'list':
        now = datetime.now()
        calendar_markup = create_calendar(now.year, now.month)
        await query.edit_message_text("Please select date(s):", reply_markup=calendar_markup)
        return SELECT_DATE
    elif query.data == 'cancel':
        await query.edit_message_text("Operation cancelled. Type /start to begin again")
        return ConversationHandler.END
    elif query.data == 'retry':
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("Let's try again. What's the event name?", reply_markup=reply_markup)
        return EVENT


async def calendar_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data.startswith("date_"):
        date = query.data.split("_")[1]
        if 'selected_dates' not in context.user_data:
            context.user_data['selected_dates'] = set()
        if date in context.user_data['selected_dates']:
            context.user_data['selected_dates'].remove(date)
        else:
            context.user_data['selected_dates'].add(date)

        year, month, _ = map(int, date.split("-"))
        calendar_markup = create_calendar(year, month)
        try:
            await query.edit_message_text(f"Selected dates: {', '.join(context.user_data['selected_dates'])}",
                                          reply_markup=calendar_markup)
        except BadRequest as e:
            if str(e) != "Message is not modified":
                raise

    elif query.data.startswith("prev_") or query.data.startswith("next_"):
        parts = query.data.split("_")
        if len(parts) >= 3:
            action, year, month = parts[:3]
            year = int(year)
            month = int(month)
            if action == "prev":
                month -= 1
                if month == 0:
                    month = 12
                    year -= 1
            elif action == "next":
                month += 1
                if month == 13:
                    month = 1
                    year += 1
            calendar_markup = create_calendar(year, month)
            try:
                await query.edit_message_text("Please select date(s):", reply_markup=calendar_markup)
            except BadRequest as e:
                if str(e) != "Message is not modified":
                    raise

    elif query.data == "done":
        return await fetch_expenses(update, context)

    elif query.data == 'cancel':
        await query.edit_message_text("Operation cancelled. Type /start to begin again.")
        return ConversationHandler.END

    return SELECT_DATE


async def get_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("Cancel", callback_data='cancel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        context.user_data['event'] = query.data
        await query.edit_message_text("Great! Now, what's the price?", reply_markup=reply_markup)
    else:
        context.user_data['event'] = update.message.text
        await update.message.reply_text("Great! Now, what's the price?", reply_markup=reply_markup)

    return PRICE


async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        price = float(update.message.text)
        context.user_data['price'] = price

        # Send data to the API
        event = context.user_data['event']
        data = {
            'event': event,
            'price': price
        }

        try:
            response = requests.post(f"{API_ENDPOINT}post/", json=data)

            if response.status_code == 201:
                print(response.text)
                keyboard = [
                    [InlineKeyboardButton("Add New Expense", callback_data='add'),
                     InlineKeyboardButton("List Expenses", callback_data='list'),
                     InlineKeyboardButton("Cancel", callback_data='cancel')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text("Data saved successfully!", reply_markup=reply_markup)
                return CHOOSING
            else:
                keyboard = [
                    [InlineKeyboardButton("Retry", callback_data='retry'),
                     InlineKeyboardButton("Cancel", callback_data='cancel')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(f"Error saving data. Status code: {response.status_code}",
                                                reply_markup=reply_markup)
                return CHOOSING
        except requests.RequestException as e:
            keyboard = [[InlineKeyboardButton("Retry", callback_data='retry')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"Error connecting to the server: {str(e)}", reply_markup=reply_markup)
            return CHOOSING

    except Exception as e:
        print(e)
        await update.message.reply_text("Invalid price. Please enter a number.")
        return PRICE


async def fetch_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    selected_dates = context.user_data.get('selected_dates', set())
    if not selected_dates:
        await query.edit_message_text("No dates selected. Please select dates first. /start again")
        return SELECT_DATE

    print("Selected dates: ", selected_dates)
    keyboard = [
        [InlineKeyboardButton("Add New Expense", callback_data='add'),
         InlineKeyboardButton("List Expenses", callback_data='list')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    a = []

    for date in selected_dates:
        print(date)
        try:
            year, month, day = date.split('-')
            response = requests.get(f"{API_ENDPOINT}get/{year}/{month}/{day}")

            if response.status_code == 200:
                expenses = response.json().get('data', [])
                if expenses:
                    expense_text = []
                    for exp in expenses:
                        date_obj = datetime.fromisoformat(exp['date'].replace('Z', '+00:00'))
                        formatted_date = date_obj.strftime("%d %b %H:%M")
                        expense_text.append(f"{exp['event']}: {exp['price']}Rs on {formatted_date}")
                    expense_text = "\n".join(expense_text)
                    a.append(expense_text)
                    await query.edit_message_text(f"Searching expenses on {date}")
                else:
                    await query.edit_message_text(f"No expenses found for the selected date {date}")
                    a.append(f'No expenses found for the selected date {date}')
            else:
                a.append(f"Error fetching data. Status code: {response.status_code}")
                await query.edit_message_text(f"Error fetching data. Status code: {response.status_code}")
        except requests.RequestException as e:
            a.append(f"Error fetching data. Status code: {str(e)}")
            await query.edit_message_text(f"Error fetching data: {str(e)}")

    await query.edit_message_text("".join(e+'\n' for e in a), reply_markup=reply_markup)
    context.user_data['selected_dates'] = set()  # Clear selected dates
    return CHOOSING


async def retry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Let's try again. What's the event name?")
    return CHOOSING


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Operation cancelled. Type /start to begin again.")
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [CallbackQueryHandler(button_click)],
            SELECT_DATE: [CallbackQueryHandler(calendar_handler)],
            EVENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_event),
                    CallbackQueryHandler(cancel, pattern='^cancel$')],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price),
                    CallbackQueryHandler(cancel, pattern='^cancel$')],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(retry, pattern='^retry$'))

    application.run_webhook(listen="0.0.0.0", port=8080, webhook_url="https://moneymoh.onrender.com")()


if __name__ == "__main__":
    main()