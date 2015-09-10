import os
import sublime, sublime_plugin
import json

plugin_home = os.path.dirname(os.path.realpath(__file__));
database_dir = os.path.join(plugin_home, "database")
commands_file = os.path.join(plugin_home, "Default.sublime-commands")

class CheatsheetOpenCommand(sublime_plugin.WindowCommand):
  def run(self, **args):
    cheatsheet = os.path.join(database_dir, args["filename"])
    self.dest_view = self.window.open_file(cheatsheet)


class CheatsheetRefreshDatabaseCommand(sublime_plugin.WindowCommand):
  def run(self, **args):
    self.getCheatsheets()
    self.getCommands()
    self.removeInvalidCheatsheetCommands()
    self.addNewCheatsheetOpenCommands()
    self.setCommands()

  def getCheatsheets(self):
    self.cheatsheets = {
      self.getRelativePath(root, filename) : filename
      for root, dirnames, filenames in os.walk(database_dir) for filename in filenames }

  def getRelativePath(self, root, filename):
    return os.path.relpath(os.path.join(root, filename), database_dir)

  def getCommands(self):
    with open(commands_file, 'r') as input:
      self.commands = json.load(input)

  def removeInvalidCheatsheetCommands(self):
    self.commands = [
      command for command in self.commands
      if self.isValidCheatsheetCommand(command) ]

  def isValidCheatsheetCommand(self, command):
    return not self.isCheatsheetOpenCommand(command) or self.isValidCheatsheetOpenCommand(command)

  def isValidCheatsheetOpenCommand(self, command):
    return self.isCheatsheetOpenCommand(command) and self.cheatsheetExists(command['args']['filename'])

  def isCheatsheetOpenCommand(self, command):
    return command['command'] == 'cheatsheet_open'

  def cheatsheetExists(self, cheatsheet):
    return cheatsheet in self.cheatsheets.keys()

  def getNewCheatsheets(self):
    return { path : cheatsheet
      for path, cheatsheet in self.cheatsheets.items() if self.isNewCheatsheet(path) }

  def isNewCheatsheet(self, path):
    for command in self.commands:
      if self.isCheatsheetOpenCommand(command) and command['args']['filename'] == path:
        return False
    return True

  def addNewCheatsheetOpenCommands(self):
    for path, cheatsheet in self.getNewCheatsheets().items():
      self.commands.append(self.newCheatsheetOpenCommand(cheatsheet, path))

  def newCheatsheetOpenCommand(self, cheatsheet, path):
    return {
      "caption": "Cheatsheet: " + cheatsheet,
      "command": "cheatsheet_open",
      "args": { "filename": path } }

  def setCommands(self):
    with open(commands_file, 'w') as output:
      json.dump(self.commands, output, sort_keys=True, indent=2, separators=(',', ': '))
