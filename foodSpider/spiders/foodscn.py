# -*- coding: utf-8 -*-

import scrapy
import os,time
from .upload import *
from ..items import *

class FoodScnSpider(scrapy.Spider):
    name = "foodscn"

    def __init__(self):
        self.urls = [
            'http://www.foodscn.cn/news/news/',      #要闻
            'http://www.foodscn.cn/news/jujiao/',    #聚焦
            'http://www.foodscn.cn/news/jianguan/'   #监管

        ];

        self.urls_name = ['要闻'];

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url = url, callback = self.parse);

    def parse(self, response):
        print("....【中国安全食品网】... " + response.url);

