from typing import Final
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
import emoji

TOKEN: Final = '6315355225:AAHjyOOu0DQi5Tfqi-UAfto3A_L_ld-XZKI'
BOT_USERNAME: Final = '@adikdn'

# Define states for the conversation
NAME, CHILD_NAME, RELATIONSHIP, GENDER = range(4)

## Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Selamat datang di layanan kami ' + emoji.emojize(':grinning_face_with_big_eyes:'))

async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Nama Anda?\n\n Jika ingin membatalkan pendaftaran silahkan ketik /cancel')
    return NAME

async def name_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.text.strip()
    if not user_name.replace(" ", "").isalpha():
        await update.message.reply_text('Nama tidak boleh mengandung simbol atau angka. Silakan masukkan nama Anda tanpa simbol atau angka.')
        return NAME  # Mengulangi langkah untuk meminta nama lagi
    else:
        context.user_data['name'] = user_name
        await update.message.reply_text('Nama buah hati Anda?')
        return CHILD_NAME

async def child_name_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    child_name = update.message.text.strip()
    if not child_name.replace(" ", "").isalpha():
        await update.message.reply_text('Nama buah hati tidak boleh mengandung simbol atau angka. Silakan masukkan nama buah hati Anda tanpa simbol atau angka.')
        return CHILD_NAME  # Mengulangi langkah untuk meminta nama buah hati lagi
    else:
        context.user_data['child_name'] = child_name
        reply_keyboard = [['Orang Tua', 'Guru', 'Kerabat']]
        await update.message.reply_text(
            "Apa hubungan anda dengan buah hati?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return RELATIONSHIP

async def relationship_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    relationship = update.message.text
    context.user_data['relationship'] = relationship
    reply_keyboard = [['Laki-laki', 'Perempuan']]
    await update.message.reply_text(
        "Jenis kelamin Anda?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return GENDER

async def gender_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gender = update.message.text
    context.user_data['gender'] = gender
    user_data = context.user_data

    biodata = (f"Terima kasih telah mendaftar!{emoji.emojize(':grinning_face_with_big_eyes:') }\n\n" 
               f"---Berikut Biodata Anda---\n"
               f"Nama Anda: {user_data['name']}\n"
               f"Nama buah hati: {user_data['child_name']}\n"
               f"Hubungan: {user_data['relationship']}\n"
               f"Jenis kelamin: {user_data['gender']}")

    await update.message.reply_text(biodata, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Pendaftaran dibatalkan.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def connect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Perangkat yang ingin dihubungkan:')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Berikut status buah hati: ')

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Berikut history status buah hati: ')

async def contactList_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Berikut daftar kontak rumah sakit terdekat yang Anda butuhkan: ')

async def myAccount_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Periksa detail akun anda')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Apa yang dapat kami bantu?')
    await update.message.reply_text('Jika bantuan ini kurang membantu anda dapat menghubungi kontak berikut: (No.Telp) ')

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    ## ConversationHandler for registration
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('register', register_command)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_received)],
            CHILD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, child_name_received)],
            RELATIONSHIP: [MessageHandler(filters.TEXT & ~filters.COMMAND, relationship_received)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender_received)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    ## Add handlers to the application
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('connect', connect_command))
    app.add_handler(CommandHandler('status', status_command))
    app.add_handler(CommandHandler('history', history_command))
    app.add_handler(CommandHandler('contactlist', contactList_command))
    app.add_handler(CommandHandler('myaccount', myAccount_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(conv_handler)

    ## Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)
