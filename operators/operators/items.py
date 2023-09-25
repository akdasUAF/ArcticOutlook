# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class OperatorsItem(scrapy.Item):
    name = scrapy.Field()
    link = scrapy.Field()
    certificates = scrapy.Field()
    systems = scrapy.Field()