# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MedicalItem(scrapy.Item):
    name = scrapy.Field()
    profession = scrapy.Field()
    date = scrapy.Field()
    time = scrapy.Field()
    text = scrapy.Field()
    response = scrapy.Field()
