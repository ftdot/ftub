
# импортируем всё для плагина
from core.pluginapi import Plugin

# создаём плагин
plugin = Plugin("CoreRP", "РП-Действия", "1.0.0", "ftdot", "https://github.com/ftdot")

# для облегчения создания РП команд
async def rp_action(event, emoji, action):
  await plugin.client.edit_message(event.chat_id, event.message, f'{emoji} Я {action} тебя')

##########################
# РП действия

@plugin.command(names=['kiss', 'поцеловать'])
async def cmd_kiss(event, args): await rp_action(event, '😘', 'поцеловал(а)')

@plugin.command(names=['hug', 'обнять'])
async def cmd_hug(event, args): await rp_action(event, '🤗', 'обнял(а)')

@plugin.command(names=['bite', 'кусь'])
async def cmd_bite(event, args): await rp_action(event, '😬', 'кусьнул(а)')

@plugin.command(names=['nsfw_sex', 'нсфв_секс'])
async def cmd_nsfw_sex(event, args): await rp_action(event, '🤗', 'трахнул(а)')