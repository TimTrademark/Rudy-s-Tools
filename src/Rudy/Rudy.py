from sys import exit, argv
from os import path, getcwd
from ast import parse, NodeVisitor
from Tree import scanTree
from Transform import Compile
class RudyLang:
    hadError = False
    def main(self):
        if len(argv) == 2 and argv[1].endswith(".rudy"):
            self.runScript(argv[1])
        else:
            print("Usage: rudy [script.rudy]")
            exit()

    def runScript(self, scriptPath):
        #refactor exception catching
        try:
            with open(path.abspath(scriptPath), 'r') as f:
                tree = parse(f.read())
                self.nodes = scanTree(tree)
            compiler = Compile()
            compiler.transform(self.nodes, scriptPath)
        except ValueError as e:
            print("Message: " + str(e) + " (does the script exist?)")

if __name__ == "__main__":
    RudyLang().main()