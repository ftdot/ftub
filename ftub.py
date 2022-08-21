
# developed by ftdot with love <3

from core.colors import Fore # цветной вывод
from core.pluginmanager import PluginManager # менеджер аддонов
from core.pluginapi import Communicator # коммуникатор

from telethon import TelegramClient, sync # для обработки сообщений тг
from telethon import events # тоже  ^
from telethon.tl.types import Message # ну типизация

from datetime import datetime # для времени

#########################
# НАСТРОЙКИ
api_id = -1
api_hash = ''

ub_onwer_id = -1 # айди владельца
ub_prefixes = ['таб.', 'tub.', 'т!', 't!'] # префиксы юзербота

dev_mode = False # режим разработчика плагинов.
#
#########################

# fTUB - инициализация
client = TelegramClient('ftub', api_id, api_hash)
client.start() # старт юзербота

pm = PluginManager(debug_mode=dev_mode) # менеджер аддонов
pcommunicator = Communicator() # коммуникатор для плагинов

##########################
# Утилиты

def have_prefixes(message): # проверка на префиксы, возвращает префикс
  for p in ub_prefixes:
    if message.lower().startswith(p):
      return p

async def check_for_command(event): # проверка на команду
  if event.sender_id != ub_onwer_id: return

  p = have_prefixes(event.text)
  if not p: return

  tmp = event.text.split(' ')

  cmd = tmp[0].lower().removeprefix(p) # название команды
  args = tmp[1:] # аргументы к команде

  await pm.execute_command(event, cmd, args)

async def raise_event_IC(en, event): # спровоцр. событие с аргументом is_command

  is_command = True if have_prefixes(event.text) else False

  await pm.raise_event(en, event, True, is_command)

##########################
# Ловля (рыбалка чиста) сообщений

@client.on(events.NewMessage) # ловим новое сообщение
async def handler(event):
  if not isinstance(event.message, Message): return # проверка на сообщение

  event.ub_date = event.message.date.strftime("%m.%d.%Y %H:%M:%S") # получение текущего времени

  await raise_event_IC('message_new', event)
  await check_for_command(event)

@client.on(events.MessageDeleted) # ловим удаление
async def handler(event):
  event.ub_date = datetime.now().strftime("%m.%d.%Y %H:%M:%S") # получение текущего времени

  await pm.raise_event('message_deleted', event, False)

@client.on(events.MessageEdited) # ловим редакт.
async def handler(event):
  event.ub_date = datetime.now().strftime("%m.%d.%Y %H:%M:%S") # получение текущего времени

  await raise_event_IC('message_edited', event)

##########################

if ub_onwer_id == -1:
  print(f'{Fore.RED}{Fore.RED}Вы не указали айди владельца! Обратитесь к гайду по установке')

if dev_mode: print(f'{Fore.CYAN}[i] Начинаем регистрацию плагинов{Fore.RESET}')
pm.register_plugins() # регистрируем плагины
pcommunicator.init(pm.plugins) # инициализируем коммуникатор
pm.register_specialities(client, pcommunicator) # регистрируем клиента
 
client.run_until_disconnected()