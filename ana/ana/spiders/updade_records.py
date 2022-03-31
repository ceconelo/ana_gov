import scrapy


class UpdadeRecordsSpider(scrapy.Spider):
    name = 'updade_records'
    allowed_domains = ['x']
    start_urls = ['http://x/']

    def parse(self, response):
        pass
