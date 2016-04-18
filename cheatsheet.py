import os
import sublime, sublime_plugin
import json

_cheatsheetExtension      = '.cheatsheet'
_commandExtension         = '.sublime-commands'

_pluginHome               = os.path.dirname(os.path.realpath(__file__));

_defaultDatabase          = os.path.join(_pluginHome, 'database')
_defaultCommandsFile      = os.path.join(_pluginHome, 'Default' + _commandExtension)

_localDatabase            = os.path.join(os.path.expanduser('~'), '.cheatsheet')
_localCommandsFile        = os.path.join(_localDatabase, 'Local' + _commandExtension)
_localCommandsFileSymlink = os.path.join(_pluginHome, 'Local' + _commandExtension)


def plugin_loaded():
  vindow = sublime.active_window()
  sublime.set_timeout(lambda: vindow.run_command('cheatsheet_refresh_local_database'), 2000)

class CheatsheetOpenCommand(sublime_plugin.WindowCommand):
  def run(self, **args):
    cheatsheet = os.path.join(_defaultDatabase, args['filename'])
    self.dest_view = self.window.open_file(cheatsheet)

class CheatsheetOpenLocalCommand(sublime_plugin.WindowCommand):
  def run(self, **args):
    cheatsheet = os.path.join(_localDatabase, args['filename'])
    self.dest_view = self.window.open_file(cheatsheet)

class CheatsheetRefreshLocalDatabaseCommand(sublime_plugin.WindowCommand):
  def run(self, **args):
    if os.path.isdir(_localDatabase):
      self.loadCheatsheetCommands()
      self.getCheatsheetFiles()
      self.filterOutInvalidCheatsheets()
      self.registerNewCheatsheets()
      self.saveCheatsheetCommands()
      self.symlinkCommandsFile()

  def loadCheatsheetCommands(self):
    if os.path.isfile(_localCommandsFile):
      with open(_localCommandsFile, 'r') as input:
        self.commands = json.load(input)
    else:
      self.commands = []

  def getCheatsheetFiles(self):
    self.cheatsheets = {
      self.getRelativePath(root, filename) : self.getFilenameWithoutExtension(filename)
      for root, dirnames, filenames in os.walk(_localDatabase)
        for filename in filenames
          if filename.endswith(_cheatsheetExtension)
    }

  def getRelativePath(self, root, filename):
    return os.path.relpath(os.path.join(root, filename), _localDatabase)

  def getFilenameWithoutExtension(self, filename):
    return filename.replace(_cheatsheetExtension, '')

  def filterOutInvalidCheatsheets(self):
    self.commands = [
      command for command in self.commands
        if self.isValidCheatsheetCommand(command)
    ]

  def isValidCheatsheetCommand(self, command):
    return not self.isCheatsheetOpenCommand(command) or self.isValidCheatsheetOpenCommand(command)

  def isValidCheatsheetOpenCommand(self, command):
    return self.isCheatsheetOpenCommand(command) and self.cheatsheetExists(command['args']['filename'])

  def isCheatsheetOpenCommand(self, command):
    return command['command'] == 'cheatsheet_open_local'

  def cheatsheetExists(self, cheatsheet):
    return cheatsheet in self.cheatsheets.keys()

  def getNewCheatsheets(self):
    return {
      path : cheatsheet
        for path, cheatsheet in self.cheatsheets.items()
          if self.isNewCheatsheet(path)
    }

  def isNewCheatsheet(self, path):
    for command in self.commands:
      if self.isCheatsheetOpenCommand(command) and command['args']['filename'] == path:
        return False
    return True

  def registerNewCheatsheets(self):
    for path, cheatsheet in self.getNewCheatsheets().items():
      self.commands.append(self.newCheatsheetOpenCommand(cheatsheet, path))

  def newCheatsheetOpenCommand(self, cheatsheet, path):
    return {
      'caption': 'Cheatsheet: ' + cheatsheet,
      'command': 'cheatsheet_open_local',
      'args': { 'filename': path }
    }

  def saveCheatsheetCommands(self):
    with open(_localCommandsFile, 'w') as output:
      json.dump(self.commands, output, sort_keys = True, indent = 2, separators = (',', ': '))

  def symlinkCommandsFile(self):
    if os.path.exists(_localCommandsFileSymlink):
      os.remove(_localCommandsFileSymlink)
    os.symlink(_localCommandsFile, _localCommandsFileSymlink)
