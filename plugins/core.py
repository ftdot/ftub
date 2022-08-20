
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
  if event.is_private:
    if Autoreply.enabled:
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

@plugin.command(names=['1000-7', '17', 'deadinside'])
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

async def calculate(event, expr):
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