
# импортируем всё для плагина
from core.pluginapi import Plugin

import time

# создаём плагин
plugin = Plugin("CachedAPI", "Утилиты кэширования", "1.0.0", "ftdot", "https://github.com/ftdot")

# Конфиг
# Время кэша (cache_time)
#   время в секундах, сколько действует кэщ
plugin.default_config = {
  "cache_time": 6000
}

##########################
# врап на функцию для удобства
class CachedFunction:

  def __init__(self, func, args=()):
    self.func = func
    self.args = args

  def call(self):
    return self.func(*self.args)

  async def async_call(self):
    return await self.func(*self.args)

##########################
# класс для кэширования объектов
class Cached:

  def __init__(self):
    self.cached_objects = {}
    self.cache_time = 6000

  def force_cache(self, key, func): # принудительное кэширование
    cached_time = time.time()+self.cache_time
    object_ = func.call()

    self.cached_objects[key] = {'cached_time':cached_time, 'object': object_}

    return object_

  def cached_object(self, key, func): # возвращает\кэширует объект по ключу
    if key in self.cached_objects:

      if self.cached_objects[key]['cache_time'] >= time.time():
        return self.force_cache(key, func)

      return self.cached_objects[key]['object']
    else:
      return self.force_cache(key, func)

  ##########################

  async def async_force_cache(self, key, func): # принудительное кэширование
    cached_time = time.time()+self.cache_time
    object_ = await func.async_call()

    self.cached_objects[key] = {'cached_time':cached_time, 'object': object_}

    return object_

  async def async_cached_object(self, key, func): # возвращает\кэширует объект по ключу
    if key in self.cached_objects:

      if self.cached_objects[key]['cache_time'] >= time.time():
        return (await self.async_force_cache(key, func))

      return self.cached_objects[key]['object']

    else:
      return (await self.async_force_cache(key, func))

  def clear_cache(self): # очищает кэш
    del self.cached_objects
    self.cached_objects = {}

@plugin.load_config
def load_config(config): # загружаем конфиг
  plugin.set_config(config)

@plugin.load
def load(): # загружаем 
  cached_inst = Cached() # создаём экземпляр
  cached_inst.cache_time = plugin.config['cache_time']

  plugin.communicator.values.cached = cached_inst
  plugin.communicator.values.cached_function = CachedFunction

@plugin.unload
def unload(): # удаляем экземпляр
  del plugin.communicator.values.cached
  del plugin.communicator.values.cached_function