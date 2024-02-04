from colorama import Fore, Style
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram.ext import CallbackContext, ContextTypes
import telepot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import subprocess
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
import requests
import asyncio

subprocess.run(["npm", "install", "-g", "javascript-obfuscator"], check=True)

user_state = {}

TOKEN = ''


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

async def command_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  chat_id = update.effective_chat.id
  framed_message = (
      '╔════════════╗\n'
      '       <b>GỬI FILE CẦN MÃ HOÁ</b>\n'
      '╚════════════╝'
  )

  await context.bot.send_message(chat_id, framed_message, parse_mode='HTML')

  context.user_data['awaiting_file'] = True


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  chat_id = update.effective_chat.id
  if context.user_data.get('awaiting_file'):
      document = update.message.document
      file_name = document.file_name.lower()

      if file_name.endswith('.js'):
          file = await context.bot.get_file(document.file_id)
          file_url = file.file_path

          file_path = f"{chat_id}.js"
          response = requests.get(file_url)
          if response.status_code == 200:
              with open(file_path, 'wb') as f:
                  f.write(response.content)
              keyboard = [
                  [
                      InlineKeyboardButton("Hexadecimal", callback_data='hexadecimal'),
                      InlineKeyboardButton("Mangled", callback_data='mangled'),
                  ],
                  [  
                      InlineKeyboardButton("Mangled-Shuffled", callback_data='mangled-shuffled'),
                  ],
                  [
                      InlineKeyboardButton("Dictionary", callback_data='dictionary'),
                  ],
              ]
              reply_markup = InlineKeyboardMarkup(keyboard)
              await context.bot.send_message(
                  chat_id, 
                  "<b>CHỌN LOẠI MÃ HOÁ</b>\n\n"
                  "<b>[+] Hexadecimal:</b> đổi tên biến theo dạng _0xabc123.\n"
                  "<b>[+] Mangled:</b> đổi tên biến thành các kí tự a,b,c.\n"
                  "<b>[+] Mangled Shuffled:</b> giống như Mangled nhưng các kí tự được xáo trộn từ bảng chữ cái.\n"
                  "<b>[+] Dictionary:</b> đổi tên biến thành tên tuỳ chọn của bạn ( giúp toàn bộ mã chứa tên của bạn ).", 
                  parse_mode='HTML',
                  reply_markup=reply_markup
              )



          else:
              await context.bot.send_message(chat_id, "Không thể tải file.")
      else:
          await context.bot.send_message(chat_id, "Vui lòng gửi một file JavaScript.")
      context.user_data['awaiting_file'] = False


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  query = update.callback_query
  await query.answer()
  identifier_names_generator_option = query.data
  chat_id = update.effective_chat.id
  data = query.data
  file_path = f"{chat_id}.js"
  encoded_file_path = f"{chat_id}_obfuscated.js"

  if data == 'dictionary':
      user_state[chat_id] = 'awaiting_var_name'
      await context.bot.send_message(chat_id, "Vui lòng nhập tên cho các biến .Bắt buộc phải trên 10 kí tự và tên biến cách nhau liền sau dấu phẩy nếu sử dụng nhiều tên biến.\n\n Ví dụ: buffadeptrai_hihi,buffacuteso1tg,vominhtudeptrai_hjhj")
  else:
      command = f"javascript-obfuscator {file_path} --output {encoded_file_path} --compact true --identifier-names-generator {identifier_names_generator_option} --control-flow-flattening true --control-flow-flattening-threshold 1 --dead-code-injection true --dead-code-injection-threshold 100 --debug-protection true --debug-protection-interval 4400 --disable-console-output false --log false --numbers-to-expressions true --rename-globals true --self-defending true --simplify true --split-strings true --split-strings-chunk-length 15 --string-array true --string-array-calls-transform true --string-array-encoding rc4,base64 --string-array-index-shift true --string-array-rotate true --string-array-shuffle true --string-array-wrappers-count 15 --string-array-wrappers-chained-calls true --string-array-wrappers-type variable --string-array-threshold 1 --transform-object-keys true --unicode-escape-sequence true --identifiers-prefix buffa_obfuscator --options-preset high-obfuscation --string-array-indexes-type hexadecimal-number,hexadecimal-numeric-string --seed 7102007 --ignore-imports true --string-array-calls-transform-threshold 1"
      release_memory = f"rm -rf {file_path} {encoded_file_path}"
      try:
          await context.bot.send_message(chat_id, f"Đang mã hoá file của bạn qua phương thức {identifier_names_generator_option}.")
          subprocess.run(command, shell=True, check=True)
          await context.bot.send_document(chat_id, document=open(encoded_file_path, 'rb'))
          subprocess.run(release_memory, shell=True, check=True)
      except subprocess.CalledProcessError as e:
          error_message = e.stderr
          await context.bot.send_message(chat_id, f"Có lỗi xảy ra trong quá trình mã hoá file: {error_message}")
          await asyncio.sleep(1)
          await context.bot.send_message(chat_id, "Vui lòng thử file khác.")
          subprocess.run(release_memory, shell=True, check=True)


