
# импортируем всё для плагина
from core.pluginapi import Plugin

# создаём плагин
plugin = Plugin("UtilsAPI", "Системные утилиты", "1.0.1", "ftdot", "https://github.com/ftdot")

async def find_message_by_id(chat_id, msg_id, client, limit=100): # поиск сообщения по айди
  async for msg in client.iter_messages(chat_id, limit):
    if msg.id == msg_id:
      return msg

@plugin.load
def load():
  # регистрация функции в коммуникаторе
  plugin.communicator.values.utils_find_message_by_id = find_message_by_id