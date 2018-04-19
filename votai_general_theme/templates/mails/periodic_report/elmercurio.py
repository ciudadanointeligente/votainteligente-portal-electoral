# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader

from diarios.items import DiariosItem


class ElmercurioSpider(scrapy.Spider):
    name = 'elmercurio'
    allowed_domains = ['www.elmercurio.com/blogs']
    start_urls = ['http://www.elmercurio.com/blogs']
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
    }

    def parse(self, response):
        """
        @url http://www.elmercurio.com/blogs
        @returns items 1 14
        @returns requests 0 0
        @scrapes author title url
        """
        selectors = response.xpath('//*[@id="contenedor_columnistas_home"]/div[3]/ul/li')
        for selector in selectors:
            yield self.parse_article(selector, response)

    def parse_article(self, selector, response):
        loader = ItemLoader(DiariosItem(), selector=selector)
        #
        loader.add_xpath('author', './/p//strong//text()')
        loader.add_xpath('title', './/a//text()')
        loader.add_xpath('url', './/@href')
        return loader.load_item()
