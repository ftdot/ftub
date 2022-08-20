
import os # для работы с файлами\дирекаториями
import json # для работы с JSON (конфигурациями аддонов)

##########################
# Основа для любого плагина
class Plugin:

  def __init__(self, plugin_name, plugin_description, plugin_version, plugin_author, plugin_author_contact):
    self.plugin_name = plugin_name
    self.plugin_description = plugin_description
    self.plugin_version = plugin_version
    self.plugin_author = plugin_author
    self.plugin_author_contact = plugin_author_contact

    self.commands = {}
    self.events = {'load': [], 'load_config': [], 'unload': [], 'message_new': [], 'message_edited': [], 'message_deleted': []}

    self.client = None # ссылка на клиент telethon
    self.communicator = None # ссылка на коммуникатор

    self.default_config = {} # конфигурация плагина по умолчанию
    self.config = {}

  ##########################
  # геттеры для удобства

  def get_name(self): return self.plugin_name
  def get_desc(self): return self.plugin_description
  def get_version(self): return self.plugin_version
  def get_author(self): return self.plugin_author
  def get_contact(self): return self.plugin_author_contact

  ##########################
  # врапперы

  def call_load(self): # вызывает все load функции
    if len(self.events['load']) > 0:
      for f in self.events['load']:
        f()

  def call_unload(self): # вызывает все unload функции
    if len(self.events['unload']) > 0:
      for f in self.events['unload']:
        f()

  def call_load_config(self, config): # вызывает все load_config функции
    if len(self.events['load_config']) > 0:
      for f in self.events['load_config']:
        f(config)

  ##########################
  # для упрощения жизни, конечно же сеттеры (пока один)

  def set_config(self, config): self.config = config

  ##########################
  # декораторы для работы с плагином

  def load(self, func): # вызывается, когда аддон загружен. В аргументе передаётся конфиг аддона
    def wrapper():
      func()

    self.events['load'].append(wrapper)

    return wrapper

  def load_config(self, func): # вызывается при загрузке конфига аддона
    def wrapper(config):
      func(config)

    self.events['load_config'].append(wrapper)

    return wrapper

  def unload(self, func): # вызывается, когда аддон разгружается
    def wrapper():
      func()

    self.events['unload'].append(wrapper)

    return wrapper

  ##########################
  # декораторы для работы сообщениями

  def message_new(self, handle_commands=False): # вызывается при новом сообщении

    def deco(func):
      async def wrapper(event, is_command):
        if not handle_commands and is_command: return
        await func(event)

      self.events['message_new'].append(wrapper)

      return wrapper

    return deco

  def message_edited(self, handle_commands=False): # вызывается при отредактированном сообщении
    
    def deco(func):
      async def wrapper(event, is_command):
        if not handle_commands and is_command: return
        await func(event)

      self.events['message_edited'].append(wrapper)

      return wrapper

    return deco

  def message_deleted(self, func): # вызывается при удалённом сообщении
    async def wrapper(event):
      await func(event)

    self.events['message_deleted'].append(wrapper)

  ##########################
  # декоратор для создания команды

  def command(self, names=[]): # декоратор для команд
    if len(names) == 0:
      names = [func.__name__.lower(),]

    def deco(func):

      async def wrapper(event, args):
        await func(event, args)

      for name in names: self.commands[name] = wrapper

      return wrapper

    return deco

# Для управления плагинами
class PluginConfig:

  def get_config_path(plugin): # сис. функция, для получения пути к конфигу плагина
    return os.path.join('configs', f'{plugin.get_name()}.config.json')

  def load_config(plugin): # возвращает конфиг плагина
    fn = PluginConfig.get_config_path(plugin)

    if not os.path.exists(fn): # сохраняем конфиг по умолчанию
      config = plugin.default_config

      with open(fn,'w') as f:
        json.dump(plugin.default_config, f, indent=4)

    else: # лоадим конфиг
      with open(fn,'r') as f:
        config = json.load(f)

    plugin.call_load_config(config)

  def save_config(plugin, config): # сохранение конфига
    fn = PluginConfig.get_config_path(plugin)

    with open(fn, 'w') as f:
      json.dump(config, f, indent=4)

# пространство имён "переменных" для использования их между плагинами
class CommunicatorValues:

  def __init__(self):
    self.values = {}

    self.__getattr__ = self.a__getattr__
    self.__setattr__ = self.a__setattr__

  def a__getattr__(self, attr):
    if attr in self.values:
      return self.values[attr]

  def a__setattr__(self, attr, value):
    self.values[attr] = value

# Коммуникатор между плагинами
class Communicator:
  
  def __init__(self):
    self.values = CommunicatorValues()

  def init(self, plugins):
    self.plugins_index = {a.lower():a for a in plugins}

  def plugin_islive(self, name): # возвращает жив ли плагин, т.е. загружен ли он
    if name.lower() in self.plugins_index:
      return True
    return False

  def get_plugin(self, name): # возвращает плагин, иначе None
    if self.plugin_islive(name):
      return self.plugins_index[name.lower()]
    return None

# Регулирует включение\отключение плагина
class PluginsSwitch:

  def __init__(self, plugins_names, config_path=os.path.join('configs', 'pluginsswitch.config.json')):
    self.config_path = config_path
    self.config = {}

    if os.path.exists(config_path):
      with open(config_path) as f:
        self.config = json.load(f)

    self.initialize_plugins(plugins_names)
    self.save()

  def initialize_plugins(self, plugins_names): # инициализирует плагины
    for pn in plugins_names:
      if pn in self.config: continue

      self.config[pn] = {
        "disabled": False,
        "fullDisable": False
      }

  def save(self):
    with open(self.config_path, 'w') as f:
      json.dump(self.config, f, indent=4)

  ##########################

  def switch_plugin(self, plugin_name, disabled, full=False):
    if plugin_name in self.config:
      self.config[plugin_name]['disabled'] = disabled
      self.config[plugin_name]['fullDisable'] = full

      return True
    return False

  def plugin_is_enabled(self, plugin_name):
    if plugin_name in self.config:
      p = self.config[plugin_name]

      return p['disabled'], p['fullDisable']
    return None, None