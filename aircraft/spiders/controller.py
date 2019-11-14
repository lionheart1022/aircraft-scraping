# -*- coding: utf-8 -*-
import scrapy
from scrapy.conf import settings
import urlparse
import re


class ControllerItem(scrapy.Item):
    # define the fields for your item here like:
    year_of_manufacture = scrapy.Field()
    manufacturer = scrapy.Field()
    model_name = scrapy.Field()
    registration = scrapy.Field()
    price = scrapy.Field()
    serial = scrapy.Field()
    total_time = scrapy.Field()
    location = scrapy.Field()
    advertisement_num = scrapy.Field()
    updated_date = scrapy.Field()
    url = scrapy.Field()

    pass


class ControllerSpider(scrapy.Spider):
    name = "controller_spider"
    allowed_domains = ['controller.com']
    start_url = 'https://www.controller.com/listings/aircraft/for-sale/list?SortOrder=35&scf=False&LS=1'

    handle_httpstatus_list = [416]

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/71.0.3578.98 Safari/537.36'
    }

    # HEADERS = {
    #     'User-Agent': 'Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)'
    # }

    def __init__(self, *args, **kwargs):
        super(ControllerSpider, self).__init__(
            site_name=self.allowed_domains[0], *args, **kwargs)

        settings.overrides['DOWNLOAD_DELAY'] = 2

    def start_requests(self):
        yield scrapy.Request(self.start_url,
                             callback=self.parse_links, headers=self.HEADERS)

    def parse_links(self, response):
        products = response.xpath('//div[@id="ListListing_"]')

        for product in products:
            link = product.xpath('.//div[@class="listing-name"]/a/@href').extract()
            url = urlparse.urljoin(response.url, link)
            updated_date = product.xpath('.//div[contains(@class, "updated")]/div/text()')[0].extract()

            yield scrapy.Request(url, callback=self.parse_product, headers=self.HEADERS,
                                 meta={'updated_date': updated_date})

    def parse_product(self, response):
        item = ControllerItem()

        item['url'] = response.url

        item['updated_date'] = response.meta['updated_date']

        item['price'] = response.xpath('//span[@class="price-value"]/text()')[0].extract()

        ad_num = re.search('ReferenceID=(\d+)', response.body)
        item['advertisement_num'] = ad_num.group(1) if ad_num else None

        item['location'] = response.xpath('//a[@class="machinelocation"]/text()')[0].extract()

        specifications = response.xpath('//div[@class="listing-bottom-information"]'
                                        '//div[contains(@class, "m-top-15")]/div[@class="row"]')

        for specification in specifications:
            field_name = specification.xpath('.//div[contains(@class, "spec-name")]/text()')[0].extract()
            value = specification.xpath('.//div[@class="spec-value")]/text()')[0].extract()
            if field_name == 'Year':
                item['year_of_manufacture'] = value
            if field_name == 'Manufacturer':
                item['manufacturer'] = value
            if field_name == 'Model':
                item['model_name'] = value
            if field_name == 'Registration #':
                item['registration'] = value
            if field_name == 'Serial Number':
                item['serial'] = value
            if field_name == 'Total Time':
                item['total_time'] = value

        return item
