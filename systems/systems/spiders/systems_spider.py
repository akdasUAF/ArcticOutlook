from pathlib import Path
from systems.items import SystemsItem
import scrapy
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

class SystemsSpider(scrapy.Spider):
    name = "systems"
    allowed_domains = ["alaska.gov"]
    start_urls = [
        ""
    ]

    rules = [
        Rule(LinkExtractor(), callback='parse', follow=True)
    ]

    def parse(self, response):
        item = SystemsItem()
        table = Selector(response).xpath('/html/body/div/div[2]/main/div[8]/div/table/tr/td//text()')
        item['ID'] = table[0].extract()[3:].strip()
        item['name'] = table[1].extract()
        item['federaltype'] = table[2].extract()
        item['county'] = table[3].extract()
        item['source'] = table[4].extract()
        item['status'] = table[5].extract()
        item['activitydate'] = table[6].extract()
        
        link = Selector(response).xpath('/html/body/div/div[2]/main/div[7]/div/div[2]/a/@href').get()
        item['link'] = response.urljoin(link)

        yield item
        

    def parse_link(self, response):
        pass