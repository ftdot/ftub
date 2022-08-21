
import random

# импортируем всё для плагина
from core.pluginapi import Plugin

from telethon.tl.functions.users import GetFullUserRequest

# Создаём плагин
plugin = Plugin("CoreFun", "Веселья", "1.0.0", "ftdot", "https://github.com/ftdot")

@plugin.load
def load():
  global cached, cached_func

  cached = plugin.communicator.values.cached
  cached_func = plugin.communicator.values.cached_function


async def get_peer_id(event): return (await plugin.client(GetFullUserRequest(event.peer_id)))
async def get_from_id(event): return (await plugin.client(GetFullUserRequest(event.from_id)))

##########################
# кто ...

@plugin.command(names=['who', 'кто'])
async def cmd_who_is(event, args):
  text = ' '.join(args).replace('?', '')

  if event.is_private:

    member1 = await cached.async_cached_object(event.peer_id.user_id, cached_func(get_peer_id,(event,)))
    author = await cached.async_cached_object(event.from_id.user_id, cached_func(get_from_id,(event,)))

    who = random.choice([member1.user.first_name, author.user.first_name])

    await plugin.client.edit_message(event.chat_id, event.message, f'❓ Кто {text}?\n🔸 Шарманка думает что `{who}` {text}')

##########################
# кого ...

@plugin.command(names=['whowas', 'кого'])
async def cmd_who_was(event, args):
  text = ' '.join(args).replace('?', '')

  if event.is_private:

    member1 = await cached.async_cached_object(event.peer_id.user_id, cached_func(get_peer_id,(event,)))
    author = await cached.async_cached_object(event.from_id.user_id, cached_func(get_from_id,(event,)))

    whowas = random.choice([member1.user.first_name, author.user.first_name])

    await plugin.client.edit_message(event.chat_id, event.message, f'❓ Кого {text}?\n🔸 Шарманка думает что `{whowas}` {text}')

##########################
# ДА или НЕТ

@plugin.command(names=['yesno', 'данет'])
async def cmd_yesno(event, args):
  yesno = random.choice(['✅ Да', '❌ Нет'])

  await plugin.client.edit_message(event.chat_id, event.message, f'**❓ Да\\Нет ❓**\n🔸 Шарманка думает что `{yesno}`')

##########################
# ПРАВДА или НЕ ПРАВДА

@plugin.command(names=['trueorfalse', 'tof', 'правдаилинет', 'пле'])
async def cmd_tof(event, args):
  true_or_false = random.choice(['✅ правда', '❌ не правда'])

  await plugin.client.edit_message(event.chat_id, event.message, f'**✅❌ Правда или не правда ❓❓**\n🔸 Шарманка думает что `{true_or_false}`')