# A simple class to help generate json-esq item for front-end view of the dynamic scraper.
class Node():
    def __init__(self, text, index):
        self.text = text
        self.index = index
        self.nodes = None

    def convert_to_dict(self):
        nodes = []
        if self.nodes:
            for x in self.nodes:
                nodes.append(x.convert_to_dict())
        if nodes:
            var = {"text": self.text, "index": self.index, "nodes": nodes}
        else:
            var = {"text": self.text, "index": self.index}
        return var
    
    def insert_node(self, child):
        if self.nodes is None:
            self.nodes = []
        self.nodes.append(child)

def delete_node(root, index):
    if root == None:
        return None
    if root.nodes == None:
        return None
    
    n = root.nodes
    for x in range(0, len(n)):
        # If we've found the correct node to delete, delete the node and update subsequent node indexes
        if n[x].index == index:
            n.pop(x)
            break

    update_index(root.nodes, 1)
    return root

def update_index(nodes, index):
    if nodes == None:
        return None
    for node in nodes:
        node.index = index 
        index += 1 # increment index
        if node.nodes:
            index = update_index(node.nodes, index)
    return index