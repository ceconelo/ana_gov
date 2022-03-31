# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AnaItem(scrapy.Item):
    url = scrapy.Field()
    reservoir_name = scrapy.Field()
    content_table = scrapy.Field()
