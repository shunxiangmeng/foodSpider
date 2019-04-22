# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FileDownloadItem(scrapy.Item):
    # define the fields for your item here like:
    file_urls = scrapy.Field();
    files = scrapy.Field();


#中国食品安全网信息
class FoodCfsnItem(scrapy.Item):
    #新闻分类
    major = scrapy.Field();
    #发布新闻日期
    publish = scrapy.Field();
    #更新日期时间
    update = scrapy.Field();
    #标题
    title = scrapy.Field();
    #来源
    source = scrapy.Field();
    #内容长度
    content_len = scrapy.Field();
    #内容
    content = scrapy.Field();
    #新闻链接
    url = scrapy.Field();
    #照片数量
    pic_num = scrapy.Field();
    #照片src
    pic_url = scrapy.Field();



