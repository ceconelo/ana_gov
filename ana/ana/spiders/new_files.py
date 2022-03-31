import scrapy


class NewFilesSpider(scrapy.Spider):
    name = 'new_files'
    allowed_domains = ['X']
    start_urls = ['http://X/']

    def parse(self, response):
        pass
