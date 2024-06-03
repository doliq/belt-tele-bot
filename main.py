from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, filters, ContextTypes
import emoji
import os
import pandas as pd

# Token dan username bot
TOKEN: Final = '6862559344:AAHYZG_2VSnYsdyArs62WogXHRLLQxdBMkw'
BOT_USERNAME: Final = '@yoursafetybelt_teddyBot'

# Define stages
NAME, CHILD_NAME, RELATIONSHIP, ID_SABUK, GENDER, CONFIRM, EDIT_CHOICE, CONNECT  = range(8)

def save_to_excel(user_data):
    df = pd.DataFrame([user_data])
    directory = "C:\\fall-detect"  # Ubah ke direktori yang diinginkan

    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, 'registrations.xlsx')

    try:
        if os.path.exists(file_path):
            with pd.ExcelWriter(file_path, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                if 'Sheet1' in writer.book.sheetnames:
                    start_row = writer.sheets['Sheet1'].max_row
                    df.to_excel(writer, index=False, header=False, startrow=start_row)
                else:
                    df.to_excel(writer, index=False, header=True)
        else:
            df.to_excel(file_path, index=False)
        print(f'File saved to {file_path}')
    except Exception as e:
        print(f'Error saving file: {e}')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Halo! Selamat datang di layanan kami ' + emoji.emojize(':grinning_face_with_big_eyes:'))

async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Nama Anda?\n\n Jika ingin membatalkan pendaftaran silahkan ketik /cancel')
    return NAME

async def name_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.text.strip()
    if not user_name.replace(" ", "").isalpha():
        await update.message.reply_text('Nama tidak boleh mengandung simbol atau angka. Silakan masukkan nama Anda tanpa simbol atau angka.')
        return NAME
    else:
        context.user_data['name'] = user_name
        if context.user_data.get('edit_mode'):
            context.user_data['edit_mode'] = False
            await show_confirmation(update, context)
            return CONFIRM
        await update.message.reply_text('Nama buah hati Anda?')
        return CHILD_NAME

async def child_name_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    child_name = update.message.text.strip()
    if not child_name.replace(" ", "").isalpha():
        await update.message.reply_text('Nama buah hati tidak boleh mengandung simbol atau angka. Silakan masukkan nama buah hati Anda tanpa simbol atau angka.')
        return CHILD_NAME
    else:
        context.user_data['child_name'] = child_name
        if context.user_data.get('edit_mode'):
            context.user_data['edit_mode'] = False
            await show_confirmation(update, context)
            return CONFIRM
        reply_keyboard = [['Orang Tua', 'Guru', 'Kerabat']]
        await update.message.reply_text(
            "Apa hubungan anda dengan buah hati?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return RELATIONSHIP

async def relationship_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    relationship = update.message.text
    context.user_data['relationship'] = relationship
    if context.user_data.get('edit_mode'):
        context.user_data['edit_mode'] = False
        await show_confirmation(update, context)
        return CONFIRM
    await update.message.reply_text('ID sabuk Anda?')
    return ID_SABUK

async def id_sabuk_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id_sabuk = update.message.text.strip()
    context.user_data['id_sabuk'] = id_sabuk
    if context.user_data.get('edit_mode'):
        context.user_data['edit_mode'] = False
        await show_confirmation(update, context)
        return CONFIRM
    reply_keyboard = [['Laki-laki', 'Perempuan']]
    await update.message.reply_text(
        "Jenis kelamin Anda?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return GENDER

async def gender_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gender = update.message.text
    context.user_data['gender'] = gender
    await show_confirmation(update, context)
    return CONFIRM

async def show_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    biodata = (f"--- Berikut Biodata Anda ---\n"
            f"Nama Anda: {user_data['name']}\n"
            f"Nama buah hati: {user_data['child_name']}\n"
            f"ID Sabuk: {user_data['id_sabuk']}\n"
            f"Hubungan: {user_data['relationship']}\n"
            f"Jenis kelamin: {user_data['gender']}\n\n"
            "Apakah Anda ingin menyimpan biodata ini?")

    keyboard = [
        [InlineKeyboardButton("Setuju", callback_data='setuju')],
        [InlineKeyboardButton("Edit", callback_data='edit')],
        [InlineKeyboardButton("Batalkan", callback_data='batalkan')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(biodata, reply_markup=reply_markup)

async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'setuju':
        save_to_excel(context.user_data)
        await query.edit_message_text(text="Biodata Anda telah disimpan. Terima kasih! " + emoji.emojize(':grinning_face_with_big_eyes:'))
        return ConversationHandler.END
    elif query.data == 'edit':
        keyboard = [
            [InlineKeyboardButton("Nama Anda", callback_data='edit_name')],
            [InlineKeyboardButton("Nama buah hati", callback_data='edit_child_name')],
            [InlineKeyboardButton("Hubungan", callback_data='edit_relationship')],
            [InlineKeyboardButton("ID Sabuk", callback_data='edit_id_sabuk')],
            [InlineKeyboardButton("Jenis kelamin", callback_data='edit_gender')],
            [InlineKeyboardButton("Batal", callback_data='batal')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Bagian mana yang ingin Anda edit?", reply_markup=reply_markup)
        return EDIT_CHOICE
    elif query.data == 'batalkan':
        await query.edit_message_text(text="Pendaftaran Anda telah dibatalkan.")
        return ConversationHandler.END

async def edit_choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data['edit_mode'] = True  # Set edit mode

    if query.data == 'edit_name':
        await query.edit_message_text(text="Nama Anda?")
        return NAME
    elif query.data == 'edit_child_name':
        await query.edit_message_text(text="Nama buah hati Anda?")
        return CHILD_NAME
    elif query.data == 'edit_relationship':
        reply_keyboard = [['Orang Tua', 'Guru', 'Kerabat']]
        await query.message.reply_text(
            text="Apa hubungan anda dengan buah hati?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return RELATIONSHIP
    elif query.data == 'edit_id_sabuk':
        await query.edit_message_text(text="ID sabuk Anda?")
        return ID_SABUK
    elif query.data == 'edit_gender':
        reply_keyboard = [['Laki-laki', 'Perempuan']]
        await query.message.reply_text(
            text="Jenis kelamin Anda?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return GENDER
    elif query.data == 'batal':
        await show_confirmation(query, context)  # Menampilkan kembali formulir konfirmasi
        return CONFIRM
    elif query.data == 'cancel':
        await query.edit_message_text(text="Pendaftaran Anda telah dibatalkan.")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Pendaftaran dibatalkan.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def connect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ambil daftar ID sabuk yang telah terdaftar dari file Excel
    directory = "C:\\fall-detect"
    file_path = os.path.join(directory, 'registrations.xlsx')
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        sabuk_ids = df['id_sabuk'].unique().tolist()
    else:
        sabuk_ids = []

    # Buat daftar tombol dengan ID sabuk
    keyboard = [[InlineKeyboardButton(sabuk_id, callback_data=sabuk_id)] for sabuk_id in sabuk_ids]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Silakan pilih ID sabuk yang ingin Anda hubungkan:",
        reply_markup=reply_markup
    )
    return CONNECT

async def connect_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    chosen_id = query.data
    # Lakukan sesuatu dengan ID sabuk yang dipilih, misalnya menyimpan ke context.user_data atau memproses lebih lanjut
    context.user_data['chosen_id'] = chosen_id
    await query.edit_message_text(text=f"Anda telah menghubungkan dengan ID sabuk: {chosen_id}")
    
    # Lanjutkan ke langkah berikutnya atau akhiri percakapan
    return ConversationHandler.END

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # ConversationHandler for registration
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('register', register_command)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_received)],
            CHILD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, child_name_received)],
            RELATIONSHIP: [MessageHandler(filters.TEXT & ~filters.COMMAND, relationship_received)],
            ID_SABUK: [MessageHandler(filters.TEXT & ~filters.COMMAND, id_sabuk_received)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender_received)],
            CONFIRM: [CallbackQueryHandler(confirm_handler, pattern='^(setuju|edit|batalkan)$')],
            EDIT_CHOICE: [CallbackQueryHandler(edit_choice_handler, pattern='^(edit_name|edit_child_name|edit_relationship|edit_id_sabuk|edit_gender|batal|cancel)$')],
            CONNECT: [CallbackQueryHandler(connect_handler)]  # Tambahkan handler untuk CONNECT state
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('connect', connect_command))
    app.add_handler(conv_handler)

    print('Polling...')
    app.run_polling(poll_interval=1.0)