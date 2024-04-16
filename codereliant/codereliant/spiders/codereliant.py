import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from codereliant.items import CodereliantItem


class CodereliantSpider(CrawlSpider):
    name = 'codereliant'

    allowed_domains = ['codereliant.io', 'www.codereliant.io']
    start_urls = ['https://www.codereliant.io/']
    rules = (Rule(LinkExtractor(allow=r'.*'), callback='parse_item'),)

    def parse_item(self, response):
        item = CodereliantItem()
        item['url'] = response.url
        item['title'] = response.css('title::text').get()
        item['description'] = response.css(
            'meta[name="description"]::attr(content)').get()
        item['body'] = response.css('body').get()
        return item
