
import re # для регулярных выражений с base64
import base64 # для операций с base64

# импортируем всё для плагина
from core.pluginapi import Plugin

# Создаём плагин
plugin = Plugin("Core", "Ядро", "1.0.1", "ftdot", "https://github.com/ftdot")

# утилиты

@plugin.load
def load():
  global find_message_by_id, cached

  find_message_by_id = plugin.communicator.values.utils_find_message_by_id
  cached = plugin.communicator.values.cached

##########################
# Автоответчик (переписан)

ar_help_message = '❌ **Ошибка при использовании команды**\n🔹 Для включения надо написать сообщение (префикс)`ar 1` ответом на сообщение, которое вы хотите поставить на автоответ\n🔹 Для выключения, используйте (префикс)`ar 2`'

ar_success_message = '✅ **Автоответчик был включён!**\n🔹 Для выключения введите (префикс)`ar 2`'

class Autoreply:

  LIMIT = 200 # константа, отвечающая за то, в каких приделах будет искать сообщения

  enabled = False
  replied_to = []

  message = ""

@plugin.message_new()
async def autoreply_nm(event):

  # отправляем сообщение, если автоответчик включён и сообщение отправлено в ЛС
  if Autoreply.enabled:
    if event.is_private:
      if not event.sender_id in Autoreply.replied_to:
        await plugin.client.send_message(event.chat_id, Autoreply.message)
        Autoreply.replied_to.append(event.sender_id)

@plugin.command(names=['autoreply', 'ar', 'автоответчик', 'ао'])
async def cmd_ar(event, args):
  # проверяем аргументы
  if len(args) == 0:
    await plugin.client.edit_message(event.chat_id, event.message, ar_help_message)
    return

  # пробуем тайп-кастить
  try:
    i = int(args[0])
  except:
    await plugin.client.edit_message(event.chat_id, event.message, ar_help_message)
    return

  if i == 1: # включаем автоответчик

    if event.reply_to:
      # ищем сообщение в пределах лимита
      msg = await find_message_by_id(event.chat_id, event.reply_to.reply_to_msg_id, plugin.client, Autoreply.LIMIT)

      if msg: # сообщение найдено
        Autoreply.enabled = True
        Autoreply.replied_to = []

        Autoreply.message = msg.message

        await plugin.client.edit_message(event.chat_id, event.message, ar_success_message)
        return

  elif i == 2: # выключаем автоответчик
    if Autoreply.enabled:
      Autoreply.enabled = False

      await plugin.client.edit_message(event.chat_id, event.message, '✅ **Автоответчик выключен!**')
      return

    await plugin.client.edit_message(event.chat_id, event.message, '❌ **Автоответчик уже выключен.**')
    return

  await plugin.client.edit_message(event.chat_id, event.message, ar_help_message)

##########################
# 1000 - 7 (не менялось с 1.0)

TIMEOUT = 0.3

@plugin.command(names=['1000-7', '17', 'deadinside', 'дединсайд'])
async def cmd_1000_7(event, args):
  await Plugin.client.edit_message(event.chat_id, event.message, '1000-7 = '+str(1000-7)) # редачим сообщение
  r = 993

  while r >= 1: # отправляем подсчёты наши
    tsleep(TIMEOUT)
    d = r - 7
    await plugin.client.send_message(event.chat_id, f'{r} - 7 = {d}')
    r = d

##########################
# Калькулятор (частично переписан)

import math

async def calculate(event, expr): # выполняет простые выражения
  try:
    await plugin.client.edit_message(event.chat_id, event.message, '**Калькулятор:** `{}`'.format(eval(expr)))
    
  except Exception as e:
    await plugin.client.edit_message(event.chat_id, event.message, f'**Калькулятор:**\n🔸 Произошла внутренняя ошибка!\nОшибка: {e}')

@plugin.command(names=['calc', 'c', 'кальк', 'к'])
async def cmd_calc(event, args):
  if event.reply_to:
    msg = await find_message_by_id(event.chat_id, event.reply_to.reply_to_msg_id, plugin.client)

    if msg:
      expr = msg.message

      await calculate(event, expr)

  else:
    await calculate(event, ' '.join(args))

##########################
# Очистка кэша

@plugin.command(names=['clearcache', 'clrcache', 'очиститькэш', 'очсткэш'])
async def cmd_clearcache(event, args):
  cached.clear_cache()

  await plugin.client.send_message(event.chat_id, '✅ **Очистка кэша**\n🔹 Кэш был очищен.')

##########################
# операции с base64

re_check_compiled = re.compile(r'(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)')

async def base64_decode(event, text, regex=True): # декодирование текста
  b64_strings = re_check_compiled.findall(text) if regex else [text,]
  header = f'🔏 **BASE64** : Декодирование текста, найдено `{len(b64_strings)}` объектов.\n'

  for b64s in b64_strings:
    if len(b64s) >= 16:  pref = b64s[:5]+'...'+b64s[-5:]
    else:                pref = b64s

    b64_decoded = base64.b64decode(b64s.encode('utf-8')).decode('utf-8')
    text = text.replace(b64s, f'`{pref} = {b64_decoded}`')

  await plugin.client.edit_message(event.chat_id, event.message, header+text)

async def base64_encode(event, text): # кодирование текста
  header = f'🔏 **BASE64** : Кодирование текста.\n'

  enc = base64.b64encode(text.encode('utf-8')).decode('utf-8')

  await plugin.client.edit_message(event.chat_id, event.message, f'{header}`{enc}`')


# Декодирование всех base64 объектов в тексте, и вывод этого текста
@plugin.command(names=['base64decode', 'b64d', 'бейс64декод', 'б64д'])
async def cmd_base64_decode(event, args):
  if event.reply_to:
    msg = await find_message_by_id(event.chat_id, event.reply_to.reply_to_msg_id, plugin.client)

    if msg:
      text = msg.message

      await base64_decode(event, text)

  else:
    await base64_decode(event, ' '.join(args))

# Декодирование всего текста (без использования регулярных выражений)
@plugin.command(names=['base64decode_wre', 'b64dwre', 'бейс64декод_брв', 'б64дбрв'])
async def cmd_base64_decode_without_regex(event, args):
  if event.reply_to:
    msg = await find_message_by_id(event.chat_id, event.reply_to.reply_to_msg_id, plugin.client)

    if msg:
      text = msg.message

      await base64_decode(event, text, regex=False)

  else:
    await base64_decode(event, ' '.join(args), regex=False)

# Кодирование в base64
@plugin.command(names=['base64encode', 'b64e', 'бейс64енкод', 'б64е'])
async def cmd_base64_encode(event, args):
  if event.reply_to:
    msg = await find_message_by_id(event.chat_id, event.reply_to.reply_to_msg_id, plugin.client)

    if msg:
      text = msg.message

      await base64_encode(event, text)

  else:
    await base64_encode(event, ' '.join(args))