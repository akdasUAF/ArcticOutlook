from pathlib import Path
from operators.items import OperatorsItem
import scrapy
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule


class OperatorsSpider(scrapy.Spider):
    name = "operators"
    allowed_domains = ["alaska.gov"]
    start_urls = [
        "https://dec.alaska.gov/Applications/Water/OpCert/Home.aspx?p=OperatorSearchResults&name=&city="
    ]

    rules = [
        Rule(LinkExtractor(), callback='parse', follow=True)
    ]

    def parse(self, response):
        """This handles the collection of the operator names and URL links to their specific page on the website.
            The spider will join the retrieved URL with the website name and yield the results to parse_op_info
            for information retrieval."""
        operators = Selector(response).xpath('//div[@id="ctl00_ContentPlaceHolder1_pnlContent"]/a')
        for op in operators:
            item = OperatorsItem()
            item['name'] = op.css('a::text').extract()[0]
            link = op.css('a::attr(href)').extract()[0]
            item['link'] = response.urljoin(link) 
            yield scrapy.Request(item['link'], callback=self.parse_op_info, meta={'item': item})
    

    def parse_op_info(self, response):
        """This function is passed a URL. It will look for 2 tables on the webpage: Active Certificates and Current Employer.
            If the information is located, it will be stored into the item and then the item will be yielded to the database.
            If the information is not provided, 'N/A' will be stored in the database."""
        certificate = Selector(response).xpath('//*[@id="ctl00_ContentPlaceHolder1_ctl00_gvCertificates"]//tr[@class="gridrow"]')
        employer = Selector(response).xpath('//*[@id="ctl00_ContentPlaceHolder1_ctl00_gvSystems"]//tr[@class="gridrow"]')

        item = response.meta['item']
        if certificate:
            l1 = []
            for c in certificate:
                cert = dict()
                cert['cert_num'] = c.xpath('td//text()')[0].extract()
                cert['cert'] = c.xpath('td//text()')[1].extract()
                cert['issue_date'] = c.xpath('td//text()')[2].extract()
                cert['exp_date'] = c.xpath('td//text()')[3].extract()
                l1.append(cert)
            item['certificates']= l1
        else:
            item['certificates'] = "N/A"

        if employer:
            l2 = []
            for em in employer:
                sys = dict()
                attr = em.xpath('td//text()')[1].extract()
                if attr:
                    sys['system_name'] = attr
                if not attr:
                    txt = em.xpath('td//span/text()').extract()
                    sys['system_name'] = txt
                sys['type'] = em.xpath('td[2]//text()')[0].extract()
                l2.append(sys)
            item['systems'] = l2
        else:
            item['systems'] = "N/A"

        yield item