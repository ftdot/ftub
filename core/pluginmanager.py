
import imp # для работы с запуском плагинов
import os # для работы с файлами

from core.colors import Fore # для цветного вывода
from core.pluginapi import PluginConfig, PluginsSwitch, Communicator
from core.info import TITLE

##########################
# Менеджер плагинов
class PluginManager:

  def __init__(self, plugins_path=os.path.join('.', 'plugins'), debug_mode=False):
    self.plugins_path = plugins_path
    self.debug_mode = debug_mode

    self.all_commands = {}
    self.all_events = {'message_new': [], 'message_edited': [], 'message_deleted': []}

    self.plugins = {} # для плагинов
    self.to_load = []

    self.client = None # для доступа к базе клиента, register_specialities
    self.communicator = None # для коммуникации плагинов

    self.plugins_mods = [] # для execute_plugin

  def register_plugin(self, plg): # регистрирует плагин, возвращает имя плагина
    # регистрируем команды из плагина
    self.all_commands.update(plg.commands)

    # регестрируем событя из плагина
    for e in plg.events: 
      if e in ['load', 'load_config', 'unload']: continue

      for f in plg.events[e]:
        self.all_events[e].append((f, plg))

    pn = plg.get_name()
    self.plugins[pn] = plg

    return pn

  def execute_plugin(self, path): # запускает плагин

    # запуск плагина
    f = open(path, 'rb')
    self.plugins_mods.append(imp.load_module('plugin_mod_'+os.path.basename(path), f, os.path.basename(path), ('.py', 'r', imp.PY_SOURCE)))
    f.close()

    idx = self.plugins_mods[-1]
    idx_plugin = None

    try:
      idx_plugin = idx.plugin
    except: pass

    # проверяем, валидный ли плагин
    if idx_plugin == None:
      print(f'{Fore.RED}[!] Плагин по пути "{path}" не может быть загружен!{Fore.RESET}')

      if self.debug_mode: exit()
    else:
      print(f'{Fore.GREEN}[+] Плагин {Fore.RESET}{idx_plugin.get_name()} : {idx_plugin.get_desc()} ({idx_plugin.get_version()}){Fore.GREEN} загружен!{Fore.RESET}')

    return idx_plugin

  def load_plugin(self, plugin_name): # запускает плагин полноценно
    if plugin_name in self.plugins:
      p = self.plugins[plugin_name]

      PluginConfig.load_config(p)
      p.call_load()

  ##########################

  def register_plugins(self): # регистрирует все плагины из заданной директории с плагинами
    if os.path.exists(self.plugins_path) and os.path.isdir(self.plugins_path):
      # находим файлы плагинов
      plugins = [os.path.join(self.plugins_path,f) for f in os.listdir(self.plugins_path) if os.path.isfile(os.path.join(self.plugins_path, f)) and f.endswith('.py')]

      # загружаем свитчер
      switch = PluginsSwitch([os.path.basename(f).removesuffix('.py') for f in plugins])

      plugins_sorted = []

      # сортировка плагинов (фигня алгоритм, ну сойдёт)
      for f in plugins:
        if os.path.basename(f).startswith('api'):
          plugins_sorted.append(f)
      for f in plugins:
        if os.path.basename(f).startswith('core'):
          plugins_sorted.append(f)
      for f in plugins:
        bn = os.path.basename(f)
        if not (bn.startswith('core') or bn.startswith('api')):
          plugins_sorted.append(f)

      # запускаем все плагины
      for p in plugins_sorted:
        if self.debug_mode:
          pfile = os.path.basename(p).removesuffix('.py')

          dis, fullDis = switch.plugin_is_enabled(pfile)

          if fullDis:
            print(f'{Fore.CYAN}[i] Плагин {pfile} полностью отключен, пропускаем{Fore.RESET}')
            continue

          pp = self.execute_plugin(p)

          if dis:
            print(f'{Fore.CYAN}[i] Плагин {pfile} отключён, но был загружен{Fore.RESET}')
            continue

          pn = self.register_plugin(pp)
          self.to_load.append(pn)

          continue

        try:
          pfile = os.path.basename(p).removesuffix('.py')

          dis, fullDis = switch.plugin_is_enabled(pfile)

          if fullDis:
            continue

          pp = self.execute_plugin(p)

          if dis:
            print(f'{Fore.CYAN}[i] Плагин {pfile} отключён, но был загружен{Fore.RESET}')
            continue

          pn = self.register_plugin(pp)
          self.to_load.append(pn)

        except Exception as e:
          print(f'{Fore.RED}[!] Плагин не смог загрузиться, по скольку была вызвана ошибка: {e}.\n{Fore.CYAN}Обратитесь к разработчку!{Fore.RESET}\n')

  ##########################

  def register_specialities(self, client, communicator): # устанавливает все ссылки
    self.client = client
    self.communicator = communicator

    for p in self.plugins:
      self.plugins[p].client = self.client
      self.plugins[p].communicator = self.communicator

    if self.debug_mode:
      print(f'{Fore.CYAN}[i] Все ссылки загружены, запускаем плагины{Fore.RESET}')

    for pn in self.to_load:
      if self.debug_mode:
        p = self.plugins[pn]
        self.load_plugin(pn)
        print(f'{Fore.YELLOW}[+] Плагин {Fore.RESET}{p.get_name()} : {p.get_desc()} ({p.get_version()}){Fore.GREEN} запущен!{Fore.RESET}')

        continue

      try:
        p = self.plugins[pn]
        self.load_plugin(pn)
        print(f'{Fore.YELLOW}[+] Плагин {Fore.RESET}{p.get_name()} : {p.get_desc()} ({p.get_version()}){Fore.GREEN} запущен!{Fore.RESET}')
      except:
        print(f'{Fore.RED}[!] Плагин не смог запуститься, по скольку была вызвана ошибка: {e}.\n{Fore.CYAN}Обратитесь к разработчку!{Fore.RESET}\n')

    print()

  ##########################

  async def raise_event(self, event_name, event, ic, is_command=None): # вызов событий
    for f in self.all_events[event_name]:

      if ic:
        func = f[0]
        await func(event, is_command)

      else:
        func = f[0]
        await func(event)

  async def execute_command(self, event, cmd, args): # запуск команды
    # проверяем, есть ли такая команда
    if not cmd in self.all_commands:
      await self.client.edit_message(event.chat_id, event.message, '❌ **Такой команды не существует.**')
      return

    # вызываем команду
    cmd_f = self.all_commands[cmd]
    await cmd_f(event, args)