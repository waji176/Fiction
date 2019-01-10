# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FictionScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    classification = scrapy.Field()
    source = scrapy.Field()
    fiction_name = scrapy.Field()
    author = scrapy.Field()
    viewing_count = scrapy.Field()
    status = scrapy.Field()
    image = scrapy.Field()
    fiction_update_time = scrapy.Field()
    chapter_name = scrapy.Field()
    chapter_content = scrapy.Field()
    is_vip = scrapy.Field()
    chapter_update_time = scrapy.Field()
