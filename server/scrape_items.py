from server.node import Node

class ScrapeItems():
    def __init__(self):
        self.scrape_items = {}
        self.url = ""
        self.base_url = ""
        self.args = []
        self.url_count = 0
        self.instructions = []
        self.jsp = False
        self.num = 1.0
        self.auto = False

        self.instruct_list = []
        self.head = Node("Head Node", -55)
        self.nodes_list = [self.head]
        self.instruct_num = -1

    def clear(self):
        self.scrape_items = {}
        self.url, self.base_url = "", ""
        self.args = []
        self.url_count = 0
        self.jsp = False
        self.instructions = []
        self.num = 1.0
        self.auto = False
        self.instruct_list = []
        self.instruct_num = 0
        self.head = Node("Head Node", -55)
        self.nodes_list = [self.head]