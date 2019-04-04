#coding:utf-8

import scrapy
import re


class FoodSpider(scrapy.Spider):
    name = "foodmate"

    def start_requests(self):
        urls = [
            'http://down.foodmate.net/standard/index.html',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
    	# 打印spider正在进行的事务
    	print("start0000000000000000000000000000000000000000000000000000");
    	print(response.url);
    	# 获取所有<a>标签
    	a_selectors = response.xpath("//a[@title]");
    	# 对每个标签进行循环操作
    	for selector in a_selectors:
    		# 解析出链接的文本
    		text = selector.xpath("text()").extract_first()
    		#print(text);
    		# 解析出链接的网址
    		link = selector.xpath("@href").extract_first();
    		#text.decode('utf-8');
    		if ((text != None) and (text == u"国内标准")):
    			print(text);
    			print(link);
    			print("");
    			yield response.follow(link, callback=self.parse_standard_inland);
        #page = response.url.split("/")[-2]
        #filename = 'food-%s.html' % page
        #with open(filename, 'wb') as f:
        #    f.write(response.body)
        #self.log('Saved file %s' % filename)

    def parse_standard_inland(self, response):
    	print("--------------国内标准-------------------------------------------------------------------");
    	print(response.url);
    	a_selectors = response.xpath("//a[@href]");
    	for selector in a_selectors:
    		text = selector.xpath("text()").extract_first();
    		link = selector.xpath("@href").extract_first();
    		if ((text != None) and (text == u"国家标准")):
    			print(text);
    			print(link);
    			yield response.follow(link, callback=self.parse_standard_inland_1);


    def parse_standard_inland_1(self, response):
    	print("--------------国家标准--------------------------------------------------------------------");
    	print(response.url);
    	#filename = '国家标准1.html';
    	#with open(filename, 'wb') as f:
    	#	f.write(response.body);
    	a_selectors = response.xpath('//div[@class="bz_list"]/ul/li');
    	#a_selectors = response.xpath("//a[@title]");
    	#print a_selectors
    	count = 0;
    	for selector in a_selectors:
    		#print selector
    		a = selector.xpath("./div/ul/a");
    		#print a
    		#print(text)
    		link = a.xpath('@href').extract_first();
    		#print(link)
    		img = a.xpath('./img[contains(@src, "xxyx.gif")]').extract_first();
    		if (img != None):
    			print('---%d------------------------------' %(count));
    			count = count + 1;
    			#print(u'现行有效')
    			head = a.xpath("string()").extract_first();
    			print(head)
    			span = selector.xpath('./div/ul/span[@class="lb_ft"]');
    			text = span.xpath("string()").extract_first();
    			print(text);
    			span = selector.xpath('./div/ul/span[@class="lb_bt"]');
    			text = span.xpath("string()").extract_first();
    			print(text);
    			span = selector.xpath('./div/ul/span[@class="lb_bq"]');
    			text = span.xpath("string()").extract_first();
    			print(text);
    			yield response.follow(link, callback=self.parse_standard_inland_2);

    		#if ((text != None)):
    		#	print(text);

    def parse_standard_inland_2(self, response):
    	print('---------------------%s---------------------------');
    	a_selectors = response.xpath('//div[@class="title2"]');
    	for selector in a_selectors:
    		span = selector.xpath('./span');
    		text = span.xpath("string()").extract_first();
    		print(text)
    		describe = selector.xpath('//div[@class="bznr_box"]');
    		#print(describe)
    		text = describe.xpath('string()').extract_first();
    		print(text);
    		downLink = response.xpath('//a[@class="telecom" and @href]')
    		downLink = downLink.xpath('@href').extract_first();
    		print('PDF file download link:  %s' %downLink)
    		yield response.follow(downLink, callback=self.parse_standard_inland_3);

    def parse_standard_inland_3(self, response):
    	print('donwload pdf file');







