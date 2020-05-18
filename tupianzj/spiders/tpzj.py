# -*- coding: utf-8 -*-
import logging

from scrapy import Request, Spider

from tupianzj.items import ImgItem


class TpzjSpider(Spider):
    name = 'tpzj'
    allowed_domains = ['www.tupianzj.com']
    meinv_url = 'https://www.tupianzj.com/meinv/'

    logger = logging.getLogger(__name__)

    def start_requests(self):
        yield Request(url=self.meinv_url, callback=self.parse_fl)

    #解析分类，把美女专区下的所有分类
    def parse_fl(self, response):
        lis = response.css('.list_nav .warp li')
        for li in lis:
            fl_url = li.css('a::attr(href)').extract_first()
            yield Request(
                url=fl_url, callback=self.parse_index
            )


    #专门处理美女专题大全的图片截二级列表
    def parse_two_index(self, response):
        lis = response.css('.d1.ico3 li')
        for li in lis:
            url = li.css('span a::attr(href)').extract_first()
            if li.css('span a[href*=html]::attr(href)').extract_first():
                yield Request(url=response.urljoin(url), callback=self.parse_img)
            else:
                yield Request(url=response.urljoin(url), callback=self.parse_two_index)

    #解析普通图片集列表
    def parse_index(self, response):
        lis = response.css('.list_con_box_ul li')
        for li in lis:
            imgs_url = li.css('a::attr(href)').extract_first()

            #加一个判断是否是美女专题大全的，是就引导到二级目录的解析
            if '/meinv/mm/' in imgs_url:
                yield Request(
                    url=response.urljoin(imgs_url), callback=self.parse_two_index
                )
            else:
                yield Request(
                    url=response.urljoin(imgs_url), callback=self.parse_img
                )

        pages = response.css('.pages ul li')
        for li in pages:
            if li.css('a::text').extract_first() == '下一页':
                next_url = li.css('a::attr(href)').extract_first()
                yield Request(
                    url=response.urljoin(next_url), callback=self.parse_index
                )
                break

    #解析图片集内容
    def parse_img(self, response):
        item = ImgItem()

        title = response.css('.warp .list_con h1::text').extract_first()
        img_url = response.css('#bigpicimg::attr(src)').extract_first()

        item['image_name'] = title
        item['image_url'] = img_url

        yield item

        pages = response.css('.pages ul li')
        for li in pages:
            if li.css('a::text').extract_first() == '下一页' and li.css('a[href*=html]::attr(href)').extract_first():
                next_url = li.css('a::attr(href)').extract_first()
                yield Request(
                    url=response.urljoin(next_url), callback=self.parse_img
                )
                break