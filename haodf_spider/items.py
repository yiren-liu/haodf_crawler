# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Review(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    province = scrapy.Field()
    hospital = scrapy.Field()
    department = scrapy.Field()
    patient = scrapy.Field()
    disease = scrapy.Field()
    time = scrapy.Field()
    doctor = scrapy.Field()
    payment = scrapy.Field()
    effect_rating = scrapy.Field()
    attitude_rating = scrapy.Field()
    text = scrapy.Field()

    pass
