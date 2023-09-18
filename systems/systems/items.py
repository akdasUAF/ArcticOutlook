# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SystemsItem(scrapy.Item):
    ID = scrapy.Field()
    name = scrapy.Field()
    county = scrapy.Field()
    status = scrapy.Field()
    federaltype = scrapy.Field()
    source = scrapy.Field()
    activitydate = scrapy.Field()
    link = scrapy.Field()
    contact = scrapy.Field()
    monitoring = scrapy.Field()

class ContactsItem(scrapy.Item):
    name = scrapy.Field()
    title = scrapy.Field()
    type = scrapy.Field()
    phone = scrapy.Field()
    address = scrapy.Field()
    email = scrapy.Field()