async def handle_var_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  message = update.message.text
  chat_id = update.effective_chat.id

  if chat_id in user_state and user_state[chat_id] == 'awaiting_var_name':
      var_name = message.strip()  
      file_path = f"{chat_id}.js"
      encoded_file_path = f"{chat_id}_obfuscated.js"
      release_memory = f"rm -rf {file_path} {encoded_file_path}"

      command = f"javascript-obfuscator {file_path} --output {encoded_file_path} --compact true --identifier-names-generator dictionary --identifiers-dictionary {var_name} --control-flow-flattening true --control-flow-flattening-threshold 1 --dead-code-injection true --dead-code-injection-threshold 100 --debug-protection true --debug-protection-interval 4400 --disable-console-output false --log false --numbers-to-expressions true --rename-globals true --self-defending true --simplify true --split-strings true --split-strings-chunk-length 15 --string-array true --string-array-calls-transform true --string-array-encoding rc4,base64 --string-array-index-shift true --string-array-rotate true --string-array-shuffle true --string-array-wrappers-count 15 --string-array-wrappers-chained-calls true --string-array-wrappers-type variable --string-array-threshold 1 --transform-object-keys true --unicode-escape-sequence true --identifiers-prefix buffa_obfuscator --options-preset high-obfuscation --string-array-indexes-type hexadecimal-number,hexadecimal-numeric-string --seed 7102007 --ignore-imports true --string-array-calls-transform-threshold 1"
      try:

          await context.bot.send_message(chat_id, "Đang mã hoá file của bạn qua phương thức Dictionary.")
          subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
          await context.bot.send_document(chat_id, document=open(encoded_file_path, 'rb'))
          subprocess.run(release_memory, shell=True, check=True)
      except subprocess.CalledProcessError as e:

          error_message = e.stderr

          await context.bot.send_message(chat_id, f"Có lỗi xảy ra trong quá trình mã hoá file: {error_message}")
          await asyncio.sleep(1)
          await context.bot.send_message(chat_id, "Vui lòng thử file khác.")
          subprocess.run(release_memory, shell=True, check=True)
      del user_state[chat_id]



app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler('jsobf', command_file))
app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_var_name))


bot = telepot.Bot(TOKEN)
bot_info = bot.getMe()
bot_name = bot_info['first_name']
bot_username = bot_info['username']
clear_screen()
print(Fore.RED + '''
██████╗ ██╗   ██╗███████╗███████╗ █████╗        ██████╗  ██████╗ ████████╗
██╔══██╗██║   ██║██╔════╝██╔════╝██╔══██╗       ██╔══██╗██╔═══██╗╚══██╔══╝
██████╔╝██║   ██║█████╗  █████╗  ███████║       ██████╔╝██║   ██║   ██║   
██╔══██╗██║   ██║██╔══╝  ██╔══╝  ██╔══██║       ██╔══██╗██║   ██║   ██║   
██████╔╝╚██████╔╝██║     ██║     ██║  ██║       ██████╔╝╚██████╔╝   ██║   
╚═════╝  ╚═════╝ ╚═╝     ╚═╝     ╚═╝  ╚═╝       ╚═════╝  ╚═════╝    ╚═╝   


''' + Style.RESET_ALL)
connection_message = f"Đã kết nối thành công tới {bot_name} (@{bot_username})"
border = "═" * (len(connection_message) + 4)
print(Fore.LIGHTGREEN_EX + f"╔{border}╗\n║  {connection_message}  ║\n╚{border}╝" + Style.RESET_ALL)

app.run_polling()
