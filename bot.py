from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import requests

# Replace with your Google Apps Script URL
BASE_URL = "https://script.google.com/macros/s/AKfycbyRZz1HLg0maMFHfaeW7qEX1mVUoVVgH05Q51q7xh7Aq59nZqYxGwWZZLumuk2CmkAW/exec"

# Global variables to store user inputs
user_inputs = {}

# Start command
def start(update: Update, context: CallbackContext) -> None:
    keyboard = [[InlineKeyboardButton("Add Item", callback_data='add_item')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Welcome! Use the button below to add an item:", reply_markup=reply_markup)

# Callback handler for the "Add Item" button
def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'add_item':
        context.user_data['action'] = 'add_item'
        query.edit_message_text("Enter item name:")

# Handle user input for adding an item
def handle_message(update: Update, context: CallbackContext) -> None:
    action = context.user_data.get('action')

    if action == 'add_item':
        if 'item_name' not in user_inputs:
            user_inputs['item_name'] = update.message.text
            update.message.reply_text("Enter quantity:")
        elif 'quantity' not in user_inputs:
            user_inputs['quantity'] = int(update.message.text)
            update.message.reply_text("Enter unit price:")
        elif 'unit_price' not in user_inputs:
            user_inputs['unit_price'] = float(update.message.text)
            user_inputs['total_price'] = user_inputs['quantity'] * user_inputs['unit_price']

            # Automatically generate the next ID
            last_id = get_last_id()
            new_id = f"No{int(last_id[2:]) + 1}"

            user_inputs['id'] = new_id
            add_item_to_sheet(user_inputs)

            update.message.reply_text(f"Item added successfully with ID {new_id}!")
            user_inputs.clear()
            context.user_data['action'] = None

# Fetch the last ID from the Inventory sheet
def get_last_id():
    response = requests.get(f"{BASE_URL}?sheet=Inventory")
    data = response.json() if response.status_code == 200 else []
    return data[-1]['ID'] if data else "No0"

# Add a new item to the sheet
def add_item_to_sheet(item):
    payload = {
        "id": item['id'],
        "item_name": item['item_name'],
        "quantity": item['quantity'],
        "unit_price": item['unit_price'],
        "total_price": item['total_price'],
    }
    requests.post(f"{BASE_URL}?sheet=add_item", json=payload)

# Main function
def main():
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
