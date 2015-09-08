from os.path import dirname, realpath, join
import sublime, sublime_plugin
import json

home     = dirname(realpath(__file__));
database = join(home, "database")

class CheatsheetCommand(sublime_plugin.WindowCommand):
  def run(self, **args):
    cheatsheet     = join(database, args["category"], args["cheatsheet"])
    self.dest_view = self.window.open_file(cheatsheet)
