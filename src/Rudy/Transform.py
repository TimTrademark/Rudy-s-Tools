import ast
from os import mkdir, getcwd, path, system
from Tree import scanTree
class Compile:
    def __init__(self):
        self.nodes_to_c_str = ""
        self.nodes_to_c = {
            ast.Module : self.module,
            ast.FunctionDef : self.functiondef,
            ast.Call : self.functioncall,
            ast.Import : self.importstatement
        }
    importtext = ""
    closecounter = 0
    #string manipulation functions and helper functions for compilation
    def module(self):
        self.closecounter += 1
        return "#include <stdio.h>\nint main() {"
    def importstatement(self, node, scriptPath):
        for name in node.names:
            #get module's location
            with open(path.join(path.abspath(scriptPath), "/lib/_modules.py"), "w") as f:
                f.write("import " + name + "\nprint(" + name + ".__file__)")
            location = system("py " + path.join(path.abspath(scriptPath), "/lib/_modules.py"))
            #non C module
            if location.endswith(".py"):
                with open(location, "r") as fr:
                    self.importtext += fr.read()
                
            else:
            #a C module
                pass
    def functiondef(self, name, body, arguments):
        print("body" + str(body))
        functionstring = ""
        argumentsstring = ""
        argcount = 0
        returnstring = ""
        returncount = 0
        argtypes = []
        for _ in range(len(arguments.args)):
            argcount += 1
            #the argument types in list form
            argtypes.append(self.findArgType(name, self.source))

            #set arg types
            argumentsstring += argtypes[argcount - 1] + " " + arguments.args[_].arg
            if argcount != len(arguments.args):
                argumentsstring += ","

  
        for node in body:
            if isinstance(node, ast.Return):
                #a count to see if there was a return statement
                returncount += 1
                #what type of function will it be
                if isinstance(node.value, ast.Num):
                    functionstring += "int " + name + "(" + argumentsstring + ") {"
                    returnstring += "return " + str(node.value.n)
                    print(arguments)
                elif isinstance(node.value, ast.Str):
                    functionstring += "char[] " + name + "(" + argumentsstring + ") {"
                    returnstring += "return \"" + str(node.value.s) + "\""
                    print(arguments)
                elif isinstance(node.value, ast.Bytes):
                    functionstring += "byte " + name + "(" + argumentsstring + ") {"
                    returnstring += "return " + str(node.value.b)
                    print(arguments)
                else:
                    #TODO return is anything but a constant so var or func call is possible
                    #TODO return can also be an arg
                    if isinstance(node.value, ast.Name):
                        self.findVarType(node.value.id, body)
        if returncount == 0:
            functionstring += "void " + name + "(" + argumentsstring + ") {"
        for node in body:
            if not isinstance(node, (ast.Return, ast.arguments, ast.Num,ast.Str,ast.Bytes)):
                functionstring += self.transpile(node, True)
        functionstring += returnstring
        functionstring += "}"
        return functionstring
    def findFuncType(self, name, scope):
        #find func type by return
        returncount = 0
        for node in scope:
            if isinstance(node, ast.Return):
                returncount += 1
                if isinstance(node.value, ast.Num):
                    return "int"
                elif isinstance(node.value, ast.Str):
                    return "char[]"
                if isinstance(node.value, ast.Bytes):
                    return "byte"
                elif isinstance(node.value, ast.Name):
                    temp = self.findVarType(node.value.id, scope)
                    if temp is not None:
                        return temp
                    else:
                        #we need a loop to find the position of the argument because findArgType takes in the function name and not the arg name
                        argcount = 0
                        argtypes = []
                        for _ in scope:
                            if isinstance(_,ast.arguments):
                                for __ in _.args:
                                    
                                    #the argument name is equal to the name in the return statement
                                    if __.id == node.value.id:
                                        argtypes.append(self.findArgType(name, self.source))
                                        return argtypes[argcount]
                                    argcount += 1
                                        
                    #if temp was None it means the var could be global
                        temp = self.findVarType(node.value.id, self.source)
                        return temp
    def findVarType(self,name, scope):
        for node in scope:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if target.id == name:
                        #var is assigned to constant
                        if hasattr(target.value, 'n'):
                            return "int"
                        elif hasattr(target.value, 's'):
                            return "char[]"
                        elif hasattr(target.value, 'b'):
                            return "byte"
                        #var is assigned to other var or call
                        else:
                            #var
                            if isinstance(target.value, ast.Name):
                                temp = self.findVarType(target.value.id, scope)
                                #check if the var was there, otherwise maybe global var
                                if temp is not None: return temp
                                else:
                                #var could be global
                                #TODO var could be in import (maybe add imports to the top of the file)
                                    temp = self.findVarType(name, self.source)
                                    if temp is not None: return temp
                            #function call
                            if isinstance(target.value, ast.Expr) and isinstance(target.value.value, ast.Call):
                                return self.findFuncType(target.value.value.func.id, target.value.value.func.body)
                            
    
    def findArgType(self, name, scope):
        for node in self.source:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and node.value.func.id == name:
                for arg in node.value.args:
                    if not isinstance(arg, (ast.Num, ast.Str, ast.Bytes)):
                        name = arg.id
                        for n in self.source:
                            #special look in imported scripts TODO
                            if isinstance(n, ast.Import):
                                pass
                            elif isinstance(n, ast.Assign):
                                for target in n.targets:
                                    if target.id == name:
                                        if isinstance(n.value, ast.Num):
                                            return "int"
                                        elif isinstance(n.value, ast.Str):
                                            return "char[]"
                                        elif isinstance(n.value, ast.Bytes):
                                            return "byte"
                                        elif isinstance(n.value, ast.Expr):
                                            if isinstance(n.value, ast.Call):
                                                #the var is assigned to a func call (a = myfunc())
                                                return self.findFuncType(n.value.func.id,n.value.func.body)
                    else:
                        if isinstance(arg, ast.Num):
                            return "int"    
                        elif isinstance(arg, ast.Str):
                            return "char[]"
                        elif isinstance(arg, ast.Bytes):
                            return "byte"                             

    #multiple functions for a multiple return
    #TODO maybe not needed as you return a tuple which could be converted to an array in c
    def definemultiplefunctions(self):
        pass
    #function call
    def functioncall(self, node):
        paramtext = ""
        paramcount = 0
        for arg in node.value.args:
            paramcount += 1
            print(arg._fields)
            if hasattr(arg, 's'):
                if paramcount == len(node.value.args):
                    paramtext += str(arg.s)
                else:
                    paramtext += str(arg.s) + ","
            elif hasattr(arg, 'n'):
                if paramcount == len(node.value.args):
                    paramtext += str(arg.n)
                else:
                    paramtext += str(arg.n) + ","
            elif hasattr(arg, 'b'):
                #TODO represent bytes in the right format (not 0b1100)
                if paramcount == len(node.value.args):
                    paramtext += str(arg.b)
                else:
                    paramtext += str(arg.b) + ","
            #TODO the function call params are vars or other calls
            else:
                pass
        return node.value.func.id + "(" + paramtext + ");"

    #function to traverse nodes and call functions correspondly
    def transform(self, nodes, scriptPath):
        if not path.exists(path.join(getcwd(), "lib")):
            mkdir(path.abspath(scriptPath), "lib"))
        for node in nodes:
            if isinstance(node, ast.Module):
                self.source = node.body
                self.transpile(node)
                for n in node.body:
                    self.transpile(n, scriptPath=scriptPath)
            else:
                break
        self.nodes_to_c_str += "}"*self.closecounter
        with open("./lib/output.c", "w") as f:
            f.write(self.nodes_to_c_str)
    
    def transpile(self, node, recursive=False, scriptPath=None):
        if isinstance(node, ast.Import):
            if recursive:
                return self.nodes_to_c.get(node.__class__)(node, scriptPath)
            else:
                self.nodes_to_c_str += self.nodes_to_c.get(node.__class__)(node)
        elif isinstance(node, ast.FunctionDef):
            if recursive:
                return self.nodes_to_c.get(node.__class__)(node.name, node.body, node.args)
            else:
                self.nodes_to_c_str += self.nodes_to_c.get(node.__class__)(node.name, node.body, node.args)
        elif isinstance(node, ast.AsyncFunctionDef) or isinstance(node, ast.If) or isinstance(node, ast.For) or isinstance(node, ast.AsyncFor) or isinstance(node, ast.While) or isinstance(node, ast.With) or isinstance(node, ast.AsyncWith):
            self.nodes_to_c_str += self.nodes_to_c.get(node.__class__)(node.body)
        else:
            if isinstance(node, ast.Expr):
                if isinstance(node.value, ast.Call):
                    self.nodes_to_c_str += self.nodes_to_c.get(node.value.__class__)(node)
            elif isinstance(node, ast.Module):  
                self.nodes_to_c_str += self.nodes_to_c.get(node.__class__)()
            else:
                self.nodes_to_c_str += self.nodes_to_c.get(node.__class__)(node)