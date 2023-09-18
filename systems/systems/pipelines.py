# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from systems.items import SystemsItem, ContactsItem
import pymongo


class SystemsPipeline:

    def __init__(self, mongodb_uri, mongodb_db, mongodb_collection):
        self.mongodb_uri = mongodb_uri
        self.mongodb_db = mongodb_db
        self.mongodb_collection = mongodb_collection
        if not self.mongodb_uri: sys.exit("No connection string provided.")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongodb_uri=crawler.settings.get('MONGODB_URI'),
            mongodb_db=crawler.settings.get('MONGODB_DATABASE', 'items'),
            mongodb_collection=crawler.settings.get('MONGODB_COLLECTION_SYSTEMS')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongodb_uri)
        self.db = self.client[self.mongodb_db]
        # Start with a clean database.
        self.db[self.mongodb_collection].delete_many({})

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if not isinstance(item,SystemsItem):
            return item
        data = dict(SystemsItem(item))
        self.db[self.mongodb_collection].insert_one(data)
        return item
    
class ContactsPipeline:
    def __init__(self, mongodb_uri, mongodb_db, mongodb_collection):
        self.mongodb_uri = mongodb_uri
        self.mongodb_db = mongodb_db
        self.mongodb_collection = mongodb_collection
        if not self.mongodb_uri: sys.exit("No connection string provided.")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongodb_uri=crawler.settings.get('MONGODB_URI'),
            mongodb_db=crawler.settings.get('MONGODB_DATABASE', 'items'),
            mongodb_collection=crawler.settings.get('MONGODB_COLLECTION_CONTACTS')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongodb_uri)
        self.db = self.client[self.mongodb_db]
        # Start with a clean database.
        self.db[self.mongodb_collection].delete_many({})

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if not isinstance(item,ContactsItem):
            return item
        data = dict(ContactsItem(item))
        self.db[self.mongodb_collection].insert_one(data)
        return item

