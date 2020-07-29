from ast import walk
def scanTree(tree):
    nodes = []
    for node in walk(tree):
        nodes.append(node)
    return nodes