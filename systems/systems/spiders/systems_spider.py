from pathlib import Path
from systems.items import SystemsItem, ContactsItem
import scrapy
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

class SystemsSpider(scrapy.Spider):
    name = "systems"
    allowed_domains = ["alaska.gov"]
    start_urls = [
        "https://dec.alaska.gov/dww/index.jsp"
    ]

    rules = [
        Rule(LinkExtractor(), callback='parse', follow=True)
    ]

    def parse(self, response):
        url = 'https://dec.alaska.gov/dww/JSP/SearchDispatch'
        headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://dec.alaska.gov",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "https://dec.alaska.gov/dww/index.jsp",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1"
        }

        body = 'number=&name=&county=&WaterSystemType=All&SourceWaterType=All&PointOfContactType=None&action=Search+For+Water+Systems'

        # Recreates the POST request made by the website
        return scrapy.Request(
            url=url,
            method='POST',
            dont_filter=True,
            headers=headers,
            body=body,
            callback=self.parse_IDs
        )

    def parse_IDs(self, response):
        table = Selector(response).xpath('/html/body/div[1]/div[2]/main/div[2]/div/table/tr')
        x = 0
        for tr in table:
            if x == 0:
                x = 1
            else:
                item = SystemsItem()
                link = tr.xpath('td[1]/a/@href')[0].extract()
                item['link'] = response.urljoin(link) 
                yield scrapy.Request(item['link'], callback=self.parse_link, meta={'item': item})


    def parse_link(self, response):
        item = response.meta['item']
        table = Selector(response).xpath('/html/body/div/div[2]/main/div[8]/div/table/tr/td//text()')
        item['ID'] = table[0].extract()[3:].strip()
        item['name'] = table[1].extract()
        item['federaltype'] = table[2].extract()
        item['county'] = table[3].extract()
        item['source'] = table[4].extract()
        item['status'] = table[5].extract()
        item['activitydate'] = table[6].extract()

        # Collects the information from the Points of Contact table.
        contacts = Selector(response).xpath('/html/body/div/div[2]/main/div[9]/div/table//tr')
        con = []
        c = dict()
        path = contacts.xpath('td/text()')
        c['name'] = path[0].extract().strip()
        c['title'] = path[1].extract().strip()
        c['type'] = path[2].extract().strip()
        c['phone'] = path[3].extract().strip()
        c['address'] = path[4].extract().strip() + path[5].extract().strip() + path[6].extract().strip()
        email = contacts.xpath('td/a/text()').extract()
        if isinstance(email, list) and email:
            email = email[0].strip()
        else:
            email = "Not Available"
        c['email'] = email
        con.append(c)
        item['contact'] = con

        # Add contact information to ContactsItem and insert into database.
        contact_item = ContactsItem()
        contact_item['name'] = c['name']
        contact_item['title'] = c['title']
        contact_item['type'] = c['type']
        contact_item['phone'] = c['phone']
        contact_item['address'] = c['address']
        contact_item['email'] = c['email']
        # Note, this does NOT check for duplicate entries. Will need to add a way to clear duplicate entries from mongodb.
        yield contact_item

        # Collects the url link to the 'Current Monitoring System'.
        link = Selector(response).xpath('/html/body/div/div[2]/main/div[7]/div/div[2]/a/@href').get()
        item['monitoring'] = response.urljoin(link)

        yield item