# -*- coding: utf-8 -*-

import scrapy
import os,time
from .upload import *
from ..items import *

class FoodSpider(scrapy.Spider):
    name = "foodcfsn"

    def __init__(self):
    	self.major_list = [u'酒业', u'饮品', u'乳业', u'婴幼', u'零食', u'茶业', u'粮油', u'糖业', u'肉畜', u'水产', u'果蔬', u'保健'];

    def start_requests(self):
    	urls = [
    		'http://www.cfsn.cn',  #中国食品安全网
    	]
    	print ("Start Time: (%s)" %time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())));
    	for url in urls:
        	yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print("....【中国食品安全网】... " + response.url);
        a_selectors = response.xpath("//div[@class='nav']/div[@class='wal']/ul/li");
        #print a_selectors
        for selector in a_selectors:
        	text = selector.xpath("string()").extract_first();
        	link = selector.xpath("./a/@href").extract_first();
        	#print text,link
        	for major in self.major_list:
        		if (text == major):
	        		info = {}                #创建信息参数
	        		info['major'] = text;
	        		request = response.follow(link, callback=self.parse_major);
	        		request.meta['info']=info;    #传递参数
	        		yield request;

    def parse_major(self, response):
    	info_p = response.meta['info'];
    	print("major:" + info_p['major'] + response.url);

    	info = {}                #创建信息参数
    	info['major'] = info_p['major'];

    	#头条
    	div_selectors = response.xpath("//div[@class='indexPart2']");
    	h1 = div_selectors.xpath('./h1/a');
    	h1_text = h1.xpath('string()').extract_first();
    	h1_link = h1.xpath('@href').extract_first();
    	request = response.follow(h1_link, callback=self.parse_upload);
    	request.meta['info']=info;    #传递参数
    	yield request;
    	
    	#时政新闻和行业新闻
    	a_selectors = response.xpath("//div[@class='fr list']//a");
    	for selector in a_selectors:
    		text = selector.xpath("string()").extract_first();
    		link = selector.xpath("@href").extract_first();
	    	request = response.follow(link, callback=self.parse_upload);
	    	request.meta['info']=info;    #传递参数
	    	yield request;



    def parse_header(self, response):
    	info_p = response.meta['info'];
    	#print("parse_header:" + info_p['major'] + response.url);
    	div_selectors = response.xpath("//div[@class='fl w655 newShow']");
    	head_text = div_selectors.xpath('./h2[@class="title"]/text()').extract_first();
    	#head_text = head.xpath('text()').extract_first();
    	print (head_text);
    	date = div_selectors.xpath('./div[@class="msg"]/div/text()').extract_first();       #时间
    	come = div_selectors.xpath('./div[@class="msg"]/div/span/text()').extract_first();  #源自
    	print (date,come);
    	content = div_selectors.xpath('./div[@class="content"]/p');
    	content_text = content.xpath('string()').extract_first();
    	print (content_text);
    	print ("------------------------------\r\n");



    def parse_upload(self, response):    
        info_p = response.meta['info'];

        div_selectors = response.xpath("//div[@class='fl w655 newShow']");
        #标题
        title = div_selectors.xpath('./h2[@class="title"]/text()').extract_first(); 
        #源自
        source = div_selectors.xpath('./div[@class="msg"]/div/span/text()').extract_first();
        source = source.split('：')[-1];
        #时间
        date = div_selectors.xpath('./div[@class="msg"]/div/text()').extract_first() + ":00";       #时间 加上秒
        #内容
        content = div_selectors.xpath('./div[@class="content"]/p');
        content_text = content.xpath('string()').extract_first();

        print ('title:', title);
        print ('source:', source);
        print ('publish:', date);

        item = FoodCfsnItem();
        item['major'] = info_p['major'];
        item['title'] = title;
        item['publish'] = date;
        item['source'] = source;
        item['content'] = content_text;
        item['content_len'] = len(content_text);

        yield item;




